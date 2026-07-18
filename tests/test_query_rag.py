import unittest

from src.query_rag import find_best_section_reference


class QueryRagRoutingTests(unittest.TestCase):
    def test_broad_query_should_not_force_a_specific_section(self):
        self.assertIsNone(find_best_section_reference("What is java?"))


if __name__ == "__main__":
    unittest.main()
