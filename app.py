# -*- coding: utf-8 -*-
"""
越捷航空油价冲击财务决策模型 - 主应用入口
VietJet Air Oil Shock Financial Decision Model - Main App Entry

运行方式 / Run: streamlit run app.py

模块化架构：
- frontend/config.py: 页面配置和CSS
- frontend/components/: 可复用UI组件
- frontend/tabs/: 各标签页渲染逻辑
"""

import streamlit as st

from vietjet_oil_model import VietJetOilShockModel, ModelConfig
from frontend import APPLE_CSS, get_page_config, get_hero_html, get_footer_html
from frontend.components.forms import render_sidebar_config
from frontend.tabs import (
    render_smart_decision_tab,
    render_scenario_scan_tab,
    render_visualization_tab,
    render_model_info_tab
)

# ============================================
# 页面配置 / Page Config
# ============================================
page_config = get_page_config()
st.set_page_config(**page_config)

# ============================================
# 加载CSS样式 / Load CSS
# ============================================
st.markdown(APPLE_CSS, unsafe_allow_html=True)

# ============================================
# HERO SECTION / 英雄区域
# ============================================
st.markdown(get_hero_html(), unsafe_allow_html=True)

# ============================================
# SIDEBAR / 侧边栏配置
# ============================================
config_params = render_sidebar_config()

# ============================================
# MODEL INITIALIZATION / 模型初始化
# ============================================
config = ModelConfig(
    R_base=config_params["R_base"],
    V_fuel_base=config_params["V_fuel_base"],
    V_other_base=config_params["V_other_base"],
    FC=config_params["FC"],
    demand_elasticity=config_params["demand_elasticity"],
    network_preserve=config_params["network_preserve"]
)
model = VietJetOilShockModel(config)

# ============================================
# TABS / 标签页
# ============================================
tab1, tab2, tab3, tab4 = st.tabs([
    " 📊  智能决策",
    " 📈  情景扫描",
    " 🎨  可视化",
    " ⚙️  模型说明"
])

# ==================== TAB 1: 智能决策 ====================
with tab1:
    render_smart_decision_tab(model)

# ==================== TAB 2: 情景扫描 ====================
with tab2:
    render_scenario_scan_tab(model)

# ==================== TAB 3: 可视化 ====================
with tab3:
    render_visualization_tab(model)

# ==================== TAB 4: 模型说明 ====================
with tab4:
    render_model_info_tab(model)

# ============================================
# FOOTER / 页脚
# ============================================
st.markdown(get_footer_html(), unsafe_allow_html=True)
