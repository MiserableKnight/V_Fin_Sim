"""
验证 Phase 2 优化修改
Verify Phase 2 optimization changes

1. 恒定弹性需求模型 (1+ΔP)^ε
2. 动态缩放变动成本
"""

import numpy as np
from vietjet_oil_model.core_model import VietJetOilShockModel, ModelConfig
from vietjet_oil_model.demand_model import DemandModel


def test_constant_elasticity_model():
    """测试恒定弹性模型"""
    print("=" * 60)
    print("测试 1: 恒定弹性需求模型")
    print("=" * 60)

    # 直接使用 DemandModel 静态方法
    # 测试不同涨价幅度下的需求因子
    fare_adjs = [0.0, 0.1, 0.2, 0.5, 1.0]  # 0%, 10%, 20%, 50%, 100%
    elasticity = -0.8

    print(f"\n需求弹性 ε = {elasticity}")
    print(f"{'票价涨幅':<12} {'线性模型':<15} {'恒定弹性模型':<15} {'差异'}")
    print("-" * 60)

    for f in fare_adjs:
        # 线性模型（旧）
        linear_demand = max(0.3, 1.0 + f * elasticity)

        # 恒定弹性模型（新）
        constant_demand = DemandModel.calculate_demand_factor(f, elasticity)

        diff = constant_demand - linear_demand
        print(f"{f*100:>6.0f}%      {linear_demand:>10.4f}      {constant_demand:>10.4f}      {diff:>6.4f}")

    # 关键验证：大幅涨价时，恒定弹性模型需求不会为负
    print("\n关键验证：大幅涨价（+200%）时")
    f_extreme = 2.0
    linear_demand = max(0.3, 1.0 + f_extreme * elasticity)
    constant_demand = DemandModel.calculate_demand_factor(f_extreme, elasticity)
    print(f"  线性模型需求因子: {linear_demand:.4f} (被max截断)")
    print(f"  恒定弹性需求因子: {constant_demand:.4f} (自然衰减，永远 > 0)")


def test_dynamic_variable_costs():
    """测试动态变动成本"""
    print("\n" + "=" * 60)
    print("测试 2: 动态变动成本缩放")
    print("=" * 60)

    config = ModelConfig(
        R_base=100.0,
        V_fuel_base=30.0,
        V_other_base=25.0,
        FC=20.0,
        demand_elasticity=-0.8
    )
    model = VietJetOilShockModel(config)

    oil_shock = 0.5  # 50%油价上涨

    print(f"\n油价涨幅: +{oil_shock*100:.0f}%")
    print(f"{'票价涨幅':<12} {'需求因子':<12} {'收入':<12} {'变动成本':<12} {'边际贡献':<12}")
    print("-" * 75)

    for fare_adj in [0.0, 0.1, 0.2, 0.3]:
        result = model.evaluate(oil_increase=oil_shock, fare_adj=fare_adj)

        demand_factor = DemandModel.calculate_demand_factor(fare_adj, config.demand_elasticity)
        scaled_V_o = config.V_other_base * demand_factor

        print(f"{fare_adj*100:>6.0f}%      {demand_factor:>8.4f}      "
              f"{result.adj_revenue:>8.2f}      {scaled_V_o:>8.2f}      "
              f"{result.total_cm:>8.2f}")


def test_phase2_optimizer():
    """测试 Phase 2 优化器"""
    print("\n" + "=" * 60)
    print("测试 3: Phase 2 优化器集成")
    print("=" * 60)

    model = VietJetOilShockModel()

    # 测试不同油价冲击下的优化建议
    oil_shocks = [0.3, 0.5, 0.8, 1.0]

    for oil in oil_shocks:
        result = model.recommend_action_sequence(
            oil_increase=oil,
            fare_cap=0.30,
            hedge_cap=0.60
        )

        print(f"\n油价涨幅 +{oil*100:.0f}%:")
        print(f"  最优票价: +{result.actions[0].value*100:.1f}%")
        print(f"  套保比例: {result.actions[1].value*100:.1f}%")
        print(f"  削班比例: {result.actions[2].value*100:.1f}%")
        print(f"  最终CM: {result.final_cm:.2f} 万亿₫")
        print(f"  预期利润: {result.final_pnl:.2f} 万亿₫")
        print(f"  可行性: {'✅ 可行' if result.is_feasible else '❌ 不可行'}")


def test_threshold_calculation():
    """测试阈值计算"""
    print("\n" + "=" * 60)
    print("测试 4: 阈值计算（恒定弹性模型）")
    print("=" * 60)

    model = VietJetOilShockModel()

    oil_increase = 0.5  # 50%油价上涨
    thresholds = model.get_thresholds(oil_increase=oil_increase, verbose=False)

    print(f"\n油价涨幅: +{oil_increase*100:.0f}%")
    print(f"  票价盈亏平衡点: +{thresholds.fare_breakeven*100:.1f}%")
    print(f"  最大可承受油价: +{thresholds.oil_tolerance*100:.1f}%")
    print(f"  削班触发套保线: {thresholds.hedge_trigger*100:.1f}%")
    print(f"  当前决策阶段: {thresholds.current_stage}")

    for step in thresholds.decision_path:
        print(f"\n  阶段 {step['stage']}: {step['action']}")
        print(f"    推荐: {step['desc']}")


if __name__ == "__main__":
    test_constant_elasticity_model()
    test_dynamic_variable_costs()
    test_phase2_optimizer()
    test_threshold_calculation()

    print("\n" + "=" * 60)
    print("✅ 所有验证测试完成！")
    print("=" * 60)
