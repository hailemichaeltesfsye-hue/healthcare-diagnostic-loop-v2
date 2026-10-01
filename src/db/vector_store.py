"""Strategic memory layer utilizing a lightweight local implementation.

This store handles historical clinical profile context injection
without requiring the native ChromaDB/HNSW index.
"""

from typing import Dict, List


class ClinicalVectorStore:
    """Manage historical clinical cases for the diagnostic workflow."""

    def __init__(self) -> None:
        """Initialize the in-memory historical case store."""

        self.records: Dict[str, Dict[str, str]] = {
            "id_1": {
                "document": (
                    "Patient with severe hypertension managed via Lisinopril 20mg. "
                    "History of high potassium."
                ),
                "case_id": "H101",
            },
            "id_2": {
                "document": (
                    "Chronic type-2 diabetic patient utilizing Metformin 1000mg "
                    "twice daily. Normal kidney function panels."
                ),
                "case_id": "D202",
            },
            "id_3": {
                "document": (
                    "Migraine case displaying resistance to OTC analgesics. "
                    "Managed successfully via Sumatriptan titration."
                ),
                "case_id": "M303",
            },
        }

    def search_similar_cases(
        self,
        query_text: str,
        max_results: int = 1,
    ) -> List[str]:
        """
        Find historically related cases using lightweight keyword matching.

        Args:
            query_text: Clinical text used to retrieve related cases.
            max_results: Maximum number of documents to return.

        Returns:
            Matching historical documents, or a deterministic no-match message.

        Raises:
            ValueError: If the query is blank or the result limit is invalid.
        """

        if not query_text.strip():
            raise ValueError(
                "query_text must contain non-whitespace characters"
            )

        if max_results < 1:
            raise ValueError(
                "max_results must be greater than zero"
            )

        query_words = {
            word.strip(".,!?;:()[]{}").lower()
            for word in query_text.split()
            if len(word.strip(".,!?;:()[]{}")) >= 3
        }

        scored_cases = []

        for record in self.records.values():
            document = record["document"]

            document_words = {
                word.strip(".,!?;:()[]{}").lower()
                for word in document.split()
                if len(word.strip(".,!?;:()[]{}")) >= 3
            }

            score = len(query_words.intersection(document_words))

            if score > 0:
                scored_cases.append((score, document))

        scored_cases.sort(key=lambda item: item[0], reverse=True)

        if scored_cases:
            return [
                document
                for _, document in scored_cases[:max_results]
            ]

        return [
            "No high-confidence semantic matches recovered from historical memory store."
        ]