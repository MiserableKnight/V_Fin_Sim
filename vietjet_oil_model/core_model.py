"""
越捷航空油价冲击财务决策模型
VietJet Air Oil Shock Financial Decision Model

基于2025经审计财报附注28/36/31校准（单位：万亿越南盾）
Calibrated based on 2025 audited financial statements notes 28/36/31

重构后：核心模型 + 专用模块
- demand_model.py: 需求模型与边际贡献计算
- threshold_calculator.py: Phase 1 阈值计算
- action_optimizer.py: Phase 2 动作优化器
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Literal, Optional, Dict, List

from .threshold_config import DEFAULT_THRESHOLD_CONFIG, ThresholdConfig
from .optimizer_results import OptimizationResult
from .demand_model import DemandModel, DemandCalculationResult
from .threshold_calculator import ThresholdCalculator, ThresholdResult
from .action_optimizer import ActionOptimizer


@dataclass
class ModelConfig:
    """模型配置参数 / Model Configuration Parameters"""

    # 核心运营收入（剔除飞机销售、干租赁、备件等非航线主业）
    R_base: float = 64.94  # 万亿越南盾

    # 变动成本拆分（附注36）
    V_fuel_base: float = 24.70   # 燃油成本
    V_other_base: float = 22.70  # 外部服务+变动人工+航路起降费等

    # 固定成本拆分（附注36/31）
    FC: float = 19.06  # 租赁+折旧+固定人工+坏账等

    # 机队规模
    fleet_size: int = 121

    # 行业典型需求价格弹性
    demand_elasticity: float = -0.8

    # 网络骨架保留权重
    network_preserve: float = 0.25


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


class VietJetOilShockModel:
    """
    越捷航空短期油价冲击航班优化模型（重构版）

    架构：
    - 核心评估逻辑：evaluate()
    - 需求模型：委托给 DemandModel
    - Phase 1 阈值计算：委托给 ThresholdCalculator
    - Phase 2 动作优化：委托给 ActionOptimizer
    """

    def __init__(
        self,
        config: Optional[ModelConfig] = None,
        threshold_config: Optional[ThresholdConfig] = None
    ):
        """
        初始化模型

        Args:
            config: 模型配置
            threshold_config: 阈值配置
        """
        self.config = config or ModelConfig()
        self.threshold_config = threshold_config or DEFAULT_THRESHOLD_CONFIG

        # 初始化专用模块
        self.demand_model = DemandModel()
        self.threshold_calculator = ThresholdCalculator(self.config, self.threshold_config)
        self.action_optimizer = ActionOptimizer(self.config, self.threshold_config)

    # ==================== 核心评估方法 ====================

    def evaluate(
        self,
        oil_increase: float,
        fare_adj: float = 0.0,
        hedge_ratio: float = 0.0,
        network_preserve: Optional[float] = None
    ) -> DecisionResult:
        """
        单情景测算

        Args:
            oil_increase: 油价涨幅 (如 0.3 表示+30%)
            fare_adj: 票价调整幅度 (如 0.05 表示+5%)
            hedge_ratio: 燃油套期保值覆盖率 (0.0~1.0)
            network_preserve: 网络骨架保留权重

        Returns:
            DecisionResult: 决策结果对象
        """
        network_preserve = network_preserve or self.config.network_preserve

        # 使用需求模型计算边际贡献
        demand_result = self.demand_model.calculate_contribution_margin(
            R_base=self.config.R_base,
            V_other=self.config.V_other_base,
            V_fuel=self.config.V_fuel_base,
            oil_increase=oil_increase,
            fare_adj=fare_adj,
            elasticity=self.config.demand_elasticity,
            hedge_ratio=hedge_ratio
        )

        total_cm = demand_result.contribution_margin
        adj_revenue = demand_result.adjusted_revenue
        eff_fuel = demand_result.fuel_cost
        demand_factor = demand_result.demand_factor

        # 三阶决策逻辑
        if total_cm <= 0:
            cut_ratio = 0.90
            status = "🚨 现金流毁灭：单班边际贡献为负，飞一班亏一班。建议战略性停飞。"
            status_type = "critical"
        elif total_cm < self.config.FC:
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
        批量情景扫描

        Args:
            oil_range: 油价涨幅范围
            fare_range: 票价调整范围
            hedge_range: 套保比例范围

        Returns:
            pd.DataFrame: 情景分析结果
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
        """获取成本收入分解"""
        demand_factor = self.demand_model.calculate_demand_factor(
            result.fare_adj, self.config.demand_elasticity
        )

        return {
            "收入": {
                "基础收入": self.config.R_base,
                "票价调整": self.config.R_base * result.fare_adj,
                "需求影响": self.config.R_base * (1 + result.fare_adj) * (demand_factor - 1),
                "调整后收入": result.adj_revenue
            },
            "变动成本": {
                "燃油成本(基础)": self.config.V_fuel_base,
                f"燃油成本(油价+{result.oil_increase*100:.0f}%)": (
                    self.config.V_fuel_base * result.oil_increase * (1 - result.hedge_ratio)
                ),
                f"其他变动成本(基础)": self.config.V_other_base,
                f"其他变动成本(需求调整后)": self.config.V_other_base * demand_factor,
                "总变动成本": self.config.V_other_base * demand_factor + result.eff_fuel
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
        """获取模型配置摘要"""
        return {
            "基础收入(万亿₫)": self.config.R_base,
            "燃油成本(万亿₫)": self.config.V_fuel_base,
            "其他变动成本(万亿₫)": self.config.V_other_base,
            "固定成本(万亿₫)": self.config.FC,
            "机队规模(架)": self.config.fleet_size,
            "需求价格弹性": self.config.demand_elasticity
        }

    # ==================== Phase 1: 阈值计算 ====================

    def get_thresholds(
        self,
        oil_increase: float = 0.0,
        fare_cap: Optional[float] = None,
        hedge_cap: Optional[float] = None,
        verbose: bool = False
    ) -> ThresholdResult:
        """
        计算关键决策阈值与响应路径（委托给 ThresholdCalculator）

        Args:
            oil_increase: 当前油价涨幅
            fare_cap: 票价调整上限
            hedge_cap: 套保比例上限
            verbose: 是否输出详细计算过程

        Returns:
            ThresholdResult: 包含所有阈值和决策路径的结果对象
        """
        result = self.threshold_calculator.calculate(
            oil_increase=oil_increase,
            fare_cap=fare_cap,
            hedge_cap=hedge_cap
        )

        if verbose:
            print(f"[阈值计算] 油价涨幅: {oil_increase*100:.1f}%")
            print(f"[阈值计算] 盈亏平衡票价: {result.fare_breakeven*100:.1f}%")
            print(f"[阈值计算] 油价容忍上限: {result.oil_tolerance*100:.1f}%")
            print(f"[阈值计算] 削班触发套保线: {result.hedge_trigger*100:.1f}%")

        return result

    # ==================== Phase 2: 动作优化 ====================

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
        约束型动作序列优化器（委托给 ActionOptimizer）

        Args:
            oil_increase: 油价涨幅
            fare_cap: 票价调整上限
            hedge_cap: 套保比例上限
            liquidity_buffer: 流动性缓冲
            optimization_method: 优化方法
            grid_resolution: 网格搜索分辨率

        Returns:
            OptimizationResult: 优化结果对象
        """
        return self.action_optimizer.recommend_sequence(
            oil_increase=oil_increase,
            fare_cap=fare_cap,
            hedge_cap=hedge_cap,
            liquidity_buffer=liquidity_buffer,
            optimization_method=optimization_method,
            grid_resolution=grid_resolution
        )
