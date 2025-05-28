#!/usr/bin/env python3
"""
Setup configuration for EMC Knowledge Graph System
Package installation and metadata configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file for long description
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Automotive Electronics EMC Standards Knowledge Graph System"

# Read requirements from requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [
            line.strip() 
            for line in fh 
            if line.strip() and not line.startswith("#")
        ]
else:
    requirements = [
        "networkx>=3.1",
        "matplotlib>=3.7.0", 
        "plotly>=5.15.0",
        "pandas>=2.0.0",
        "pyyaml>=6.0"
    ]

# Read version from src/__init__.py or use default
version = "1.0.0"
try:
    with open("src/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break
except FileNotFoundError:
    pass

setup(
    name="emc-knowledge-graph",
    version=version,
    author="EMC Standards Research Team",
    author_email="emc-research@example.com",
    description="Comprehensive automotive electronics EMC standards knowledge graph system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/emc-research/emc-knowledge-graph",
    project_urls={
        "Bug Reports": "https://github.com/emc-research/emc-knowledge-graph/issues",
        "Source": "https://github.com/emc-research/emc-knowledge-graph",
        "Documentation": "https://emc-knowledge-graph.readthedocs.io/",
    },
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Classification metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Install dependencies
    install_requires=requirements,
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "pre-commit>=3.4.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipykernel>=6.25.0",
            "jupyterlab>=4.0.0",
        ],
        "web": [
            "dash>=2.12.0",
            "dash-bootstrap-components>=1.4.0",
        ],
    },
    
    # Command line entry points
    entry_points={
        "console_scripts": [
            "emc-kg=knowledge_graph:main",
            "emc-build=build:main",
            "emc-analyze=analyzer:main",
        ],
    },
    
    # Include additional files
    include_package_data=True,
    package_data={
        "": [
            "*.json", 
            "*.yaml", 
            "*.yml", 
            "*.md",
            "*.txt",
            "*.csv"
        ],
    },
    
    # Data files
    data_files=[
        ("config", ["config.yaml"]),
        ("data", [
            "data/standards.json",
            "data/organizations.json", 
            "data/relationships.json"
        ]),
    ],
    
    # Development dependencies
    test_suite="tests",
    tests_require=[
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.11.0",
    ],
    
    # Keywords for PyPI
    keywords=[
        "emc", 
        "automotive", 
        "electronics", 
        "standards", 
        "knowledge-graph",
        "cispr", 
        "iso", 
        "sae",
        "visualization",
        "compliance"
    ],
    
    # Minimum Python and package versions
    zip_safe=False,
)