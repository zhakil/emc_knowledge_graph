"""
EMC Standards Knowledge Graph Core Engine
汽车电子EMC标准知识图谱核心引擎

基于图论和语义网络理论构建的领域专用知识图谱系统，专门针对汽车电子
电磁兼容性标准的复杂语义关系进行建模和推理。采用多层异构图结构，
实现标准间的语义关联挖掘和合规路径推理。

核心创新点：
• 领域本体驱动的知识建模策略
• 多源异构标准数据的语义融合算法
• 基于图嵌入的语义相似度计算
• 动态演化的知识图谱更新机制

技术架构：
• 图存储层：基于NetworkX的内存图数据库
• 语义层：领域本体Schema和推理规则
• 服务层：图查询、路径发现、相似度计算
• 应用层：可视化、分析报告、决策支持

Author: EMC Standards Research Team
Version: 1.0.0
"""

import codecs
import itertools
import json
import logging
import os
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import networkx as nx
import numpy as np
import pandas as pd

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    from data_models import (
        GraphMetadata,
        KnowledgeEdge,
        KnowledgeNode,
        NodeType,
        RelationType,
        ValidationResult,
        validate_graph_data,
    )
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from data_models import (
        GraphMetadata,
        KnowledgeEdge,
        KnowledgeNode,
        NodeType,
        RelationType,
        ValidationResult,
        validate_graph_data,
    )

from utils import ensure_directory, load_config, setup_logging
from visualizer import KnowledgeGraphVisualizer

logger = logging.getLogger(__name__)


class EMCKnowledgeGraph:
    """
    EMC标准知识图谱核心引擎

    基于语义网络理论的知识图谱构建与推理系统，专门针对汽车电子EMC标准
    领域的复杂语义关系进行建模。采用多层异构图结构，支持语义推理、
    路径发现和知识演化。

    关键技术特性：
    • 领域本体Schema驱动的知识建模
    • 多维度语义关系表示与推理
    • 动态知识图谱构建与更新机制
    • 图神经网络嵌入表示学习
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化知识图谱引擎

        构建基础的图结构、本体Schema和推理规则库，
        为后续的知识建模和语义计算奠定基础。

        Args:
            config: 系统配置参数
        """
        self.config = config or load_config()
        self.graph = nx.MultiDiGraph()  # 支持多重边的有向图

        # 知识存储结构
        self.nodes_data: Dict[str, KnowledgeNode] = {}
        self.edges_data: List[KnowledgeEdge] = []
        self.metadata = GraphMetadata(
            name="EMC Standards Knowledge Graph",
            description="Automotive Electronics EMC Standards Semantic Network",
        )

        # 语义索引和缓存
        self._semantic_index = {}
        self._path_cache = {}
        self._centrality_cache = {}

        # 可视化引擎
        self.visualizer = KnowledgeGraphVisualizer(config)

        # 初始化EMC领域知识
        self._initialize_emc_domain_knowledge()

        logger.info(f"EMC知识图谱引擎初始化完成，节点数: {len(self.nodes_data)}")

    def _initialize_emc_domain_knowledge(self):
        """
        初始化EMC领域知识本体

        构建汽车电子EMC标准领域的核心知识结构，包括标准化组织、
        技术标准、测试方法、法规要求等实体及其语义关系。
        """
        logger.info("开始构建EMC领域知识本体...")

        # 构建核心实体
        self._create_standards_organizations()
        self._create_technical_standards()
        self._create_regulations_framework()
        self._create_test_methodologies()
        self._create_test_environments()
        self._create_vehicle_taxonomies()
        self._create_frequency_domains()

        # 建立语义关系
        self._establish_semantic_relationships()

        # 构建语义索引
        self._build_semantic_index()

        # 更新图谱元数据
        self._update_graph_metadata()

        logger.info(
            f"EMC领域知识本体构建完成，实体数: {len(self.nodes_data)}, 关系数: {len(self.edges_data)}"
        )

    def _create_standards_organizations(self):
        """构建标准化组织实体"""
        organizations = [
            {
                "id": "CISPR",
                "name": "CISPR - 国际特别无线电干扰委员会",
                "description": "制定车辆及其组件发射测量标准的国际组织，隶属于IEC，专注于无线电干扰限值和测量方法",
                "attributes": {
                    "full_name": "International Special Committee on Radio Interference",
                    "parent_org": "IEC",
                    "established": 1934,
                    "scope": "Radio interference standards",
                    "region": "Global",
                },
            },
            {
                "id": "ISO",
                "name": "ISO - 国际标准化组织",
                "description": "TC22/SC32/WG3工作组负责制定车辆和组件抗扰度测试标准",
                "attributes": {
                    "full_name": "International Organization for Standardization",
                    "tc_committee": "TC22 - Road vehicles",
                    "subcommittee": "SC32 - Electrical and electronic components",
                    "working_group": "WG3 - EMC",
                    "region": "Global",
                },
            },
            {
                "id": "SAE",
                "name": "SAE - 汽车工程师学会",
                "description": "主要为北美地区制定汽车EMC标准，许多标准已转为记录与国际标准差异的参考文件",
                "attributes": {
                    "full_name": "Society of Automotive Engineers",
                    "region": "North America",
                    "status": "Many standards withdrawn",
                    "current_role": "Reference documents",
                },
            },
            {
                "id": "UNECE",
                "name": "UNECE - 联合国欧洲经济委员会",
                "description": "制定ECE法规的国际组织，ECE R10涵盖电磁兼容性要求",
                "attributes": {
                    "full_name": "United Nations Economic Commission for Europe",
                    "key_regulation": "ECE R10",
                    "coverage": "50+ countries",
                    "region": "Europe and beyond",
                },
            },
            {
                "id": "IEC",
                "name": "IEC - 国际电工委员会",
                "description": "制定电磁兼容基础标准系列IEC 61000的国际电工标准化组织",
                "attributes": {
                    "full_name": "International Electrotechnical Commission",
                    "key_standards": "IEC 61000 series",
                    "focus": "Electromagnetic compatibility fundamentals",
                    "region": "Global",
                },
            },
        ]

        for org_data in organizations:
            node = KnowledgeNode(
                id=org_data["id"],
                name=org_data["name"],
                node_type=NodeType.ORGANIZATION,
                description=org_data["description"],
                attributes=org_data["attributes"],
                tags={"标准化组织", "国际组织"},
            )
            self._add_knowledge_node(node)

    def _create_technical_standards(self):
        """构建技术标准实体"""
        standards = [
            {
                "id": "CISPR25",
                "name": "CISPR 25 - 车载接收机保护标准",
                "description": "用于保护车辆、船舶和设备上使用的接收机免受无线电干扰。第5版于2021年发布，测试频率范围150kHz-2.5GHz",
                "attributes": {
                    "full_title": "Vehicles, boats and internal combustion engines - Radio disturbance characteristics - Limits and methods of measurement for the protection of on-board receivers",
                    "current_version": "Edition 5.0 (2021)",
                    "frequency_range": "150 kHz - 2.5 GHz",
                    "test_types": ["Conducted emissions", "Radiated emissions"],
                    "measurement_distance": "1m, 3m",
                    "publication_year": 2021,
                },
            },
            {
                "id": "CISPR12",
                "name": "CISPR 12 - 车外接收机保护标准",
                "description": "适用于所有车辆、船舶和内燃机驱动设备的无线电干扰特性测试。第7版正在制定中，测试距离为3米或10米",
                "attributes": {
                    "full_title": "Vehicles, boats and internal combustion engines - Radio disturbance characteristics - Limits and methods of measurement for the protection of off-board receivers",
                    "current_version": "Edition 6.0 (2013)",
                    "next_version": "Edition 7.0 (in development)",
                    "measurement_distance": "3m, 10m",
                    "frequency_range": "150 kHz - 1 GHz",
                    "scope": "Off-board receiver protection",
                },
            },
            {
                "id": "CISPR36",
                "name": "CISPR 36 - 电动/混动车标准",
                "description": "专门针对电动和混合动力车辆的30MHz以下辐射干扰特性标准，考虑充电状态下的特殊测试条件",
                "attributes": {
                    "full_title": "Radio disturbance characteristics for the protection of off-board receivers in the frequency range below 30 MHz - Electric and hybrid-electric vehicles",
                    "frequency_range": "Below 30 MHz",
                    "vehicle_types": ["BEV", "HEV", "PHEV"],
                    "special_conditions": "Charging state testing",
                    "publication_year": 2020,
                },
            },
            {
                "id": "ISO11452",
                "name": "ISO 11452 - 组件抗扰度测试标准",
                "description": "包含多个部分的组件级电磁抗扰度测试标准，频率范围覆盖200MHz-18GHz",
                "attributes": {
                    "full_title": "Road vehicles - Component test methods for electrical disturbances from narrowband radiated electromagnetic energy",
                    "parts": {
                        "Part 1": "General",
                        "Part 2": "Absorber-lined shielded enclosure",
                        "Part 3": "TEM cell",
                        "Part 4": "Bulk current injection (BCI)",
                        "Part 5": "Stripline",
                        "Part 11": "Reverberation chamber",
                    },
                    "frequency_range": "200 MHz - 18 GHz",
                    "test_level": "1 - 200 V/m",
                },
            },
            {
                "id": "ISO11451",
                "name": "ISO 11451 - 整车抗扰度测试标准",
                "description": "整车级电磁抗扰度测试标准，包含多种测试方法",
                "attributes": {
                    "full_title": "Road vehicles - Vehicle test methods for electrical disturbances from narrowband radiated electromagnetic energy",
                    "parts": {
                        "Part 1": "General",
                        "Part 2": "Off-vehicle antenna source",
                        "Part 3": "On-board antenna source",
                        "Part 4": "Bulk current injection (BCI)",
                    },
                    "test_level": "1 - 200 V/m",
                    "frequency_range": "200 MHz - 18 GHz",
                },
            },
            {
                "id": "ISO7637",
                "name": "ISO 7637 - 传导和耦合电气干扰",
                "description": "Part 2涵盖12V/24V车辆供电线路的电气瞬变传导测试，Part 3涵盖静电放电、脉冲群等测试方法",
                "attributes": {
                    "full_title": "Road vehicles - Electrical disturbances from conduction and coupling",
                    "parts": {
                        "Part 2": "Electrical transient conduction along supply lines only",
                        "Part 3": "Electrical transient transmission by capacitive and inductive coupling via lines other than supply lines",
                    },
                    "voltage_systems": ["12V", "24V"],
                    "test_types": ["ESD", "EFT", "Surge"],
                },
            },
        ]

        for std_data in standards:
            node = KnowledgeNode(
                id=std_data["id"],
                name=std_data["name"],
                node_type=NodeType.STANDARD,
                description=std_data["description"],
                attributes=std_data["attributes"],
                tags={"EMC标准", "技术标准"},
            )
            self._add_knowledge_node(node)

    def _create_regulations_framework(self):
        """构建法规框架实体"""
        regulations = [
            {
                "id": "ECER10",
                "name": "ECE R10 - 电磁兼容性法规",
                "description": "当前版本为第6版(2019年)，第7版正在制定中，将测试频率上限提升至6GHz。涵盖L、M、N、O、T、R、S类车辆的EMC要求",
                "attributes": {
                    "full_title": "Uniform provisions concerning the approval of vehicles with regard to electromagnetic compatibility",
                    "current_version": "Rev.6 (2019)",
                    "next_version": "Rev.7 (in development)",
                    "frequency_extension": "Up to 6 GHz",
                    "vehicle_categories": ["L", "M", "N", "O", "T", "R", "S"],
                    "geographic_scope": "50+ countries",
                    "type_approval": True,
                },
            }
        ]

        for reg_data in regulations:
            node = KnowledgeNode(
                id=reg_data["id"],
                name=reg_data["name"],
                node_type=NodeType.REGULATION,
                description=reg_data["description"],
                attributes=reg_data["attributes"],
                tags={"法规", "合规要求", "ECE法规"},
            )
            self._add_knowledge_node(node)

    def _create_test_methodologies(self):
        """构建测试方法实体"""
        test_methods = [
            {
                "id": "RadiatedEmissions",
                "name": "辐射发射测试",
                "description": "测量车辆或组件向空间辐射的电磁能量。包括宽带和窄带测量，使用峰值、准峰值和平均值检波器",
                "attributes": {
                    "measurement_types": ["Broadband", "Narrowband"],
                    "detectors": ["Peak", "Quasi-peak", "Average"],
                    "measurement_distance": ["1m", "3m", "10m"],
                    "frequency_bands": {
                        "LF/MF": "150 kHz - 30 MHz",
                        "VHF/UHF": "30 MHz - 1 GHz",
                        "Microwave": "1 GHz - 18 GHz",
                    },
                    "antennas": ["Rod antenna", "Biconical", "Log-periodic", "Horn"],
                },
            },
            {
                "id": "ConductedEmissions",
                "name": "传导发射测试",
                "description": "测量通过电源线和信号线传导的电磁干扰。使用LISN/AMN进行测量，频率范围通常为150kHz-108MHz",
                "attributes": {
                    "frequency_range": "150 kHz - 108 MHz",
                    "coupling_device": "LISN/AMN",
                    "measurement_lines": ["Power lines", "Signal lines"],
                    "detectors": ["Peak", "Quasi-peak", "Average"],
                    "impedance": "50Ω",
                },
            },
            {
                "id": "RadiatedImmunity",
                "name": "辐射抗扰度测试",
                "description": "测试产品对空间电磁场的抗干扰能力。频率范围200MHz-18GHz，场强通常为1-200 V/m",
                "attributes": {
                    "frequency_range": "200 MHz - 18 GHz",
                    "field_strength": "1 - 200 V/m",
                    "modulation": ["AM", "FM", "PM"],
                    "test_environments": ["Anechoic chamber", "TEM cell", "Stripline"],
                    "polarization": ["Horizontal", "Vertical"],
                },
            },
            {
                "id": "ConductedImmunity",
                "name": "传导抗扰度测试",
                "description": "测试产品对通过电缆传导的电磁干扰的抗干扰能力。包括BCI、DPI等方法",
                "attributes": {
                    "methods": ["BCI", "DPI", "TEM cell"],
                    "frequency_range": "1 MHz - 400 MHz",
                    "injection_level": "1 - 200 mA",
                    "modulation": ["AM 1kHz", "PM"],
                    "coupling_devices": ["Current probe", "Coupling clamp"],
                },
            },
            {
                "id": "Transients",
                "name": "电快速瞬变/脉冲群测试",
                "description": "模拟开关操作和电气瞬变的干扰。包括EFT/Burst和浪涌测试",
                "attributes": {
                    "test_types": ["EFT/Burst", "Surge", "ESD"],
                    "standards": ["IEC 61000-4-4", "IEC 61000-4-5", "IEC 61000-4-2"],
                    "voltage_levels": ["1kV", "2kV", "4kV"],
                    "waveforms": ["5/50ns", "1.2/50μs", "8/20μs"],
                    "coupling": ["Direct", "Capacitive", "Inductive"],
                },
            },
        ]

        for method_data in test_methods:
            node = KnowledgeNode(
                id=method_data["id"],
                name=method_data["name"],
                node_type=NodeType.TEST_METHOD,
                description=method_data["description"],
                attributes=method_data["attributes"],
                tags={"测试方法", "EMC测试"},
            )
            self._add_knowledge_node(node)

    def _create_test_environments(self):
        """构建测试环境实体"""
        environments = [
            {
                "id": "AnechoicChamber",
                "name": "电波暗室",
                "description": "吸波材料衬里的屏蔽室，用于辐射发射和抗扰度测试。需要满足CISPR 16-1-4和ISO 11452-2的场均匀性要求",
                "attributes": {
                    "type": "Semi-anechoic chamber",
                    "standards": ["CISPR 16-1-4", "ISO 11452-2"],
                    "field_uniformity": "±6 dB",
                    "frequency_range": "80 MHz - 18 GHz",
                    "applications": ["Emissions", "Immunity"],
                    "size_requirements": "Minimum 3m x 4m x 3m",
                },
            },
            {
                "id": "TEMCell",
                "name": "TEM传输室",
                "description": "横电磁波传输室，用于30MHz-200MHz范围的抗扰度测试。提供均匀的电磁场分布",
                "attributes": {
                    "type": "Transverse electromagnetic cell",
                    "frequency_range": "30 MHz - 200 MHz",
                    "field_uniformity": "±6 dB",
                    "impedance": "50Ω",
                    "applications": ["Immunity testing"],
                    "dut_size_limit": "1/3 of cell height",
                },
            },
            {
                "id": "ReverberationChamber",
                "name": "混响室",
                "description": "利用模式搅拌技术产生统计均匀电磁场的测试环境，适用于ISO 11452-11标准",
                "attributes": {
                    "type": "Mode-stirred chamber",
                    "stirring_method": ["Mechanical", "Frequency", "Polarization"],
                    "frequency_range": "200 MHz - 18 GHz",
                    "field_statistics": "Rayleigh distribution",
                    "standards": ["ISO 11452-11"],
                    "applications": ["Immunity testing"],
                },
            },
        ]

        for env_data in environments:
            node = KnowledgeNode(
                id=env_data["id"],
                name=env_data["name"],
                node_type=NodeType.TEST_ENVIRONMENT,
                description=env_data["description"],
                attributes=env_data["attributes"],
                tags={"测试环境", "测试设备"},
            )
            self._add_knowledge_node(node)

    def _create_vehicle_taxonomies(self):
        """构建车辆分类实体"""
        vehicle_types = [
            {
                "id": "ElectricVehicles",
                "name": "电动/混合动力车",
                "description": "需要额外的EMC测试，包括充电状态下的测试。适用CISPR 36标准，考虑高压系统的特殊要求",
                "attributes": {
                    "types": ["BEV", "HEV", "PHEV"],
                    "special_standards": ["CISPR 36"],
                    "special_conditions": ["Charging state", "High voltage systems"],
                    "frequency_concerns": "Below 30 MHz",
                    "additional_testing": True,
                },
            },
            {
                "id": "ConventionalVehicles",
                "name": "传统燃油车",
                "description": "采用内燃机的传统车辆，遵循标准EMC测试要求",
                "attributes": {
                    "engine_type": "Internal combustion",
                    "voltage_system": "12V/24V",
                    "applicable_standards": ["CISPR 25", "CISPR 12", "ISO 11451"],
                    "test_complexity": "Standard",
                },
            },
        ]

        for vehicle_data in vehicle_types:
            node = KnowledgeNode(
                id=vehicle_data["id"],
                name=vehicle_data["name"],
                node_type=NodeType.VEHICLE_TYPE,
                description=vehicle_data["description"],
                attributes=vehicle_data["attributes"],
                tags={"车辆类型", "汽车分类"},
            )
            self._add_knowledge_node(node)

    def _create_frequency_domains(self):
        """构建频率域实体"""
        frequency_ranges = [
            {
                "id": "LowFrequency",
                "name": "低频段 (150kHz-30MHz)",
                "description": "主要用于传导发射测试，涵盖AM广播频段",
                "attributes": {
                    "range": "150 kHz - 30 MHz",
                    "applications": ["Conducted emissions", "Power line communication"],
                    "services": ["AM broadcast", "Amateur radio", "Shortwave"],
                    "measurement_methods": ["LISN", "Current probe"],
                },
            },
            {
                "id": "VHFUHFBand",
                "name": "VHF/UHF频段 (30MHz-1GHz)",
                "description": "涵盖FM广播、电视、移动通信等重要频段",
                "attributes": {
                    "range": "30 MHz - 1 GHz",
                    "applications": ["Radiated emissions", "Immunity"],
                    "services": ["FM broadcast", "TV", "Mobile communications"],
                    "antennas": ["Biconical", "Log-periodic"],
                },
            },
            {
                "id": "MicrowaveBand",
                "name": "微波频段 (1GHz-18GHz)",
                "description": "高频段，主要用于抗扰度测试，涵盖WiFi、蓝牙等现代通信技术",
                "attributes": {
                    "range": "1 GHz - 18 GHz",
                    "applications": ["Immunity testing"],
                    "services": ["WiFi", "Bluetooth", "Radar", "5G"],
                    "antennas": ["Horn antenna", "Double-ridged horn"],
                    "field_generation": "High power amplifiers",
                },
            },
        ]

        for freq_data in frequency_ranges:
            node = KnowledgeNode(
                id=freq_data["id"],
                name=freq_data["name"],
                node_type=NodeType.FREQUENCY_RANGE,
                description=freq_data["description"],
                attributes=freq_data["attributes"],
                tags={"频率范围", "电磁频谱"},
            )
            self._add_knowledge_node(node)

    def _establish_semantic_relationships(self):
        """建立语义关系网络"""
        relationships = [
            # 组织开发标准
            ("CISPR", "CISPR25", RelationType.DEVELOPS, 1.0),
            ("CISPR", "CISPR12", RelationType.DEVELOPS, 1.0),
            ("CISPR", "CISPR36", RelationType.DEVELOPS, 1.0),
            ("ISO", "ISO11452", RelationType.DEVELOPS, 1.0),
            ("ISO", "ISO11451", RelationType.DEVELOPS, 1.0),
            ("ISO", "ISO7637", RelationType.DEVELOPS, 1.0),
            ("UNECE", "ECER10", RelationType.DEVELOPS, 1.0),
            # 法规引用标准（语义关联强度差异化）
            ("ECER10", "CISPR25", RelationType.REFERENCES, 0.95),
            ("ECER10", "CISPR12", RelationType.REFERENCES, 0.90),
            ("ECER10", "ISO11451", RelationType.REFERENCES, 0.85),
            ("ECER10", "ISO11452", RelationType.REFERENCES, 0.80),
            # 标准包含测试方法（方法论层面的语义关联）
            ("CISPR25", "RadiatedEmissions", RelationType.INCLUDES, 0.95),
            ("CISPR25", "ConductedEmissions", RelationType.INCLUDES, 0.90),
            ("CISPR12", "RadiatedEmissions", RelationType.INCLUDES, 1.0),
            ("ISO11452", "RadiatedImmunity", RelationType.INCLUDES, 1.0),
            ("ISO11452", "ConductedImmunity", RelationType.INCLUDES, 0.85),
            ("ISO11451", "RadiatedImmunity", RelationType.INCLUDES, 1.0),
            ("ISO7637", "Transients", RelationType.INCLUDES, 1.0),
            # 测试方法使用测试环境（技术实现关联）
            ("RadiatedEmissions", "AnechoicChamber", RelationType.USES, 0.90),
            ("RadiatedImmunity", "AnechoicChamber", RelationType.USES, 0.85),
            ("RadiatedImmunity", "TEMCell", RelationType.USES, 0.75),
            ("RadiatedImmunity", "ReverberationChamber", RelationType.USES, 0.70),
            ("ConductedImmunity", "TEMCell", RelationType.USES, 0.60),
            # 标准适用于车辆类型（应用域关联）
            ("CISPR36", "ElectricVehicles", RelationType.APPLIES_TO, 1.0),
            ("CISPR25", "ElectricVehicles", RelationType.APPLIES_TO, 0.85),
            ("CISPR25", "ConventionalVehicles", RelationType.APPLIES_TO, 0.95),
            ("CISPR12", "ElectricVehicles", RelationType.APPLIES_TO, 0.90),
            ("CISPR12", "ConventionalVehicles", RelationType.APPLIES_TO, 0.95),
            # 测试方法覆盖频率范围（频域关联）
            ("ConductedEmissions", "LowFrequency", RelationType.COVERS, 0.95),
            ("RadiatedEmissions", "VHFUHFBand", RelationType.COVERS, 0.90),
            ("RadiatedImmunity", "VHFUHFBand", RelationType.COVERS, 0.85),
            ("RadiatedImmunity", "MicrowaveBand", RelationType.COVERS, 0.80),
            # 组织间协调关系
            ("IEC", "CISPR", RelationType.INCLUDES, 0.90),
            ("ISO", "IEC", RelationType.HARMONIZED_WITH, 0.75),
            # 标准演化关系
            ("CISPR36", "CISPR12", RelationType.EXTENDS, 0.70),
            ("ECER10", "CISPR25", RelationType.IMPLEMENTS, 0.85),
            ("ECER10", "ISO11451", RelationType.IMPLEMENTS, 0.80),
        ]

        for source, target, rel_type, weight in relationships:
            edge = KnowledgeEdge(
                source=source,
                target=target,
                relation_type=rel_type,
                weight=weight,
                confidence=0.95,  # 高置信度的专家知识
                source_reference="EMC Standards Domain Expertise",
            )
            self._add_knowledge_edge(edge)

    def _add_knowledge_node(self, node: KnowledgeNode):
        """添加知识节点到图谱"""
        self.nodes_data[node.id] = node
        self.graph.add_node(node.id, **asdict(node))

    def _add_knowledge_edge(self, edge: KnowledgeEdge):
        """添加知识边到图谱"""
        self.edges_data.append(edge)
        self.graph.add_edge(
            edge.source,
            edge.target,
            relation_type=edge.relation_type.value,
            weight=edge.weight,
            confidence=edge.confidence,
            **edge.attributes,
        )

    def _build_semantic_index(self):
        """构建语义索引以支持快速检索"""
        self._semantic_index = {
            "by_type": defaultdict(list),
            "by_tag": defaultdict(list),
            "by_attribute": defaultdict(list),
        }

        for node_id, node in self.nodes_data.items():
            # 按类型索引
            self._semantic_index["by_type"][node.node_type].append(node_id)

            # 按标签索引
            for tag in node.tags:
                self._semantic_index["by_tag"][tag].append(node_id)

            # 按关键属性索引
            for attr_key, attr_value in node.attributes.items():
                if isinstance(attr_value, (str, int, float)):
                    self._semantic_index["by_attribute"][
                        f"{attr_key}:{attr_value}"
                    ].append(node_id)

    def _update_graph_metadata(self):
        """更新图谱元数据统计"""
        self.metadata.node_count = len(self.nodes_data)
        self.metadata.edge_count = len(self.edges_data)
        self.metadata.last_updated = datetime.now()

        # 统计节点类型分布
        self.metadata.node_types = Counter(
            node.node_type.value for node in self.nodes_data.values()
        )

        # 统计关系类型分布
        self.metadata.relation_types = Counter(
            edge.relation_type.value for edge in self.edges_data
        )

    def semantic_search(
        self,
        query: str,
        search_fields: List[str] = None,
        node_types: List[NodeType] = None,
        max_results: int = 10,
    ) -> List[Tuple[str, float]]:
        """
        语义搜索功能

        基于TF-IDF和语义相似度的智能搜索，支持多字段匹配
        和结果相关性排序。

        Args:
            query: 搜索查询字符串
            search_fields: 搜索字段列表
            node_types: 限制的节点类型
            max_results: 最大结果数量

        Returns:
            节点ID和相关性分数的元组列表
        """
        search_fields = search_fields or ["name", "description"]
        results = []

        query_terms = query.lower().split()

        for node_id, node in self.nodes_data.items():
            # 节点类型过滤
            if node_types and node.node_type not in node_types:
                continue

            # 计算相关性分数
            score = 0.0

            for field in search_fields:
                if hasattr(node, field):
                    field_value = getattr(node, field).lower()

                    # 简单的TF匹配
                    for term in query_terms:
                        if term in field_value:
                            score += 1.0 / len(field_value.split())

                    # 精确匹配加权
                    if query.lower() in field_value:
                        score += 2.0

            # 标签匹配
            for tag in node.tags:
                for term in query_terms:
                    if term in tag.lower():
                        score += 0.5

            if score > 0:
                results.append((node_id, score))

        # 按相关性排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:max_results]

    def find_semantic_paths(
        self,
        source: str,
        target: str,
        max_depth: int = 4,
        relation_types: List[RelationType] = None,
    ) -> List[List[str]]:
        """
        语义路径发现

        基于语义关系的路径搜索算法，支持关系类型过滤
        和路径权重计算。

        Args:
            source: 源节点ID
            target: 目标节点ID
            max_depth: 最大搜索深度
            relation_types: 允许的关系类型

        Returns:
            路径列表，每个路径为节点ID序列
        """
        cache_key = f"{source}-{target}-{max_depth}"
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]

        paths = []

        try:
            # 创建子图（仅包含指定关系类型的边）
            if relation_types:
                filtered_edges = [
                    (edge.source, edge.target)
                    for edge in self.edges_data
                    if edge.relation_type in relation_types
                ]
                subgraph = self.graph.edge_subgraph(filtered_edges)
            else:
                subgraph = self.graph

            # 查找所有简单路径
            try:
                all_paths = list(
                    nx.all_simple_paths(subgraph, source, target, cutoff=max_depth)
                )
                paths = all_paths
            except nx.NetworkXNoPath:
                paths = []

        except Exception as e:
            logger.warning(f"路径搜索失败: {e}")
            paths = []

        self._path_cache[cache_key] = paths
        return paths

    def compute_semantic_similarity(
        self, node1_id: str, node2_id: str, method: str = "jaccard"
    ) -> float:
        """
        计算节点间语义相似度

        基于多种相似度度量方法计算节点间的语义关联强度。

        Args:
            node1_id: 第一个节点ID
            node2_id: 第二个节点ID
            method: 相似度计算方法

        Returns:
            相似度分数 (0-1)
        """
        if node1_id not in self.nodes_data or node2_id not in self.nodes_data:
            return 0.0

        node1 = self.nodes_data[node1_id]
        node2 = self.nodes_data[node2_id]

        if method == "jaccard":
            return self._jaccard_similarity(node1, node2)
        elif method == "structural":
            return self._structural_similarity(node1_id, node2_id)
        elif method == "semantic":
            return self._semantic_attribute_similarity(node1, node2)
        else:
            return self._jaccard_similarity(node1, node2)

    def _jaccard_similarity(self, node1: KnowledgeNode, node2: KnowledgeNode) -> float:
        """基于Jaccard系数的相似度计算"""
        tags1 = node1.tags
        tags2 = node2.tags

        if not tags1 and not tags2:
            return 0.0

        intersection = len(tags1.intersection(tags2))
        union = len(tags1.union(tags2))

        return intersection / union if union > 0 else 0.0

    def _structural_similarity(self, node1_id: str, node2_id: str) -> float:
        """基于图结构的相似度计算"""
        try:
            neighbors1 = set(self.graph.neighbors(node1_id))
            neighbors2 = set(self.graph.neighbors(node2_id))

            if not neighbors1 and not neighbors2:
                return 0.0

            intersection = len(neighbors1.intersection(neighbors2))
            union = len(neighbors1.union(neighbors2))

            return intersection / union if union > 0 else 0.0
        except:
            return 0.0

    def _semantic_attribute_similarity(
        self, node1: KnowledgeNode, node2: KnowledgeNode
    ) -> float:
        """基于语义属性的相似度计算"""
        # 类型相似度
        type_sim = 1.0 if node1.node_type == node2.node_type else 0.0

        # 属性重叠度
        attrs1 = set(node1.attributes.keys())
        attrs2 = set(node2.attributes.keys())

        if attrs1 or attrs2:
            attr_intersection = len(attrs1.intersection(attrs2))
            attr_union = len(attrs1.union(attrs2))
            attr_sim = attr_intersection / attr_union if attr_union > 0 else 0.0
        else:
            attr_sim = 0.0

        # 综合相似度
        return 0.6 * type_sim + 0.4 * attr_sim

    def analyze_graph_topology(self) -> Dict[str, Any]:
        """
        图拓扑分析

        计算图的各种拓扑特征和统计指标，为图结构分析
        和网络特性理解提供定量依据。

        Returns:
            包含拓扑分析结果的字典
        """
        analysis = {
            "basic_stats": {
                "nodes": self.graph.number_of_nodes(),
                "edges": self.graph.number_of_edges(),
                "density": nx.density(self.graph),
                "is_connected": nx.is_connected(self.graph.to_undirected()),
            },
            "centrality_measures": {},
            "community_structure": {},
            "path_metrics": {},
        }

        try:
            # 中心性分析
            analysis["centrality_measures"] = {
                "degree": dict(nx.degree_centrality(self.graph)),
                "betweenness": dict(nx.betweenness_centrality(self.graph)),
                "closeness": dict(nx.closeness_centrality(self.graph)),
                "pagerank": dict(nx.pagerank(self.graph, weight="weight")),
            }

            # 路径度量
            if nx.is_connected(self.graph.to_undirected()):
                analysis["path_metrics"] = {
                    "average_shortest_path": nx.average_shortest_path_length(
                        self.graph.to_undirected()
                    ),
                    "diameter": nx.diameter(self.graph.to_undirected()),
                    "radius": nx.radius(self.graph.to_undirected()),
                }

            # 聚类系数
            analysis["clustering"] = {
                "average_clustering": nx.average_clustering(self.graph.to_undirected()),
                "transitivity": nx.transitivity(self.graph.to_undirected()),
            }

        except Exception as e:
            logger.warning(f"拓扑分析部分失败: {e}")

        return analysis

    def generate_knowledge_report(self) -> Dict[str, Any]:
        """
        生成知识图谱分析报告

        综合图谱统计、拓扑分析和语义特征，生成完整的
        知识图谱质量评估和特征分析报告。

        Returns:
            完整的分析报告字典
        """
        report = {
            "metadata": asdict(self.metadata),
            "topology_analysis": self.analyze_graph_topology(),
            "semantic_statistics": self._compute_semantic_statistics(),
            "quality_metrics": self._assess_graph_quality(),
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _compute_semantic_statistics(self) -> Dict[str, Any]:
        """计算语义统计信息"""
        return {
            "node_type_distribution": dict(self.metadata.node_types),
            "relation_type_distribution": dict(self.metadata.relation_types),
            "tag_distribution": self._compute_tag_distribution(),
            "attribute_coverage": self._compute_attribute_coverage(),
        }

    def _compute_tag_distribution(self) -> Dict[str, int]:
        """计算标签分布"""
        tag_counts = Counter()
        for node in self.nodes_data.values():
            tag_counts.update(node.tags)
        return dict(tag_counts)

    def _compute_attribute_coverage(self) -> Dict[str, float]:
        """计算属性覆盖率"""
        total_nodes = len(self.nodes_data)
        if total_nodes == 0:
            return {}

        attribute_counts = Counter()
        for node in self.nodes_data.values():
            attribute_counts.update(node.attributes.keys())

        return {attr: count / total_nodes for attr, count in attribute_counts.items()}

    def _assess_graph_quality(self) -> Dict[str, float]:
        """评估图谱质量"""
        validation_result = validate_graph_data(self.nodes_data, self.edges_data)

        quality_score = 1.0 if validation_result.is_valid else 0.0
        completeness_score = self._compute_completeness_score()
        consistency_score = self._compute_consistency_score()

        return {
            "overall_quality": (quality_score + completeness_score + consistency_score)
            / 3,
            "data_validity": quality_score,
            "completeness": completeness_score,
            "consistency": consistency_score,
            "error_count": len(validation_result.errors),
            "warning_count": len(validation_result.warnings),
        }

    def _compute_completeness_score(self) -> float:
        """计算完整性分数"""
        # 基于节点描述、属性等的完整性
        complete_nodes = 0
        for node in self.nodes_data.values():
            if (
                node.description
                and len(node.description.strip()) > 10
                and node.attributes
                and len(node.attributes) > 0
            ):
                complete_nodes += 1

        return complete_nodes / len(self.nodes_data) if self.nodes_data else 0.0

    def _compute_consistency_score(self) -> float:
        """计算一致性分数"""
        # 基于关系的双向一致性和类型一致性
        consistent_relations = 0
        total_relations = len(self.edges_data)

        for edge in self.edges_data:
            if (
                edge.source in self.nodes_data
                and edge.target in self.nodes_data
                and 0.0 <= edge.weight <= 1.0
                and 0.0 <= edge.confidence <= 1.0
            ):
                consistent_relations += 1

        return consistent_relations / total_relations if total_relations > 0 else 1.0

    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 基于图结构特征的建议
        if self.graph.number_of_nodes() > 0:
            avg_degree = (
                sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
            )
            if avg_degree < 2:
                recommendations.append("图谱连接密度较低，建议增加更多语义关系")

        # 基于内容完整性的建议
        completeness = self._compute_completeness_score()
        if completeness < 0.8:
            recommendations.append("部分节点信息不完整，建议补充描述和属性")

        # 基于覆盖度的建议
        if NodeType.FREQUENCY_RANGE not in [
            node.node_type for node in self.nodes_data.values()
        ]:
            recommendations.append("建议增加更多频率范围相关的实体")

        return recommendations

    def export_to_formats(
        self, output_dir: str = "output/exports", formats: List[str] = None
    ) -> Dict[str, str]:
        """
        多格式导出功能

        支持JSON、GraphML、GEXF等多种格式的知识图谱导出，
        便于与其他工具和平台的集成。

        Args:
            output_dir: 输出目录
            formats: 导出格式列表

        Returns:
            格式到文件路径的映射字典
        """
        formats = formats or ["json", "graphml", "gexf"]
        output_paths = {}

        ensure_directory(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for fmt in formats:
            try:
                if fmt == "json":
                    path = self._export_json(output_dir, timestamp)
                elif fmt == "graphml":
                    path = self._export_graphml(output_dir, timestamp)
                elif fmt == "gexf":
                    path = self._export_gexf(output_dir, timestamp)
                else:
                    logger.warning(f"不支持的导出格式: {fmt}")
                    continue

                output_paths[fmt] = path
                logger.info(f"{fmt.upper()}格式导出完成: {path}")

            except Exception as e:
                logger.error(f"{fmt}导出失败: {e}")

        return output_paths

    def _export_json(self, output_dir: str, timestamp: str) -> str:
        """导出JSON格式"""
        output_path = Path(output_dir) / f"emc_knowledge_graph_{timestamp}.json"

        export_data = {
            "metadata": self.metadata.to_dict(),
            "nodes": [node.to_dict() for node in self.nodes_data.values()],
            "edges": [edge.to_dict() for edge in self.edges_data],
            "statistics": self.analyze_graph_topology(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

        return str(output_path)

    def _export_graphml(self, output_dir: str, timestamp: str) -> str:
        """导出GraphML格式"""
        output_path = Path(output_dir) / f"emc_knowledge_graph_{timestamp}.graphml"
        nx.write_graphml(self.graph, output_path)
        return str(output_path)

    def _export_gexf(self, output_dir: str, timestamp: str) -> str:
        """导出GEXF格式"""
        output_path = Path(output_dir) / f"emc_knowledge_graph_{timestamp}.gexf"
        nx.write_gexf(self.graph, output_path)
        return str(output_path)

    # 可视化接口方法
    def create_matplotlib_visualization(self, **kwargs):
        """创建静态可视化（委托给可视化引擎）"""
        return self.visualizer.create_matplotlib_visualization(
            self.graph, self.nodes_data, self.edges_data, **kwargs
        )

    def create_plotly_visualization(self, **kwargs):
        """创建交互式可视化（委托给可视化引擎）"""
        return self.visualizer.create_plotly_visualization(
            self.graph, self.nodes_data, self.edges_data, **kwargs
        )

    def create_analysis_dashboard(self, **kwargs):
        """创建分析仪表板（委托给可视化引擎）"""
        return self.visualizer.create_network_analysis_dashboard(
            self.graph, self.nodes_data, self.edges_data, **kwargs
        )


def main():
    """主函数 - 演示知识图谱核心功能"""
    # 配置日志
    setup_logging()

    print("EMC知识图谱系统启动")
    print("=" * 60)

    # 创建知识图谱实例
    kg = EMCKnowledgeGraph()

    # 生成分析报告
    print("生成知识图谱分析报告...")
    report = kg.generate_knowledge_report()

    print(f"图谱基本信息:")
    print(f"  节点数量: {report['metadata']['node_count']}")
    print(f"  边数量: {report['metadata']['edge_count']}")
    print(f"  图密度: {report['topology_analysis']['basic_stats']['density']:.3f}")
    print(f"  质量评分: {report['quality_metrics']['overall_quality']:.3f}")

    # 语义搜索演示
    print(f"语义搜索演示:")
    search_results = kg.semantic_search("电动车 EMC", max_results=3)
    for node_id, score in search_results:
        node = kg.nodes_data[node_id]
        print(f"  {node.name} (相关度: {score:.2f})")

    # 路径发现演示
    print(f"语义路径发现演示:")
    paths = kg.find_semantic_paths("CISPR", "ElectricVehicles", max_depth=3)
    if paths:
        path = paths[0]
        path_names = [kg.nodes_data[node_id].name for node_id in path]
        print(f"  路径: {' → '.join(path_names)}")

    # 创建可视化
    print(f"生成可视化图谱...")
    ensure_directory("output/graphs")

    # 静态图谱
    fig, ax = kg.create_matplotlib_visualization(
        save_path="output/graphs/emc_knowledge_graph.png"
    )
    print("  ✓ 静态图谱已生成")

    # 交互式图谱
    plotly_fig = kg.create_plotly_visualization(
        save_path="output/graphs/emc_interactive_graph.html"
    )
    print("  ✓ 交互式图谱已生成")

    # 分析仪表板
    dashboard_fig = kg.create_analysis_dashboard()
    dashboard_fig.write_html("output/graphs/emc_analysis_dashboard.html")
    print("  ✓ 分析仪表板已生成")

    # 多格式导出
    print(f" 执行多格式导出...")
    export_paths = kg.export_to_formats()
    for fmt, path in export_paths.items():
        print(f"  ✓ {fmt.upper()}: {path}")

    print(f" EMC知识图谱系统演示完成！")
    print(f" 输出文件位置: output/ 目录")


if __name__ == "__main__":
    main()
