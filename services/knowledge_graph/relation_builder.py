"""
EMC Relationship Builder

This module is responsible for identifying and establishing relationships
between extracted EMC entities, based on the defined ontology.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from .emc_ontology import (
    # Node Labels
    NODE_EMC_STANDARD, NODE_PRODUCT, NODE_TEST, NODE_FREQUENCY, NODE_FREQUENCY_RANGE,
    NODE_PHENOMENON, NODE_TEST_RESULT, NODE_DOCUMENT,
    # Relationship Types
    REL_APPLIES_TO, REL_PERFORMED_TEST, REL_HAS_STANDARD, REL_OBSERVES_PHENOMENON,
    REL_USES_FREQUENCY, REL_HAS_FREQUENCY_RANGE, REL_REFERENCES_STANDARD, REL_MENTIONS_PRODUCT,
    # Relationship Schemas
    get_relationship_schema, BaseRelationship, AppliesToRel
)
# Assuming entities are passed as a list of dictionaries,
# where each dictionary has "label" and "data" (the dataclass instance)
# e.g., {"label": NODE_EMC_STANDARD, "data": EMCStandardNode(...), "id_in_document": "ent_1"}
# We'll need a way to uniquely identify entities within the scope of a document processing session.

logger = logging.getLogger(__name__)

class EMCRelationBuilder:
    def __init__(self, deepseek_service: Optional[Any] = None): # Placeholder for AI service
        self.deepseek_service = deepseek_service

    def _get_entity_id(self, entity_data: Dict[str, Any]) -> str:
        """
        Generates a unique ID for an entity based on its name and label.
        This is a simple approach. More robust ID generation might be needed
        for merging across documents or handling very similar names.
        """
        return f"{entity_data['label']}_{entity_data['data']['name']}"

    def build_relationships_rule_based(
        self,
        entities: List[Dict[str, Any]],
        text_content: str, # Original text for context if needed
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Identifies relationships between entities using rule-based methods.
        Args:
            entities: A list of extracted entity dicts. Each dict should have at least:
                      'label': str (e.g., NODE_PRODUCT)
                      'data': dict (the __dict__ of the ontology dataclass instance)
                      'id_in_document': str (a unique temporary ID for this entity within this document context)
            text_content: The original text from which entities were extracted.
            document_id: ID of the source document.
        Returns:
            A list of relationship dicts, e.g.:
            {
                "type": REL_APPLIES_TO,
                "from_entity_id": "ent_product_1",
                "to_entity_id": "ent_standard_2",
                "data": AppliesToRel(...).__dict__
            }
        """
        relationships = []
        source_doc_ids = [document_id] if document_id else []

        # For simplicity, let's add unique IDs to entities if not present
        # These IDs are temporary, for linking within this context.
        # GraphManager will handle persistent graph node IDs.
        entities_with_ids = []
        for i, entity_dict in enumerate(entities):
            # Ensure 'data' is a dict if it's a dataclass instance
            entity_data_dict = entity_dict['data']
            if not isinstance(entity_data_dict, dict) and hasattr(entity_data_dict, '__dict__'):
                 entity_data_dict = entity_data_dict.__dict__

            # If 'name' is not directly in entity_data_dict, it might be an attribute of the object
            entity_name = entity_data_dict.get('name')
            if not entity_name and 'name' in entity_dict: # Check one level up
                entity_name = entity_dict['name']

            if not entity_name: # Still no name, log and skip (or use a default)
                logger.warning(f"Entity missing name: {entity_dict}. Cannot generate reliable ID.")
                temp_id = f"temp_ent_idx_{i}"
            else:
                temp_id = f"{entity_dict['label']}_{entity_name}_{i}" # Add index to ensure uniqueness for now

            entities_with_ids.append({**entity_dict, "id_in_document": temp_id, "data": entity_data_dict})


        # --- Rule Examples ---

        # 1. Product <-> EMCStandard (APPLIES_TO / HAS_STANDARD)
        #    If a Product and an EMCStandard are mentioned closely, or common phrases appear.
        #    This is a very simplified rule. Real NLP would look at sentence structure.
        products = [e for e in entities_with_ids if e['label'] == NODE_PRODUCT]
        standards = [e for e in entities_with_ids if e['label'] == NODE_EMC_STANDARD]
        documents = [e for e in entities_with_ids if e['label'] == NODE_DOCUMENT]

        for product_entity in products:
            for standard_entity in standards:
                # Simplistic proximity: if both appear in text (improve with actual proximity/sentence analysis)
                # A more robust check would involve analyzing the text_content for co-occurrence patterns.
                # For now, let's assume if both are extracted from the same document, a potential link exists.
                # This needs significant refinement.

                # Example: Product HAS_STANDARD Standard
                rel_schema_hs = get_relationship_schema(REL_HAS_STANDARD) or BaseRelationship
                rel_instance_hs = rel_schema_hs(
                    source_document_ids=source_doc_ids,
                    confidence_score=0.5, # Arbitrary score for rule-based
                    properties={"method": "co-occurrence_in_document"}
                )
                relationships.append({
                    "type": REL_HAS_STANDARD,
                    "from_entity_id": product_entity["id_in_document"],
                    "to_entity_id": standard_entity["id_in_document"],
                    "data": rel_instance_hs.__dict__
                })

                # Example: Standard APPLIES_TO Product
                # This is often context-dependent, e.g. "Product X complies with Standard Y"
                # For now, let's create a symmetric relationship for demonstration if not contradictory.
                # In a real scenario, APPLIES_TO might be inferred from specific phrases.
                rel_schema_at = get_relationship_schema(REL_APPLIES_TO) or BaseRelationship
                rel_instance_at = rel_schema_at(
                    source_document_ids=source_doc_ids,
                    confidence_score=0.5,
                    properties={"method": "co-occurrence_in_document"}
                )
                if isinstance(rel_instance_at, AppliesToRel):
                    rel_instance_at.conditions = "Assumed from co-occurrence"

                relationships.append({
                    "type": REL_APPLIES_TO,
                    "from_entity_id": standard_entity["id_in_document"], # Standard APPLIES_TO Product
                    "to_entity_id": product_entity["id_in_document"],
                    "data": rel_instance_at.__dict__
                })

        # 2. Document <-> EMCStandard (REFERENCES_STANDARD)
        for doc_entity in documents:
            for std_entity in standards:
                # If a standard is mentioned in a document.
                rel_schema_rs = get_relationship_schema(REL_REFERENCES_STANDARD) or BaseRelationship
                rel_instance_rs = rel_schema_rs(
                    source_document_ids=source_doc_ids, # or specifically doc_entity['data']['file_id'] if available
                    confidence_score=0.7,
                    properties={"method": "mention_in_document_content"}
                )
                relationships.append({
                    "type": REL_REFERENCES_STANDARD,
                    "from_entity_id": doc_entity["id_in_document"],
                    "to_entity_id": std_entity["id_in_document"],
                    "data": rel_instance_rs.__dict__
                })

        # 3. Document <-> Product (MENTIONS_PRODUCT)
        for doc_entity in documents:
            for prod_entity in products:
                rel_schema_mp = get_relationship_schema(REL_MENTIONS_PRODUCT) or BaseRelationship
                rel_instance_mp = rel_schema_mp(
                    source_document_ids=source_doc_ids,
                    confidence_score=0.7,
                    properties={"method": "mention_in_document_content"}
                )
                relationships.append({
                    "type": REL_MENTIONS_PRODUCT,
                    "from_entity_id": doc_entity["id_in_document"],
                    "to_entity_id": prod_entity["id_in_document"],
                    "data": rel_instance_mp.__dict__
                })

        # 4. Test <-> Frequency/FrequencyRange (USES_FREQUENCY / HAS_FREQUENCY_RANGE)
        tests = [e for e in entities_with_ids if e['label'] == NODE_TEST]
        frequencies = [e for e in entities_with_ids if e['label'] == NODE_FREQUENCY]
        freq_ranges = [e for e in entities_with_ids if e['label'] == NODE_FREQUENCY_RANGE]

        for test_entity in tests:
            for freq_entity in frequencies:
                # Simplified: if a test and a frequency are mentioned.
                # Needs context: e.g., "test performed AT 100MHz"
                rel_schema_uf = get_relationship_schema(REL_USES_FREQUENCY) or BaseRelationship
                rel_instance_uf = rel_schema_uf(source_document_ids=source_doc_ids, confidence_score=0.4)
                relationships.append({
                    "type": REL_USES_FREQUENCY,
                    "from_entity_id": test_entity["id_in_document"],
                    "to_entity_id": freq_entity["id_in_document"],
                    "data": rel_instance_uf.__dict__
                })
            for fr_entity in freq_ranges:
                # Simplified: if a test and a frequency range are mentioned.
                # Needs context: e.g., "test scanned OVER 30MHz-1GHz"
                rel_schema_hfr = get_relationship_schema(REL_HAS_FREQUENCY_RANGE) or BaseRelationship
                rel_instance_hfr = rel_schema_hfr(source_document_ids=source_doc_ids, confidence_score=0.4)
                relationships.append({
                    "type": REL_HAS_FREQUENCY_RANGE,
                    "from_entity_id": test_entity["id_in_document"],
                    "to_entity_id": fr_entity["id_in_document"],
                    "data": rel_instance_hfr.__dict__
                })

        # TODO: Add more rules for other relationships like:
        # - Test PERFORMED_TEST_ON Product
        # - TestResult OBSERVES_PHENOMENON Phenomenon
        # - Test HAS_TEST_RESULT TestResult

        # Deduplicate relationships (simple check for from_id, to_id, type)
        # Proper deduplication would also consider properties.
        final_rels_map = {(r["from_entity_id"], r["to_entity_id"], r["type"]): r for r in relationships}
        final_relationships = list(final_rels_map.values())

        logger.info(f"Rule-based relationship builder found {len(final_relationships)} relationships for doc {document_id or 'N/A'}.")
        return final_relationships

    async def build_relationships_ai(
        self,
        entities: List[Dict[str, Any]],
        text_content: str,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Identifies relationships using an AI service.
        The AI would need the text and the list of pre-identified entities (with their temp IDs).
        """
        if not self.deepseek_service:
            logger.warning("DeepSeek service not available for AI relationship extraction.")
            return []

        try:
            # This is a conceptual call. The AI would need context about entities and their types.
            # The prompt might include the list of entities and ask to find connections between them.
            # Example payload for AI:
            # {
            #   "text_content": "...",
            #   "entities": [
            #     {"id": "ent_1", "type": "Product", "name": "Laptop X1"},
            #     {"id": "ent_2", "type": "EMCStandard", "name": "CISPR 32"}
            #   ],
            #   "desired_relationships": ["APPLIES_TO", "HAS_STANDARD"]
            # }
            # Expected AI response:
            # {
            #   "relationships": [
            #     {"type": "APPLIES_TO", "from_id": "ent_2", "to_id": "ent_1", "properties": {"conditions": "Class B"}}
            #   ]
            # }
            # ai_response = await self.deepseek_service.extract_emc_relationships_structured(...)

            # For now, returning empty as AI part is not implemented
            logger.info(f"AI relationship extraction (not implemented) called for doc {document_id or 'N/A'}.")
            return []

        except Exception as e:
            logger.error(f"Error during AI relationship extraction: {e}", exc_info=True)
            return []

    async def build_relationships(
        self,
        entities: List[Dict[str, Any]], # Entities with 'id_in_document'
        text_content: str,
        document_id: Optional[str] = None,
        use_ai: bool = False, # Defaulting AI to False for relationships initially
        use_rules: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Orchestrates relationship extraction.
        """
        all_relationships = []

        if use_rules:
            rule_relationships = self.build_relationships_rule_based(entities, text_content, document_id)
            all_relationships.extend(rule_relationships)

        if use_ai and self.deepseek_service:
            ai_relationships = await self.build_relationships_ai(entities, text_content, document_id)
            # Needs merging/deduplication logic if both AI and rules are used
            all_relationships.extend(ai_relationships)
            # Basic deduplication
            final_rels_map = {(r["from_entity_id"], r["to_entity_id"], r["type"]): r for r in all_relationships}
            all_relationships = list(final_rels_map.values())

        logger.info(f"Total relationships extracted for doc {document_id or 'N/A'}: {len(all_relationships)}")
        return all_relationships


# Example Usage (conceptual)
if __name__ == '__main__':
    import asyncio
    from .emc_ontology import ProductNode, EMCStandardNode, DocumentNode, TestNode, FrequencyNode, FrequencyRangeNode

    logging.basicConfig(level=logging.INFO)
    builder = EMCRelationBuilder()

    # Sample entities (output from EMCEntityExtractor)
    # Ensure 'data' is a dictionary here (as if from __dict__)
    sample_entities = [
        {"label": NODE_DOCUMENT, "data": DocumentNode(name="TestReport_XYZ.pdf", file_id="doc001").__dict__, "id_in_document": "doc_entity_1"},
        {"label": NODE_PRODUCT, "data": ProductNode(name="SuperDevice X1000", model_number="SDX1000").__dict__, "id_in_document": "prod_entity_1"},
        {"label": NODE_EMC_STANDARD, "data": EMCStandardNode(name="EN 55032", version="2015").__dict__, "id_in_document": "std_entity_1"},
        {"label": NODE_EMC_STANDARD, "data": EMCStandardNode(name="IEC 61000-3-2").__dict__, "id_in_document": "std_entity_2"},
        {"label": NODE_TEST, "data": TestNode(name="Radiated Emissions").__dict__, "id_in_document": "test_entity_1"},
        {"label": NODE_FREQUENCY, "data": FrequencyNode(name="120MHz", value_hz=120e6).__dict__, "id_in_document": "freq_entity_1"},
        {"label": NODE_FREQUENCY_RANGE, "data": FrequencyRangeNode(name="30MHz-1GHz", min_value_hz=30e6, max_value_hz=1e9).__dict__, "id_in_document": "freqrange_entity_1"},
    ]

    sample_text = """
    The SuperDevice X1000 (SDX1000) was tested according to EN 55032:2015.
    This TestReport_XYZ.pdf also references IEC 61000-3-2 for harmonic current emissions.
    Radiated Emissions test was performed from 30 MHz to 1 GHz. A peak was noted at 120MHz.
    """

    async def main():
        print("--- Building Relationships (Rules only) ---")
        relationships = await builder.build_relationships(sample_entities, sample_text, "doc001", use_ai=False, use_rules=True)
        for rel in relationships:
            print(f"  {rel['from_entity_id']} -[{rel['type']}]-> {rel['to_entity_id']}")
            # print(f"    Properties: {rel['data']}")

    asyncio.run(main())
