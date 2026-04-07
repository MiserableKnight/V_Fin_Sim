"""
Phase 2: 约束型动作序列优化器
Phase 2: Constrained Action Sequence Optimizer

在给定约束下优化票价、套保、削班动作序列
"""

from typing import List, Tuple, Optional
import numpy as np

from .demand_model import DemandModel, DemandCalculationResult
from .optimizer_results import (
    OptimizationResult, ActionStep, ActionType, ActionStatus
)
from .threshold_config import ThresholdConfig


class ActionOptimizer:
    """
    动作序列优化器
    按优先级依次优化票价、套保、削班动作
    """

    def __init__(self, config, threshold_config: ThresholdConfig):
        """
        Args:
            config: ModelConfig 实例
            threshold_config: 阈值配置
        """
        self.config = config
        self.threshold_config = threshold_config

    def recommend_sequence(
        self,
        oil_increase: float,
        fare_cap: Optional[float] = None,
        hedge_cap: Optional[float] = None,
        liquidity_buffer: float = 0.0,
        optimization_method: str = "grid",
        grid_resolution: int = 50
    ) -> OptimizationResult:
        """
        推荐最优动作序列

        Args:
            oil_increase: 油价涨幅
            fare_cap: 票价调整上限
            hedge_cap: 套保比例上限
            liquidity_buffer: 流动性缓冲
            optimization_method: 优化方法
            grid_resolution: 网格搜索分辨率

        Returns:
            OptimizationResult: 优化结果
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

        actions: List[ActionStep] = []
        constraints_violated: List[str] = []

        # Step 1: 票价寻优
        best_fare, fare_rationale = self._optimize_fare(
            oil_increase, fare_cap, R, V_o, V_f, eps,
            method=optimization_method, resolution=grid_resolution
        )

        actions.append(ActionStep(
            type=ActionType.FARE_ADJUSTMENT,
            value=best_fare,
            status=ActionStatus.OPTIMIZED if best_fare > 0 else ActionStatus.SKIPPED,
            description=f"票价调整 {best_fare*100:+.1f}%",
            rationale=fare_rationale,
            priority=1
        ))

        # 计算票价后的边际贡献
        cm_after_fare = self._calculate_cm(R, V_o, V_f, oil_increase, best_fare, eps, 0.0)

        # Step 2: 套保寻优
        best_hedge = 0.0
        hedge_status = ActionStatus.SKIPPED
        hedge_rationale = "票价调整后CM已覆盖固定成本，无需套保"

        if cm_after_fare < FC:
            best_hedge, hedge_rationale = self._optimize_hedge(
                oil_increase, best_fare, hedge_cap, R, V_o, V_f, FC, eps
            )
            hedge_status = ActionStatus.OPTIMIZED if best_hedge > 0 else ActionStatus.SKIPPED

            if best_hedge >= hedge_cap * 0.99 and cm_after_fare < FC:
                hedge_status = ActionStatus.CAP_EXCEEDED
                constraints_violated.append("套保比例触及上限，无法完全对冲")

        actions.append(ActionStep(
            type=ActionType.HEDGE_POSITION,
            value=best_hedge,
            status=hedge_status,
            description=f"套保比例 {best_hedge*100:.1f}%",
            rationale=hedge_rationale,
            priority=2
        ))

        # 计算套保后的边际贡献
        cm_after_hedge = self._calculate_cm(R, V_o, V_f, oil_increase, best_fare, eps, best_hedge)

        # Step 3: 削班判断
        cut_ratio, cut_status, cut_rationale = self._determine_cut_ratio(cm_after_hedge, FC)

        actions.append(ActionStep(
            type=ActionType.CAPACITY_REDUCTION,
            value=cut_ratio,
            status=cut_status,
            description=f"削减航班 {cut_ratio*100:.1f}%" if cut_ratio > 0 else "保持运力",
            rationale=cut_rationale,
            priority=3
        ))

        # 计算最终利润
        final_pnl = cm_after_hedge * (1 - cut_ratio) - FC
        is_feasible = len(constraints_violated) == 0 and cm_after_hedge > 0

        # 流动性压力测试
        if liquidity_buffer > 0 and final_pnl < -liquidity_buffer:
            is_feasible = False
            constraints_violated.append(
                f"预期利润({final_pnl:.2f})低于流动性缓冲(-{liquidity_buffer:.2f})"
            )

        return OptimizationResult(
            triggered_by=f"油价+{oil_increase*100:.0f}%",
            actions=actions,
            final_cm=cm_after_hedge,
            final_pnl=final_pnl,
            constraints_violated=constraints_violated,
            is_feasible=is_feasible,
            optimization_summary={
                "oil_increase_pct": f"+{oil_increase*100:.1f}%",
                "cm_after_fare": cm_after_fare,
                "cm_after_hedge": cm_after_hedge,
                "fc_coverage_ratio": cm_after_hedge / FC if FC > 0 else float('inf'),
                "fare_cap_pct": f"+{fare_cap*100:.1f}%",
                "hedge_cap_pct": f"{hedge_cap*100:.1f}%",
                "optimization_method": optimization_method
            }
        )

    def _calculate_cm(
        self, R: float, V_o: float, V_f: float,
        oil_increase: float, fare_adj: float, eps: float, hedge_ratio: float
    ) -> float:
        """计算边际贡献"""
        result = DemandModel.calculate_contribution_margin(
            R, V_o, V_f, oil_increase, fare_adj, eps, hedge_ratio
        )
        return result.contribution_margin

    def _optimize_fare(
        self, oil_increase: float, fare_cap: float,
        R: float, V_o: float, V_f: float, eps: float,
        method: str = "grid", resolution: int = 50
    ) -> Tuple[float, str]:
        """票价寻优"""
        best_fare = 0.0
        best_cm = float('-inf')

        for f in np.linspace(0, fare_cap, resolution):
            cm = self._calculate_cm(R, V_o, V_f, oil_increase, f, eps, 0.0)
            if cm > best_cm:
                best_cm = cm
                best_fare = f

        # 生成推荐理由
        cm_at_best = self._calculate_cm(R, V_o, V_f, oil_increase, best_fare, eps, 0.0)
        cm_at_zero = self._calculate_cm(R, V_o, V_f, oil_increase, 0.0, eps, 0.0)

        if best_fare > 0:
            rationale = (
                f"最优票价+{best_fare*100:.1f}%，"
                f"边际贡献从{cm_at_zero:.2f}提升至{cm_at_best:.2f}"
            )
        else:
            rationale = "维持原票价可使边际贡献最大化"

        return best_fare, rationale

    def _optimize_hedge(
        self, oil_increase: float, fare_adj: float, hedge_cap: float,
        R: float, V_o: float, V_f: float, FC: float, eps: float
    ) -> Tuple[float, str]:
        """套保寻优"""
        price_ratio = 1.0 + fare_adj
        demand_factor = price_ratio ** eps
        R_adj = R * price_ratio * demand_factor
        scaled_V_o = V_o * demand_factor

        cm_no_hedge = R_adj - scaled_V_o - V_f * (1 + oil_increase)

        if cm_no_hedge >= FC:
            return 0.0, "当前CM已覆盖FC，无需套保"

        numerator = R_adj - scaled_V_o - V_f - FC
        denominator = V_f * oil_increase

        if abs(denominator) < 1e-10:
            return 0.0, "油价无变化，无需套保"

        needed_hedge = 1 - numerator / denominator
        needed_hedge = np.clip(needed_hedge, 0.0, hedge_cap)

        cm_at_hedge = R_adj - scaled_V_o - V_f * (1 + oil_increase * (1 - needed_hedge))
        fc_coverage = cm_at_hedge / FC if FC > 0 else 0

        if needed_hedge >= hedge_cap * 0.99:
            rationale = (
                f"即使套保{hedge_cap*100:.0f}%，也只能覆盖FC的{fc_coverage*100:.1f}%，需削班"
            )
        else:
            rationale = (
                f"套保{needed_hedge*100:.1f}%可使CM达到{cm_at_hedge:.2f}，"
                f"覆盖FC的{fc_coverage*100:.1f}%"
            )

        return needed_hedge, rationale

    def _determine_cut_ratio(
        self, cm: float, FC: float
    ) -> Tuple[float, ActionStatus, str]:
        """削班判断"""
        network_preserve = self.config.network_preserve

        if cm <= 0:
            cut_ratio = 0.90
            status = ActionStatus.TRIGGERED
            rationale = f"边际贡献为负({cm:.2f})，建议削减90%运力"

        elif cm < FC:
            preserve_ratio = (cm / FC) * (1 - network_preserve) + network_preserve
            cut_ratio = max(0.05, min(0.80, 1.0 - preserve_ratio))
            status = ActionStatus.TRIGGERED
            rationale = (
                f"边际贡献({cm:.2f})仅覆盖FC的{cm/FC*100:.1f}%，"
                f"建议削减{cut_ratio*100:.1f}%运力"
            )

        else:
            cut_ratio = 0.0
            status = ActionStatus.NOT_TRIGGERED
            rationale = f"边际贡献({cm:.2f})充足覆盖FC({FC:.2f})，无需削班"

        return cut_ratio, status, rationale
