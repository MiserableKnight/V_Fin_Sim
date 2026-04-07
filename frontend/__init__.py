# -*- coding: utf-8 -*-
"""
前端模块
Frontend Module

包含 Streamlit 应用的所有前端组件和标签页
"""

from .config import (
    APPLE_CSS,
    get_page_config,
    get_hero_html,
    get_footer_html
)

__all__ = [
    "APPLE_CSS",
    "get_page_config",
    "get_hero_html",
    "get_footer_html",
]
