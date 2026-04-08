# 模型配置说明

## 配置文件位置

`config/model_config.yaml` - 所有可调参数的统一配置文件

## 使用方式

### 方式1: 使用默认配置（推荐）

直接使用，会自动加载 `config/model_config.yaml`：

```python
from vietjet_oil_model import VietJetOilShockModel

model = VietJetOilShockModel()
```

### 方式2: 使用自定义 YAML 文件

```python
model = VietJetOilShockModel(config_path="my_config.yaml")
```

### 方式3: 代码中直接指定参数

```python
from vietjet_oil_model import ModelConfig

config = ModelConfig(
    R_base=70.0,              # 调整基础收入
    V_fuel_base=25.0,          # 调整燃油成本
    demand_elasticity=-0.9     # 调整需求弹性
)
model = VietJetOilShockModel(config=config)
```

## 参数说明

### 财务参数 (financial)
| 参数 | 说明 | 默认值 |
|------|------|--------|
| R_base | 基础运营收入（万亿₫） | 64.94 |
| V_fuel_base | 燃油成本（万亿₫） | 24.70 |
| V_other_base | 其他变动成本（万亿₫） | 22.70 |
| FC | 固定成本（万亿₫） | 19.06 |
| fleet_size | 机队规模（架） | 121 |

### 需求参数 (demand)
| 参数 | 说明 | 默认值 |
|------|------|--------|
| elasticity | 需求价格弹性 | -0.8 |
| demand_floor | 需求因子下限 | 0.3 |

### 约束参数 (constraints)
| 参数 | 说明 | 默认值 |
|------|------|--------|
| fare_adjust_max | 票价最大上调幅度 | 0.30 (30%) |
| hedge_ratio_max | 套保比例上限 | 0.60 (60%) |
| network_preserve | 网络保留权重 | 0.25 |

### 阈值参数 (threshold)
| 参数 | 说明 | 默认值 |
|------|------|--------|
| stage_monitor_threshold | 监控阶段触发系数 | 0.60 |
| stage_fare_threshold | 票价阶段触发系数 | 0.85 |
| stage_hedge_threshold | 套保阶段触发系数 | 1.00 |
