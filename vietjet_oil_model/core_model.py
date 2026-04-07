"""
越捷航空油价冲击财务决策模型
VietJet Air Oil Shock Financial Decision Model

基于2025经审计财报附注28/36/31校准（单位：万亿越南盾）
Calibrated based on 2025 audited financial statements notes 28/36/31
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Literal, Optional


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


class VietJetOilShockModel:
    """
    越捷航空短期油价冲击航班优化模型
    VietJet Short-term Oil Shock Flight Optimization Model

    基于2025经审计财报附注28/36/31校准
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        self.config = config or ModelConfig()

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
