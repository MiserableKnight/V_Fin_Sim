"""
需求模型与边际贡献计算
Demand Model and Contribution Margin Calculation

包含恒定弹性需求模型和边际贡献计算逻辑
"""

from dataclasses import dataclass


@dataclass
class DemandCalculationResult:
    """需求计算结果"""
    demand_factor: float       # 需求因子
    adjusted_revenue: float    # 调整后收入
    scaled_variable_cost: float  # 缩放后的变动成本
    fuel_cost: float           # 燃油成本
    contribution_margin: float  # 边际贡献


class DemandModel:
    """
    恒定弹性需求模型
    Constant Elasticity Demand Model

    使用经济学标准的恒定弹性公式：demand_factor = (1 + ΔP)^ε
    """

    @staticmethod
    def calculate_demand_factor(fare_adj: float, elasticity: float) -> float:
        """
        计算需求因子（恒定弹性模型）

        Args:
            fare_adj: 票价调整幅度（小数形式）
            elasticity: 需求价格弹性（通常为负数，如 -0.8）

        Returns:
            需求因子（0 < demand_factor，涨价时 < 1）
        """
        price_ratio = 1.0 + fare_adj
        demand_factor = price_ratio ** elasticity
        return demand_factor

    @classmethod
    def calculate_contribution_margin(
        cls,
        R_base: float,
        V_other: float,
        V_fuel: float,
        oil_increase: float,
        fare_adj: float,
        elasticity: float,
        hedge_ratio: float = 0.0
    ) -> DemandCalculationResult:
        """
        计算边际贡献（使用恒定弹性模型 + 动态变动成本）

        Args:
            R_base: 基础收入
            V_other: 其他变动成本
            V_fuel: 燃油成本
            oil_increase: 油价涨幅
            fare_adj: 票价调整幅度
            elasticity: 需求价格弹性
            hedge_ratio: 套保比例

        Returns:
            DemandCalculationResult: 计算结果对象
        """
        # 1. 恒定弹性需求模型
        demand_factor = cls.calculate_demand_factor(fare_adj, elasticity)

        # 2. 调整后收入
        price_ratio = 1.0 + fare_adj
        adjusted_revenue = R_base * price_ratio * demand_factor

        # 3. 动态缩放其他变动成本
        scaled_variable_cost = V_other * demand_factor

        # 4. 燃油成本（套保调整后）
        fuel_cost = V_fuel * (1 + oil_increase * (1 - hedge_ratio))

        # 5. 边际贡献
        contribution_margin = adjusted_revenue - scaled_variable_cost - fuel_cost

        return DemandCalculationResult(
            demand_factor=demand_factor,
            adjusted_revenue=adjusted_revenue,
            scaled_variable_cost=scaled_variable_cost,
            fuel_cost=fuel_cost,
            contribution_margin=contribution_margin
        )

    @staticmethod
    def solve_fare_breakeven(
        oil_increase: float,
        R: float,
        V_o: float,
        V_f: float,
        eps: float,
        min_fare: float = 0.0,
        max_fare: float = 0.50
    ) -> float:
        """
        求解票价盈亏平衡点（恒定弹性模型）

        定义：CM = R*(1+f)^(1+eps) - V_o*(1+f)^eps - V_f*(1+oil_increase) = 0

        Args:
            oil_increase: 油价涨幅
            R: 基础收入
            V_o: 其他变动成本
            V_f: 燃油成本
            eps: 需求价格弹性
            min_fare: 票价调整下限
            max_fare: 票价调整上限

        Returns:
            盈亏平衡票价调整幅度
        """
        from scipy.optimize import fsolve
        import numpy as np

        if oil_increase <= 0:
            return 0.0

        # 构建方程：CM(f) = 0
        def cm_zero_equation(f: float) -> float:
            price_ratio = 1.0 + f
            demand_factor = price_ratio ** eps
            revenue = R * price_ratio * demand_factor
            scaled_V_o = V_o * demand_factor
            fuel_cost = V_f * (1 + oil_increase)
            return revenue - scaled_V_o - fuel_cost

        try:
            fare_breakeven = fsolve(cm_zero_equation, x0=0.1)[0]
        except RuntimeError:
            fare_breakeven = 0.15

        return float(np.clip(fare_breakeven, min_fare, max_fare))
