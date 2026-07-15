from pypdf import PdfReader
from langchain_core.documents import Document

# The exact structural roadmap extracted from your Table of Contents
# Format: "Section_ID": (Start_Page, "Topic Title")
TOC_MAP = {
    # Chapter 1
    "1.0": (1, "Java Primer"),
    "1.1": (2, "Getting Started"),
    "1.1.1": (4, "Base Types"),
    "1.2": (5, "Classes and Objects"),
    "1.2.1": (6, "Creating and Using Objects"),
    "1.2.2": (9, "Defining a Class"),
    "1.3": (17, "Strings, Wrappers, Arrays, and Enum Types"),
    "1.4": (23, "Expressions"),
    "1.4.1": (23, "Literals"),
    "1.4.2": (24, "Operators"),
    "1.4.3": (28, "Type Conversions"),
    "1.5": (30, "Control Flow"),
    "1.5.1": (30, "The If and Switch Statements"),
    "1.5.2": (33, "Loops"),
    "1.5.3": (37, "Explicit Control-Flow Statements"),
    "1.6": (38, "Simple Input and Output"),
    "1.7": (41, "An Example Program"),
    "1.8": (44, "Packages and Imports"),
    "1.9": (46, "Software Development"),
    "1.9.1": (46, "Design"),
    "1.9.2": (48, "Pseudocode"),
    "1.9.3": (49, "Coding"),
    "1.9.4": (50, "Documentation and Style"),
    "1.9.5": (53, "Testing and Debugging"),
    "1.10": (55, "Exercises"),

    # Chapter 2
    "2.0": (59, "Object-Oriented Design"),
    "2.1": (60, "Goals, Principles, and Patterns"),
    "2.1.1": (60, "Object-Oriented Design Goals"),
    "2.1.2": (61, "Object-Oriented Design Principles"),
    "2.1.3": (63, "Design Patterns"),
    "2.2": (64, "Inheritance"),
    "2.2.1": (65, "Extending the CreditCard Class"),
    "2.2.2": (68, "Polymorphism and Dynamic Dispatch"),
    "2.2.3": (69, "Inheritance Hierarchies"),
    "2.3": (76, "Interfaces and Abstract Classes"),
    "2.3.1": (76, "Interfaces in Java"),
    "2.3.2": (79, "Multiple Inheritance for Interfaces"),
    "2.3.3": (80, "Abstract Classes"),
    "2.4": (82, "Exceptions"),
    "2.4.1": (82, "Catching Exceptions"),
    "2.4.2": (85, "Throwing Exceptions"),
    "2.4.3": (86, "Java's Exception Hierarchy"),
    "2.5": (88, "Casting and Generics"),
    "2.5.1": (88, "Casting"),
    "2.5.2": (91, "Generics"),
    "2.6": (96, "Nested Classes"),
    "2.7": (97, "Exercises"),

    # Chapter 3
    "3.0": (103, "Fundamental Data Structures"),
    "3.1": (104, "Using Arrays"),
    "3.1.1": (104, "Storing Game Entries in an Array"),
    "3.1.2": (110, "Sorting an Array"),
    "3.1.3": (112, "java.util Methods for Arrays and Random Numbers"),
    "3.1.4": (115, "Simple Cryptography with Character Arrays"),
    "3.1.5": (118, "Two-Dimensional Arrays and Positional Games"),
    "3.2": (122, "Singly Linked Lists"),
    "3.2.1": (126, "Implementing a Singly Linked List Class"),
    "3.3": (128, "Circularly Linked Lists"),
    "3.3.1": (128, "Round-Robin Scheduling"),
    "3.3.2": (129, "Designing and Implementing a Circularly Linked List"),
    "3.4": (132, "Doubly Linked Lists"),
    "3.4.1": (135, "Implementing a Doubly Linked List Class"),
    "3.5": (138, "Equivalence Testing"),
    "3.5.1": (139, "Equivalence Testing with Arrays"),
    "3.5.2": (140, "Equivalence Testing with Linked Lists"),
    "3.6": (141, "Cloning Data Structures"),
    "3.6.1": (142, "Cloning Arrays"),
    "3.6.2": (144, "Cloning Linked Lists"),
    "3.7": (145, "Exercises"),

    # Chapter 4
    "4.0": (149, "Algorithm Analysis"),
    "4.1": (151, "Experimental Studies"),
    "4.1.1": (154, "Moving Beyond Experimental Analysis"),
    "4.2": (156, "The Seven Functions Used in This Book"),
    "4.2.1": (163, "Comparing Growth Rates"),
    "4.3": (164, "Asymptotic Analysis"),
    "4.3.1": (164, "The Big-Oh Notation"),
    "4.3.2": (168, "Comparative Analysis"),
    "4.3.3": (170, "Examples of Algorithm Analysis"),
    "4.4": (178, "Simple Justification Techniques"),
    "4.4.1": (178, "By Example"),
    "4.4.2": (178, "The Contra Attack"),
    "4.4.3": (179, "Induction and Loop Invariants"),
    "4.5": (182, "Exercises"),

    # Chapter 5
    "5.0": (189, "Recursion"),
    "5.1": (191, "Illustrative Examples"),
    "5.1.1": (191, "The Factorial Function"),
    "5.1.2": (193, "Drawing an English Ruler"),
    "5.1.3": (196, "Binary Search"),
    "5.1.4": (198, "File Systems"),
    "5.2": (202, "Analyzing Recursive Algorithms"),
    "5.3": (206, "Further Examples of Recursion"),
    "5.3.1": (206, "Linear Recursion"),
    "5.3.2": (211, "Binary Recursion"),
    "5.3.3": (212, "Multiple Recursion"),
    "5.4": (214, "Designing Recursive Algorithms"),
    "5.5": (215, "Recursion Run Amok"),
    "5.5.1": (218, "Maximum Recursive Depth in Java"),
    "5.6": (219, "Eliminating Tail Recursion"),
    "5.7": (221, "Exercises"),

    # Chapter 6
    "6.0": (225, "Stacks, Queues, and Deques"),
    "6.1": (226, "Stacks"),
    "6.1.1": (227, "The Stack Abstract Data Type"),
    "6.1.2": (230, "A Simple Array-Based Stack Implementation"),
    "6.1.3": (233, "Implementing a Stack with a Singly Linked List"),
    "6.1.4": (234, "Reversing an Array Using a Stack"),
    "6.1.5": (235, "Matching Parentheses and HTML Tags"),
    "6.2": (238, "Queues"),
    "6.2.1": (239, "The Queue Abstract Data Type"),
    "6.2.2": (241, "Array-Based Queue Implementation"),
    "6.2.3": (245, "Implementing a Queue with a Singly Linked List"),
    "6.2.4": (246, "A Circular Queue"),
    "6.3": (248, "Double-Ended Queues"),
    "6.3.1": (248, "The Deque Abstract Data Type"),
    "6.3.2": (250, "Implementing a Deque"),
    "6.3.3": (251, "Deques in the Java Collections Framework"),
    "6.4": (252, "Exercises"),

    # Chapter 7
    "7.0": (257, "List and Iterator ADTs"),
    "7.1": (258, "The List ADT"),
    "7.2": (260, "Array Lists"),
    "7.2.1": (263, "Dynamic Arrays"),
    "7.2.2": (264, "Implementing a Dynamic Array"),
    "7.2.3": (265, "Amortized Analysis of Dynamic Arrays"),
    "7.2.4": (269, "Java's StringBuilder class"),
    "7.3": (270, "Positional Lists"),
    "7.3.1": (272, "Positions"),
    "7.3.2": (272, "The Positional List Abstract Data Type"),
    "7.3.3": (276, "Doubly Linked List Implementation"),
    "7.4": (282, "Iterators"),
    "7.4.1": (283, "The Iterable Interface and Java's For-Each Loop"),
    "7.4.2": (284, "Implementing Iterators"),
    "7.5": (288, "The Java Collections Framework"),
    "7.5.1": (289, "List Iterators in Java"),
    "7.5.2": (290, "Comparison to Our Positional List ADT"),
    "7.5.3": (291, "List-Based Algorithms in the Java Collections Framework"),
    "7.6": (293, "Sorting a Positional List"),
    "7.7": (294, "Case Study: Maintaining Access Frequencies"),
    "7.7.1": (294, "Using a Sorted List"),
    "7.7.2": (297, "Using a List with the Move-to-Front Heuristic"),
    "7.8": (300, "Exercises"),

    # Chapter 8
    "8.0": (307, "Trees"),
    "8.1": (308, "General Trees"),
    "8.1.1": (309, "Tree Definitions and Properties"),
    "8.1.2": (312, "The Tree Abstract Data Type"),
    "8.1.3": (314, "Computing Depth and Height"),
    "8.2": (317, "Binary Trees"),
    "8.2.1": (319, "The Binary Tree Abstract Data Type"),
    "8.2.2": (321, "Properties of Binary Trees"),
    "8.3": (323, "Implementing Trees"),
    "8.3.1": (323, "Linked Structure for Binary Trees"),
    "8.3.2": (331, "Array-Based Representation of a Binary Tree"),
    "8.3.3": (333, "Linked Structure for General Trees"),
    "8.4": (334, "Tree Traversal Algorithms"),
    "8.4.1": (334, "Preorder and Postorder Traversals of General Trees"),
    "8.4.2": (336, "Breadth-First Tree Traversal"),
    "8.4.3": (337, "Inorder Traversal of a Binary Tree"),
    "8.4.4": (339, "Implementing Tree Traversals in Java"),
    "8.4.5": (343, "Applications of Tree Traversals"),
    "8.4.6": (348, "Euler Tours"),
    "8.5": (350, "Exercises"),

    # Chapter 9
    "9.0": (359, "Priority Queues"),
    "9.1": (360, "The Priority Queue Abstract Data Type"),
    "9.1.1": (360, "Priorities"),
    "9.1.2": (361, "The Priority Queue ADT"),
    "9.2": (362, "Implementing a Priority Queue"),
    "9.2.1": (362, "The Entry Composite"),
    "9.2.2": (363, "Comparing Keys with Total Orders"),
    "9.2.3": (364, "The AbstractPriorityQueue Base Class"),
    "9.2.4": (366, "Implementing a Priority Queue with an Unsorted List"),
    "9.2.5": (368, "Implementing a Priority Queue with a Sorted List"),
    "9.3": (370, "Heaps"),
    "9.3.1": (370, "The Heap Data Structure"),
    "9.3.2": (372, "Implementing a Priority Queue with a Heap"),
    "9.3.3": (379, "Analysis of a Heap-Based Priority Queue"),
    "9.3.4": (380, "Bottom-Up Heap Construction"),
    "9.3.5": (384, "Using the java.util.PriorityQueue Class"),
    "9.4": (385, "Sorting with a Priority Queue"),
    "9.4.1": (386, "Selection-Sort and Insertion-Sort"),
    "9.4.2": (388, "Heap-Sort"),
    "9.5": (390, "Adaptable Priority Queues"),
    "9.5.1": (391, "Location-Aware Entries"),
    "9.5.2": (392, "Implementing an Adaptable Priority Queue"),
    "9.6": (395, "Exercises"),

    # Chapter 10
    "10.0": (401, "Maps, Hash Tables, and Skip Lists"),
    "10.1": (402, "Maps"),
    "10.1.1": (403, "The Map ADT"),
    "10.1.2": (405, "Application: Counting Word Frequencies"),
    "10.1.3": (406, "An AbstractMap Base Class"),
    "10.1.4": (408, "A Simple Unsorted Map Implementation"),
    "10.2": (410, "Hash Tables"),
    "10.2.1": (411, "Hash Functions"),
    "10.2.2": (417, "Collision-Handling Schemes"),
    "10.2.3": (420, "Load Factors, Rehashing, and Efficiency"),
    "10.2.4": (422, "Java Hash Table Implementation"),
    "10.3": (428, "Sorted Maps"),
    "10.3.1": (429, "Sorted Search Tables"),
    "10.3.2": (433, "Two Applications of Sorted Maps"),
    "10.4": (436, "Skip Lists"),
    "10.4.1": (438, "Search and Update Operations in a Skip List"),
    "10.4.2": (442, "Probabilistic Analysis of Skip Lists"),
    "10.5": (445, "Sets, Multisets, and Multimaps"),
    "10.5.1": (445, "The Set ADT"),
    "10.5.2": (447, "The Multiset ADT"),
    "10.5.3": (448, "The Multimap ADT"),
    "10.6": (451, "Exercises"),

    # Chapter 11
    "11.0": (459, "Search Trees"),
    "11.1": (460, "Binary Search Trees"),
    "11.1.1": (461, "Searching Within a Binary Search Tree"),
    "11.1.2": (463, "Insertions and Deletions"),
    "11.1.3": (466, "Java Implementation"),
    "11.1.4": (470, "Performance of a Binary Search Tree"),
    "11.2": (472, "Balanced Search Trees"),
    "11.2.1": (475, "Java Framework for Balancing Search Trees"),
    "11.3": (479, "AVL Trees"),
    "11.3.1": (481, "Update Operations"),
    "11.3.2": (486, "Java Implementation"),
    "11.4": (488, "Splay Trees"),
    "11.4.1": (488, "Splaying"),
    "11.4.2": (492, "When to Splay"),
    "11.4.3": (494, "Java Implementation"),
    "11.4.4": (495, "Amortized Analysis of Splaying"),
    "11.5": (500, "(2,4) Trees"),
    "11.5.1": (500, "Multiway Search Trees"),
    "11.5.2": (503, "(2,4)-Tree Operations"),
    "11.6": (510, "Red-Black Trees"),
    "11.6.1": (512, "Red-Black Tree Operations"),
    "11.6.2": (522, "Java Implementation"),
    "11.7": (525, "Exercises"),

    # Chapter 12
    "12.0": (531, "Sorting and Selection"),
    "12.1": (532, "Merge-Sort"),
    "12.1.1": (532, "Divide-and-Conquer"),
    "12.1.2": (537, "Array-Based Implementation of Merge-Sort"),
    "12.1.3": (538, "The Running Time of Merge-Sort"),
    "12.1.4": (540, "Merge-Sort and Recurrence Equations"),
    "12.1.5": (541, "Alternative Implementations of Merge-Sort"),
    "12.2": (544, "Quick-Sort"),
    "12.2.1": (551, "Randomized Quick-Sort"),
    "12.2.2": (553, "Additional Optimizations for Quick-Sort"),
    "12.3": (556, "Studying Sorting through an Algorithmic Lens"),
    "12.3.1": (556, "Lower Bound for Sorting"),
    "12.3.2": (558, "Linear-Time Sorting: Bucket-Sort and Radix-Sort"),
    "12.4": (561, "Comparing Sorting Algorithms"),
    "12.5": (563, "Selection"),
    "12.5.1": (563, "Prune-and-Search"),
    "12.5.2": (564, "Randomized Quick-Select"),
    "12.5.3": (565, "Analyzing Randomized Quick-Select"),
    "12.6": (566, "Exercises"),

    # Chapter 13
    "13.0": (573, "Text Processing"),
    "13.1": (574, "Abundance of Digitized Text"),
    "13.1.1": (575, "Notations for Character Strings"),
    "13.2": (576, "Pattern-Matching Algorithms"),
    "13.2.1": (576, "Brute Force"),
    "13.2.2": (578, "The Boyer-Moore Algorithm"),
    "13.2.3": (582, "The Knuth-Morris-Pratt Algorithm"),
    "13.3": (586, "Tries"),
    "13.3.1": (586, "Standard Tries"),
    "13.3.2": (590, "Compressed Tries"),
    "13.3.3": (592, "Suffix Tries"),
    "13.3.4": (594, "Search Engine Indexing"),
    "13.4": (595, "Text Compression and the Greedy Method"),
    "13.4.1": (596, "The Huffman Coding Algorithm"),
    "13.4.2": (597, "The Greedy Method"),
    "13.5": (598, "Dynamic Programming"),
    "13.5.1": (598, "Matrix Chain-Product"),
    "13.5.2": (601, "DNA and Text Sequence Alignment"),
    "13.6": (605, "Exercises"),

    # Chapter 14
    "14.0": (611, "Graph Algorithms"),
    "14.1": (612, "Graphs"),
    "14.1.1": (618, "The Graph ADT"),
    "14.2": (619, "Data Structures for Graphs"),
    "14.2.1": (620, "Edge List Structure"),
    "14.2.2": (622, "Adjacency List Structure"),
    "14.2.3": (624, "Adjacency Map Structure"),
    "14.2.4": (625, "Adjacency Matrix Structure"),
    "14.2.5": (626, "Java Implementation"),
    "14.3": (630, "Graph Traversals"),
    "14.3.1": (631, "Depth-First Search"),
    "14.3.2": (636, "DFS Implementation and Extensions"),
    "14.3.3": (640, "Breadth-First Search"),
    "14.4": (643, "Transitive Closure"),
    "14.5": (647, "Directed Acyclic Graphs"),
    "14.5.1": (647, "Topological Ordering"),
    "14.5.2": (651, "Shortest Paths"),
    "14.6.1": (651, "Weighted Graphs"),
    "14.6.2": (653, "Dijkstra's Algorithm"),
    "14.7": (662, "Minimum Spanning Trees"),
    "14.7.1": (664, "Prim-Jarnik Algorithm"),
    "14.7.2": (667, "Kruskal's Algorithm"),
    "14.7.3": (672, "Disjoint Partitions and Union-Find Structures"),
    "14.8": (677, "Exercises"),

    # Chapter 15
    "15.0": (687, "Memory Management and B-Trees"),
    "15.1": (688, "Memory Management"),
    "15.1.1": (688, "Stacks in the Java Virtual Machine"),
    "15.1.2": (691, "Allocating Space in the Memory Heap"),
    "15.1.3": (693, "Garbage Collection"),
    "15.2": (695, "Memory Hierarchies and Caching"),
    "15.2.1": (695, "Memory Systems"),
    "15.2.2": (696, "Caching Strategies"),
    "15.3": (701, "External Searching and B-Trees"),
    "15.3.1": (702, "(a,b) Trees"),
    "15.3.2": (704, "B-Trees"),
    "15.4": (705, "External-Memory Sorting"),
    "15.4.1": (706, "Multiway Merging"),
    "15.5": (707, "Exercises"),
}

def split_pdf_by_toc(pdf_path: str, offset: int = 0) -> list[Document]:
    """
    Slices the PDF into large parent documents based strictly on the hardcoded TOC.
    'offset' handles shifting if physical PDF pages don't line up perfectly with book pages.
    """
    reader = PdfReader(pdf_path)
    total_pdf_pages = len(reader.pages)
    
    # Sort keys sequentially by page number
    sorted_keys = sorted(TOC_MAP.keys(), key=lambda k: TOC_MAP[k][0])
    
    parent_documents = []
    
    for i, key in enumerate(sorted_keys):
        section_id = key
        title = TOC_MAP[key][1]
        
        # Calculate book start page adjusted by the PDF file offset
        book_start = TOC_MAP[key][0]
        start_idx = max(0, book_start + offset - 1) 
        
        # End index is the start index of the next section, or the last page of the PDF
        if i + 1 < len(sorted_keys):
            next_key = sorted_keys[i + 1]
            book_end = TOC_MAP[next_key][0]
            end_idx = min(total_pdf_pages, book_end + offset - 1)
        else:
            end_idx = total_pdf_pages
            
        # Extract text within this explicit section range
        section_text = ""
        for page_num in range(start_idx, end_idx):
            page_text = reader.pages[page_num].extract_text()
            if page_text:
                section_text += page_text + "\n"
                
        # Generate parent chunk with precise structure tags
        if section_text.strip():
            doc = Document(
                page_content=section_text,
                metadata={
                    "section_id": section_id,
                    "title": title,
                    "start_page": book_start,
                    "pdf_start_page": start_idx + 1,
                    "pdf_end_page": end_idx
                }
            )
            parent_documents.append(doc)
            
    print(f" Successfully sliced PDF into {len(parent_documents)} semantic subtopics.")
    return parent_documents