"""
集成服务模块

这个模块包含与外部AI框架和服务的集成适配器
"""

from .kag_adapter import EMCKAGAdapter, create_emc_kag_adapter

__all__ = ["EMCKAGAdapter", "create_emc_kag_adapter"]