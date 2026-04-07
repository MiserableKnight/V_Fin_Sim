# -*- coding: utf-8 -*-
"""
智能决策标签页
Smart Decision Tab

Phase 1 阈值计算与决策路径展示
"""

import streamlit as st

from vietjet_oil_model.core_model import ModelConfig
from ..components.cards import (
    render_threshold_cards,
    render_metric_cards,
    render_status_badge,
    render_decision_path
)
from ..components.forms import (
    render_oil_input,
    render_decision_constraints,
    render_manual_inputs
)


def render_smart_decision_tab(model: ModelConfig):
    """
    渲染智能决策标签页

    Args:
        model: VietJetOilShockModel 实例
    """
    st.markdown('<h2 class="apple-section-title">智能决策分析</h2>', unsafe_allow_html=True)
    st.markdown('<p class="apple-section-description">输入油价涨幅，系统自动计算最优响应策略</p>', unsafe_allow_html=True)

    col_mode, col_display = st.columns([3, 1])
    with col_mode:
        auto_mode = st.checkbox("🤖 启用智能决策模式", value=True)
    with col_display:
        show_details = st.checkbox("显示详情", value=False)

    # 油价输入
    oil_increase_input = render_oil_input()

    if auto_mode:
        constraints = render_decision_constraints()

        try:
            threshold_result = model.get_thresholds(
                oil_increase=oil_increase_input,
                fare_cap=constraints["fare_cap"],
                hedge_cap=constraints["hedge_cap"],
                verbose=show_details
            )

            # 当前状态
            tc = model.threshold_calculator.threshold_config
            urgency_info = tc.get_urgency_info(threshold_result.current_stage)
            stage_name = tc.get_stage_name(threshold_result.current_stage)

            status_class = f"apple-status-{urgency_info['level']}" if urgency_info['level'] in ['healthy', 'warning', 'critical'] else 'apple-status-warning'

            st.markdown(f"""
            <div class="apple-info-box" style="text-align: center; margin: 32px 0;">
                <span class="apple-status-badge {status_class}">
                    {urgency_info['icon']} 当前状态: 阶段 {threshold_result.current_stage} — {stage_name}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # 三阈值卡片
            render_threshold_cards(threshold_result)

            # 决策路径
            st.markdown('<h3 style="font-size: 24px; font-weight: 600; margin: 48px 0 24px;">📈 决策响应路径</h3>', unsafe_allow_html=True)
            render_decision_path(threshold_result.decision_path)

            # 推荐动作预览
            if threshold_result.decision_path:
                recommended = threshold_result.decision_path[0]
                preview_result = model.evaluate(
                    oil_increase_input,
                    recommended['recommended_fare'],
                    recommended['recommended_hedge']
                )

                st.markdown('<h3 style="font-size: 24px; font-weight: 600; margin: 48px 0 24px;">🎬 推荐动作预览</h3>', unsafe_allow_html=True)

                render_metric_cards([
                    {
                        "label": "推荐票价调整",
                        "value": f"+{recommended['recommended_fare']*100:.1f}%"
                    },
                    {
                        "label": "推荐套保比例",
                        "value": f"{recommended['recommended_hedge']*100:.1f}%"
                    },
                    {
                        "label": "预期边际贡献",
                        "value": f"{preview_result.total_cm:,.1f}",
                        "unit": "万亿₫"
                    }
                ])

            # 预警信息
            if threshold_result.warnings:
                st.markdown('<h3 style="font-size: 20px; font-weight: 600; margin: 32px 0 16px;">⚠️ 预警信息</h3>', unsafe_allow_html=True)
                for warning in threshold_result.warnings:
                    st.warning(warning)

            # 详细计算过程
            if show_details:
                with st.expander("🔍 详细计算过程"):
                    st.json({
                        "输入参数": {
                            "油价涨幅": f"{oil_increase_input*100:.1f}%",
                            "票价上限": f"{constraints['fare_cap']*100:.1f}%",
                            "套保上限": f"{constraints['hedge_cap']*100:.1f}%"
                        },
                        "计算结果": {
                            "票价盈亏平衡": f"{threshold_result.fare_breakeven*100:.2f}%",
                            "油价容忍度": f"{threshold_result.oil_tolerance*100:.2f}%",
                            "套保触发线": f"{threshold_result.hedge_trigger*100:.2f}%"
                        },
                        "决策路径": threshold_result.decision_path
                    })

        except ValueError as e:
            st.error(f"❌ 参数错误: {str(e)}")
        except Exception as e:
            st.error(f"❌ 计算失败: {str(e)}")

    else:
        st.info("👆 关闭智能推荐以使用手动模式")

        inputs = render_manual_inputs()
        result = model.evaluate(
            oil_increase=inputs["oil_increase"],
            fare_adj=inputs["fare_adj"],
            hedge_ratio=inputs["hedge_ratio"]
        )

        # 结果展示
        render_status_badge(result.status, result.status_type)

        # 获取基础配置用于计算变化率
        config = model.get_config_summary()
        V_fuel_base = config.get("燃油成本(万亿₫)", 24.70)
        R_base = config.get("基础收入(万亿₫)", 64.94)

        render_metric_cards([
            {
                "label": "有效燃油成本",
                "value": f"{result.eff_fuel:.2f}",
                "unit": "万亿₫",
                "change": (result.eff_fuel/V_fuel_base - 1)*100 if result.eff_fuel != V_fuel_base else None,
                "change_type": "positive" if result.eff_fuel < V_fuel_base else "negative"
            },
            {
                "label": "调整后收入",
                "value": f"{result.adj_revenue:.2f}",
                "unit": "万亿₫",
                "change": (result.adj_revenue/R_base - 1)*100 if result.adj_revenue != R_base else None,
                "change_type": "positive" if result.adj_revenue > R_base else "negative"
            },
            {
                "label": "总边际贡献",
                "value": f"{result.total_cm:.2f}",
                "unit": "万亿₫"
            },
            {
                "label": "预期运营利润",
                "value": f"{result.expected_pnl:+.2f}",
                "unit": "万亿₫"
            }
        ])

        st.markdown(f"""
        <div class="apple-info-box" style="margin-top: 32px;">
            <strong>✂️ 航班调整建议</strong><br>
            建议航班削减比例: <strong>{result.cut_ratio*100:.1f}%</strong><br>
            预计保留航班数量: <strong>{121 * (1 - result.cut_ratio):.0f}</strong> 架次
        </div>
        """, unsafe_allow_html=True)
