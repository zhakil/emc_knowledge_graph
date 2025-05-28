"""
EMC Knowledge Graph System Package
Automotive Electronics EMC Standards Knowledge Graph and Analysis System

This package provides comprehensive tools for modeling, analyzing, and visualizing
the relationships between automotive electronics EMC (Electromagnetic Compatibility)
standards, organizations, test methods, and regulations.

Main modules:
- knowledge_graph: Core knowledge graph implementation
- data_models: Data structures and type definitions
- visualizer: Visualization components and tools
- utils: Utility functions and helpers

Author: EMC Standards Research Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "EMC Standards Research Team"
__email__ = "emc-research@example.com"
__license__ = "MIT"
__status__ = "Production"

# Package metadata
__title__ = "EMC Knowledge Graph System"
__description__ = (
    "Automotive Electronics EMC Standards Knowledge Graph and Analysis System"
)
__url__ = "https://github.com/emc-research/emc-knowledge-graph"
__doc_url__ = "https://emc-knowledge-graph.readthedocs.io/"
__bug_reports__ = "https://github.com/emc-research/emc-knowledge-graph/issues"

# Version information tuple
VERSION_INFO = tuple(int(part) for part in __version__.split("."))

# Import main classes and functions for easy access
try:
    from .data_models import KnowledgeEdge, KnowledgeNode, NodeType, RelationType
    from .knowledge_graph import EMCKnowledgeGraph
    from .utils import load_config, setup_logging, validate_data_structure
    from .visualizer import KnowledgeGraphVisualizer

    # Define what gets imported with "from emc_kg import *"
    __all__ = [
        # Main classes
        "EMCKnowledgeGraph",
        "KnowledgeGraphVisualizer",
        # Data models
        "NodeType",
        "RelationType",
        "KnowledgeNode",
        "KnowledgeEdge",
        # Utility functions
        "load_config",
        "setup_logging",
        "validate_data_structure",
        # Package metadata
        "__version__",
        "__author__",
        "__license__",
        "VERSION_INFO",
    ]

except ImportError as e:
    # Handle import errors gracefully during development
    import warnings

    warnings.warn(
        f"Could not import all modules: {e}. "
        "This may be normal during development or if optional dependencies are missing.",
        ImportWarning,
    )

    # Minimal exports if imports fail
    __all__ = ["__version__", "__author__", "__license__", "VERSION_INFO"]

# Package configuration
DEFAULT_CONFIG = {
    "debug_mode": False,
    "log_level": "INFO",
    "max_workers": 4,
    "cache_enabled": True,
    "graph_layout": "spring",
    "output_dir": "output",
}

# Supported Python versions
PYTHON_REQUIRES = ">=3.8"

# Key dependencies
CORE_DEPENDENCIES = [
    "networkx>=3.1",
    "matplotlib>=3.7.0",
    "plotly>=5.15.0",
    "pandas>=2.0.0",
    "pyyaml>=6.0",
]

# Optional dependencies for extended functionality
OPTIONAL_DEPENDENCIES = {
    "dev": ["pytest>=7.4.0", "black>=23.7.0", "flake8>=6.0.0", "mypy>=1.5.0"],
    "web": ["dash>=2.12.0", "flask>=2.3.0"],
    "jupyter": ["jupyter>=1.0.0", "ipykernel>=6.25.0"],
}


def get_version():
    """
    Get the package version string.

    Returns:
        str: Version string in format "major.minor.patch"
    """
    return __version__


def get_version_info():
    """
    Get detailed version information.

    Returns:
        dict: Dictionary containing version details
    """
    return {
        "version": __version__,
        "version_info": VERSION_INFO,
        "author": __author__,
        "license": __license__,
        "status": __status__,
        "python_requires": PYTHON_REQUIRES,
    }


def check_dependencies():
    """
    Check if core dependencies are available.

    Returns:
        dict: Dictionary with dependency status
    """
    import importlib

    status = {}

    core_modules = {
        "networkx": "networkx",
        "matplotlib": "matplotlib",
        "plotly": "plotly",
        "pandas": "pandas",
        "yaml": "pyyaml",
    }

    for module_name, package_name in core_modules.items():
        try:
            importlib.import_module(module_name)
            status[package_name] = True
        except ImportError:
            status[package_name] = False

    return status


def print_system_info():
    """
    Print system and package information for debugging.
    """
    import platform
    import sys

    print(f"EMC Knowledge Graph System v{__version__}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Python executable: {sys.executable}")

    deps = check_dependencies()
    print("\nCore dependencies:")
    for dep, available in deps.items():
        status = "✓" if available else "✗"
        print(f"  {status} {dep}")


# Module-level docstring for help()
def _get_module_help():
    """Return help text for the module."""
    return f"""
EMC Knowledge Graph System v{__version__}

A comprehensive system for modeling and analyzing automotive electronics 
EMC (Electromagnetic Compatibility) standards and their relationships.

Quick start:
    from emc_kg import EMCKnowledgeGraph
    
    # Create knowledge graph
    kg = EMCKnowledgeGraph()
    
    # Generate visualization
    fig, ax = kg.create_matplotlib_visualization()
    
    # Export data
    kg.export_to_json('emc_graph.json')

For more information:
    - Documentation: {__doc_url__}
    - Issues: {__bug_reports__}
    - Source: {__url__}
"""


# Set module docstring
__doc__ = _get_module_help()
