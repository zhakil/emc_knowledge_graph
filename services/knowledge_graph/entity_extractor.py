"""
EMC Entity Extractor

This module is responsible for extracting entities relevant to the EMC domain
from text content. It uses the defined ontology and can leverage AI services
as well as rule-based methods.
"""

import re
import logging
from typing import List, Dict, Any, Optional

# Assuming deepseek_service is correctly configured and passed
# from ..ai_integration.deepseek_service import DeepSeekEMCService
# For now, we'll mock or not use it directly in this initial implementation phase

from .emc_ontology import (
    # Node Labels
    NODE_EMC_STANDARD, NODE_PRODUCT, NODE_COMPONENT, NODE_TEST,
    NODE_TEST_RESULT, NODE_FREQUENCY, NODE_FREQUENCY_RANGE,
    NODE_PHENOMENON, NODE_REGULATION, NODE_MITIGATION_MEASURE,
    NODE_DOCUMENT, NODE_ORGANIZATION, NODE_EQUIPMENT,
    # Node Schemas
    get_node_schema, BaseNode, FrequencyNode, FrequencyRangeNode,
    EMCStandardNode, ProductNode # Import other specific node types as needed
)

logger = logging.getLogger(__name__)

class EMCEntityExtractor:
    # Placeholder for DeepSeekEMCService, will be properly initialized later
    # def __init__(self, deepseek_service: Optional[DeepSeekEMCService] = None):
    def __init__(self, deepseek_service: Optional[Any] = None): # Using Any for now
        self.deepseek_service = deepseek_service
        # Pre-compile regex patterns for efficiency
        self.patterns = {
            # Basic pattern for EMC standards (e.g., CISPR 32, EN 55032, IEC 61000-4-2)
            NODE_EMC_STANDARD: re.compile(r'((?:CISPR|EN|IEC|FCC|VCCI|MIL-STD|GJB|GB)[ -]?(?:\d+[-:\d\.]*)+[A-Z]?)', re.IGNORECASE),
            # Pattern for frequencies (e.g., 100 MHz, 2.4GHz, 50 Hz)
            NODE_FREQUENCY: re.compile(r'(\d+(?:\.\d+)?)\s*(k|M|G)?Hz', re.IGNORECASE),
            # Pattern for frequency ranges (e.g., 30MHz-1GHz, 150 kHz to 80 MHz)
            NODE_FREQUENCY_RANGE: re.compile(r'(\d+(?:\.\d+)?)\s*(k|M|G)?Hz\s*(?:-|to|至)\s*(\d+(?:\.\d+)?)\s*(k|M|G)?Hz', re.IGNORECASE),
            # Add more specific regex for other entities if useful for rule-based fallback
        }

    def _parse_frequency_value(self, value_str: str, unit_prefix: Optional[str]) -> float:
        """Converts frequency string with prefix to Hz."""
        value = float(value_str)
        if unit_prefix:
            unit_prefix = unit_prefix.lower()
            if unit_prefix == 'k':
                value *= 1e3
            elif unit_prefix == 'm':
                value *= 1e6
            elif unit_prefix == 'g':
                value *= 1e9
        return value

    def extract_entities_rule_based(self, text_content: str, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extracts entities using rule-based methods (regex, keywords).
        This can serve as a baseline or a supplement to AI-based extraction.
        """
        extracted_entities = []
        source_doc_ids = [document_id] if document_id else []

        # Extract EMC Standards
        for match in self.patterns[NODE_EMC_STANDARD].finditer(text_content):
            schema_class = get_node_schema(NODE_EMC_STANDARD) or BaseNode
            entity = schema_class(
                name=match.group(1).upper(),
                description=f"Detected EMC Standard: {match.group(1)}",
                source_document_ids=source_doc_ids,
                properties={'detection_method': 'regex'}
            )
            if isinstance(entity, EMCStandardNode): # Example of adding specific props
                 # Try to parse version if possible from name or surrounding text (simplified here)
                pass
            extracted_entities.append({"label": NODE_EMC_STANDARD, "data": entity.__dict__})

        # Extract Frequencies
        for match in self.patterns[NODE_FREQUENCY].finditer(text_content):
            value_str, unit_prefix = match.groups()
            value_hz = self._parse_frequency_value(value_str, unit_prefix)
            original_unit = f"{unit_prefix or ''}Hz"

            schema_class = get_node_schema(NODE_FREQUENCY) or BaseNode
            entity = schema_class(
                name=f"{value_str}{original_unit}",
                description=f"Detected Frequency: {value_str}{original_unit}",
                source_document_ids=source_doc_ids,
                properties={'detection_method': 'regex'}
            )
            if isinstance(entity, FrequencyNode):
                entity.value_hz = value_hz
                entity.unit = original_unit
            extracted_entities.append({"label": NODE_FREQUENCY, "data": entity.__dict__})

        # Extract Frequency Ranges
        for match in self.patterns[NODE_FREQUENCY_RANGE].finditer(text_content):
            min_val_str, min_pref, max_val_str, max_pref = match.groups()
            min_hz = self._parse_frequency_value(min_val_str, min_pref)
            max_hz = self._parse_frequency_value(max_val_str, max_pref)

            original_min_unit = f"{min_pref or ''}Hz"
            original_max_unit = f"{max_pref or ''}Hz"
            range_name = f"{min_val_str}{original_min_unit}-{max_val_str}{original_max_unit}"

            schema_class = get_node_schema(NODE_FREQUENCY_RANGE) or BaseNode
            entity = schema_class(
                name=range_name,
                description=f"Detected Frequency Range: {range_name}",
                source_document_ids=source_doc_ids,
                properties={'detection_method': 'regex'}
            )
            if isinstance(entity, FrequencyRangeNode):
                entity.min_value_hz = min_hz
                entity.max_value_hz = max_hz
                # Decide on a common unit for display if necessary, or store original parts
                entity.unit = "Hz" # Storing base unit for values
            extracted_entities.append({"label": NODE_FREQUENCY_RANGE, "data": entity.__dict__})

        # Placeholder for other entity types (Product, Component, etc.)
        # These often require more sophisticated NLP or AI.

        logger.info(f"Rule-based extraction found {len(extracted_entities)} entities from document {document_id or 'N/A'}.")
        return extracted_entities

    async def extract_entities_ai(self, text_content: str, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extracts entities using an AI service (e.g., DeepSeek).
        The AI service should ideally return structured data matching the ontology.
        """
        if not self.deepseek_service:
            logger.warning("DeepSeek service not available for AI entity extraction.")
            return []

        try:
            # This is a conceptual call. The actual method and parameters
            # for deepseek_service.extract_entities_from_text will depend on its implementation.
            # It should be prompted to return entities and their types according to our ontology.
            ai_response = await self.deepseek_service.extract_emc_entities_structured(
                text_content=text_content,
                # We might need to pass ontology hints or desired output structure to the prompt
                prompt_context=f"Extract entities according to EMC ontology. Node types: {NODE_EMC_STANDARD}, {NODE_PRODUCT}, etc."
            )

            # Process ai_response:
            # This part is crucial and depends on the exact format of ai_response.
            # We expect a list of dictionaries, where each dict has 'label', 'name', and 'properties'.
            # Example: [{"label": "EMCStandard", "name": "CISPR 32", "version": "2.0"}, ...]
            processed_entities = []
            raw_entities = ai_response.get("entities", []) # Assuming this structure

            for raw_entity in raw_entities:
                label = raw_entity.get("label")
                name = raw_entity.get("name")
                if not label or not name or not get_node_schema(label):
                    logger.warning(f"Skipping AI entity with missing label/name or unknown label: {raw_entity}")
                    continue

                schema_class = get_node_schema(label) or BaseNode
                # Create properties dict from raw_entity, excluding 'label' and 'name'
                properties_data = {k: v for k, v in raw_entity.items() if k not in ['label', 'name']}

                # Initialize with common fields
                entity_args = {
                    'name': name,
                    'description': properties_data.pop('description', f"AI Detected {label}: {name}"),
                    'source_document_ids': [document_id] if document_id else [],
                    'properties': properties_data # Store any other fields from AI here
                }

                # For specific node types, map known fields from properties_data
                # to the dataclass fields.
                # Example for EMCStandardNode:
                if label == NODE_EMC_STANDARD and isinstance(schema_class, type(EMCStandardNode)):
                    entity_args['version'] = properties_data.pop('version', None)
                    entity_args['publication_date'] = properties_data.pop('publication_date', None)
                # Add similar blocks for other specific node types if AI provides those fields

                entity = schema_class(**entity_args)
                processed_entities.append({"label": label, "data": entity.__dict__})

            logger.info(f"AI extraction found {len(processed_entities)} entities from document {document_id or 'N/A'}.")
            return processed_entities

        except Exception as e:
            logger.error(f"Error during AI entity extraction: {e}", exc_info=True)
            return []

    async def extract_entities(
        self,
        text_content: str,
        document_id: Optional[str] = None,
        use_ai: bool = True,
        use_rules: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Orchestrates entity extraction using either AI, rules, or both.
        If both are used, results might need merging/deduplication.
        """
        all_entities = []

        if use_ai and self.deepseek_service:
            ai_entities = await self.extract_entities_ai(text_content, document_id)
            all_entities.extend(ai_entities)

        if use_rules:
            rule_entities = self.extract_entities_rule_based(text_content, document_id)
            # Simple combination for now. Could implement more sophisticated merging/deduplication.
            # For example, prefer AI entities if names are very similar, or combine properties.
            all_entities.extend(rule_entities)
            # A basic deduplication by name and label
            # This is very naive, proper deduplication is complex.
            final_entities_map = {(e["data"]["name"], e["label"]): e for e in all_entities}
            all_entities = list(final_entities_map.values())


        logger.info(f"Total entities extracted for doc {document_id or 'N/A'}: {len(all_entities)}")
        return all_entities

# Example Usage (conceptual, typically called by GraphManager)
if __name__ == '__main__':
    # This block is for testing purposes only
    import asyncio

    # Mock DeepSeekService for testing if not available
    class MockDeepSeekService:
        async def extract_emc_entities_structured(self, text_content: str, prompt_context: str):
            print(f"MockDeepSeekService called with context: {prompt_context}")
            # Simulate AI returning some entities
            if "CISPR 32" in text_content:
                return {
                    "entities": [
                        {"label": NODE_EMC_STANDARD, "name": "CISPR 32", "version": "Ed. 2.0", "description": "Standard for ITE"},
                        {"label": NODE_PRODUCT, "name": "Example Product"},
                        {"label": NODE_FREQUENCY, "name": "50MHz", "value_hz": 50e6, "unit": "MHz"}
                    ]
                }
            return {"entities": []}

    # Configure logging for testing
    logging.basicConfig(level=logging.INFO)

    # extractor = EMCEntityExtractor(deepseek_service=MockDeepSeekService())
    extractor = EMCEntityExtractor() # Test without AI first, or with Mock

    sample_text_1 = """
    This document describes testing for SuperWidget X100 according to EN 55032 (CISPR 32).
    Radiated emissions were measured from 30MHz to 1GHz.
    A key frequency observed was 120 MHz. Max emission at 450 MHz.
    The device failed testing at 120MHz.
    """

    sample_text_2 = """
    The equipment complies with IEC 61000-4-2 for ESD tests.
    Another standard is MIL-STD-461G. Frequency range 10kHz-40GHz.
    """

    async def main():
        print("--- Extracting from Sample Text 1 (Rules only) ---")
        entities1_rules = await extractor.extract_entities(sample_text_1, "doc1", use_ai=False, use_rules=True)
        for entity in entities1_rules:
            print(f"  {entity['label']}: {entity['data']['name']} (Properties: {entity['data'].get('properties', {})})")
            if entity['label'] == NODE_FREQUENCY:
                print(f"    Value in Hz: {entity['data'].get('value_hz')}")
            if entity['label'] == NODE_FREQUENCY_RANGE:
                 print(f"    Min: {entity['data'].get('min_value_hz')} Hz, Max: {entity['data'].get('max_value_hz')} Hz")


        # print("\n--- Extracting from Sample Text 1 (AI then Rules) ---")
        # extractor_with_ai = EMCEntityExtractor(deepseek_service=MockDeepSeekService())
        # entities1_ai_rules = await extractor_with_ai.extract_entities(sample_text_1, "doc1_ai", use_ai=True, use_rules=True)
        # for entity in entities1_ai_rules:
        #     print(f"  {entity['label']}: {entity['data']['name']} (Version: {entity['data'].get('version')})")

        print("\n--- Extracting from Sample Text 2 (Rules only) ---")
        entities2_rules = await extractor.extract_entities(sample_text_2, "doc2", use_ai=False, use_rules=True)
        for entity in entities2_rules:
            print(f"  {entity['label']}: {entity['data']['name']}")
            if entity['label'] == NODE_FREQUENCY_RANGE:
                 print(f"    Min: {entity['data'].get('min_value_hz')} Hz, Max: {entity['data'].get('max_value_hz')} Hz")


    asyncio.run(main())
