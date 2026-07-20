import unittest

from src.query_rag import find_best_section_reference


class QueryRagRoutingTests(unittest.TestCase):
    def test_broad_query_should_not_force_a_specific_section(self):
        self.assertEqual(find_best_section_reference("What is java?"), [])

    def test_targeted_query_returns_confidence_ranked_sections(self):
        references = find_best_section_reference("How does binary search work in trees?")

        self.assertGreaterEqual(len(references), 2)
        self.assertEqual(references[0].section_id, "11.1")
        self.assertGreater(references[0].confidence, references[1].confidence)


if __name__ == "__main__":
    unittest.main()
