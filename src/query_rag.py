import ast
import os
import re
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

_SECTION_ROUTING_STOPWORDS = {
      "a",
      "an",
      "and",
      "are",
      "can",
      "do",
      "does",
      "for",
      "from",
      "how",
      "in",
      "is",
      "of",
      "on",
      "the",
      "to",
      "what",
      "when",
      "where",
      "which",
      "why",
      "with",
}


@dataclass(frozen=True)
class SectionReference:
      section_id: str
      confidence: float
      matched_terms: tuple[str, ...]
      title_terms: tuple[str, ...]


def _format_section_reason(section_reference: SectionReference) -> str:
      matched_terms = ", ".join(section_reference.matched_terms) if section_reference.matched_terms else "no token overlap"
      title_terms = ", ".join(section_reference.title_terms)
      return (
            f"matched terms [{matched_terms}] against title terms [{title_terms}] "
            f"(confidence={section_reference.confidence:.3f})"
      )


def _print_context_chunks(chunks: list[Any], label: str) -> None:
      if not chunks:
            print(f"   {label}: no chunks retrieved")
            return

      print(f"   {label}: {len(chunks)} chunk(s)")
      for index, chunk in enumerate(chunks, start=1):
            metadata = getattr(chunk, "metadata", {}) or {}
            page_content = getattr(chunk, "page_content", "")
            snippet = " ".join(page_content.split())[:240]
            print(
                  f"      [{index}] section={metadata.get('parent_section')} "
                  f"page={metadata.get('start_page')} confidence={metadata.get('section_confidence', 'n/a')}"
            )
            print(f"          text={snippet}")


def _normalize_token(token: str) -> str:
      if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
            return token[:-1]

      return token


def _tokenize(text: str) -> list[str]:
      return [_normalize_token(token) for token in re.findall(r"[a-z0-9]+", text.lower())]


@lru_cache(maxsize=1)
def _get_toc_map():
      source_path = Path(__file__).with_name("document_utils.py")
      source_text = source_path.read_text(encoding="utf-8")
      module = ast.parse(source_text, filename=str(source_path))

      for node in module.body:
            if not isinstance(node, ast.Assign):
                  continue

            for target in node.targets:
                  if isinstance(target, ast.Name) and target.id == "TOC_MAP":
                        return ast.literal_eval(node.value)

      raise RuntimeError("Unable to load TOC_MAP from src/document_utils.py")


def find_best_section_reference(query_text: str, limit: int = 3) -> list[SectionReference]:
      """
      A lightweight router that scans the table-of-contents titles to find a
      confidence-ranked shortlist of section matches for targeted queries.
      """
      query_terms = {
            token
            for token in _tokenize(query_text)
            if token not in _SECTION_ROUTING_STOPWORDS
      }

      if not query_terms:
            return []

      toc_map = _get_toc_map()
      candidate_sections: list[tuple[str, float, int]] = []

      for section_id, (page, title) in toc_map.items():
            title_terms = [
                  token
                  for token in _tokenize(title)
                  if token not in _SECTION_ROUTING_STOPWORDS
            ]

            if not title_terms:
                  continue

            matches = sum(1 for token in title_terms if token in query_terms)

            if matches == 0:
                  continue

            # Keep broad questions from forcing a narrow section filter.
            if len(title_terms) > 1 and matches < 2:
                  continue

            confidence = matches / len(title_terms)
            candidate_sections.append((section_id, confidence, matches, tuple(sorted(query_terms & set(title_terms))), tuple(title_terms)))

      candidate_sections.sort(
            key=lambda item: (
                  -item[2],
                  -item[1],
                  toc_map[item[0]][0],
                  item[0],
            )
      )

      return [
            SectionReference(
                  section_id=section_id,
                  confidence=round(confidence, 3),
                  matched_terms=matched_terms,
                  title_terms=title_terms,
            )
            for section_id, confidence, _, matched_terms, title_terms in candidate_sections[:limit]
      ]


def build_section_aware_retriever(
      vector_store: Any,
      section_references: list[SectionReference],
      top_k_per_section: int = 2,
) -> Any:
      from langchain_core.documents import Document
      from langchain_core.runnables import RunnableLambda

      def retrieve(query_input: Any) -> list[Document]:
            query = query_input["input"] if isinstance(query_input, dict) else query_input
            retrieved_documents: list[Document] = []
            seen_documents: set[tuple[Any, Any, Any]] = set()

            print("🧭 Section shortlist used for retrieval:")
            for section_reference in section_references:
                  print(f"   - Section {section_reference.section_id}: {_format_section_reason(section_reference)}")

            for section_reference in section_references:
                  section_documents = vector_store.similarity_search(
                        query,
                        k=top_k_per_section,
                        filter={"parent_section": section_reference.section_id},
                  )

                  for document in section_documents:
                        document_key = (
                              document.metadata.get("parent_section"),
                              document.metadata.get("start_page"),
                              document.page_content,
                        )

                        if document_key in seen_documents:
                              continue

                        seen_documents.add(document_key)
                        retrieved_documents.append(
                              Document(
                                    page_content=document.page_content,
                                    metadata={
                                          **document.metadata,
                                          "section_confidence": section_reference.confidence,
                                    },
                              )
                        )

            _print_context_chunks(retrieved_documents, "Context chunks sent to the LLM")

            return retrieved_documents

      return RunnableLambda(retrieve)


def build_global_retriever(vector_store: Any, top_k: int = 3) -> Any:
      from langchain_core.documents import Document
      from langchain_core.runnables import RunnableLambda

      def retrieve(query_input: Any) -> list[Document]:
            query = query_input["input"] if isinstance(query_input, dict) else query_input
            retrieved_documents = vector_store.similarity_search(query, k=top_k)

            print("🌐 Global search used because no confident section shortlist was found.")
            _print_context_chunks(retrieved_documents, "Context chunks sent to the LLM")

            return retrieved_documents

      return RunnableLambda(retrieve)


def ask_dsa_system_guided(query_text: str):
      from langchain_classic.chains import create_retrieval_chain
      from langchain_classic.chains.combine_documents import create_stuff_documents_chain
      from langchain_google_genai import ChatGoogleGenerativeAI
      from langchain_ollama import ChatOllama

      from src import config
      from src.database import get_vector_store
      from langchain_core.prompts import ChatPromptTemplate

      toc_map = _get_toc_map()

      vector_store = get_vector_store()

      section_references = find_best_section_reference(query_text)

      if section_references:
            print("🎯 Reference Router matched query to these sections:")
            for section_reference in section_references:
                  print(
                        f"   - Section {section_reference.section_id} "
                        f"({toc_map[section_reference.section_id][1]}): "
                        f"{_format_section_reason(section_reference)}"
                  )

            retriever = build_section_aware_retriever(
                  vector_store=vector_store,
                  section_references=section_references,
                  top_k_per_section=2,
            )
      else:
            print("🌐 No direct reference matched. Performing a global database search...")
            retriever = build_global_retriever(vector_store=vector_store, top_k=3)

      llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_output_tokens=config.LLM_MAX_TOKENS,
      )

      prompt_template = ChatPromptTemplate.from_messages(
            [
                  ("system", config.SYSTEM_PROMPT),
                  ("human", "{input}"),
            ]
      )
      document_chain = create_stuff_documents_chain(
            llm=llm,
            prompt=prompt_template,
      )
      return create_retrieval_chain(retriever=retriever, combine_docs_chain=document_chain)