# -*- coding: utf-8 -*-
"""
前端配置模块
Frontend Configuration Module

包含页面配置、Apple 设计系统 CSS 样式
"""

# ============================================
# APPLE DESIGN SYSTEM CSS / 苹果设计系统样式
# ============================================
APPLE_CSS = """
<style>
    /* ============================================
       APPLE DESIGN SYSTEM - 核心样式
       ============================================ */

    /* 全局字体 - SF Pro */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --apple-bg: #FFFFFF;
        --apple-bg-secondary: #F5F5F7;
        --apple-text: #1D1D1F;
        --apple-text-secondary: #86868B;
        --apple-accent: #0071E3;
        --apple-accent-hover: #0077ED;
        --apple-border: rgba(0, 0, 0, 0.08);
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.08);
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
    }

    /* 基础重置 */
    .main {
        background: var(--apple-bg) !important;
    }

    /* 字体系统 */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Helvetica Neue", sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }

    /* 隐藏默认菜单 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: visible; }

    /* 侧边栏样式 */
    .css-1d391kg {
        background: var(--apple-bg-secondary) !important;
        border-right: 1px solid var(--apple-border) !important;
    }

    /* ============================================
       HERO HEADER / 英雄标题区
       ============================================ */
    .apple-hero {
        text-align: center;
        padding: 80px 20px 60px;
        background: linear-gradient(180deg, #FFFFFF 0%, #F5F5F7 100%);
    }

    .apple-hero-title {
        font-size: clamp(48px, 8vw, 72px);
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--apple-text);
        margin-bottom: 16px;
        line-height: 1.1;
    }

    .apple-hero-subtitle {
        font-size: clamp(20px, 3vw, 24px);
        font-weight: 400;
        letter-spacing: -0.01em;
        color: var(--apple-text-secondary);
        max-width: 680px;
        margin: 0 auto 32px;
        line-height: 1.4;
    }

    .apple-hero-badge {
        display: inline-block;
        padding: 8px 16px;
        background: rgba(0, 113, 227, 0.1);
        color: var(--apple-accent);
        font-size: 14px;
        font-weight: 600;
        border-radius: 20px;
        margin-bottom: 24px;
        letter-spacing: 0.02em;
    }

    /* ============================================
       METRIC CARDS / 指标卡片
       ============================================ */
    .apple-metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 40px 0;
    }

    .apple-metric-card {
        background: var(--apple-bg);
        border: 1px solid var(--apple-border);
        border-radius: var(--radius-lg);
        padding: 28px 24px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-sm);
    }

    .apple-metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--apple-accent);
    }

    .apple-metric-label {
        font-size: 13px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--apple-text-secondary);
        margin-bottom: 12px;
    }

    .apple-metric-value {
        font-size: 36px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--apple-text);
        line-height: 1;
        margin-bottom: 8px;
    }

    .apple-metric-change {
        font-size: 14px;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    .apple-metric-change.positive {
        color: #34C759;
    }

    .apple-metric-change.negative {
        color: #FF3B30;
    }

    /* ============================================
       THRESHOLD CARDS / 阈值卡片
       ============================================ */
    .apple-threshold-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
        margin: 48px 0;
    }

    .apple-threshold-card {
        background: var(--apple-bg-secondary);
        border-radius: var(--radius-xl);
        padding: 32px 24px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .apple-threshold-card:hover {
        background: var(--apple-bg);
        box-shadow: var(--shadow-md);
    }

    .apple-threshold-card .icon {
        font-size: 32px;
        margin-bottom: 16px;
    }

    .apple-threshold-value {
        font-size: 48px;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--apple-accent);
        line-height: 1;
        margin-bottom: 8px;
    }

    .apple-threshold-label {
        font-size: 14px;
        font-weight: 500;
        color: var(--apple-text-secondary);
        letter-spacing: 0.02em;
    }

    /* ============================================
       DECISION PATH / 决策路径
       ============================================ */
    .apple-decision-path {
        margin: 48px 0;
    }

    .apple-decision-step {
        display: flex;
        align-items: flex-start;
        gap: 20px;
        padding: 24px;
        background: var(--apple-bg);
        border: 1px solid var(--apple-border);
        border-radius: var(--radius-lg);
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }

    .apple-decision-step:hover {
        box-shadow: var(--shadow-md);
        transform: translateX(8px);
    }

    .apple-step-indicator {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
        font-weight: 600;
    }

    .apple-step-indicator.low {
        background: rgba(52, 199, 89, 0.15);
        color: #34C759;
    }

    .apple-step-indicator.medium {
        background: rgba(255, 149, 0, 0.15);
        color: #FF9500;
    }

    .apple-step-indicator.high {
        background: rgba(255, 159, 10, 0.15);
        color: #FF9F0A;
    }

    .apple-step-indicator.critical {
        background: rgba(255, 59, 48, 0.15);
        color: #FF3B30;
    }

    .apple-step-content h4 {
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 8px 0;
        color: var(--apple-text);
        letter-spacing: -0.01em;
    }

    .apple-step-content p {
        font-size: 15px;
        color: var(--apple-text-secondary);
        margin: 4px 0 0 0;
        line-height: 1.5;
    }

    /* ============================================
       STATUS BADGE / 状态徽章
       ============================================ */
    .apple-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        border-radius: 24px;
        font-size: 15px;
        font-weight: 500;
        letter-spacing: 0.01em;
    }

    .apple-status-healthy {
        background: rgba(52, 199, 89, 0.12);
        color: #34C759;
    }

    .apple-status-warning {
        background: rgba(255, 149, 0, 0.12);
        color: #FF9500;
    }

    .apple-status-critical {
        background: rgba(255, 59, 48, 0.12);
        color: #FF3B30;
    }

    /* ============================================
       INFO BOX / 信息框
       ============================================ */
    .apple-info-box {
        padding: 20px 24px;
        background: var(--apple-bg-secondary);
        border-left: 3px solid var(--apple-accent);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        font-size: 15px;
        line-height: 1.6;
        color: var(--apple-text);
    }

    .apple-info-box strong {
        font-weight: 600;
        color: var(--apple-text);
    }

    /* ============================================
       SECTION STYLES / 区域样式
       ============================================ */
    .apple-section {
        padding: 60px 0;
        border-bottom: 1px solid var(--apple-border);
    }

    .apple-section-title {
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--apple-text);
        margin-bottom: 12px;
    }

    .apple-section-description {
        font-size: 17px;
        color: var(--apple-text-secondary);
        line-height: 1.5;
        margin-bottom: 32px;
        max-width: 720px;
    }

    /* ============================================
       BUTTON STYLES / 按钮样式
       ============================================ */
    .stButton > button {
        background: var(--apple-accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 12px 28px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: var(--apple-accent-hover) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3) !important;
    }

    /* ============================================
       TAB STYLES / 标签页样式
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 12px 24px;
        font-size: 15px;
        font-weight: 500;
        color: var(--apple-text-secondary);
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--apple-bg-secondary);
        color: var(--apple-text);
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--apple-bg-secondary);
    }

    /* ============================================
       SLIDER STYLES / 滑块样式
       ============================================ */
    .stSlider [data-testid="stSlider"] {
        background: transparent;
    }

    /* ============================================
       EXPANDER STYLES / 折叠面板样式
       ============================================ */
    .streamlit-expanderHeader {
        background: var(--apple-bg-secondary) !important;
        border: 1px solid var(--apple-border) !important;
        border-radius: var(--radius-md) !important;
        padding: 16px 20px !important;
        font-weight: 500 !important;
    }

    .streamlit-expanderContent {
        background: var(--apple-bg) !important;
        border: 1px solid var(--apple-border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
        padding: 20px !important;
    }

    /* ============================================
       DATAFRAME STYLES / 数据表格样式
       ============================================ */
    .stDataFrame {
        border: 1px solid var(--apple-border);
        border-radius: var(--radius-lg);
        overflow: hidden;
    }

    /* ============================================
       RESPONSIVE / 响应式设计
       ============================================ */
    @media (max-width: 768px) {
        .apple-threshold-container {
            grid-template-columns: 1fr;
        }

        .apple-hero-title {
            font-size: 40px;
        }

        .apple-metric-container {
            grid-template-columns: 1fr;
        }
    }
</style>
"""


def get_page_config():
    """返回 Streamlit 页面配置"""
    return {
        "page_title": "VietJet Oil Shock Model",
        "page_icon": "✈️",
        "layout": "wide",
        "initial_sidebar_state": "collapsed"
    }


def get_hero_html():
    """返回英雄区域的 HTML"""
    return """
    <div class="apple-hero">
        <div class="apple-hero-badge">Financial Decision Model</div>
        <h1 class="apple-hero-title">VietJet Oil Shock</h1>
        <p class="apple-hero-subtitle">
            基于财报校准的智能决策系统，助力油价冲击下的运营优化
        </p>
    </div>
    """


def get_footer_html():
    """返回页脚 HTML"""
    return """
    ---
    <div style="text-align: center; padding: 40px 20px; color: var(--apple-text-secondary); font-size: 14px;">
        <p>VietJet Air Oil Shock Financial Decision Model v1.0</p>
        <p style="margin-top: 8px;">基于2025经审计财报数据 · Apple Design Style</p>
    </div>
    """
