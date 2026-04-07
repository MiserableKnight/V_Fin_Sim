# -*- coding: utf-8 -*-
"""
油价冲击决策阈值配置模块
Oil Shock Decision Threshold Configuration Module

将原本硬编码的决策系数提取为可配置参数，
便于后续基于历史数据校准和情景调整。
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class ThresholdConfig:
    """决策阈值配置类 / Decision Threshold Configuration"""

    # 决策阶段触发系数（基于油价容忍上限的百分比）
    # Decision stage trigger coefficients (based on percentage of oil tolerance limit)
    STAGE_MONITOR_THRESHOLD: float = 0.60      # 监控阶段：油价 ≤ 容忍上限×60%
    STAGE_FARE_THRESHOLD: float = 0.85         # 票价阶段：油价 ≤ 容忍上限×85%
    STAGE_HEDGE_THRESHOLD: float = 1.00        # 套保阶段：油价 ≤ 容忍上限×100%

    # 动作约束 / Action constraints
    FARE_ADJUST_MIN: float = -0.20             # 票价最小调整幅度（允许降价20%）
    FARE_ADJUST_MAX: float = 0.20              # 票价最大调整幅度
    HEDGE_RATIO_MIN: float = 0.0               # 最小套保比例
    HEDGE_RATIO_MAX: float = 0.8               # 最大套保比例

    # 求解器容差 / Solver tolerance
    SOLVER_TOLERANCE: float = 1e-6
    SOLVER_MAX_ITER: int = 100

    # 决策路径描述模板 / Decision path description templates
    ACTION_DESCRIPTIONS: Dict[str, str] = field(default_factory=lambda: {
        "monitor": "边际贡献健康，保持商业监控",
        "fare_increase": "启动票价传导机制，逐步上调",
        "hedge_position": "同时动用票价与套保工具",
        "capacity_reduction": "商业/金融工具耗尽，触发运力压降"
    })

    # 紧急程度配置 / Urgency level configuration
    URGENCY_CONFIG: Dict[int, Dict[str, str]] = field(default_factory=lambda: {
        1: {"level": "低", "icon": "🟢", "color": "green"},
        2: {"level": "中", "icon": "🟡", "color": "yellow"},
        3: {"level": "高", "icon": "🟠", "color": "orange"},
        4: {"level": "紧急", "icon": "🔴", "color": "red"}
    })

    # 阶段名称映射 / Stage name mapping
    STAGE_NAMES: Dict[int, str] = field(default_factory=lambda: {
        1: "正常监控",
        2: "票价传导",
        3: "套保加仓",
        4: "削班启动"
    })

    def get_trigger_thresholds(self) -> Tuple[float, float, float]:
        """返回三阶段触发阈值 / Return three-stage trigger thresholds"""
        return (
            self.STAGE_MONITOR_THRESHOLD,
            self.STAGE_FARE_THRESHOLD,
            self.STAGE_HEDGE_THRESHOLD
        )

    def get_urgency_info(self, stage: int) -> Dict[str, str]:
        """获取指定阶段的紧急程度信息 / Get urgency info for specified stage"""
        return self.URGENCY_CONFIG.get(stage, self.URGENCY_CONFIG[1])

    def get_stage_name(self, stage: int) -> str:
        """获取阶段名称 / Get stage name"""
        return self.STAGE_NAMES.get(stage, "未知")


# 默认配置实例 / Default configuration instance
DEFAULT_THRESHOLD_CONFIG = ThresholdConfig()
