"""
运行示例脚本 / Run Example Script

演示如何使用 VietJetOilShockModel 进行决策分析
"""

from vietjet_oil_model import VietJetOilShockModel

def main():
    print("=" * 60)
    print("越捷航空油价冲击财务决策模型 - 演示")
    print("=" * 60)

    # 方式1: 使用默认配置（从 config/model_config.yaml 加载）
    print("\n【方式1: 使用默认配置】")
    model = VietJetOilShockModel()

    # 方式2: 从自定义 YAML 配置文件加载
    # model = VietJetOilShockModel(config_path="my_config.yaml")

    # 方式3: 直接创建配置对象
    # config = ModelConfig(
    #     R_base=70.0,
    #     V_fuel_base=25.0,
    #     demand_elasticity=-0.9
    # )
    # model = VietJetOilShockModel(config=config)

    print("\n【当前配置】")
    config_dict = model.config.to_dict()
    for section, params in config_dict.items():
        print(f"\n  {section}:")
        for k, v in params.items():
            print(f"    {k}: {v}")

    print("\n【单情景测算示例】")
    print("情景: 油价+40%, 票价+8%, 套保30%")

    result = model.evaluate(
        oil_increase=0.4,
        fare_adj=0.08,
        hedge_ratio=0.3
    )

    print(f"\n  决策状态: {result.status}")
    print(f"  有效燃油成本: {result.eff_fuel:.2f} 万亿₫")
    print(f"  调整后收入: {result.adj_revenue:.2f} 万亿₫")
    print(f"  总边际贡献: {result.total_cm:.2f} 万亿₫")
    print(f"  预期运营利润: {result.expected_pnl:.2f} 万亿₫")
    print(f"  建议航班削减比例: {result.cut_ratio*100:.1f}%")

    print("\n【批量情景扫描示例】")
    print("扫描范围: 油价 0%-100%, 票价 0%/5%/10%, 套保 0%/30%/50%")

    import numpy as np
    df = model.scenario_sweep(
        oil_range=np.arange(0.0, 1.1, 0.2),
        fare_range=[0.0, 0.05, 0.10],
        hedge_range=[0.0, 0.3, 0.5]
    )

    print(f"\n  共计算 {len(df)} 种情景")
    print("\n  前5种情景:")
    print(df.head().to_string(index=False))

    print("\n【运行可视化界面】")
    print("  请在终端运行: streamlit run app.py")
    print("  或使用: pip install -e . && vietjet-model")

if __name__ == "__main__":
    main()
