# -*- coding: utf-8 -*-
"""
图表组件
Chart Components

包含所有可视化图表组件
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def get_apple_layout():
    """返回 Apple 风格的图表布局配置"""
    return {
        'font': {'family': '-apple-system, SF Pro Display, sans-serif'},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'margin': dict(l=20, r=20, t=40, b=20),
        'xaxis': {'gridcolor': 'rgba(0,0,0,0.05)'},
        'yaxis': {'gridcolor': 'rgba(0,0,0,0.05)'}
    }


def render_profit_heatmap(df, hedge_ratio=0.3):
    """
    渲染利润热力图

    Args:
        df: 情景扫描数据
        hedge_ratio: 套保比例过滤值
    """
    pivot_df = df[df["套保比例"] == hedge_ratio].pivot(
        index="油价涨幅",
        columns="票价调整",
        values="预期利润"
    )

    fig = px.imshow(
        pivot_df,
        labels=dict(x="票价调整", y="油价涨幅", color="预期利润(万亿₫)"),
        x=[f"{f*100:.0f}%" for f in pivot_df.columns],
        y=[f"{f*100:.0f}%" for f in pivot_df.index],
        color_continuous_scale=["#FF3B30", "#FF9500", "#FFCC00", "#34C759"],
        aspect="auto"
    )
    fig.update_layout(height=500, **get_apple_layout())
    st.plotly_chart(fig, use_container_width=True)


def render_cut_ratio_heatmap(df, hedge_ratio=0.3):
    """
    渲染航班削减比例热力图

    Args:
        df: 情景扫描数据
        hedge_ratio: 套保比例过滤值
    """
    pivot_df = df[df["套保比例"] == hedge_ratio].pivot(
        index="油价涨幅",
        columns="票价调整",
        values="航班削减比例"
    )

    fig = px.imshow(
        pivot_df * 100,
        labels=dict(x="票价调整", y="油价涨幅", color="削减比例(%)"),
        x=[f"{f*100:.0f}%" for f in pivot_df.columns],
        y=[f"{f*100:.0f}%" for f in pivot_df.index],
        color_continuous_scale=["#34C759", "#FFCC00", "#FF9500", "#FF3B30"],
        aspect="auto"
    )
    fig.update_layout(height=500, **get_apple_layout())
    st.plotly_chart(fig, use_container_width=True)


def render_status_distribution(df):
    """
    渲染状态分布图

    Args:
        df: 情景扫描数据
    """
    status_count = df["状态类型"].value_counts().reset_index()
    status_count.columns = ["状态类型", "数量"]

    status_map = {"healthy": "✅ 健康", "warning": "⚠️ 承压", "critical": "🚨 危险"}
    status_count["状态名称"] = status_count["状态类型"].map(status_map)

    color_map = {"healthy": "#34C759", "warning": "#FF9500", "critical": "#FF3B30"}

    fig = px.bar(
        status_count,
        x="状态名称",
        y="数量",
        color="状态类型",
        color_discrete_map=color_map
    )
    fig.update_layout(showlegend=False, xaxis_title="", height=400, **get_apple_layout())
    st.plotly_chart(fig, use_container_width=True)


def render_cm_trend(df, FC, fare_range, hedge_range):
    """
    渲染边际贡献趋势图

    Args:
        df: 情景扫描数据
        FC: 固定成本
        fare_range: 票价范围
        hedge_range: 套保范围
    """
    fig = go.Figure()

    colors = ["#0071E3", "#34C759", "#FF9500", "#FF3B30"]
    color_idx = 0

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
                line=dict(width=2.5, color=colors[color_idx % len(colors)]),
                marker=dict(size=6)
            ))
            color_idx += 1

    fig.add_hline(
        y=FC,
        line_dash="dash",
        line_color="#FF3B30",
        annotation_text="固定成本线"
    )
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#86868B",
        annotation_text="盈亏平衡线"
    )

    fig.update_layout(
        xaxis_title="油价涨幅 (%)",
        yaxis_title="总边际贡献 (万亿₫)",
        height=500,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.02),
        **get_apple_layout()
    )
    st.plotly_chart(fig, use_container_width=True)


def render_3d_surface(df, hedge_ratio=0.3):
    """
    渲染三维决策曲面

    Args:
        df: 情景扫描数据
        hedge_ratio: 套保比例过滤值
    """
    df_filtered = df[df["套保比例"] == hedge_ratio]

    fig = go.Figure(data=[go.Surface(
        x=df_filtered["票价调整"].unique() * 100,
        y=df_filtered["油价涨幅"].unique() * 100,
        z=df_filtered["预期利润"].values.reshape(
            len(df_filtered["票价调整"].unique()),
            len(df_filtered["油价涨幅"].unique())
        ).T,
        colorscale=[
            [0, "#FF3B30"],
            [0.25, "#FF9500"],
            [0.5, "#FFCC00"],
            [0.75, "#34C759"],
            [1, "#30D158"]
        ],
        colorbar=dict(title="预期利润(万亿₫)")
    )])

    fig.update_layout(
        scene=dict(
            xaxis_title="票价调整 (%)",
            yaxis_title="油价涨幅 (%)",
            zaxis_title="预期利润(万亿₫)",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        height=600,
        **get_apple_layout()
    )
    st.plotly_chart(fig, use_container_width=True)
