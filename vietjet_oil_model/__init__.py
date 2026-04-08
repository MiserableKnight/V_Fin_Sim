"""越捷航空油价冲击财务决策模型 / VietJet Air Oil Shock Financial Decision Model"""

from .core_model import VietJetOilShockModel, DecisionResult
from .config_loader import ModelConfig, load_config

__all__ = ["VietJetOilShockModel", "ModelConfig", "load_config", "DecisionResult"]
__version__ = "1.1.0"
