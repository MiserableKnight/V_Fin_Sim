"""
Phase 1: 阈值计算与决策路径
Phase 1: Threshold Calculation and Decision Path

计算关键决策阈值与响应路径
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import numpy as np
from scipy.optimize import fsolve

from .demand_model import DemandModel
from .threshold_config import ThresholdConfig


@dataclass
class ThresholdResult:
    """阈值计算结果数据类"""
    fare_breakeven: float          # 票价盈亏平衡点
    oil_tolerance: float           # 最大可承受油价涨幅
    hedge_trigger: float           # 触发削班的临界套保比例
    current_stage: int             # 当前决策阶段（1-4）
    decision_path: List[Dict]      # 决策路径
    warnings: List[str]            # 预警信息

    def to_dict(self) -> dict:
        return {
            "fare_breakeven_pct": f"+{self.fare_breakeven*100:.1f}%",
            "oil_tolerance_pct": f"+{self.oil_tolerance*100:.1f}%",
            "hedge_trigger_pct": f"{self.hedge_trigger*100:.1f}%",
            "current_stage": self.current_stage,
            "decision_path": self.decision_path,
            "warnings": self.warnings
        }


class ThresholdCalculator:
    """
    阈值计算器
    计算关键决策阈值与响应路径
    """

    def __init__(self, config, threshold_config: ThresholdConfig):
        """
        Args:
            config: ModelConfig 实例
            threshold_config: 阈值配置
        """
        self.config = config
        self.threshold_config = threshold_config

    def calculate(
        self,
        oil_increase: float,
        fare_cap: Optional[float] = None,
        hedge_cap: Optional[float] = None
    ) -> ThresholdResult:
        """
        计算所有阈值

        Args:
            oil_increase: 油价涨幅
            fare_cap: 票价调整上限
            hedge_cap: 套保比例上限

        Returns:
            ThresholdResult: 阈值计算结果
        """
        if oil_increase < 0:
            raise ValueError(f"油价涨幅不能为负: {oil_increase}")

        fare_cap = fare_cap or self.threshold_config.FARE_ADJUST_MAX
        hedge_cap = hedge_cap or self.threshold_config.HEDGE_RATIO_MAX

        V_f = self.config.V_fuel_base
        V_o = self.config.V_other_base
        R = self.config.R_base
        FC = self.config.FC
        eps = self.config.demand_elasticity

        warnings = []

        # 阈值1: 票价盈亏平衡点
        fare_breakeven = self._solve_fare_breakeven(oil_increase, R, V_o, V_f, eps)
        if fare_breakeven > fare_cap:
            warnings.append(
                f"⚠️ 票价盈亏平衡点(+{fare_breakeven*100:.1f}%) "
                f"超过上限(+{fare_cap*100:.1f}%)"
            )

        # 阈值2: 最大可承受油价涨幅
        oil_tolerance = self._calculate_oil_tolerance(R, V_o, V_f, fare_cap, hedge_cap, eps)
        if oil_increase > oil_tolerance:
            warnings.append(
                f"🚨 当前油价(+{oil_increase*100:.1f}%) "
                f"超过容忍上限(+{oil_tolerance*100:.1f}%)"
            )

        # 阈值3: 触发削班的临界套保比例
        hedge_trigger = self._solve_hedge_trigger(oil_increase, R, V_o, V_f, FC, fare_cap)
        if hedge_trigger > hedge_cap:
            warnings.append(
                f"🚨 避免削班需套保{hedge_trigger*100:.1f}%，"
                f"超过上限({hedge_cap*100:.1f}%)"
            )

        # 构建决策路径
        decision_path, current_stage = self._build_decision_path(
            oil_increase, oil_tolerance, fare_breakeven, hedge_trigger, fare_cap
        )

        return ThresholdResult(
            fare_breakeven=fare_breakeven,
            oil_tolerance=oil_tolerance,
            hedge_trigger=hedge_trigger,
            current_stage=current_stage,
            decision_path=decision_path,
            warnings=warnings
        )

    def _solve_fare_breakeven(
        self, oil_increase: float, R: float, V_o: float, V_f: float, eps: float
    ) -> float:
        """求解票价盈亏平衡点"""
        return DemandModel.solve_fare_breakeven(
            oil_increase, R, V_o, V_f, eps,
            min_fare=self.threshold_config.FARE_ADJUST_MIN,
            max_fare=self.threshold_config.FARE_ADJUST_MAX
        )

    def _calculate_oil_tolerance(
        self, R: float, V_o: float, V_f: float, fare_cap: float, hedge_cap: float, eps: float
    ) -> float:
        """计算最大可承受油价涨幅"""
        price_ratio = 1.0 + fare_cap
        demand_factor = price_ratio ** eps
        adjusted_revenue = R * price_ratio * demand_factor
        scaled_V_o = V_o * demand_factor

        denominator = V_f * (1 - hedge_cap)
        if abs(denominator) < self.threshold_config.SOLVER_TOLERANCE:
            return np.inf

        oil_tolerance = (adjusted_revenue - scaled_V_o - V_f) / denominator
        return max(oil_tolerance, 0.0)

    def _solve_hedge_trigger(
        self, oil_increase: float, R: float, V_o: float, V_f: float, FC: float, fare_cap: float
    ) -> float:
        """求解触发削班的临界套保比例"""
        if oil_increase <= 0:
            return 0.0

        price_ratio = 1.0 + fare_cap
        eps = self.config.demand_elasticity
        demand_factor = price_ratio ** eps
        adjusted_revenue = R * price_ratio * demand_factor
        scaled_V_o = V_o * demand_factor

        def hedge_trigger_equation(h: float) -> float:
            fuel_cost = V_f * (1 + oil_increase * (1 - h))
            return adjusted_revenue - scaled_V_o - fuel_cost - FC

        try:
            hedge_trigger = fsolve(hedge_trigger_equation, x0=0.3)[0]
        except RuntimeError:
            hedge_trigger = 0.5

        return float(np.clip(hedge_trigger, 0.0, 1.0))

    def _build_decision_path(
        self,
        oil_increase: float,
        oil_tolerance: float,
        fare_breakeven: float,
        hedge_trigger: float,
        fare_cap: float
    ) -> Tuple[List[Dict], int]:
        """构建决策响应路径"""
        monitor_thresh, fare_thresh, hedge_thresh = self.threshold_config.get_trigger_thresholds()

        path = []
        current_stage = 1

        # 阶段1: 监控
        if oil_increase <= oil_tolerance * monitor_thresh:
            current_stage = 1
            urgency = self.threshold_config.get_urgency_info(1)
            path.append({
                "stage": 1,
                "action": "监控",
                "trigger_value": f"≤{oil_tolerance*monitor_thresh*100:.1f}%",
                "desc": self.threshold_config.ACTION_DESCRIPTIONS["monitor"],
                "recommended_fare": 0.0,
                "recommended_hedge": 0.0,
                "urgency": f"{urgency['icon']} {urgency['level']}",
                "urgency_icon": urgency["icon"],
                "urgency_level": urgency["level"],
                "urgency_color": urgency["color"]
            })

        # 阶段2: 票价传导
        elif oil_increase <= oil_tolerance * fare_thresh:
            current_stage = 2
            urgency = self.threshold_config.get_urgency_info(2)
            recommended_fare = min(fare_breakeven, fare_cap)
            path.append({
                "stage": 2,
                "action": "票价上调",
                "trigger_value": f">{oil_tolerance*monitor_thresh*100:.1f}%",
                "desc": f"建议票价+{recommended_fare*100:.0f}% (盈亏平衡点: {fare_breakeven*100:.1f}%)",
                "recommended_fare": recommended_fare,
                "recommended_hedge": 0.0,
                "urgency": f"{urgency['icon']} {urgency['level']}",
                "urgency_icon": urgency["icon"],
                "urgency_level": urgency["level"],
                "urgency_color": urgency["color"]
            })

        # 阶段3: 套保加仓
        elif oil_increase <= oil_tolerance * hedge_thresh:
            current_stage = 3
            urgency = self.threshold_config.get_urgency_info(3)
            path.append({
                "stage": 3,
                "action": "套保加仓 + 票价",
                "trigger_value": f">{oil_tolerance*fare_thresh*100:.1f}%",
                "desc": f"套保≥{hedge_trigger*100:.0f}%，票价已达上限({fare_cap*100:.0f}%)",
                "recommended_fare": fare_cap,
                "recommended_hedge": min(hedge_trigger, self.threshold_config.HEDGE_RATIO_MAX),
                "urgency": f"{urgency['icon']} {urgency['level']}",
                "urgency_icon": urgency["icon"],
                "urgency_level": urgency["level"],
                "urgency_color": urgency["color"]
            })

        # 阶段4: 削班启动
        else:
            current_stage = 4
            urgency = self.threshold_config.get_urgency_info(4)
            path.append({
                "stage": 4,
                "action": "削班启动",
                "trigger_value": f">{oil_tolerance*100:.1f}%",
                "desc": self.threshold_config.ACTION_DESCRIPTIONS["capacity_reduction"],
                "recommended_fare": fare_cap,
                "recommended_hedge": self.threshold_config.HEDGE_RATIO_MAX,
                "urgency": f"{urgency['icon']} {urgency['level']}",
                "urgency_icon": urgency["icon"],
                "urgency_level": urgency["level"],
                "urgency_color": urgency["color"]
            })

        return path, current_stage
