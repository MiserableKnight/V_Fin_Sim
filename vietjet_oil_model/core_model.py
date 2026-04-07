"""
越捷航空油价冲击财务决策模型
VietJet Air Oil Shock Financial Decision Model

基于2025经审计财报附注28/36/31校准（单位：万亿越南盾）
Calibrated based on 2025 audited financial statements notes 28/36/31
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, List, Tuple
from scipy.optimize import fsolve

from .threshold_config import DEFAULT_THRESHOLD_CONFIG, ThresholdConfig
from .optimizer_results import (
    OptimizationResult, ActionStep, ActionType, ActionStatus
)


@dataclass
class ModelConfig:
    """模型配置参数 / Model Configuration Parameters"""

    # 核心运营收入（剔除飞机销售、干租赁、备件等非航线主业）
    # Core operating revenue (excluding aircraft sales, dry leases, spare parts, etc.)
    R_base: float = 64.94  # 万亿越南盾 / trillion VND

    # 变动成本拆分（附注36） / Variable cost breakdown (Note 36)
    V_fuel_base: float = 24.70   # 燃油成本 / Fuel cost
    V_other_base: float = 22.70  # 外部服务+变动人工+航路起降费等 / External services + variable labor + route fees

    # 固定成本拆分（附注36/31） / Fixed cost breakdown (Note 36/31)
    FC: float = 19.06  # 租赁+折旧+固定人工+坏账等 / Lease + depreciation + fixed labor + bad debts

    # 机队规模 / Fleet size
    fleet_size: int = 121  # 2025Q3机队规模（架） / 2025Q3 fleet size (aircraft)

    # 行业典型需求价格弹性 / Industry typical demand price elasticity
    demand_elasticity: float = -0.8

    # 网络骨架保留权重 / Network backbone preservation weight
    network_preserve: float = 0.25  # 防止过度砍航班破坏枢纽 / Prevent excessive flight cuts from destroying hubs


@dataclass
class DecisionResult:
    """决策结果 / Decision Result"""

    oil_increase: float
    fare_adj: float
    hedge_ratio: float
    eff_fuel: float
    adj_revenue: float
    total_cm: float
    cut_ratio: float
    expected_pnl: float
    status: str
    status_type: Literal["critical", "warning", "healthy"]
    network_preserve: float

    def to_dict(self) -> dict:
        return {
            "油价涨幅": f"+{self.oil_increase*100:.0f}%",
            "票价调整": f"+{self.fare_adj*100:.0f}%",
            "套保比例": f"{self.hedge_ratio*100:.0f}%",
            "有效燃油成本(万亿₫)": round(self.eff_fuel, 2),
            "调整后收入(万亿₫)": round(self.adj_revenue, 2),
            "总边际贡献(万亿₫)": round(self.total_cm, 2),
            "建议航班削减比例": f"{self.cut_ratio*100:.1f}%",
            "预期运营利润/亏损(万亿₫)": round(self.expected_pnl, 2),
            "决策状态": self.status,
            "状态类型": self.status_type
        }


@dataclass
class ThresholdResult:
    """阈值计算结果数据类 / Threshold Calculation Result"""

    fare_breakeven: float          # 票价盈亏平衡点（小数形式，如0.12表示+12%）
    oil_tolerance: float           # 最大可承受油价涨幅
    hedge_trigger: float           # 触发削班的临界套保比例
    current_stage: int             # 当前所处决策阶段（1-4）
    decision_path: List[Dict]      # 决策路径步骤列表
    warnings: List[str]            # 预警信息

    def to_dict(self) -> dict:
        """转换为字典格式 / Convert to dictionary format"""
        return {
            "fare_breakeven_pct": f"+{self.fare_breakeven*100:.1f}%",
            "oil_tolerance_pct": f"+{self.oil_tolerance*100:.1f}%",
            "hedge_trigger_pct": f"{self.hedge_trigger*100:.1f}%",
            "current_stage": self.current_stage,
            "decision_path": self.decision_path,
            "warnings": self.warnings
        }


class VietJetOilShockModel:
    """
    越捷航空短期油价冲击航班优化模型
    VietJet Short-term Oil Shock Flight Optimization Model

    基于2025经审计财报附注28/36/31校准
    """

    def __init__(
        self,
        config: Optional[ModelConfig] = None,
        threshold_config: Optional[ThresholdConfig] = None
    ):
        """
        初始化模型 / Initialize model

        Args:
            config: 模型配置 / Model configuration
            threshold_config: 阈值配置 / Threshold configuration
        """
        self.config = config or ModelConfig()
        self.threshold_config = threshold_config or DEFAULT_THRESHOLD_CONFIG

    def evaluate(
        self,
        oil_increase: float,
        fare_adj: float = 0.0,
        hedge_ratio: float = 0.0,
        network_preserve: Optional[float] = None
    ) -> DecisionResult:
        """
        单情景测算 / Single scenario evaluation

        Args:
            oil_increase: 油价涨幅 (如 0.3 表示+30%) / Oil price increase (e.g., 0.3 means +30%)
            fare_adj: 票价调整幅度 (如 0.05 表示+5%) / Fare adjustment (e.g., 0.05 means +5%)
            hedge_ratio: 燃油套期保值覆盖率 (0.0~1.0) / Fuel hedge coverage ratio
            network_preserve: 网络骨架保留权重 / Network backbone preservation weight

        Returns:
            DecisionResult: 决策结果对象 / Decision result object
        """
        network_preserve = network_preserve or self.config.network_preserve

        # 1. 套保修正后的有效燃油成本
        # Effective fuel cost after hedge adjustment
        eff_fuel = self.config.V_fuel_base * (1 + oil_increase * (1 - hedge_ratio))

        # 2. 票价调整后的预期收入（含需求弹性衰减修正）
        # Expected revenue after fare adjustment (including demand elasticity decay)
        demand_factor = 1.0 + fare_adj * self.config.demand_elasticity
        demand_factor = max(demand_factor, 0.3)  # 最低保留30%需求 / Minimum 30% demand retention
        adj_revenue = self.config.R_base * (1 + fare_adj) * demand_factor

        # 3. 总边际贡献 / Total contribution margin
        total_cm = adj_revenue - self.config.V_other_base - eff_fuel

        # 4. 三阶决策逻辑 / Three-tier decision logic
        if total_cm <= 0:
            cut_ratio = 0.90  # 仅保留10%战略骨架 / Keep only 10% strategic backbone
            status = "🚨 现金流毁灭：单班边际贡献为负，飞一班亏一班。建议战略性停飞。"
            status_type = "critical"
        elif total_cm < self.config.FC:
            # 边际贡献为正，但无法覆盖固定成本
            # Positive contribution margin, but cannot cover fixed costs
            preserve_base = total_cm / self.config.FC
            preserve_adj = preserve_base * (1 - network_preserve) + network_preserve
            cut_ratio = max(0.05, min(0.80, 1.0 - preserve_adj))
            status = "⚠️ 现金流承压：单班贡献为正，建议保核心网络，压降低效边缘航班。"
            status_type = "warning"
        else:
            cut_ratio = 0.0
            status = "✅ 运营健康：边际贡献完全覆盖固定成本，无需砍航班，可优化排班提效。"
            status_type = "healthy"

        expected_pnl = total_cm - self.config.FC

        return DecisionResult(
            oil_increase=oil_increase,
            fare_adj=fare_adj,
            hedge_ratio=hedge_ratio,
            eff_fuel=eff_fuel,
            adj_revenue=adj_revenue,
            total_cm=total_cm,
            cut_ratio=cut_ratio,
            expected_pnl=expected_pnl,
            status=status,
            status_type=status_type,
            network_preserve=network_preserve
        )

    def scenario_sweep(
        self,
        oil_range: Optional[np.ndarray] = None,
        fare_range: Optional[list] = None,
        hedge_range: Optional[list] = None
    ) -> pd.DataFrame:
        """
        批量情景扫描 / Batch scenario sweep

        Args:
            oil_range: 油价涨幅范围 / Oil price increase range
            fare_range: 票价调整范围 / Fare adjustment range
            hedge_range: 套保比例范围 / Hedge ratio range

        Returns:
            pd.DataFrame: 情景分析结果 / Scenario analysis results
        """
        if oil_range is None:
            oil_range = np.arange(0.0, 1.2, 0.1)
        if fare_range is None:
            fare_range = [0.0, 0.05, 0.10]
        if hedge_range is None:
            hedge_range = [0.0, 0.30, 0.50]

        results = []
        for oil in oil_range:
            for fare in fare_range:
                for hedge in hedge_range:
                    res = self.evaluate(oil, fare, hedge)
                    results.append({
                        "油价涨幅": oil,
                        "票价调整": fare,
                        "套保比例": hedge,
                        "有效燃油成本": res.eff_fuel,
                        "调整后收入": res.adj_revenue,
                        "总边际贡献": res.total_cm,
                        "航班削减比例": res.cut_ratio,
                        "预期利润": res.expected_pnl,
                        "状态类型": res.status_type
                    })

        df = pd.DataFrame(results)
        return df.sort_values(by=["油价涨幅", "套保比例", "票价调整"]).reset_index(drop=True)

    def get_breakdown(self, result: DecisionResult) -> dict:
        """
        获取成本收入分解 / Get cost and revenue breakdown

        Args:
            result: 决策结果 / Decision result

        Returns:
            dict: 成本收入分解 / Cost and revenue breakdown
        """
        return {
            "收入": {
                "基础收入": self.config.R_base,
                "票价调整": self.config.R_base * result.fare_adj,
                "需求影响": self.config.R_base * (1 + result.fare_adj) * (1 - 1 / max(1.0 + result.fare_adj * self.config.demand_elasticity, 0.3)),
                "调整后收入": result.adj_revenue
            },
            "变动成本": {
                "燃油成本(基础)": self.config.V_fuel_base,
                f"燃油成本(油价+{result.oil_increase*100:.0f}%)": self.config.V_fuel_base * result.oil_increase * (1 - result.hedge_ratio),
                "其他变动成本": self.config.V_other_base,
                "总变动成本": self.config.V_other_base + result.eff_fuel
            },
            "固定成本": {
                "固定成本": self.config.FC
            },
            "利润分析": {
                "边际贡献": result.total_cm,
                "固定成本": self.config.FC,
                "运营利润": result.expected_pnl
            }
        }

    def get_config_summary(self) -> dict:
        """获取模型配置摘要 / Get model configuration summary"""
        return {
            "基础收入(万亿₫)": self.config.R_base,
            "燃油成本(万亿₫)": self.config.V_fuel_base,
            "其他变动成本(万亿₫)": self.config.V_other_base,
            "固定成本(万亿₫)": self.config.FC,
            "机队规模(架)": self.config.fleet_size,
            "需求价格弹性": self.config.demand_elasticity
        }

    # ==================== Phase 1: 阈值计算与决策路径 ====================
    # Phase 1: Threshold Calculation and Decision Path

    def get_thresholds(
        self,
        oil_increase: float = 0.0,
        fare_cap: Optional[float] = None,
        hedge_cap: Optional[float] = None,
        verbose: bool = False
    ) -> ThresholdResult:
        """
        计算关键决策阈值与响应路径（Phase 1 核心）
        Calculate key decision thresholds and response paths (Phase 1 Core)

        Args:
            oil_increase: 当前油价涨幅（小数形式，如0.4表示+40%）
            fare_cap: 票价调整上限，默认使用配置中的FARE_ADJUST_MAX
            hedge_cap: 套保比例上限，默认使用配置中的HEDGE_RATIO_MAX
            verbose: 是否输出详细计算过程

        Returns:
            ThresholdResult: 包含所有阈值和决策路径的结果对象

        Raises:
            ValueError: 当输入参数超出合理范围时
        """
        # 参数校验
        if oil_increase < 0:
            raise ValueError(f"油价涨幅不能为负数: {oil_increase}")

        # 使用默认配置或传入的约束
        fare_cap = fare_cap or self.threshold_config.FARE_ADJUST_MAX
        hedge_cap = hedge_cap or self.threshold_config.HEDGE_RATIO_MAX

        # 提取基础参数
        V_f = self.config.V_fuel_base      # 基础燃油成本
        V_o = self.config.V_other_base     # 其他变动成本
        R = self.config.R_base             # 基础收入
        FC = self.config.FC                # 固定成本
        eps = self.config.demand_elasticity  # 需求价格弹性

        warnings = []

        # ===== 阈值1：票价盈亏平衡点（CM=0，无套保保护） =====
        fare_breakeven = self._solve_fare_breakeven(
            oil_increase, R, V_o, V_f, eps
        )

        # 检查盈亏平衡点是否超过票价上限
        if fare_breakeven > fare_cap:
            warnings.append(
                f"⚠️ 票价盈亏平衡点(+{fare_breakeven*100:.1f}%) "
                f"超过设定上限(+{fare_cap*100:.1f}%)，需动用套保或削班"
            )

        # ===== 阈值2：最大可承受油价涨幅 =====
        oil_tolerance = self._calculate_oil_tolerance(
            R, V_o, V_f, fare_cap, hedge_cap, eps
        )

        if oil_increase > oil_tolerance:
            warnings.append(
                f"🚨 当前油价涨幅(+{oil_increase*100:.1f}%) "
                f"已超过理论容忍上限(+{oil_tolerance*100:.1f}%)"
            )

        # ===== 阈值3：触发削班的临界套保比例 =====
        hedge_trigger = self._solve_hedge_trigger(
            oil_increase, R, V_o, V_f, FC, fare_cap
        )

        if hedge_trigger > hedge_cap:
            warnings.append(
                f"🚨 避免削班所需套保比例({hedge_trigger*100:.1f}%) "
                f"超过政策上限({hedge_cap*100:.1f}%)，削班不可避免"
            )

        # ===== 构建决策路径 =====
        decision_path, current_stage = self._build_decision_path(
            oil_increase, oil_tolerance, fare_breakeven, hedge_trigger, fare_cap
        )

        if verbose:
            print(f"[阈值计算] 油价涨幅: {oil_increase*100:.1f}%")
            print(f"[阈值计算] 盈亏平衡票价: {fare_breakeven*100:.1f}%")
            print(f"[阈值计算] 油价容忍上限: {oil_tolerance*100:.1f}%")
            print(f"[阈值计算] 削班触发套保线: {hedge_trigger*100:.1f}%")

        return ThresholdResult(
            fare_breakeven=fare_breakeven,
            oil_tolerance=oil_tolerance,
            hedge_trigger=hedge_trigger,
            current_stage=current_stage,
            decision_path=decision_path,
            warnings=warnings
        )

    def _solve_fare_breakeven(
        self,
        oil_increase: float,
        R: float,
        V_o: float,
        V_f: float,
        eps: float
    ) -> float:
        """
        求解票价盈亏平衡点
        Solve fare breakeven point

        定义：CM = R*(1+f)*(1+eps*f) - V_o - V_f*(1+oil_increase) = 0
        求解：f = ?
        """
        if oil_increase <= 0:
            return 0.0

        # 构建方程：CM(f) = 0
        def cm_zero_equation(f: float) -> float:
            return R * (1 + f) * (1 + eps * f) - V_o - V_f * (1 + oil_increase)

        # 使用scipy.optimize.fsolve求解
        try:
            fare_breakeven = fsolve(
                cm_zero_equation,
                x0=0.1,  # 初始猜测值10%
                full_output=False
            )[0]
        except RuntimeError:
            # 求解失败，返回保守估计
            fare_breakeven = 0.15

        # 限制在合理区间
        min_fare, max_fare = self.threshold_config.FARE_ADJUST_MIN, self.threshold_config.FARE_ADJUST_MAX
        return np.clip(fare_breakeven, min_fare, max_fare)

    def _calculate_oil_tolerance(
        self,
        R: float,
        V_o: float,
        V_f: float,
        fare_cap: float,
        hedge_cap: float,
        eps: float
    ) -> float:
        """
        计算最大可承受油价涨幅
        Calculate maximum tolerable oil price increase

        推导：
        调整后收入 = R * (1 + fare_cap) * (1 + eps * fare_cap)
        套保后燃油成本 = V_f * (1 + oil_increase * (1 - hedge_cap))
        盈亏平衡条件：调整后收入 = V_o + 套保后燃油成本
        """
        # 调整后收入
        adjusted_revenue = R * (1 + fare_cap) * (1 + eps * fare_cap)

        # 计算油价容忍度
        # adjusted_revenue = V_o + V_f * (1 + oil_tol * (1 - hedge_cap))
        # => oil_tol = (adjusted_revenue - V_o - V_f) / (V_f * (1 - hedge_cap))

        denominator = V_f * (1 - hedge_cap)

        if abs(denominator) < self.threshold_config.SOLVER_TOLERANCE:
            # 套保比例100%，燃油成本完全锁定
            return np.inf

        oil_tolerance = (adjusted_revenue - V_o - V_f) / denominator

        return max(oil_tolerance, 0.0)

    def _solve_hedge_trigger(
        self,
        oil_increase: float,
        R: float,
        V_o: float,
        V_f: float,
        FC: float,
        fare_cap: float
    ) -> float:
        """
        求解触发削班的临界套保比例
        Solve hedge ratio trigger for capacity reduction

        定义：CM_min = FC（边际贡献刚好覆盖固定成本）
        求解：h = ?
        """
        if oil_increase <= 0:
            return 0.0

        # 调整后收入
        adjusted_revenue = R * (1 + fare_cap) * (1 + self.config.demand_elasticity * fare_cap)

        # 构建方程：CM(h) - FC = 0
        def hedge_trigger_equation(h: float) -> float:
            fuel_cost_hedged = V_f * (1 + oil_increase * (1 - h))
            return adjusted_revenue - V_o - fuel_cost_hedged - FC

        try:
            hedge_trigger = fsolve(
                hedge_trigger_equation,
                x0=0.3,  # 初始猜测值30%
                full_output=False
            )[0]
        except RuntimeError:
            hedge_trigger = 0.5

        # 限制在[0, 1]区间
        return np.clip(hedge_trigger, 0.0, 1.0)

    def _build_decision_path(
        self,
        oil_increase: float,
        oil_tolerance: float,
        fare_breakeven: float,
        hedge_trigger: float,
        fare_cap: float
    ) -> Tuple[List[Dict], int]:
        """
        构建决策响应路径
        Build decision response path

        基于当前油价涨幅和计算出的阈值，生成阶梯式响应方案
        """
        # 获取配置的触发阈值
        monitor_thresh, fare_thresh, hedge_thresh = self.threshold_config.get_trigger_thresholds()

        path = []
        current_stage = 1

        # 阶段1：监控区间
        if oil_increase <= oil_tolerance * monitor_thresh:
            current_stage = 1
            urgency_info = self.threshold_config.get_urgency_info(1)
            path.append({
                "stage": 1,
                "action": "监控",
                "trigger": f"油价涨幅 ≤ {oil_tolerance*100:.0f}%×{monitor_thresh:.0f}",
                "trigger_value": f"≤{oil_tolerance*monitor_thresh*100:.1f}%",
                "desc": self.threshold_config.ACTION_DESCRIPTIONS["monitor"],
                "recommended_fare": 0.0,
                "recommended_hedge": 0.0,
                "urgency": f"{urgency_info['icon']} {urgency_info['level']}",
                "urgency_icon": urgency_info["icon"],
                "urgency_level": urgency_info["level"],
                "urgency_color": urgency_info["color"]
            })

        # 阶段2：票价传导区间
        elif oil_increase <= oil_tolerance * fare_thresh:
            current_stage = 2
            urgency_info = self.threshold_config.get_urgency_info(2)
            recommended_fare = min(fare_breakeven, fare_cap)
            path.append({
                "stage": 2,
                "action": "票价上调",
                "trigger": f"油价突破 {oil_tolerance*100:.0f}%×{monitor_thresh:.2f}",
                "trigger_value": f">{oil_tolerance*monitor_thresh*100:.1f}%",
                "desc": (
                    f"建议票价上调至 {recommended_fare*100:.0f}% "
                    f"(目标盈亏平衡点: {fare_breakeven*100:.1f}%)"
                ),
                "recommended_fare": recommended_fare,
                "recommended_hedge": 0.0,
                "urgency": f"{urgency_info['icon']} {urgency_info['level']}",
                "urgency_icon": urgency_info["icon"],
                "urgency_level": urgency_info["level"],
                "urgency_color": urgency_info["color"]
            })

        # 阶段3：套保加仓区间
        elif oil_increase <= oil_tolerance * hedge_thresh:
            current_stage = 3
            urgency_info = self.threshold_config.get_urgency_info(3)
            recommended_fare = fare_cap  # 票价已触及上限
            path.append({
                "stage": 3,
                "action": "套保加仓 + 票价",
                "trigger": f"油价突破 {oil_tolerance*100:.0f}%×{fare_thresh:.2f}",
                "trigger_value": f">{oil_tolerance*fare_thresh*100:.1f}%",
                "desc": (
                    f"套保需覆盖 ≥{hedge_trigger*100:.0f}%，"
                    f"票价已触及上限({fare_cap*100:.0f}%)"
                ),
                "recommended_fare": recommended_fare,
                "recommended_hedge": min(hedge_trigger, self.threshold_config.HEDGE_RATIO_MAX),
                "urgency": f"{urgency_info['icon']} {urgency_info['level']}",
                "urgency_icon": urgency_info["icon"],
                "urgency_level": urgency_info["level"],
                "urgency_color": urgency_info["color"]
            })

        # 阶段4：削班启动
        else:
            current_stage = 4
            urgency_info = self.threshold_config.get_urgency_info(4)
            path.append({
                "stage": 4,
                "action": "削班启动",
                "trigger": f"油价 > {oil_tolerance*100:.0f}%",
                "trigger_value": f">{oil_tolerance*100:.1f}%",
                "desc": self.threshold_config.ACTION_DESCRIPTIONS["capacity_reduction"],
                "recommended_fare": fare_cap,
                "recommended_hedge": self.threshold_config.HEDGE_RATIO_MAX,
                "urgency": f"{urgency_info['icon']} {urgency_info['level']}",
                "urgency_icon": urgency_info["icon"],
                "urgency_level": urgency_info["level"],
                "urgency_color": urgency_info["color"]
            })

        return path, current_stage

    # ==================== Phase 2: 约束型动作序列优化器 ====================
    # Phase 2: Constrained Action Sequence Optimizer

    def recommend_action_sequence(
        self,
        oil_increase: float,
        fare_cap: Optional[float] = None,
        hedge_cap: Optional[float] = None,
        liquidity_buffer: float = 0.0,
        optimization_method: str = "grid",
        grid_resolution: int = 50
    ) -> OptimizationResult:
        """
        约束型动作序列优化器（Phase 2 核心）
        Constrained Action Sequence Optimizer (Phase 2 Core)

        在给定约束下，按优先级依次优化票价、套保、削班动作，
        输出最优决策序列和推荐理由。

        Args:
            oil_increase: 油价涨幅（小数形式，如 0.4 表示 +40%）
            fare_cap: 票价调整上限，默认使用配置值
            hedge_cap: 套保比例上限，默认使用配置值
            liquidity_buffer: 流动性缓冲（万亿₫），用于现金压力测试
            optimization_method: 优化方法 ("grid"网格搜索 | "gradient"梯度法)
            grid_resolution: 网格搜索分辨率

        Returns:
            OptimizationResult: 优化结果对象

        Raises:
            ValueError: 当输入参数无效时
        """
        # 参数校验
        if oil_increase < 0:
            raise ValueError(f"油价涨幅不能为负: {oil_increase}")

        # 使用默认约束
        fare_cap = fare_cap or self.threshold_config.FARE_ADJUST_MAX
        hedge_cap = hedge_cap or self.threshold_config.HEDGE_RATIO_MAX

        # 提取基础参数
        V_f = self.config.V_fuel_base
        V_o = self.config.V_other_base
        R = self.config.R_base
        FC = self.config.FC
        eps = self.config.demand_elasticity

        actions: List[ActionStep] = []
        constraints_violated: List[str] = []

        # ===== Step 1: 票价寻优（最大化边际贡献） =====
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

        # 计算票价调整后的边际贡献
        cm_after_fare = self._calculate_cm(
            R, V_o, V_f, oil_increase, best_fare, eps, hedge_ratio=0.0
        )

        # ===== Step 2: 套保寻优（若CM仍不足覆盖FC） =====
        best_hedge = 0.0
        hedge_status = ActionStatus.SKIPPED
        hedge_rationale = "票价调整后CM已覆盖固定成本，无需套保"

        if cm_after_fare < FC:
            best_hedge, hedge_rationale = self._optimize_hedge(
                oil_increase, best_fare, hedge_cap, R, V_o, V_f, FC, eps
            )
            hedge_status = ActionStatus.OPTIMIZED if best_hedge > 0 else ActionStatus.SKIPPED

            # 检查是否触及上限
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
        cm_after_hedge = self._calculate_cm(
            R, V_o, V_f, oil_increase, best_fare, eps, hedge_ratio=best_hedge
        )

        # ===== Step 3: 削班判断（若CM仍为负或不足） =====
        cut_ratio, cut_status, cut_rationale = self._determine_cut_ratio(
            cm_after_hedge, FC
        )

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

        # 判断是否找到可行解
        is_feasible = len(constraints_violated) == 0 and cm_after_hedge > 0

        # 流动性压力测试
        if liquidity_buffer > 0 and final_pnl < -liquidity_buffer:
            is_feasible = False
            constraints_violated.append(
                f"预期利润({final_pnl:.2f}万亿₫)低于流动性缓冲(-{liquidity_buffer:.2f}万亿₫)"
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

    def _optimize_fare(
        self,
        oil_increase: float,
        fare_cap: float,
        R: float,
        V_o: float,
        V_f: float,
        eps: float,
        method: str = "grid",
        resolution: int = 50
    ) -> Tuple[float, str]:
        """
        票价寻优：在约束内寻找使边际贡献最大的票价调整幅度
        Fare Optimization: Find fare adjustment that maximizes contribution margin

        目标函数：max CM(f) = R*(1+f)*(1+eps*f) - V_o - V_f*(1+oil)
        约束：0 ≤ f ≤ fare_cap

        Args:
            oil_increase: 油价涨幅
            fare_cap: 票价调整上限
            R: 基础收入
            V_o: 其他变动成本
            V_f: 燃油成本
            eps: 需求价格弹性
            method: 优化方法 ("grid" | "gradient")
            resolution: 网格搜索分辨率

        Returns:
            (最优票价调整幅度, 推荐理由)
        """
        if method == "grid":
            # 网格搜索
            best_fare = 0.0
            best_cm = float('-inf')

            for f in np.linspace(0, fare_cap, resolution):
                cm = self._calculate_cm(R, V_o, V_f, oil_increase, f, eps, 0.0)
                if cm > best_cm:
                    best_cm = cm
                    best_fare = f

        elif method == "gradient":
            # 梯度法（利用二次函数性质可直接求极值）
            # CM(f) = R*(1+f)*(1+eps*f) - constant
            #      = R*(1 + (1+eps)f + eps*f^2) - constant
            # dCM/df = R*((1+eps) + 2*eps*f) = 0
            # f* = -(1+eps) / (2*eps)
            if eps < -1e-6:  # 弹性为负
                f_star = -(1 + eps) / (2 * eps)
                best_fare = np.clip(f_star, 0, fare_cap)
            else:
                # 弹性非负时，单调关系
                best_fare = fare_cap if (1 + eps) > 0 else 0
        else:
            best_fare = 0.0

        # 生成推荐理由
        cm_at_best = self._calculate_cm(R, V_o, V_f, oil_increase, best_fare, eps, 0.0)
        cm_at_zero = self._calculate_cm(R, V_o, V_f, oil_increase, 0.0, eps, 0.0)

        if best_fare > 0:
            rationale = (
                f"油价冲击下，最优票价调整+{best_fare*100:.1f}%，"
                f"使边际贡献从{cm_at_zero:.2f}提升至{cm_at_best:.2f}万亿₫"
            )
        else:
            rationale = "当前油价下，维持原票价可使边际贡献最大化"

        return best_fare, rationale

    def _optimize_hedge(
        self,
        oil_increase: float,
        fare_adj: float,
        hedge_cap: float,
        R: float,
        V_o: float,
        V_f: float,
        FC: float,
        eps: float
    ) -> Tuple[float, str]:
        """
        套保寻优：计算覆盖固定成本所需的最小套保比例
        Hedge Optimization: Calculate minimum hedge ratio to cover fixed costs

        目标：CM(h) ≥ FC
        约束：0 ≤ h ≤ hedge_cap

        推导：
        CM(h) = R_adj - V_o - V_f*(1 + oil*(1-h))
        设 CM(h) = FC，解出 h

        Args:
            oil_increase: 油价涨幅
            fare_adj: 票价调整幅度
            hedge_cap: 套保比例上限
            R: 基础收入
            V_o: 其他变动成本
            V_f: 燃油成本
            FC: 固定成本
            eps: 需求价格弹性

        Returns:
            (最优套保比例, 推荐理由)
        """
        # 计算调整后收入
        R_adj = R * (1 + fare_adj) * (1 + eps * fare_adj)

        # 当前CM（无套保）
        cm_no_hedge = R_adj - V_o - V_f * (1 + oil_increase)

        if cm_no_hedge >= FC:
            return 0.0, "当前CM已覆盖FC，无需套保"

        # 计算所需套保比例
        # R_adj - V_o - V_f*(1 + oil*(1-h)) = FC
        # => h = 1 - (R_adj - V_o - V_f - FC) / (V_f * oil_increase)

        numerator = R_adj - V_o - V_f - FC
        denominator = V_f * oil_increase

        if abs(denominator) < 1e-10:
            return 0.0, "油价无变化，无需套保"

        needed_hedge = 1 - numerator / denominator
        needed_hedge = np.clip(needed_hedge, 0.0, hedge_cap)

        # 生成推荐理由
        cm_at_hedge = R_adj - V_o - V_f * (1 + oil_increase * (1 - needed_hedge))
        fc_coverage = cm_at_hedge / FC if FC > 0 else 0

        if needed_hedge >= hedge_cap * 0.99:
            rationale = (
                f"即使套保达到上限{hedge_cap*100:.0f}%，"
                f"也只能覆盖FC的{fc_coverage*100:.1f}%，需考虑削班"
            )
        else:
            rationale = (
                f"套保{needed_hedge*100:.1f}%可使CM达到{cm_at_hedge:.2f}万亿₫，"
                f"覆盖FC的{fc_coverage*100:.1f}%"
            )

        return needed_hedge, rationale

    def _determine_cut_ratio(
        self,
        cm: float,
        FC: float
    ) -> Tuple[float, ActionStatus, str]:
        """
        削班判断：根据边际贡献与固定成本的关系确定削减比例
        Capacity Reduction Decision: Determine cut ratio based on CM vs FC

        分级逻辑：
        - CM ≤ 0: 重度削减（90%）
        - 0 < CM < FC: 轻度削减（按比例）
        - CM ≥ FC: 不削减

        Args:
            cm: 边际贡献
            FC: 固定成本

        Returns:
            (削减比例, 动作状态, 推荐理由)
        """
        network_preserve = self.config.network_preserve

        if cm <= 0:
            # 边际贡献为负，大幅削减
            cut_ratio = 0.90
            status = ActionStatus.TRIGGERED
            rationale = (
                f"边际贡献为负({cm:.2f}万亿₫)，"
                f"每飞一班亏损加剧，建议削减90%运力"
            )

        elif cm < FC:
            # 边际贡献不足覆盖固定成本，按比例削减
            # preserve = (CM/FC) * (1 - network_preserve) + network_preserve
            # 保留更多核心航线，削减边缘航线
            preserve_ratio = (cm / FC) * (1 - network_preserve) + network_preserve
            cut_ratio = max(0.05, min(0.80, 1.0 - preserve_ratio))

            status = ActionStatus.TRIGGERED
            rationale = (
                f"边际贡献({cm:.2f}万亿₫)仅覆盖FC的{cm/FC*100:.1f}%，"
                f"建议削减{cut_ratio*100:.1f}%运力以保核心网络"
            )

        else:
            # 边际贡献充足，不削减
            cut_ratio = 0.0
            status = ActionStatus.NOT_TRIGGERED
            rationale = (
                f"边际贡献({cm:.2f}万亿₫)充足覆盖FC({FC:.2f}万亿₫)，"
                f"无需削班"
            )

        return cut_ratio, status, rationale

    def _calculate_cm(
        self,
        R: float,
        V_o: float,
        V_f: float,
        oil_increase: float,
        fare_adj: float,
        eps: float,
        hedge_ratio: float
    ) -> float:
        """
        计算边际贡献的辅助方法
        Helper method to calculate contribution margin

        Args:
            R: 基础收入
            V_o: 其他变动成本
            V_f: 燃油成本
            oil_increase: 油价涨幅
            fare_adj: 票价调整幅度
            eps: 需求价格弹性
            hedge_ratio: 套保比例

        Returns:
            边际贡献值
        """
        revenue = R * (1 + fare_adj) * (1 + eps * fare_adj)
        fuel_cost = V_f * (1 + oil_increase * (1 - hedge_ratio))
        return revenue - V_o - fuel_cost
