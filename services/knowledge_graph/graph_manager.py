"""
EMC Graph Manager

This service orchestrates the process of building the EMC knowledge graph.
It uses the Entity Extractor, Relation Builder, and Neo4j Service to
process documents, extract information, and store it in the graph.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import asdict


# Assuming services are in the same directory or paths are correctly configured
from .emc_ontology import ONTOLOGY_DEFINITIONS # For reference or validation if needed
from .entity_extractor import EMCEntityExtractor
from .relation_builder import EMCRelationBuilder
from .neo4j_emc_service import Neo4jEMCService # This will be used conceptually

# Placeholder for AI service if needed by extractor/builder
# from ..ai_integration.deepseek_service import DeepSeekEMCService
import os

logger = logging.getLogger(__name__)

class EMCGraphManager:
    def __init__(
        self,
        entity_extractor: Optional[EMCEntityExtractor] = None,
        relation_builder: Optional[EMCRelationBuilder] = None,
        neo4j_service: Optional[Neo4jEMCService] = None,
        # deepseek_service: Optional[DeepSeekEMCService] = None # If AI is used directly here or passed down
    ):
        # Initialize with existing services or create new ones
        # if deepseek_service:
        #     self.deepseek_service = deepseek_service
        # else:
        #     # This would require DeepSeekEMCService to be importable and configurable
        #     # self.deepseek_service = DeepSeekEMCService() # Or handle its absence
        #     self.deepseek_service = None

        # For now, EMCEntityExtractor and EMCRelationBuilder might instantiate their own AI services
        # or be passed a shared one. Let's assume they can be initialized simply for now.
        self.entity_extractor = entity_extractor or EMCEntityExtractor(deepseek_service=None) # Pass AI service if available
        self.relation_builder = relation_builder or EMCRelationBuilder(deepseek_service=None) # Pass AI service if available

        # Critical: Neo4j service might not be fully functional due to previous tool issues.
        # We proceed with the assumption that it *would* work, or this part is a placeholder.
        if neo4j_service:
            self.neo4j_service = neo4j_service
        else:
            try:
                self.neo4j_service = Neo4jEMCService()
                # Call ensure_constraints_and_indexes on first use or system startup
                # For a manager, it might be better to do this explicitly outside init.
                # self.neo4j_service.ensure_constraints_and_indexes()
            except Exception as e:
                logger.error(f"EMCGraphManager: Failed to initialize Neo4jEMCService: {e}. Graph operations will likely fail.", exc_info=True)
                self.neo4j_service = None


    async def process_document_content(
        self,
        text_content: str,
        document_id: str, # A unique identifier for the document
        document_metadata: Optional[Dict[str, Any]] = None # e.g., filename, type from FileMetadata
    ) -> Dict[str, Any]:
        """
        Processes the textual content of a document to extract entities and relationships,
        and attempts to store them in the knowledge graph.

        Args:
            text_content: The raw text from the document.
            document_id: A unique ID for this document (e.g., hash, database ID).
            document_metadata: Optional dictionary containing metadata about the document.

        Returns:
            A dictionary summarizing the processing results.
        """
        logger.info(f"Starting processing for document_id: {document_id}")
        processing_summary = {
            "document_id": document_id,
            "status": "pending",
            "entities_extracted_count": 0,
            "relationships_extracted_count": 0,
            "nodes_added_count": 0,
            "relationships_added_count": 0,
            "errors": []
        }

        try:
            # 1. Add/Update Document Node itself
            if self.neo4j_service and document_metadata:
                doc_node_data = {
                    "file_id": document_id, # Assuming document_id can serve as unique file_id for Document node
                    "name": document_metadata.get("filename", document_id),
                    "document_type": document_metadata.get("document_type", "Unknown"),
                    "mime_type": document_metadata.get("mime_type", "N/A"),
                    "size_bytes": document_metadata.get("size_bytes", 0),
                    # Add other relevant metadata from document_metadata
                }
                # Use 'file_id' as the unique identifier for Document nodes
                try:
                    logger.info(f"Attempting to merge document node for {document_id}")
                    # Ensure entity_data is a flat dict.
                    self.neo4j_service.add_emc_entity(
                        entity_label="Document", # Using string literal from ontology if not imported
                        entity_data=doc_node_data,
                        unique_id_field="file_id"
                    )
                    logger.info(f"Document node for {document_id} merged successfully.")
                except Exception as e:
                    logger.error(f"Failed to merge document node for {document_id}: {e}", exc_info=True)
                    processing_summary["errors"].append(f"Document node merge error: {str(e)}")


            # 2. Extract Entities
            # The EMCEntityExtractor returns a list of dicts, where each dict has 'label' and 'data' (a dataclass instance)
            # The 'data' part needs to be converted to a dict for Neo4j.
            logger.info(f"Extracting entities from document: {document_id}")
            # TODO: Determine if AI or rules or both should be used based on config/strategy
            extracted_entity_dicts = await self.entity_extractor.extract_entities(
                text_content=text_content,
                document_id=document_id,
                use_ai=False, # Defaulting to rules; AI integration needs more setup
                use_rules=True
            )
            processing_summary["entities_extracted_count"] = len(extracted_entity_dicts)
            logger.info(f"Extracted {len(extracted_entity_dicts)} entities for document {document_id}.")

            # Prepare entities for relationship building and Neo4j storage
            # We need temporary IDs for entities within this document context for relation builder
            entities_for_relation_builder = []
            for i, entity_info in enumerate(extracted_entity_dicts):
                entity_data_as_dict = {}
                if hasattr(entity_info['data'], '__dict__'):
                    entity_data_as_dict = entity_info['data'].__dict__
                elif isinstance(entity_info['data'], dict):
                    entity_data_as_dict = entity_info['data']
                else:
                    logger.warning(f"Entity data for {entity_info.get('label')} is not a dict or dataclass instance. Skipping.")
                    continue

                # Ensure 'name' exists for temporary ID generation
                entity_name = entity_data_as_dict.get("name", f"unnamed_entity_{i}")

                entities_for_relation_builder.append({
                    "label": entity_info["label"],
                    "data": entity_data_as_dict, # This is already a dict
                    "id_in_document": f"{entity_info['label']}_{entity_name}_{i}" # Temp ID
                })

            # 3. Extract Relationships
            logger.info(f"Building relationships for document: {document_id}")
            extracted_relation_dicts = await self.relation_builder.build_relationships(
                entities=entities_for_relation_builder, # Pass entities with temp IDs
                text_content=text_content,
                document_id=document_id,
                use_ai=False, # Defaulting to rules
                use_rules=True
            )
            processing_summary["relationships_extracted_count"] = len(extracted_relation_dicts)
            logger.info(f"Extracted {len(extracted_relation_dicts)} relationships for document {document_id}.")

            # 4. Store Entities and Relationships in Neo4j
            if not self.neo4j_service:
                logger.warning("Neo4j service not available. Skipping graph storage.")
                processing_summary["errors"].append("Neo4j service unavailable, skipping storage.")
                processing_summary["status"] = "completed_without_storage"
                return processing_summary

            # Map temp entity IDs to Neo4j node objects/IDs after creation for linking relationships
            # For simplicity, we'll re-fetch or rely on merge_node to handle uniqueness.
            # A more robust way would be to get actual Neo4j elementIds.

            nodes_added_this_run = 0
            for entity_detail in entities_for_relation_builder: # Using the list with temp IDs
                label = entity_detail["label"]
                # Data should be a dict of the dataclass from ontology (e.g. EMCStandardNode.__dict__)
                data_dict = entity_detail["data"]

                # Determine unique_id_field based on label, default to "name"
                unique_id_field = "name"
                if label == "Document" and "file_id" in data_dict: # Using string literal for "Document"
                    unique_id_field = "file_id"
                # Add other specific unique_id_fields if necessary for other labels

                try:
                    # add_emc_entity expects a flat dict of properties
                    self.neo4j_service.add_emc_entity(
                        entity_label=label,
                        entity_data=data_dict,
                        unique_id_field=unique_id_field
                    )
                    nodes_added_this_run +=1
                except Exception as e:
                    error_msg = f"Failed to add entity {label} ({data_dict.get(unique_id_field, 'N/A')}): {e}"
                    logger.error(error_msg, exc_info=True)
                    processing_summary["errors"].append(error_msg)
            processing_summary["nodes_added_count"] = nodes_added_this_run

            rels_added_this_run = 0
            # Create a mapping from id_in_document to the actual unique property value (e.g., name)
            # This is crucial for linking relationships correctly.
            entity_id_to_unique_value_map = {}
            for entity_detail in entities_for_relation_builder:
                unique_id_field = "name" # Default
                if entity_detail["label"] == "Document" and "file_id" in entity_detail["data"]:
                    unique_id_field = "file_id"

                entity_id_to_unique_value_map[entity_detail["id_in_document"]] = {
                    "label": entity_detail["label"],
                    "unique_field": unique_id_field,
                    "unique_value": entity_detail["data"].get(unique_id_field)
                }

            for rel_info in extracted_relation_dicts:
                from_id_temp = rel_info["from_entity_id"]
                to_id_temp = rel_info["to_entity_id"]

                from_entity_details = entity_id_to_unique_value_map.get(from_id_temp)
                to_entity_details = entity_id_to_unique_value_map.get(to_id_temp)

                if not from_entity_details or not to_entity_details:
                    error_msg = f"Could not find entity details for relationship {rel_info['type']} between {from_id_temp} and {to_id_temp}."
                    logger.error(error_msg)
                    processing_summary["errors"].append(error_msg)
                    continue

                # Ensure unique values exist
                if not from_entity_details["unique_value"] or not to_entity_details["unique_value"]:
                    error_msg = f"Missing unique value for entities in relationship {rel_info['type']}. From: {from_entity_details}, To: {to_entity_details}."
                    logger.error(error_msg)
                    processing_summary["errors"].append(error_msg)
                    continue

                try:
                    self.neo4j_service.add_emc_relationship(
                        from_entity_label=from_entity_details["label"],
                        from_entity_unique_id_value=from_entity_details["unique_value"],
                        from_entity_unique_id_field=from_entity_details["unique_field"],
                        to_entity_label=to_entity_details["label"],
                        to_entity_unique_id_value=to_entity_details["unique_value"],
                        to_entity_unique_id_field=to_entity_details["unique_field"],
                        relationship_type=rel_info["type"],
                        relationship_data=rel_info["data"] # This should be a dict of properties
                    )
                    rels_added_this_run += 1
                except Exception as e:
                    error_msg = f"Failed to add relationship {rel_info['type']} between {from_entity_details['unique_value']} and {to_entity_details['unique_value']}: {e}"
                    logger.error(error_msg, exc_info=True)
                    processing_summary["errors"].append(error_msg)
            processing_summary["relationships_added_count"] = rels_added_this_run

            processing_summary["status"] = "completed"
            if processing_summary["errors"]:
                 processing_summary["status"] = "completed_with_errors"

        except Exception as e:
            logger.error(f"Unhandled error in process_document_content for {document_id}: {e}", exc_info=True)
            processing_summary["errors"].append(f"General processing error: {str(e)}")
            processing_summary["status"] = "failed"

        logger.info(f"Finished processing for document_id: {document_id}. Status: {processing_summary['status']}")
        return processing_summary

    def close_connections(self):
        """Closes any underlying service connections, like to Neo4j."""
        if self.neo4j_service:
            try:
                self.neo4j_service.close()
                logger.info("Neo4j service connection closed via GraphManager.")
            except Exception as e:
                logger.error(f"Error closing Neo4j service connection: {e}", exc_info=True)


# Example Usage (Conceptual - typically called by a higher-level service like file processor)
async def example_run():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # This example assumes Neo4j is running and configured (e.g., via environment variables for Neo4jEMCService)
    # And that emc_ontology, entity_extractor, relation_builder are in place.

    graph_manager = None
    try:
        # Initialize Neo4jEMCService first to ensure constraints if it's the first run for the DB
        # In a real app, ensure_constraints_and_indexes might be a separate startup step.
        temp_neo4j_service = Neo4jEMCService()
        if temp_neo4j_service._driver: # Check if connection was successful
            temp_neo4j_service.ensure_constraints_and_indexes()
            temp_neo4j_service.close() # Close after setup
            logger.info("Initial constraints and indexes ensured (if Neo4j was available).")
        else:
            logger.warning("Neo4j service could not connect for initial constraint setup. Proceeding without...")

        graph_manager = EMCGraphManager() # This will attempt to init its own Neo4j service

        sample_text = """
        The SuperCharger Model SC-5000 was tested according to the EMC Standard EN 55011.
        This document (DOC001) details the radiated emissions test from 30MHz to 1GHz.
        A notable emission was found at 150MHz.
        Manufacturer: ChargeCorp. Product Type: Industrial Charger.
        """
        doc_meta = {
            "filename": "SC-5000_Test_Report.pdf",
            "document_type": "Test Report",
            "mime_type": "application/pdf",
            "size_bytes": 102400
        }

        result = await graph_manager.process_document_content(
            text_content=sample_text,
            document_id="DOC001_SC5000_TestReport",
            document_metadata=doc_meta
        )

        print("\n--- Processing Summary ---")
        for key, value in result.items():
            if key == "errors" and value:
                print(f"  Errors Encountered ({len(value)}):")
                for err in value:
                    print(f"    - {err[:200]}...") # Print first 200 chars of error
            else:
                print(f"  {key.replace('_', ' ').title()}: {value}")

    except Exception as e:
        logger.error(f"Error in example_run: {e}", exc_info=True)
    finally:
        if graph_manager:
            graph_manager.close_connections()

if __name__ == '__main__':
    # Ensure NEO4J_PASSWORD is set in env for example_run to connect to Neo4j
    # e.g. export EMC_NEO4J_PASSWORD="your_password"
    if not os.getenv("EMC_NEO4J_PASSWORD"):
        print("WARNING: EMC_NEO4J_PASSWORD environment variable is not set.")
        print("The example_run will likely fail to connect to Neo4j and store data.")
        print("Please set it if you intend to test Neo4j integration.")
        # You might choose to exit or run a version of example_run that mocks Neo4j

    asyncio.run(example_run())
