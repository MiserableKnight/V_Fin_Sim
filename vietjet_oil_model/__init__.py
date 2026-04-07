"""越捷航空油价冲击财务决策模型 / VietJet Air Oil Shock Financial Decision Model"""

from .core_model import (
    VietJetOilShockModel,
    ModelConfig,
    DecisionResult
)

__all__ = ["VietJetOilShockModel", "ModelConfig", "DecisionResult"]
__version__ = "1.0.0"
