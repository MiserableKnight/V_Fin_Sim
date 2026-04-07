"""越捷航空油价冲击财务决策模型 - 安装配置"""

from setuptools import setup, find_packages

setup(
    name="vietjet-oil-model",
    version="1.0.0",
    description="越捷航空油价冲击财务决策模型 / VietJet Air Oil Shock Financial Decision Model",
    author="V_Fin_Sim Team",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.17.0",
        "openpyxl>=3.1.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "vietjet-model=streamlit.cli.main:main",
        ],
    },
)
