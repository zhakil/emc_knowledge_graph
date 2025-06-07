"""
Unit tests for EMCGraphManager.
Dependencies (EntityExtractor, RelationBuilder, Neo4jService) will be mocked.
"""

import unittest
from unittest.mock import MagicMock, AsyncMock, patch, call # AsyncMock for async methods
import asyncio
from dataclasses import asdict


from services.knowledge_graph.graph_manager import EMCGraphManager
from services.knowledge_graph.emc_ontology import (
    NODE_DOCUMENT, NODE_PRODUCT, NODE_EMC_STANDARD, DocumentNode, ProductNode, EMCStandardNode,
    REL_MENTIONS_PRODUCT, REL_HAS_STANDARD
)
# Assuming FileMetadata is defined somewhere accessible for EMCFileProcessor's output,
# or we can mock its structure if graph_manager consumes it.
# For now, we'll assume document_metadata is a simple dict.
# from services.file_processing.emc_file_processor import FileMetadata # If needed

class TestEMCGraphManager(unittest.TestCase):

    def setUp(self):
        # Mock dependencies
        self.mock_entity_extractor = AsyncMock() # EMCEntityExtractor has async methods
        self.mock_relation_builder = AsyncMock() # EMCRelationBuilder has async methods
        self.mock_neo4j_service = MagicMock()    # Neo4jEMCService methods might be sync or async, adjust if needed

        # Instantiate EMCGraphManager with mocked dependencies
        self.graph_manager = EMCGraphManager(
            entity_extractor=self.mock_entity_extractor,
            relation_builder=self.mock_relation_builder,
            neo4j_service=self.mock_neo4j_service
        )

        # Sample document data
        self.sample_text = "ProductX is a new device. It complies with StandardA."
        self.document_id = "doc_test_001"
        self.document_metadata = {
            "file_id": self.document_id, # GraphManager uses this for Document node
            "filename": "test_doc.txt",
            "document_type": "Test Specification",
            "mime_type": "text/plain",
            "size_bytes": 12345
        }

        # Expected entities from extractor (as dicts, like after dataclass conversion)
        self.product_entity_data = ProductNode(name="ProductX", source_document_ids=[self.document_id]).__dict__
        self.standard_entity_data = EMCStandardNode(name="StandardA", source_document_ids=[self.document_id]).__dict__

        self.extracted_entities_raw = [
            {"label": NODE_PRODUCT, "data": self.product_entity_data},
            {"label": NODE_EMC_STANDARD, "data": self.standard_entity_data}
        ]

        # Processed entities as they would be passed to relation_builder (with id_in_document)
        self.entities_for_relation_builder = [
            {"label": NODE_PRODUCT, "data": self.product_entity_data, "id_in_document": f"{NODE_PRODUCT}_ProductX_0"},
            {"label": NODE_EMC_STANDARD, "data": self.standard_entity_data, "id_in_document": f"{NODE_EMC_STANDARD}_StandardA_1"}
        ]

        # Expected relations from builder
        self.extracted_relations = [
            {
                "type": REL_HAS_STANDARD,
                "from_entity_id": self.entities_for_relation_builder[0]["id_in_document"], # ProductX
                "to_entity_id": self.entities_for_relation_builder[1]["id_in_document"],   # StandardA
                "data": {"confidence_score": 0.9, "source_document_ids": [self.document_id]}
            }
        ]


    def test_process_document_content_happy_path(self):
        # Configure mocks to return expected values
        self.mock_entity_extractor.extract_entities.return_value = self.extracted_entities_raw
        self.mock_relation_builder.build_relationships.return_value = self.extracted_relations
        self.mock_neo4j_service.add_emc_entity.return_value = {"status": "merged_node"} # Simplified return
        self.mock_neo4j_service.add_emc_relationship.return_value = {"status": "merged_relationship"}

        # Run the method
        summary = asyncio.run(
            self.graph_manager.process_document_content(
                self.sample_text, self.document_id, self.document_metadata
            )
        )

        # Assertions
        self.assertEqual(summary["status"], "completed")
        self.assertEqual(summary["document_id"], self.document_id)
        self.assertEqual(summary["entities_extracted_count"], 2)
        self.assertEqual(summary["relationships_extracted_count"], 1)
        self.assertEqual(summary["nodes_added_count"], 3) # Doc node + 2 entities
        self.assertEqual(summary["relationships_added_count"], 1)
        self.assertEqual(len(summary["errors"]), 0)

        # Verify mock calls
        self.mock_entity_extractor.extract_entities.assert_called_once_with(
            text_content=self.sample_text, document_id=self.document_id, use_ai=False, use_rules=True
        )
        self.mock_relation_builder.build_relationships.assert_called_once_with(
            entities=self.entities_for_relation_builder, # Check if structure matches
            text_content=self.sample_text, document_id=self.document_id, use_ai=False, use_rules=True
        )

        # Check Document node creation
        self.mock_neo4j_service.add_emc_entity.assert_any_call(
            entity_label=NODE_DOCUMENT,
            entity_data={
                "file_id": self.document_id,
                "name": self.document_metadata["filename"],
                "document_type": self.document_metadata["document_type"],
                "mime_type": self.document_metadata["mime_type"],
                "size_bytes": self.document_metadata["size_bytes"]
            },
            unique_id_field="file_id"
        )

        # Check other entity creations (order might vary)
        self.mock_neo4j_service.add_emc_entity.assert_any_call(
            entity_label=NODE_PRODUCT, entity_data=self.product_entity_data, unique_id_field="name"
        )
        self.mock_neo4j_service.add_emc_entity.assert_any_call(
            entity_label=NODE_EMC_STANDARD, entity_data=self.standard_entity_data, unique_id_field="name"
        )

        # Check relationship creation
        self.mock_neo4j_service.add_emc_relationship.assert_called_once_with(
            from_entity_label=NODE_PRODUCT,
            from_entity_unique_id_value="ProductX", # From self.product_entity_data['name']
            from_entity_unique_id_field="name",
            to_entity_label=NODE_EMC_STANDARD,
            to_entity_unique_id_value="StandardA",   # From self.standard_entity_data['name']
            to_entity_unique_id_field="name",
            relationship_type=REL_HAS_STANDARD,
            relationship_data=self.extracted_relations[0]["data"]
        )

    def test_process_document_no_entities_found(self):
        self.mock_entity_extractor.extract_entities.return_value = [] # No entities
        self.mock_relation_builder.build_relationships.return_value = [] # No relations

        summary = asyncio.run(
            self.graph_manager.process_document_content(
                "No relevant info.", self.document_id, self.document_metadata
            )
        )
        self.assertEqual(summary["status"], "completed") # Completed, but with 0 entities/relations from text
        self.assertEqual(summary["entities_extracted_count"], 0)
        self.assertEqual(summary["relationships_extracted_count"], 0)
        self.assertEqual(summary["nodes_added_count"], 1) # Only Document node
        self.assertEqual(summary["relationships_added_count"], 0)
        self.mock_relation_builder.build_relationships.assert_called_once() # Still called, but with empty entities list


    def test_process_document_neo4j_service_unavailable_at_init(self):
        # Re-initialize GraphManager with Neo4j service that fails on init or is None
        failing_graph_manager = EMCGraphManager(
            entity_extractor=self.mock_entity_extractor,
            relation_builder=self.mock_relation_builder,
            neo4j_service=None # Simulate it being unavailable
        )
        # Ensure the graph_manager's neo4j_service attribute is indeed None
        failing_graph_manager.neo4j_service = None


        self.mock_entity_extractor.extract_entities.return_value = self.extracted_entities_raw
        self.mock_relation_builder.build_relationships.return_value = self.extracted_relations

        summary = asyncio.run(
            failing_graph_manager.process_document_content(
                self.sample_text, self.document_id, self.document_metadata
            )
        )

        self.assertEqual(summary["status"], "completed_without_storage")
        self.assertIn("Neo4j service unavailable, skipping storage.", summary["errors"])
        self.assertEqual(summary["nodes_added_count"], 0) # No nodes added if service is out
        self.assertEqual(summary["relationships_added_count"], 0)
        # self.mock_neo4j_service.add_emc_entity.assert_not_called() # This mock belongs to self.graph_manager, not failing_graph_manager

    def test_process_document_entity_addition_fails(self):
        self.mock_entity_extractor.extract_entities.return_value = self.extracted_entities_raw
        self.mock_relation_builder.build_relationships.return_value = self.extracted_relations
        # Simulate failure for adding the first entity (Document node)
        self.mock_neo4j_service.add_emc_entity.side_effect = [
            Exception("DB connection error for Document"), # Fails for Document
            {"status": "merged_product"}, # Succeeds for Product
            {"status": "merged_standard"}  # Succeeds for Standard
        ]
        # Relationship addition should still be attempted if other entities succeed
        self.mock_neo4j_service.add_emc_relationship.return_value = {"status": "merged_relationship"}


        summary = asyncio.run(
            self.graph_manager.process_document_content(
                self.sample_text, self.document_id, self.document_metadata
            )
        )

        self.assertEqual(summary["status"], "completed_with_errors")
        self.assertIn("Failed to add entity Document (test_doc.txt): DB connection error for Document", summary["errors"][0])
        self.assertEqual(summary["nodes_added_count"], 2) # Product + Standard, Document failed
        self.assertEqual(summary["relationships_added_count"], 1) # Relationship should still be added

    def test_process_document_relationship_addition_fails(self):
        self.mock_entity_extractor.extract_entities.return_value = self.extracted_entities_raw
        self.mock_relation_builder.build_relationships.return_value = self.extracted_relations
        self.mock_neo4j_service.add_emc_entity.return_value = {"status": "merged_node"}
        self.mock_neo4j_service.add_emc_relationship.side_effect = Exception("DB error adding relationship")

        summary = asyncio.run(
            self.graph_manager.process_document_content(
                self.sample_text, self.document_id, self.document_metadata
            )
        )

        self.assertEqual(summary["status"], "completed_with_errors")
        self.assertTrue(any("Failed to add relationship HAS_STANDARD" in e for e in summary["errors"]))
        self.assertEqual(summary["nodes_added_count"], 3) # All 3 nodes (Doc, Prod, Std)
        self.assertEqual(summary["relationships_added_count"], 0)

    def test_close_connections_called(self):
        self.graph_manager.close_connections()
        self.mock_neo4j_service.close.assert_called_once()

    def test_close_connections_handles_no_service(self):
        # Create a new graph_manager instance for this specific test case
        # to avoid interference with self.mock_neo4j_service from other tests.
        mock_entity_extractor_local = AsyncMock()
        mock_relation_builder_local = AsyncMock()

        manager_no_neo = EMCGraphManager(
            entity_extractor=mock_entity_extractor_local,
            relation_builder=mock_relation_builder_local,
            neo4j_service=None
        )
        manager_no_neo.neo4j_service = None # Ensure it's None

        try:
            manager_no_neo.close_connections() # Should not raise error
        except Exception as e:
            self.fail(f"close_connections raised an exception with no neo4j_service: {e}")

        # Ensure that the original self.mock_neo4j_service (if it exists and has a close method)
        # was not called by this specific test instance.
        # This assertion is a bit tricky because self.mock_neo4j_service is defined in setUp
        # and might be called by other tests.
        # A cleaner way might be to ensure the specific neo4j_service of manager_no_neo (which is None)
        # doesn't lead to a call. The try-except block already checks for errors.


if __name__ == '__main__':
    unittest.main()
