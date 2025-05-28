"""
Data Models and Type Definitions for EMC Knowledge Graph System

This module defines the core data structures, enumerations, and type definitions
used throughout the EMC Knowledge Graph System. It provides a structured approach
to representing automotive electronics EMC standards, organizations, relationships,
and associated metadata.

Classes:
    NodeType: Enumeration of knowledge graph node types
    RelationType: Enumeration of relationship types between nodes
    KnowledgeNode: Data class representing a knowledge graph node
    KnowledgeEdge: Data class representing a knowledge graph edge
    GraphMetadata: Data class for graph-level metadata
    ValidationResult: Data class for data validation results

Author: EMC Standards Research Team
Version: 1.0.0
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum, unique
from typing import Any, Dict, List, Optional, Set, Union

# Configure logging
logger = logging.getLogger(__name__)


@unique
class NodeType(Enum):
    """
    Enumeration of knowledge graph node types.

    This enumeration defines all possible types of entities that can be
    represented as nodes in the EMC knowledge graph system.
    """

    ORGANIZATION = "organization"
    STANDARD = "standard"
    REGULATION = "regulation"
    TEST_METHOD = "test_method"
    TEST_ENVIRONMENT = "test_environment"
    VEHICLE_TYPE = "vehicle_type"
    FREQUENCY_RANGE = "frequency_range"
    EQUIPMENT = "equipment"
    COMPLIANCE_REQUIREMENT = "compliance_requirement"
    DOCUMENT = "document"

    @classmethod
    def get_display_names(cls) -> Dict[str, str]:
        """Get human-readable display names for node types."""
        return {
            cls.ORGANIZATION: "标准化组织",
            cls.STANDARD: "技术标准",
            cls.REGULATION: "法规要求",
            cls.TEST_METHOD: "测试方法",
            cls.TEST_ENVIRONMENT: "测试环境",
            cls.VEHICLE_TYPE: "车辆类型",
            cls.FREQUENCY_RANGE: "频率范围",
            cls.EQUIPMENT: "测试设备",
            cls.COMPLIANCE_REQUIREMENT: "合规要求",
            cls.DOCUMENT: "技术文档",
        }

    @classmethod
    def get_color_scheme(cls) -> Dict[str, str]:
        """Get default color scheme for node types."""
        return {
            cls.ORGANIZATION: "#667eea",
            cls.STANDARD: "#11998e",
            cls.REGULATION: "#fa709a",
            cls.TEST_METHOD: "#fee140",
            cls.TEST_ENVIRONMENT: "#a8caba",
            cls.VEHICLE_TYPE: "#fcb69f",
            cls.FREQUENCY_RANGE: "#c471ed",
            cls.EQUIPMENT: "#4ecdc4",
            cls.COMPLIANCE_REQUIREMENT: "#ff6b6b",
            cls.DOCUMENT: "#95e1d3",
        }


@unique
class RelationType(Enum):
    """
    Enumeration of relationship types between knowledge graph nodes.

    This enumeration defines all possible relationships that can exist
    between different entities in the EMC knowledge graph.
    """

    DEVELOPS = "develops"
    INCLUDES = "includes"
    APPLIES_TO = "applies_to"
    USES = "uses"
    REQUIRES = "requires"
    REFERENCES = "references"
    COVERS = "covers"
    EXTENDS = "extends"
    SUPERSEDES = "supersedes"
    EQUIVALENT_TO = "equivalent_to"
    BASED_ON = "based_on"
    HARMONIZED_WITH = "harmonized_with"
    VALIDATED_BY = "validated_by"
    IMPLEMENTS = "implements"
    COMPLIES_WITH = "complies_with"

    @classmethod
    def get_display_names(cls) -> Dict[str, str]:
        """Get human-readable display names for relationship types."""
        return {
            cls.DEVELOPS: "制定",
            cls.INCLUDES: "包含",
            cls.APPLIES_TO: "适用于",
            cls.USES: "使用",
            cls.REQUIRES: "要求",
            cls.REFERENCES: "引用",
            cls.COVERS: "涵盖",
            cls.EXTENDS: "扩展",
            cls.SUPERSEDES: "取代",
            cls.EQUIVALENT_TO: "等同于",
            cls.BASED_ON: "基于",
            cls.HARMONIZED_WITH: "协调统一",
            cls.VALIDATED_BY: "验证通过",
            cls.IMPLEMENTS: "实施",
            cls.COMPLIES_WITH: "符合",
        }

    @classmethod
    def get_relationship_weights(cls) -> Dict[str, float]:
        """Get default weights for different relationship types."""
        return {
            cls.DEVELOPS: 1.0,
            cls.INCLUDES: 0.9,
            cls.APPLIES_TO: 0.8,
            cls.USES: 0.7,
            cls.REQUIRES: 0.9,
            cls.REFERENCES: 0.6,
            cls.COVERS: 0.8,
            cls.EXTENDS: 0.7,
            cls.SUPERSEDES: 0.9,
            cls.EQUIVALENT_TO: 1.0,
            cls.BASED_ON: 0.8,
            cls.HARMONIZED_WITH: 0.7,
            cls.VALIDATED_BY: 0.8,
            cls.IMPLEMENTS: 0.8,
            cls.COMPLIES_WITH: 0.9,
        }


@dataclass
class KnowledgeNode:
    """
    Data class representing a knowledge graph node.

    This class encapsulates all information associated with a single entity
    in the EMC knowledge graph, including its identification, classification,
    and descriptive attributes.

    Attributes:
        id: Unique identifier for the node
        name: Human-readable name of the entity
        node_type: Type classification of the node
        description: Detailed description of the entity
        attributes: Additional metadata and properties
        created_date: Timestamp when the node was created
        last_updated: Timestamp when the node was last modified
        version: Version number for tracking changes
        tags: Set of tags for categorization
        status: Current status of the entity
        source: Source of information for this entity
    """

    id: str
    name: str
    node_type: NodeType
    description: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_date: Optional[datetime] = field(default_factory=datetime.now)
    last_updated: Optional[datetime] = field(default_factory=datetime.now)
    version: str = "1.0"
    tags: Set[str] = field(default_factory=set)
    status: str = "active"
    source: Optional[str] = None

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.node_type, str):
            self.node_type = NodeType(self.node_type)

        if isinstance(self.tags, list):
            self.tags = set(self.tags)

        # Ensure timestamps are datetime objects
        if isinstance(self.created_date, str):
            self.created_date = datetime.fromisoformat(self.created_date)
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        result = asdict(self)
        result["node_type"] = self.node_type.value
        result["tags"] = list(self.tags)

        # Convert datetime objects to ISO format strings
        if self.created_date:
            result["created_date"] = self.created_date.isoformat()
        if self.last_updated:
            result["last_updated"] = self.last_updated.isoformat()

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeNode":
        """Create node from dictionary representation."""
        # Handle node_type conversion
        if "node_type" in data and isinstance(data["node_type"], str):
            data["node_type"] = NodeType(data["node_type"])

        # Handle tags conversion
        if "tags" in data and isinstance(data["tags"], list):
            data["tags"] = set(data["tags"])

        return cls(**data)

    def update_timestamp(self):
        """Update the last_updated timestamp."""
        self.last_updated = datetime.now()

    def add_tag(self, tag: str):
        """Add a tag to the node."""
        self.tags.add(tag)
        self.update_timestamp()

    def remove_tag(self, tag: str):
        """Remove a tag from the node."""
        self.tags.discard(tag)
        self.update_timestamp()

    def get_display_name(self) -> str:
        """Get the display name for the node type."""
        return NodeType.get_display_names().get(self.node_type, self.node_type.value)

    def get_color(self) -> str:
        """Get the default color for this node type."""
        return NodeType.get_color_scheme().get(self.node_type, "#cccccc")

    def validate(self) -> List[str]:
        """Validate the node data and return list of validation errors."""
        errors = []

        if not self.id or not self.id.strip():
            errors.append("Node ID cannot be empty")

        if not self.name or not self.name.strip():
            errors.append("Node name cannot be empty")

        if not isinstance(self.node_type, NodeType):
            errors.append("Invalid node type")

        if not self.description or not self.description.strip():
            errors.append("Node description cannot be empty")

        if len(self.description) > 1000:
            errors.append("Description too long (max 1000 characters)")

        return errors


@dataclass
class KnowledgeEdge:
    """
    Data class representing a knowledge graph edge (relationship).

    This class encapsulates information about relationships between entities
    in the EMC knowledge graph, including relationship type, strength, and metadata.

    Attributes:
        source: Source node identifier
        target: Target node identifier
        relation_type: Type of relationship
        weight: Strength or importance of the relationship (0.0 to 1.0)
        attributes: Additional metadata about the relationship
        created_date: Timestamp when the edge was created
        last_updated: Timestamp when the edge was last modified
        version: Version number for tracking changes
        confidence: Confidence level in the relationship (0.0 to 1.0)
        source_reference: Reference to source document or authority
        bidirectional: Whether the relationship is bidirectional
    """

    source: str
    target: str
    relation_type: RelationType
    weight: float = 1.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_date: Optional[datetime] = field(default_factory=datetime.now)
    last_updated: Optional[datetime] = field(default_factory=datetime.now)
    version: str = "1.0"
    confidence: float = 1.0
    source_reference: Optional[str] = None
    bidirectional: bool = False

    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.relation_type, str):
            self.relation_type = RelationType(self.relation_type)

        # Ensure weight and confidence are in valid range
        self.weight = max(0.0, min(1.0, self.weight))
        self.confidence = max(0.0, min(1.0, self.confidence))

        # Ensure timestamps are datetime objects
        if isinstance(self.created_date, str):
            self.created_date = datetime.fromisoformat(self.created_date)
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated)

    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary representation."""
        result = asdict(self)
        result["relation_type"] = self.relation_type.value

        # Convert datetime objects to ISO format strings
        if self.created_date:
            result["created_date"] = self.created_date.isoformat()
        if self.last_updated:
            result["last_updated"] = self.last_updated.isoformat()

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeEdge":
        """Create edge from dictionary representation."""
        # Handle relation_type conversion
        if "relation_type" in data and isinstance(data["relation_type"], str):
            data["relation_type"] = RelationType(data["relation_type"])

        return cls(**data)

    def update_timestamp(self):
        """Update the last_updated timestamp."""
        self.last_updated = datetime.now()

    def get_display_name(self) -> str:
        """Get the display name for the relationship type."""
        return RelationType.get_display_names().get(
            self.relation_type, self.relation_type.value
        )

    def get_default_weight(self) -> float:
        """Get the default weight for this relationship type."""
        return RelationType.get_relationship_weights().get(self.relation_type, 0.5)

    def validate(self) -> List[str]:
        """Validate the edge data and return list of validation errors."""
        errors = []

        if not self.source or not self.source.strip():
            errors.append("Source node ID cannot be empty")

        if not self.target or not self.target.strip():
            errors.append("Target node ID cannot be empty")

        if self.source == self.target:
            errors.append("Self-loops not allowed")

        if not isinstance(self.relation_type, RelationType):
            errors.append("Invalid relation type")

        if not 0.0 <= self.weight <= 1.0:
            errors.append("Weight must be between 0.0 and 1.0")

        if not 0.0 <= self.confidence <= 1.0:
            errors.append("Confidence must be between 0.0 and 1.0")

        return errors


@dataclass
class GraphMetadata:
    """
    Data class for graph-level metadata.

    This class stores information about the overall knowledge graph,
    including creation details, statistics, and configuration.
    """

    name: str
    description: str
    version: str = "1.0.0"
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    author: str = "EMC Standards Research Team"
    license: str = "MIT"
    node_count: int = 0
    edge_count: int = 0
    node_types: Dict[str, int] = field(default_factory=dict)
    relation_types: Dict[str, int] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary representation."""
        result = asdict(self)
        result["tags"] = list(self.tags)
        result["created_date"] = self.created_date.isoformat()
        result["last_updated"] = self.last_updated.isoformat()
        return result


@dataclass
class ValidationResult:
    """
    Data class for validation results.

    This class encapsulates the results of data validation operations,
    including success status, error messages, and warnings.
    """

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_nodes: int = 0
    validated_edges: int = 0

    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)

    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return asdict(self)


# Type aliases for better code readability
NodeDict = Dict[str, KnowledgeNode]
EdgeList = List[KnowledgeEdge]
AttributeDict = Dict[str, Any]

# Constants for validation
MAX_DESCRIPTION_LENGTH = 1000
MAX_NAME_LENGTH = 200
MIN_WEIGHT = 0.0
MAX_WEIGHT = 1.0
MIN_CONFIDENCE = 0.0
MAX_CONFIDENCE = 1.0


def create_sample_node(node_id: str, node_type: NodeType) -> KnowledgeNode:
    """
    Create a sample node for testing purposes.

    Args:
        node_id: Unique identifier for the node
        node_type: Type of the node

    Returns:
        KnowledgeNode: Sample node instance
    """
    return KnowledgeNode(
        id=node_id,
        name=f"Sample {node_type.value.title()}",
        node_type=node_type,
        description=f"This is a sample {node_type.value} node for testing purposes.",
        tags={"sample", "test"},
    )


def create_sample_edge(
    source: str, target: str, relation_type: RelationType
) -> KnowledgeEdge:
    """
    Create a sample edge for testing purposes.

    Args:
        source: Source node identifier
        target: Target node identifier
        relation_type: Type of relationship

    Returns:
        KnowledgeEdge: Sample edge instance
    """
    return KnowledgeEdge(
        source=source,
        target=target,
        relation_type=relation_type,
        weight=RelationType.get_relationship_weights().get(relation_type, 0.5),
    )


def validate_graph_data(nodes: NodeDict, edges: EdgeList) -> ValidationResult:
    """
    Validate graph data structure.

    Args:
        nodes: Dictionary of nodes indexed by ID
        edges: List of edges

    Returns:
        ValidationResult: Validation results
    """
    result = ValidationResult(is_valid=True)

    # Validate nodes
    for node_id, node in nodes.items():
        if node.id != node_id:
            result.add_error(f"Node ID mismatch: {node_id} vs {node.id}")

        node_errors = node.validate()
        for error in node_errors:
            result.add_error(f"Node {node_id}: {error}")

        result.validated_nodes += 1

    # Validate edges
    for i, edge in enumerate(edges):
        edge_errors = edge.validate()
        for error in edge_errors:
            result.add_error(f"Edge {i}: {error}")

        # Check if referenced nodes exist
        if edge.source not in nodes:
            result.add_error(f"Edge {i}: Source node {edge.source} not found")

        if edge.target not in nodes:
            result.add_error(f"Edge {i}: Target node {edge.target} not found")

        result.validated_edges += 1

    return result
