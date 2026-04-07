"""
越捷航空油价冲击财务决策模型 - 交互式可视化界面
VietJet Air Oil Shock Financial Decision Model - Interactive Visualization

运行方式 / Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from vietjet_oil_model import VietJetOilShockModel, ModelConfig

# 页面配置 / Page config
st.set_page_config(
    page_title="越捷航空油价冲击模型",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS / Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .status-critical {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
    }
    .status-warning {
        background: linear-gradient(135deg, #feca57 0%, #ff9f43 100%);
    }
    .status-healthy {
        background: linear-gradient(135deg, #1dd1a1 0%, #10ac84 100%);
    }
    .info-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# 标题 / Title
st.markdown('<p class="main-header">✈️ 越捷航空油价冲击财务决策模型</p>', unsafe_allow_html=True)
st.markdown("""
**基于2025经审计财报附注28/36/31校准**

💰 **金额单位：万亿越南盾（Trillion VND，符号：万亿₫）**
> 1 万亿₫ ≈ 400 万美元 ≈ 2,900 万人民币

本模型帮助分析油价冲击下的航班运营决策，支持：
- 🎯 单情景决策分析
- 📊 多情景批量扫描
- 📈 可视化图表展示
- ⚙️ 参数自定义调整
""")

# 侧边栏 - 参数配置 / Sidebar - Parameter Configuration
st.sidebar.header("⚙️ 参数配置")

st.sidebar.info("""
💡 **参数说明**
- "基础财务参数"来自财报，可根据最新数据调整
- "油价涨幅"是外生冲击，独立于基础燃油成本
- 有效燃油成本 = 基础燃油成本 × (1 + 油价涨幅 × (1 - 套保比例))
""")

# 基础参数 / Base Parameters
st.sidebar.subheader("📊 基础财务参数 (万亿₫)")
R_base = st.sidebar.slider("基础运营收入", 50.0, 80.0, 64.94, 0.01,
                           help="来自财报附注28，剔除非航线主业收入")
V_fuel_base = st.sidebar.slider("基础燃油成本", 15.0, 35.0, 24.70, 0.01,
                                help="来自财报附注36，作为计算有效燃油成本的基准值")
V_other_base = st.sidebar.slider("其他变动成本", 15.0, 30.0, 22.70, 0.01,
                                help="来自财报附注36，含外部服务费、变动人工、航路费等")
FC = st.sidebar.slider("固定成本", 10.0, 30.0, 19.06, 0.01,
                      help="来自财报附注36/31，含租赁费、折旧、固定人工等")

# 弹性参数 / Elasticity Parameters
st.sidebar.subheader("📈 弹性与权重")
demand_elasticity = st.sidebar.slider("需求价格弹性", -1.5, -0.3, -0.8, 0.1)
network_preserve = st.sidebar.slider("网络骨架保留权重", 0.1, 0.5, 0.25, 0.05)

# 创建模型 / Create Model
config = ModelConfig(
    R_base=R_base,
    V_fuel_base=V_fuel_base,
    V_other_base=V_other_base,
    FC=FC,
    demand_elasticity=demand_elasticity,
    network_preserve=network_preserve
)
model = VietJetOilShockModel(config)

# 选项卡 / Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 单情景分析",
    "📊 多情景扫描",
    "📈 可视化分析",
    "🔧 模型配置"
])

# ==================== Tab 1: 单情景分析 ====================
with tab1:
    st.header("🎯 单情景决策分析")

    col1, col2, col3 = st.columns(3)

    with col1:
        oil_increase = st.slider(
            "油价涨幅 (%)",
            0, 150, 40,
            help="油价相对基准的涨幅百分比。例如+40%表示油价上涨40%。"
        ) / 100

    with col2:
        fare_adj = st.slider(
            "票价调整 (%)",
            -20, 50, 8,
            help="票价调整百分比，负数表示降价。涨价会增加收入但会抑制需求（需求弹性=-0.8）"
        ) / 100

    with col3:
        hedge_ratio = st.slider(
            "套保比例 (%)",
            0, 100, 30,
            help="燃油套期保值覆盖率。套保部分不受油价波动影响，可降低风险但油价下跌时会产生机会成本"
        ) / 100

    # 计算结果 / Calculate Result
    result = model.evaluate(
        oil_increase=oil_increase,
        fare_adj=fare_adj,
        hedge_ratio=hedge_ratio
    )

    # 决策状态卡片 / Decision Status Card
    status_class = f"status-{result.status_type}"
    st.markdown(f"""
    <div class="metric-card {status_class}" style="margin: 1.5rem 0; padding: 2rem;">
        <h2 style="margin: 0; font-size: 1.5rem;">{result.status}</h2>
    </div>
    """, unsafe_allow_html=True)

    # 核心指标 / Core Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "有效燃油成本 (万亿₫)",
            f"{result.eff_fuel:.2f}",
            f"+{(result.eff_fuel/V_fuel_base - 1)*100:.1f}%",
            help="考虑油价冲击和套保后的燃油成本"
        )

    with col2:
        st.metric(
            "调整后收入 (万亿₫)",
            f"{result.adj_revenue:.2f}",
            f"{(result.adj_revenue/R_base - 1)*100:+.1f}%",
            help="考虑票价调整和需求变化后的预期收入"
        )

    with col3:
        st.metric(
            "总边际贡献 (万亿₫)",
            f"{result.total_cm:.2f}",
            f"{(result.total_cm/(R_base - V_other_base - V_fuel_base) - 1)*100:+.1f}%",
            help="调整后收入减去变动成本，用于覆盖固定成本"
        )

    with col4:
        profit_delta = f"{result.expected_pnl:+.2f}" if result.expected_pnl != 0 else "0.00"
        st.metric(
            "预期运营利润 (万亿₫)",
            profit_delta,
            delta_color="normal" if result.expected_pnl >= 0 else "inverse",
            help="总边际贡献减去固定成本，正值表示盈利"
        )

    # 航班削减建议 / Flight Cut Recommendation
    st.subheader("✂️ 航班调整建议")
    st.markdown(f"""
    <div class="info-box">
        <h3>建议航班削减比例：<strong>{result.cut_ratio*100:.1f}%</strong></h3>
        <p>预计保留航班数量：<strong>{121 * (1 - result.cut_ratio):.0f} 架次</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # 成本收入分解 / Cost Revenue Breakdown
    with st.expander("📋 查看详细成本收入分解"):
        breakdown = model.get_breakdown(result)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("收入分析")
            for k, v in breakdown["收入"].items():
                if isinstance(v, float):
                    st.metric(k, f"{v:.2f} 万亿₫")

        with col2:
            st.subheader("成本分析")
            st.write("**变动成本**")
            for k, v in breakdown["变动成本"].items():
                if isinstance(v, float):
                    st.metric(k, f"{v:.2f} 万亿₫")
            st.write("**固定成本**")
            for k, v in breakdown["固定成本"].items():
                st.metric(k, f"{v:.2f} 万亿₫")

# ==================== Tab 2: 多情景扫描 ====================
with tab2:
    st.header("📊 多情景批量扫描")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("扫描参数设置")
        oil_min = st.slider("油价涨幅最小值 (%)", 0, 100, 0) / 100
        oil_max = st.slider("油价涨幅最大值 (%)", 50, 200, 100) / 100
        oil_step = st.slider("油价涨幅步长 (%)", 5, 20, 10) / 100

    with col2:
        st.subheader("票价与套保选项")
        fare_options = st.multiselect(
            "选择票价调整选项 (%)",
            [0, 5, 10, 15, 20],
            default=[0, 5, 10]
        )
        hedge_options = st.multiselect(
            "选择套保比例选项 (%)",
            [0, 20, 30, 40, 50],
            default=[0, 30, 50]
        )

    if st.button("🚀 开始扫描", type="primary"):
        with st.spinner("正在计算..."):
            oil_range = np.arange(oil_min, oil_max + oil_step, oil_step)
            fare_range = [f/100 for f in fare_options]
            hedge_range = [h/100 for h in hedge_options]

            df = model.scenario_sweep(oil_range, fare_range, hedge_range)

            st.success(f"✅ 扫描完成！共计算 {len(df)} 种情景")

            # 数据表格 / Data Table
            st.subheader("📋 情景分析结果")
            st.dataframe(
                df.round(2),
                use_container_width=True,
                height=300
            )

            # 下载按钮 / Download Button
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 下载CSV文件",
                data=csv,
                file_name="vietjet_oil_shock_scenarios.csv",
                mime="text/csv"
            )

            # 统计摘要 / Statistical Summary
            st.subheader("📈 统计摘要")
            st.info("""
            **状态说明**
            - ✅ **健康**：边际贡献 ≥ 固定成本，无需削减航班
            - ⚠️ **承压**：0 < 边际贡献 < 固定成本，建议部分削减航班
            - 🚨 **危险**：边际贡献 ≤ 0，建议战略性停飞（保留10%骨架）
            """)
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("情景总数", len(df))

            with col2:
                healthy_count = (df["状态类型"] == "healthy").sum()
                st.metric("✅ 健康", f"{healthy_count} ({healthy_count/len(df)*100:.1f}%)")

            with col3:
                warning_count = (df["状态类型"] == "warning").sum()
                st.metric("⚠️ 承压", f"{warning_count} ({warning_count/len(df)*100:.1f}%)")

            with col4:
                critical_count = (df["状态类型"] == "critical").sum()
                st.metric("🚨 危险", f"{critical_count} ({critical_count/len(df)*100:.1f}%)")

# ==================== Tab 3: 可视化分析 ====================
with tab3:
    st.header("📈 可视化分析图表")

    viz_type = st.selectbox(
        "选择图表类型",
        ["利润热力图", "航班削减热力图", "状态分布图", "边际贡献趋势图", "三维决策曲面"]
    )

    # 生成演示数据 / Generate demo data
    oil_range = np.arange(0.0, 1.1, 0.1)
    fare_range = [0.0, 0.05, 0.10]
    hedge_range = [0.0, 0.3, 0.5]
    df = model.scenario_sweep(oil_range, fare_range, hedge_range)

    if viz_type == "利润热力图":
        st.subheader("📊 预期运营利润热力图")

        # 创建透视表 / Create pivot table
        pivot_df = df[df["套保比例"] == 0.3].pivot(
            index="油价涨幅",
            columns="票价调整",
            values="预期利润"
        )

        fig = px.imshow(
            pivot_df,
            labels=dict(x="票价调整", y="油价涨幅", color="预期利润(万亿₫)"),
            x=[f"{f*100:.0f}%" for f in pivot_df.columns],
            y=[f"{o*100:.0f}%" for o in pivot_df.index],
            color_continuous_scale="RdYlGn",
            aspect="auto"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "航班削减热力图":
        st.subheader("✂️ 建议航班削减比例热力图")

        pivot_df = df[df["套保比例"] == 0.3].pivot(
            index="油价涨幅",
            columns="票价调整",
            values="航班削减比例"
        )

        fig = px.imshow(
            pivot_df * 100,
            labels=dict(x="票价调整", y="油价涨幅", color="削减比例(%)"),
            x=[f"{f*100:.0f}%" for f in pivot_df.columns],
            y=[f"{o*100:.0f}%" for o in pivot_df.index],
            color_continuous_scale="Reds",
            aspect="auto"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "状态分布图":
        st.subheader("🎯 决策状态分布")

        status_count = df["状态类型"].value_counts().reset_index()
        status_count.columns = ["状态类型", "数量"]

        # 添加中文标签
        status_map = {"healthy": "✅ 健康", "warning": "⚠️ 承压", "critical": "🚨 危险"}
        status_count["状态名称"] = status_count["状态类型"].map(status_map)

        color_map = {"healthy": "#1dd1a1", "warning": "#feca57", "critical": "#ff6b6b"}

        fig = px.bar(
            status_count,
            x="状态名称",
            y="数量",
            color="状态类型",
            color_discrete_map=color_map,
            title="各状态类型情景数量分布"
        )
        fig.update_layout(showlegend=False, xaxis_title="决策状态")
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "边际贡献趋势图":
        st.subheader("📈 边际贡献 vs 油价涨幅")

        fig = go.Figure()

        for fare in fare_range:
            for hedge in hedge_range:
                df_filtered = df[
                    (df["票价调整"] == fare) &
                    (df["套保比例"] == hedge)
                ]

                label = f"票价+{fare*100:.0f}%, 套保{hedge*100:.0f}%"
                fig.add_trace(go.Scatter(
                    x=df_filtered["油价涨幅"] * 100,
                    y=df_filtered["总边际贡献"],
                    mode="lines+markers",
                    name=label,
                    line=dict(width=2)
                ))

        # 添加固定成本参考线 / Add fixed cost reference line
        fig.add_hline(
            y=FC,
            line_dash="dash",
            line_color="red",
            annotation_text="固定成本线"
        )
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray",
            annotation_text="盈亏平衡线"
        )

        fig.update_layout(
            xaxis_title="油价涨幅 (%)",
            yaxis_title="总边际贡献 (万亿₫)",
            height=500,
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "三维决策曲面":
        st.subheader("🎨 三维决策曲面 (套保30%)")

        df_filtered = df[df["套保比例"] == 0.3]

        fig = go.Figure(data=[go.Surface(
            x=df_filtered["票价调整"].unique() * 100,
            y=df_filtered["油价涨幅"].unique() * 100,
            z=df_filtered["预期利润"].values.reshape(
                len(df_filtered["票价涨幅"].unique()),
                len(df_filtered["油价涨幅"].unique())
            ).T,
            colorscale="RdYlGn",
            colorbar=dict(title="预期利润(万亿₫)")
        )])

        fig.update_layout(
            scene=dict(
                xaxis_title="票价调整 (%)",
                yaxis_title="油价涨幅 (%)",
                zaxis_title="预期利润(万亿₫)"
            ),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== Tab 4: 模型配置 ====================
with tab4:
    st.header("🔧 模型配置信息")

    st.subheader("当前配置参数")

    config_summary = model.get_config_summary()

    col1, col2 = st.columns(2)

    with col1:
        st.write("**收入与成本参数**")
        for k, v in config_summary.items():
            if "弹性" not in k and "机队" not in k:
                st.metric(k, f"{v}")

    with col2:
        st.write("**运营参数**")
        st.metric("机队规模", f"{config_summary['机队规模(架)']} 架")
        st.metric("需求价格弹性", f"{config_summary['需求价格弹性']}")

    st.subheader("📖 模型说明")

    st.markdown("""
    ### 决策状态分类

    | 状态 | 条件 | 说明 | 建议 |
    |------|------|------|------|
    | 🚨 **危险** | 边际贡献 ≤ 0 | 单班边际贡献为负，飞一班亏一班 | 战略性停飞，保留10%骨架 |
    | ⚠️ **承压** | 0 < 边际贡献 < 固定成本 | 单班贡献为正，但无法覆盖全部固定成本 | 保核心网络，压降低效边缘航班 |
    | ✅ **健康** | 边际贡献 ≥ 固定成本 | 边际贡献完全覆盖固定成本 | 无需砍航班，可优化排班提效 |

    ### 关键公式

    - **有效燃油成本** = 基础燃油成本 × (1 + 油价涨幅 × (1 - 套保比例))
    - **需求因子** = 1 + 票价调整 × 需求弹性（弹性=-0.8）
    - **调整后收入** = 基础收入 × (1 + 票价调整) × 需求因子
    - **总边际贡献** = 调整后收入 - 其他变动成本 - 有效燃油成本
    - **预期运营利润** = 总边际贡献 - 固定成本

    ### ⚠️ 使用提醒

    - 本模型为简化分析工具，实际决策需考虑更多因素
    - 砍航班可能扩大账面亏损，但可缓解短期现金流压力
    - 套保具有双刃剑效应，油价下跌时可能产生机会成本
    - 国际航线受双边协定约束，需考虑合规性风险
    """)

# 页脚 / Footer
st.markdown("""
---
<center>
<small>越捷航空油价冲击财务决策模型 v1.0 | 基于2025经审计财报数据</small>
</center>
""", unsafe_allow_html=True)
