"""
Unit tests for EMCRelationBuilder, focusing on rule-based relationship identification.
"""
import unittest
import asyncio

from services.knowledge_graph.relation_builder import EMCRelationBuilder
from services.knowledge_graph.emc_ontology import (
    NODE_PRODUCT, NODE_EMC_STANDARD, NODE_DOCUMENT, NODE_TEST, NODE_FREQUENCY, NODE_FREQUENCY_RANGE,
    REL_HAS_STANDARD, REL_APPLIES_TO, REL_REFERENCES_STANDARD, REL_MENTIONS_PRODUCT,
    REL_USES_FREQUENCY, REL_HAS_FREQUENCY_RANGE,
    ProductNode, EMCStandardNode, DocumentNode, TestNode, FrequencyNode, FrequencyRangeNode
)

class TestEMCRelationBuilderRuleBased(unittest.TestCase):

    def setUp(self):
        self.builder = EMCRelationBuilder(deepseek_service=None)
        # Sample entities - ensure 'data' is a dictionary (like after asdict() or .__dict__)
        # and each entity has a unique 'id_in_document' for the builder to use.
        self.doc1 = {"label": NODE_DOCUMENT, "data": DocumentNode(name="Report1.pdf", file_id="doc001").__dict__, "id_in_document": "doc_entity_1"}
        self.prod1 = {"label": NODE_PRODUCT, "data": ProductNode(name="DeviceAlpha").__dict__, "id_in_document": "prod_entity_1"}
        self.std1 = {"label": NODE_EMC_STANDARD, "data": EMCStandardNode(name="EN 55032").__dict__, "id_in_document": "std_entity_1"}
        self.std2 = {"label": NODE_EMC_STANDARD, "data": EMCStandardNode(name="IEC 61000-3-2").__dict__, "id_in_document": "std_entity_2"}
        self.test1 = {"label": NODE_TEST, "data": TestNode(name="Radiated Emissions").__dict__, "id_in_document": "test_entity_1"}
        self.freq1 = {"label": NODE_FREQUENCY, "data": FrequencyNode(name="100MHz", value_hz=100e6).__dict__, "id_in_document": "freq_entity_1"}
        self.frange1 = {"label": NODE_FREQUENCY_RANGE, "data": FrequencyRangeNode(name="30MHz-1GHz", min_value_hz=30e6, max_value_hz=1e9).__dict__, "id_in_document": "frange_entity_1"}

        self.sample_text_context = "DeviceAlpha was tested per EN 55032. Report1.pdf covers this. Radiated Emissions test used frequencies from 30MHz-1GHz, with a specific check at 100MHz."


    def test_product_has_standard_and_standard_applies_to_product(self):
        entities = [self.prod1, self.std1]
        relationships = asyncio.run(
            self.builder.build_relationships(entities, self.sample_text_context, "doc001", use_ai=False, use_rules=True)
        )

        # Current rule creates both from co-occurrence
        self.assertEqual(len(relationships), 2)

        has_std_rels = [r for r in relationships if r['type'] == REL_HAS_STANDARD]
        self.assertEqual(len(has_std_rels), 1)
        self.assertEqual(has_std_rels[0]['from_entity_id'], self.prod1['id_in_document'])
        self.assertEqual(has_std_rels[0]['to_entity_id'], self.std1['id_in_document'])

        applies_to_rels = [r for r in relationships if r['type'] == REL_APPLIES_TO]
        self.assertEqual(len(applies_to_rels), 1)
        self.assertEqual(applies_to_rels[0]['from_entity_id'], self.std1['id_in_document']) # Standard APPLIES_TO Product
        self.assertEqual(applies_to_rels[0]['to_entity_id'], self.prod1['id_in_document'])


    def test_document_references_standard_and_mentions_product(self):
        entities = [self.doc1, self.std1, self.prod1]
        relationships = asyncio.run(
            self.builder.build_relationships(entities, self.sample_text_context, "doc001", use_ai=False, use_rules=True)
        )

        # Expected: DOC->STD, DOC->PROD, PROD<->STD (2 rels) = 4 relationships
        # The rule based system is simple and generates all co-occurrence based relationships

        ref_std_rels = [r for r in relationships if r['type'] == REL_REFERENCES_STANDARD]
        self.assertTrue(any(r['from_entity_id'] == self.doc1['id_in_document'] and r['to_entity_id'] == self.std1['id_in_document'] for r in ref_std_rels))

        mentions_prod_rels = [r for r in relationships if r['type'] == REL_MENTIONS_PRODUCT]
        self.assertTrue(any(r['from_entity_id'] == self.doc1['id_in_document'] and r['to_entity_id'] == self.prod1['id_in_document'] for r in mentions_prod_rels))

        # Check total number of relationships, considering Product<->Standard links too
        # prod1-std1 (HAS_STANDARD), std1-prod1 (APPLIES_TO)
        # doc1-std1 (REFERENCES_STANDARD)
        # doc1-prod1 (MENTIONS_PRODUCT)
        # Total should be 4 if only these entities are present and rules are simple co-occurrence
        self.assertEqual(len(relationships), 4)


    def test_test_uses_frequency_and_has_frequency_range(self):
        entities = [self.test1, self.freq1, self.frange1]
        relationships = asyncio.run(
            self.builder.build_relationships(entities, self.sample_text_context, "doc001", use_ai=False, use_rules=True)
        )
        # Expected: TEST->FREQ, TEST->FRANGE = 2 relationships
        self.assertEqual(len(relationships), 2)

        uses_freq_rels = [r for r in relationships if r['type'] == REL_USES_FREQUENCY]
        self.assertEqual(len(uses_freq_rels), 1)
        self.assertEqual(uses_freq_rels[0]['from_entity_id'], self.test1['id_in_document'])
        self.assertEqual(uses_freq_rels[0]['to_entity_id'], self.freq1['id_in_document'])

        has_frange_rels = [r for r in relationships if r['type'] == REL_HAS_FREQUENCY_RANGE]
        self.assertEqual(len(has_frange_rels), 1)
        self.assertEqual(has_frange_rels[0]['from_entity_id'], self.test1['id_in_document'])
        self.assertEqual(has_frange_rels[0]['to_entity_id'], self.frange1['id_in_document'])

    def test_no_relationships_for_unrelated_entities(self):
        # std2 is not mentioned in relation to prod1 in the simple rules
        entities = [self.prod1, self.std2, self.freq1] # freq1 is not related to prod1 or std2 by current rules
        relationships = asyncio.run(
            self.builder.build_relationships(entities, "Product DeviceAlpha. Standard IEC 61000-3-2. Freq 100MHz", "doc001", use_ai=False, use_rules=True)
        )
        # Current simple rules: prod1<->std2 (2 rels). No direct link for freq1 to these.
        self.assertEqual(len(relationships), 2)
        has_std_rel = any(r['type'] == REL_HAS_STANDARD and r['from_entity_id'] == self.prod1['id_in_document'] and r['to_entity_id'] == self.std2['id_in_document'] for r in relationships)
        applies_to_rel = any(r['type'] == REL_APPLIES_TO and r['from_entity_id'] == self.std2['id_in_document'] and r['to_entity_id'] == self.prod1['id_in_document'] for r in relationships)
        self.assertTrue(has_std_rel)
        self.assertTrue(applies_to_rel)


    def test_all_entity_types_present(self):
        # This test ensures that when all types of entities are present,
        # the expected pairwise relationships are formed by the current simple rules.
        all_entities = [self.doc1, self.prod1, self.std1, self.std2, self.test1, self.freq1, self.frange1]
        relationships = asyncio.run(
            self.builder.build_relationships(all_entities, self.sample_text_context, "doc001", use_ai=False, use_rules=True)
        )

        # Expected relationships based on simple co-occurrence rules:
        # Prod1 <-> Std1 (2 rels: HAS_STANDARD, APPLIES_TO)
        # Prod1 <-> Std2 (2 rels)
        # Doc1 -> Prod1 (1 rel: MENTIONS_PRODUCT)
        # Doc1 -> Std1 (1 rel: REFERENCES_STANDARD)
        # Doc1 -> Std2 (1 rel: REFERENCES_STANDARD)
        # Test1 -> Freq1 (1 rel: USES_FREQUENCY)
        # Test1 -> Frange1 (1 rel: HAS_FREQUENCY_RANGE)
        # Total = 2 + 2 + 1 + 1 + 1 + 1 + 1 = 9

        # Count them by type to be more specific
        rel_counts = {}
        for r in relationships:
            rel_counts[r['type']] = rel_counts.get(r['type'], 0) + 1

        self.assertEqual(rel_counts.get(REL_HAS_STANDARD, 0), 2) # prod1-std1, prod1-std2
        self.assertEqual(rel_counts.get(REL_APPLIES_TO, 0), 2)   # std1-prod1, std2-prod1
        self.assertEqual(rel_counts.get(REL_MENTIONS_PRODUCT, 0), 1) # doc1-prod1
        self.assertEqual(rel_counts.get(REL_REFERENCES_STANDARD, 0), 2) # doc1-std1, doc1-std2
        self.assertEqual(rel_counts.get(REL_USES_FREQUENCY, 0), 1) # test1-freq1
        self.assertEqual(rel_counts.get(REL_HAS_FREQUENCY_RANGE, 0), 1) # test1-frange1

        self.assertEqual(len(relationships), 9)


if __name__ == '__main__':
    unittest.main()
