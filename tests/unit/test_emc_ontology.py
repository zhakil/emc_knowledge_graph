"""
Unit tests for the EMC Knowledge Graph Ontology.
"""

import unittest
from dataclasses import is_dataclass, fields

from services.knowledge_graph.emc_ontology import (
    # Node Labels
    NODE_EMC_STANDARD, NODE_PRODUCT, NODE_COMPONENT, NODE_TEST, NODE_TEST_RESULT,
    NODE_FREQUENCY, NODE_FREQUENCY_RANGE, NODE_PHENOMENON, NODE_REGULATION,
    NODE_MITIGATION_MEASURE, NODE_DOCUMENT, NODE_ORGANIZATION, NODE_EQUIPMENT,
    # Relationship Types
    REL_APPLIES_TO, REL_CONTAINS_COMPONENT, REL_HAS_STANDARD, REL_PERFORMED_TEST,
    REL_HAS_TEST_RESULT, REL_OBSERVES_PHENOMENON, REL_REGULATES, REL_MITIGATES,
    REL_REFERENCES_STANDARD, REL_MENTIONS_PRODUCT, REL_USES_FREQUENCY,
    REL_HAS_FREQUENCY_RANGE, REL_SPECIFIES_LIMIT, REL_CONDUCTED_BY,
    REL_MANUFACTURED_BY, REL_ISSUED_BY, REL_USES_EQUIPMENT, REL_PART_OF,
    # Node Schemas (Dataclasses)
    BaseNode, EMCStandardNode, ProductNode, ComponentNode, TestNode, TestResultNode,
    FrequencyNode, FrequencyRangeNode, PhenomenonNode, RegulationNode, MitigationMeasureNode,
    DocumentNode, OrganizationNode, EquipmentNode,
    # Relationship Schemas (Dataclasses)
    BaseRelationship, AppliesToRel, SpecifiesLimitRel,
    # Main ontology definition dict and helper functions
    ONTOLOGY_DEFINITIONS, get_node_schema, get_relationship_schema
)

class TestEMCOntology(unittest.TestCase):

    def test_node_labels_defined(self):
        """Test that all expected node labels are defined and are strings."""
        expected_node_labels = [
            NODE_EMC_STANDARD, NODE_PRODUCT, NODE_COMPONENT, NODE_TEST, NODE_TEST_RESULT,
            NODE_FREQUENCY, NODE_FREQUENCY_RANGE, NODE_PHENOMENON, NODE_REGULATION,
            NODE_MITIGATION_MEASURE, NODE_DOCUMENT, NODE_ORGANIZATION, NODE_EQUIPMENT
        ]
        for label in expected_node_labels:
            self.assertIsInstance(label, str)
            self.assertTrue(label) # Not empty

        # Check against ONTOLOGY_DEFINITIONS
        self.assertCountEqual(expected_node_labels, ONTOLOGY_DEFINITIONS["node_labels"])

    def test_relationship_types_defined(self):
        """Test that all expected relationship types are defined and are strings."""
        expected_relationship_types = [
            REL_APPLIES_TO, REL_CONTAINS_COMPONENT, REL_HAS_STANDARD, REL_PERFORMED_TEST,
            REL_HAS_TEST_RESULT, REL_OBSERVES_PHENOMENON, REL_REGULATES, REL_MITIGATES,
            REL_REFERENCES_STANDARD, REL_MENTIONS_PRODUCT, REL_USES_FREQUENCY,
            REL_HAS_FREQUENCY_RANGE, REL_SPECIFIES_LIMIT, REL_CONDUCTED_BY,
            REL_MANUFACTURED_BY, REL_ISSUED_BY, REL_USES_EQUIPMENT, REL_PART_OF
        ]
        for rel_type in expected_relationship_types:
            self.assertIsInstance(rel_type, str)
            self.assertTrue(rel_type) # Not empty

        # Check against ONTOLOGY_DEFINITIONS
        self.assertCountEqual(expected_relationship_types, ONTOLOGY_DEFINITIONS["relationship_types"])

    def test_node_schemas_are_dataclasses(self):
        """Test that all defined node schemas are indeed dataclasses."""
        for label, schema_class in ONTOLOGY_DEFINITIONS["node_schemas"].items():
            self.assertTrue(is_dataclass(schema_class), f"Schema for {label} is not a dataclass.")
            self.assertIn(label, ONTOLOGY_DEFINITIONS["node_labels"], f"Schema defined for unknown label {label}")

    def test_relationship_schemas_are_dataclasses(self):
        """Test that all defined relationship schemas are dataclasses."""
        for rel_type, schema_class in ONTOLOGY_DEFINITIONS["relationship_schemas"].items():
            self.assertTrue(is_dataclass(schema_class), f"Schema for {rel_type} is not a dataclass.")
            self.assertIn(rel_type, ONTOLOGY_DEFINITIONS["relationship_types"], f"Schema defined for unknown rel type {rel_type}")

    def test_base_node_properties(self):
        """Test the fields and default types of BaseNode."""
        base = BaseNode(name="Test Base")
        self.assertEqual(base.name, "Test Base")
        self.assertIsNone(base.description)
        self.assertEqual(base.source_document_ids, [])
        self.assertEqual(base.properties, {})

        field_names = {f.name for f in fields(BaseNode)}
        self.assertIn("name", field_names)
        self.assertIn("description", field_names)
        self.assertIn("source_document_ids", field_names)
        self.assertIn("properties", field_names)

    def test_emc_standard_node_properties(self):
        """Test specific properties of EMCStandardNode."""
        standard = EMCStandardNode(name="CISPR 32")
        self.assertEqual(standard.name, "CISPR 32")
        self.assertIsNone(standard.version)
        self.assertIsNone(standard.publication_date)
        self.assertIsNone(standard.category)
        field_names = {f.name for f in fields(EMCStandardNode)}
        self.assertIn("version", field_names)
        self.assertIn("publication_date", field_names)
        self.assertIn("category", field_names)

    def test_frequency_node_properties(self):
        """Test specific properties of FrequencyNode."""
        freq = FrequencyNode(name="100MHz", value_hz=100e6, unit="MHz")
        self.assertEqual(freq.value_hz, 100e6)
        self.assertEqual(freq.unit, "MHz")

    def test_frequency_range_node_properties(self):
        """Test specific properties of FrequencyRangeNode."""
        frange = FrequencyRangeNode(name="30MHz-1GHz", min_value_hz=30e6, max_value_hz=1e9)
        self.assertEqual(frange.min_value_hz, 30e6)
        self.assertEqual(frange.max_value_hz, 1e9)

    def test_base_relationship_properties(self):
        """Test the fields and default types of BaseRelationship."""
        base_rel = BaseRelationship(confidence_score=0.8)
        self.assertEqual(base_rel.source_document_ids, [])
        self.assertEqual(base_rel.confidence_score, 0.8)
        self.assertEqual(base_rel.properties, {})

    def test_specifies_limit_rel_properties(self):
        """Test specific properties of SpecifiesLimitRel."""
        limit_rel = SpecifiesLimitRel(limit_value="50 dBuV/m", frequency_range="30-230MHz")
        self.assertEqual(limit_rel.limit_value, "50 dBuV/m")
        self.assertEqual(limit_rel.frequency_range, "30-230MHz")
        self.assertIsNone(limit_rel.detector_type)


    def test_get_node_schema_function(self):
        """Test the get_node_schema helper function."""
        self.assertIs(get_node_schema(NODE_PRODUCT), ProductNode)
        self.assertIsNone(get_node_schema("NonExistentNodeLabel"))

    def test_get_relationship_schema_function(self):
        """Test the get_relationship_schema helper function."""
        self.assertIs(get_relationship_schema(REL_APPLIES_TO), AppliesToRel)
        # For relationships without a specific schema, it should default to BaseRelationship
        self.assertIs(get_relationship_schema(REL_CONTAINS_COMPONENT), BaseRelationship)
        self.assertIs(get_relationship_schema("NonExistentRelType"), BaseRelationship)


if __name__ == '__main__':
    unittest.main()
