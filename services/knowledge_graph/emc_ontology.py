"""
EMC Knowledge Graph Ontology

This module defines the schema for the EMC knowledge graph, including node labels,
relationship types, and their properties.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# --- Node Labels ---
NODE_EMC_STANDARD = "EMCStandard"  # e.g., CISPR 32, IEC 61000-4-2
NODE_PRODUCT = "Product"  # e.g., Laptop Model X, Power Supply Unit Y
NODE_COMPONENT = "Component"  # e.g., CPU, Capacitor, Shielding Case
NODE_TEST = "Test"  # e.g., Radiated Emissions Test, ESD Test
NODE_TEST_RESULT = "TestResult"  # e.g., Pass, Fail, Margin
NODE_FREQUENCY = "Frequency"  # e.g., 100 MHz, 2.4 GHz
NODE_FREQUENCY_RANGE = "FrequencyRange" # e.g., 30MHz-1GHz
NODE_PHENOMENON = "Phenomenon"  # e.g., Radiated Emission, Electrostatic Discharge
NODE_REGULATION = "Regulation"  # e.g., FCC Part 15, EU EMC Directive
NODE_MITIGATION_MEASURE = "MitigationMeasure"  # e.g., Ferrite Bead, Shielding
NODE_DOCUMENT = "Document" # e.g., Test Report, Standard Document, Datasheet
NODE_ORGANIZATION = "Organization" # e.g., Test Lab, Manufacturer, Regulatory Body
NODE_EQUIPMENT = "Equipment" # e.g., Spectrum Analyzer, LISN

# --- Relationship Types ---
REL_APPLIES_TO = "APPLIES_TO"  # (EMCStandard) -[APPLIES_TO]-> (Product)
REL_CONTAINS_COMPONENT = "CONTAINS_COMPONENT"  # (Product) -[CONTAINS_COMPONENT]-> (Component)
REL_HAS_STANDARD = "HAS_STANDARD"  # (Product) -[HAS_STANDARD]-> (EMCStandard)
REL_PERFORMED_TEST = "PERFORMED_TEST"  # (Product) -[PERFORMED_TEST]-> (Test)
REL_HAS_TEST_RESULT = "HAS_TEST_RESULT"  # (Test) -[HAS_TEST_RESULT]-> (TestResult)
REL_OBSERVES_PHENOMENON = "OBSERVES_PHENOMENON"  # (TestResult) -[OBSERVES_PHENOMENON]-> (Phenomenon)
REL_REGULATES = "REGULATES"  # (Regulation) -[REGULATES]-> (Product)
REL_MITIGATES = "MITIGATES"  # (MitigationMeasure) -[MITIGATES]-> (Phenomenon)
REL_REFERENCES_STANDARD = "REFERENCES_STANDARD" # (Document) -[REFERENCES_STANDARD]-> (EMCStandard)
REL_MENTIONS_PRODUCT = "MENTIONS_PRODUCT" # (Document) -[MENTIONS_PRODUCT]-> (Product)
REL_USES_FREQUENCY = "USES_FREQUENCY" # (Test) -[USES_FREQUENCY]-> (Frequency) or (Product) -[USES_FREQUENCY]-> (Frequency)
REL_HAS_FREQUENCY_RANGE = "HAS_FREQUENCY_RANGE" # (Test) -[HAS_FREQUENCY_RANGE]-> (FrequencyRange) or (EMCStandard) -[HAS_FREQUENCY_RANGE]-> (FrequencyRange)
REL_SPECIFIES_LIMIT = "SPECIFIES_LIMIT" # (EMCStandard) -[SPECIFIES_LIMIT]-> (Phenomenon)
REL_CONDUCTED_BY = "CONDUCTED_BY" # (Test) -[CONDUCTED_BY]-> (Organization)
REL_MANUFACTURED_BY = "MANUFACTURED_BY" # (Product) -[MANUFACTURED_BY]-> (Organization)
REL_ISSUED_BY = "ISSUED_BY" # (Regulation) -[ISSUED_BY]-> (Organization)
REL_USES_EQUIPMENT = "USES_EQUIPMENT" # (Test) -[USES_EQUIPMENT]-> (Equipment)
REL_PART_OF = "PART_OF" # (Component) -[PART_OF]-> (Product) or (Frequency) -[PART_OF]-> (FrequencyRange)

# --- Node Properties ---
# It's good practice to define common properties if they appear in many nodes,
# or define them per node if they are specific.

@dataclass
class BaseNode:
    name: str
    description: Optional[str] = None
    source_document_ids: List[str] = field(default_factory=list) # IDs of documents where this was extracted
    properties: Dict[str, Any] = field(default_factory=dict) # For additional, less structured data

@dataclass
class EMCStandardNode(BaseNode):
    version: Optional[str] = None
    publication_date: Optional[str] = None # ISO format date string
    category: Optional[str] = None # e.g., Emissions, Immunity, Generic, Product-specific

@dataclass
class ProductNode(BaseNode):
    model_number: Optional[str] = None
    manufacturer: Optional[str] = None # Could also be a relationship to an Organization node
    product_type: Optional[str] = None # e.g., ITE, Medical, Automotive

@dataclass
class ComponentNode(BaseNode):
    part_number: Optional[str] = None
    manufacturer: Optional[str] = None
    component_type: Optional[str] = None # e.g., IC, Resistor, Connector

@dataclass
class TestNode(BaseNode):
    test_date: Optional[str] = None # ISO format date string
    test_setup_description: Optional[str] = None
    test_procedure_id: Optional[str] = None

@dataclass
class TestResultNode(BaseNode): # Name could be 'Pass', 'Fail'
    value: Optional[str] = None # e.g., "Pass", "Fail", "45 dBµV/m"
    margin: Optional[str] = None # e.g., "-3.5 dB"
    limit_value: Optional[str] = None # The limit against which it was tested
    frequency_at_max_emission: Optional[str] = None # For emission tests

@dataclass
class FrequencyNode(BaseNode): # Name could be '100MHz'
    value_hz: Optional[float] = None # Always store in Hz for consistency
    unit: Optional[str] = "Hz" # Original unit like MHz, GHz for display convenience

@dataclass
class FrequencyRangeNode(BaseNode): # Name could be '30MHz-1GHz'
    min_value_hz: Optional[float] = None
    max_value_hz: Optional[float] = None
    unit: Optional[str] = "Hz" # Common unit for the range

@dataclass
class PhenomenonNode(BaseNode): # Name could be 'Radiated Emission'
    phenomenon_type: Optional[str] = None # e.g., Conducted, Radiated, ESD, Surge

@dataclass
class RegulationNode(BaseNode): # Name could be 'FCC Part 15 Subpart B'
    jurisdiction: Optional[str] = None # e.g., USA, EU, Global
    effective_date: Optional[str] = None

@dataclass
class MitigationMeasureNode(BaseNode): # Name could be 'Common Mode Choke XF123'
    measure_type: Optional[str] = None # e.g., Filter, Shield, Grounding
    effectiveness_description: Optional[str] = None

@dataclass
class DocumentNode(BaseNode): # Name is filename or title
    file_id: Optional[str] = None # From FileMetadata
    document_type: Optional[str] = None # e.g., Test Report, Standard, Application Note
    creation_date: Optional[str] = None
    author: Optional[str] = None

@dataclass
class OrganizationNode(BaseNode): # Name is organization name
    organization_type: Optional[str] = None # e.g., Test Laboratory, Manufacturer, Government Agency
    location: Optional[str] = None

@dataclass
class EquipmentNode(BaseNode): # Name is equipment model
    equipment_type: Optional[str] = None # e.g., Spectrum Analyzer, LISN, ESD Gun
    serial_number: Optional[str] = None
    calibration_due_date: Optional[str] = None

# --- Relationship Properties ---
@dataclass
class BaseRelationship:
    source_document_ids: List[str] = field(default_factory=list)
    confidence_score: Optional[float] = None
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AppliesToRel(BaseRelationship):
    conditions: Optional[str] = None # e.g., "For Class A equipment"

@dataclass
class SpecifiesLimitRel(BaseRelationship):
    limit_value: str # e.g., "50 dBuV/m"
    frequency_range: Optional[str] = None # e.g., "30MHz-230MHz"
    detector_type: Optional[str] = None # e.g., Quasi-Peak, Peak, Average

# Example of how one might use these:
# standard_cispr32 = EMCStandardNode(name="CISPR 32 Ed. 2.0", version="2.0", publication_date="2015-03-01")
# product_laptop = ProductNode(name="SuperLaptop X1", model_number="SLX1-2024")
# rel_applies = AppliesToRel(conditions="Class B ITE equipment")
# Storing in graph: (standard_cispr32)-[rel_applies_to_product_laptop:APPLIES_TO {conditions: "..."}]->(product_laptop)

# This file primarily defines the constants and data structures.
# The actual graph interaction logic will be in other service files.

ONTOLOGY_DEFINITIONS = {
    "node_labels": [
        NODE_EMC_STANDARD, NODE_PRODUCT, NODE_COMPONENT, NODE_TEST, NODE_TEST_RESULT,
        NODE_FREQUENCY, NODE_FREQUENCY_RANGE, NODE_PHENOMENON, NODE_REGULATION,
        NODE_MITIGATION_MEASURE, NODE_DOCUMENT, NODE_ORGANIZATION, NODE_EQUIPMENT
    ],
    "relationship_types": [
        REL_APPLIES_TO, REL_CONTAINS_COMPONENT, REL_HAS_STANDARD, REL_PERFORMED_TEST,
        REL_HAS_TEST_RESULT, REL_OBSERVES_PHENOMENON, REL_REGULATES, REL_MITIGATES,
        REL_REFERENCES_STANDARD, REL_MENTIONS_PRODUCT, REL_USES_FREQUENCY,
        REL_HAS_FREQUENCY_RANGE, REL_SPECIFIES_LIMIT, REL_CONDUCTED_BY,
        REL_MANUFACTURED_BY, REL_ISSUED_BY, REL_USES_EQUIPMENT, REL_PART_OF
    ],
    "node_schemas": {
        NODE_EMC_STANDARD: EMCStandardNode,
        NODE_PRODUCT: ProductNode,
        NODE_COMPONENT: ComponentNode,
        NODE_TEST: TestNode,
        NODE_TEST_RESULT: TestResultNode,
        NODE_FREQUENCY: FrequencyNode,
        NODE_FREQUENCY_RANGE: FrequencyRangeNode,
        NODE_PHENOMENON: PhenomenonNode,
        NODE_REGULATION: RegulationNode,
        NODE_MITIGATION_MEASURE: MitigationMeasureNode,
        NODE_DOCUMENT: DocumentNode,
        NODE_ORGANIZATION: OrganizationNode,
        NODE_EQUIPMENT: EquipmentNode,
    },
    "relationship_schemas": {
        REL_APPLIES_TO: AppliesToRel,
        REL_SPECIFIES_LIMIT: SpecifiesLimitRel,
        # Other relationships can use BaseRelationship if no specific properties needed yet
    }
}

def get_node_schema(node_label: str) -> Optional[type]:
    return ONTOLOGY_DEFINITIONS["node_schemas"].get(node_label)

def get_relationship_schema(rel_type: str) -> Optional[type]:
    return ONTOLOGY_DEFINITIONS["relationship_schemas"].get(rel_type, BaseRelationship)
