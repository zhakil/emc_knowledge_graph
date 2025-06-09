#!/usr/bin/env python3
"""
EMC知识图谱系统安装配置
"""

from setuptools import setup, find_packages
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def read_requirements(filename):
    """读取requirements文件"""
    requirements_path = os.path.join(ROOT_DIR, filename)
    try:
        with open(requirements_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        requirements = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-r'):
                requirements.append(line)
        return requirements
    except FileNotFoundError:
        return []

# 依赖配置
install_requires = read_requirements('requirements.txt')

extras_require = {
    'dev': [
        'ruff>=0.2.1',
        'pytest>=8.0.0',
        'pytest-asyncio>=0.23.2',
        'ipython>=8.18.1',
        'rich>=13.7.0',
    ],
    'ml': [
        'faiss-cpu>=1.7.4',
        'sentence-transformers>=2.3.1',
        'transformers>=4.36.2',
    ],
    'graph': [
        'igraph>=0.11.3',
        'pyvis>=0.3.2',
        'plotly>=5.17.0',
    ]
}

setup(
    name="emc-knowledge-graph",
    version="1.0.0",
    description="EMC企业级知识图谱系统",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require=extras_require,
    
    entry_points={
        'console_scripts': [
            'emc-kg=emc_kg.cli:main',
        ],
    },
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)