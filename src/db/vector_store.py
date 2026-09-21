"""
Strategic memory layer utilizing local ChromaDB implementations.

The store handles historical clinical profile context injection and fulfills
the semantic-memory portion of the diagnostic loop architecture.
"""

from typing import Any, Dict, List

import chromadb


class ClinicalVectorStore:
    """Manage semantic vector configuration for historical case tracking."""

    def __init__(self) -> None:
        """
        Initialize an isolated in-memory ChromaDB client and seed its examples.

        An ephemeral client keeps this Part 2 component deterministic and
        deployment-independent. A later deployment can replace the client with
        a persistent ChromaDB implementation without changing the search API.
        """
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name="historical_cases"
        )
        self._seed_mock_data()

    def _seed_mock_data(self) -> None:
        """Seed the collection with representative clinical histories."""
        seeded_ids = {"id_1", "id_2", "id_3"}
        existing = self.collection.get(include=[])
        existing_ids = set(existing.get("ids", []))
        missing_ids = seeded_ids - existing_ids
        if not missing_ids:
            return

        records: Dict[str, Dict[str, str]] = {
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
        ordered_ids = sorted(missing_ids)
        self.collection.add(
            documents=[records[record_id]["document"] for record_id in ordered_ids],
            metadatas=[
                {"case_id": records[record_id]["case_id"]}
                for record_id in ordered_ids
            ],
            ids=ordered_ids,
        )

    def search_similar_cases(
        self,
        query_text: str,
        max_results: int = 1,
    ) -> List[str]:
        """
        Query historical cases using ChromaDB's configured embedding function.

        Args:
            query_text: Clinical text used to retrieve semantically related cases.
            max_results: Maximum number of documents to return; must be positive.

        Returns:
            Matching historical documents, or a deterministic no-match message.

        Raises:
            ValueError: If the query is blank or the result limit is not positive.
        """
        if not query_text.strip():
            raise ValueError("query_text must contain non-whitespace characters")
        if max_results < 1:
            raise ValueError("max_results must be greater than zero")

        results: Dict[str, Any] = self.collection.query(
            query_texts=[query_text],
            n_results=max_results,
        )
        documents = results.get("documents")
        if isinstance(documents, list) and documents and documents[0]:
            return [str(document) for document in documents[0]]
        return [
            "No high-confidence semantic matches recovered from historical memory store."
        ]