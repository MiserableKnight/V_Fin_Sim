# -*- coding: utf-8 -*-
"""
统一配置加载器
Unified Configuration Loader

从 YAML 文件加载所有模型参数，提供统一的配置管理接口
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ModelConfig:
    """
    统一模型配置类
    Unified Model Configuration

    从 YAML 配置文件加载的所有参数
    """

    # ============================================
    # 财务参数
    # ============================================
    R_base: float = 64.94
    V_fuel_base: float = 24.70
    V_other_base: float = 22.70
    FC: float = 19.06
    fleet_size: int = 121

    # ============================================
    # 需求模型参数
    # ============================================
    demand_elasticity: float = -0.8
    demand_floor: float = 0.3

    # ============================================
    # 决策约束参数
    # ============================================
    fare_adjust_min: float = -0.20
    fare_adjust_max: float = 0.30
    hedge_ratio_min: float = 0.0
    hedge_ratio_max: float = 0.60
    cut_ratio_min: float = 0.05
    cut_ratio_max: float = 0.90
    cut_ratio_critical: float = 0.90
    network_preserve: float = 0.25

    # ============================================
    # Phase 1 阈值参数
    # ============================================
    stage_monitor_threshold: float = 0.60
    stage_fare_threshold: float = 0.85
    stage_hedge_threshold: float = 1.00
    solver_tolerance: float = 1.0e-6
    solver_max_iter: int = 100

    # ============================================
    # Phase 2 优化器参数
    # ============================================
    grid_resolution: int = 50
    default_optimization_method: str = "grid"

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "ModelConfig":
        """
        从 YAML 文件加载配置

        Args:
            config_path: YAML 配置文件路径

        Returns:
            ModelConfig 实例
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # 提取各部分参数
        financial = data.get("financial", {})
        demand = data.get("demand", {})
        constraints = data.get("constraints", {})
        threshold = data.get("threshold", {})
        optimizer = data.get("optimizer", {})

        # 合并 urgency_config 和 stage_names
        urgency_config = threshold.get("urgency_config", {})
        action_descriptions = threshold.get("action_descriptions", {})
        stage_names = threshold.get("stage_names", {})

        return cls(
            # 财务参数
            R_base=financial.get("R_base", 64.94),
            V_fuel_base=financial.get("V_fuel_base", 24.70),
            V_other_base=financial.get("V_other_base", 22.70),
            FC=financial.get("FC", 19.06),
            fleet_size=financial.get("fleet_size", 121),
            # 需求参数
            demand_elasticity=demand.get("elasticity", -0.8),
            demand_floor=demand.get("demand_floor", 0.3),
            # 约束参数
            fare_adjust_min=constraints.get("fare_adjust_min", -0.20),
            fare_adjust_max=constraints.get("fare_adjust_max", 0.30),
            hedge_ratio_min=constraints.get("hedge_ratio_min", 0.0),
            hedge_ratio_max=constraints.get("hedge_ratio_max", 0.60),
            cut_ratio_min=constraints.get("cut_ratio_min", 0.05),
            cut_ratio_max=constraints.get("cut_ratio_max", 0.90),
            cut_ratio_critical=constraints.get("cut_ratio_critical", 0.90),
            network_preserve=constraints.get("network_preserve", 0.25),
            # 阈值参数
            stage_monitor_threshold=threshold.get("stage_monitor_threshold", 0.60),
            stage_fare_threshold=threshold.get("stage_fare_threshold", 0.85),
            stage_hedge_threshold=threshold.get("stage_hedge_threshold", 1.00),
            solver_tolerance=threshold.get("solver_tolerance", 1.0e-6),
            solver_max_iter=threshold.get("solver_max_iter", 100),
            # 优化器参数
            grid_resolution=optimizer.get("grid_resolution", 50),
            default_optimization_method=optimizer.get("default_method", "grid")
        )

    def get_urgency_config(self) -> Dict[int, Dict[str, str]]:
        """从 YAML 加载紧急程度配置"""
        return self._load_yaml_section("threshold.urgency_config", {
            1: {"level": "低", "icon": "🟢", "color": "green"},
            2: {"level": "中", "icon": "🟡", "color": "yellow"},
            3: {"level": "高", "icon": "🟠", "color": "orange"},
            4: {"level": "紧急", "icon": "🔴", "color": "red"}
        })

    def get_action_descriptions(self) -> Dict[str, str]:
        """从 YAML 加载决策路径描述"""
        return self._load_yaml_section("threshold.action_descriptions", {
            "monitor": "边际贡献健康，保持商业监控",
            "fare_increase": "启动票价传导机制，逐步上调",
            "hedge_position": "同时动用票价与套保工具",
            "capacity_reduction": "商业/金融工具耗尽，触发运力压降"
        })

    def get_stage_names(self) -> Dict[int, str]:
        """从 YAML 加载阶段名称映射"""
        return self._load_yaml_section("threshold.stage_names", {
            1: "正常监控",
            2: "票价传导",
            3: "套保加仓",
            4: "削班启动"
        })

    def _load_yaml_section(self, key: str, default: Any) -> Any:
        """辅助方法：从 YAML 加载特定节"""
        config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            # 支持嵌套key如 "threshold.urgency_config"
            keys = key.split(".")
            result = data
            for k in keys:
                result = result.get(k, {})
            if not result or isinstance(result, dict) and not default:
                return default
            return result if result else default
        return default

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "财务参数": {
                "基础运营收入(万亿₫)": self.R_base,
                "燃油成本(万亿₫)": self.V_fuel_base,
                "其他变动成本(万亿₫)": self.V_other_base,
                "固定成本(万亿₫)": self.FC,
                "机队规模(架)": self.fleet_size
            },
            "需求参数": {
                "需求价格弹性": self.demand_elasticity,
                "需求因子下限": self.demand_floor
            },
            "决策约束": {
                "票价调整下限": f"{self.fare_adjust_min*100:.0f}%",
                "票价调整上限": f"{self.fare_adjust_max*100:.0f}%",
                "套保比例上限": f"{self.hedge_ratio_max*100:.0f}%",
                "网络保留权重": self.network_preserve
            }
        }


# 默认配置实例
DEFAULT_CONFIG = ModelConfig()


def load_config(config_path: Optional[str] = None) -> ModelConfig:
    """
    加载模型配置

    Args:
        config_path: YAML 配置文件路径，如果为 None 则使用默认配置

    Returns:
        ModelConfig 实例
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "model_config.yaml"

        if config_path.exists():
            return ModelConfig.from_yaml(config_path)

    return DEFAULT_CONFIG
