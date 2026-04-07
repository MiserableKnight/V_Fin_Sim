# ✈️ 越捷航空油价冲击财务决策模型

VietJet Air Oil Shock Financial Decision Model

基于2025经审计财报附注28/36/31校准的短期油价冲击下的航班优化决策模型

---

## 🧮 数学模型

### 问题定义

面对油价外生冲击，航空公司需要回答三个核心问题：

1. **盈利性判断**：当前运营条件下能否实现盈利？
2. **边际决策**：是否应该削减航班？削减多少？
3. **策略评估**：票价调整和套期保值如何影响决策？

### 模型假设

| 假设 | 说明 |
|------|------|
| 成本性态 | 成本按性态分为变动成本（随运量变化）和固定成本（不随运量变化） |
| 线性关系 | 变动成本与运量呈线性关系，固定成本在决策期内保持不变 |
| 需求弹性 | 客运需求对票价变化服从恒定价格弹性 |
| 套保效应 | 套期保值可锁定部分燃油成本，仅未覆盖部分受油价波动影响 |
| 网络效应 | 航班削减需保留最小网络骨架（默认25%）以维持枢纽运营 |

### 符号定义

#### 基础财务参数（财报校准值）

| 符号 | 含义 | 数值 | 数据来源 |
|------|------|------|----------|
| $R_{base}$ | 基础运营收入（剔除非航线主业收入） | 64.94 万亿₫ | 2025财报附注28 |
| $V_{fuel}$ | 基础燃油成本 | 24.70 万亿₫ | 2025财报附注36 |
| $V_{other}$ | 其他变动成本（外部服务费、变动人工、航路起降费等） | 22.70 万亿₫ | 2025财报附注36 |
| $FC$ | 固定成本（租赁费、折旧、固定人工、坏账等） | 19.06 万亿₫ | 2025财报附注36/31 |

#### 外生冲击变量（决策输入）

| 符号 | 含义 | 取值范围 | 示例 |
|------|------|----------|------|
| $\Delta P_{oil}$ | 油价涨幅 | $[-1, +\infty)$ | +40% 记为 0.4 |
| $\Delta P_{fare}$ | 票价调整幅度 | $[-1, +\infty)$ | +8% 记为 0.08 |
| $h$ | 燃油套期保值覆盖率 | $[0, 1]$ | 30% 套保记为 0.3 |

#### 模型参数

| 符号 | 含义 | 取值 | 依据 |
|------|------|------|------|
| $\varepsilon$ | 需求价格弹性 | -0.8 | 行业研究文献 |
| $\alpha$ | 网络骨架保留权重 | 0.25 | 航空运营实践 |

#### 中间变量与决策输出

| 符号 | 含义 | 计算方式 |
|------|------|----------|
| $C_{fuel}$ | 有效燃油成本（考虑油价冲击和套保后） | 公式(1)计算 |
| $D$ | 需求因子（票价调整后的客流量变化） | 公式(2)计算 |
| $R_{adj}$ | 调整后收入（考虑票价和需求变化） | 公式(3)计算 |
| $CM$ | 总边际贡献（Contribution Margin） | 公式(4)计算 |
| $\pi$ | 预期运营利润 | 公式(5)计算 |
| $\gamma$ | 航班削减比例（建议削减的航班占比） | 决策逻辑计算 |

### 核心方程

#### 方程(1)：有效燃油成本

燃油成本受油价冲击和套期保值共同影响：

$$C_{fuel} = V_{fuel} \times \left[ 1 + \Delta P_{oil} \times (1 - h) \right]$$

**经济含义**：
- 套期保值覆盖比例为 $h$ 的燃油需求，这部分成本被锁定
- 仅 $(1-h)$ 部分暴露于油价波动
- 当油价上涨时（$\Delta P_{oil} > 0$），套保可降低燃油成本增长

**示例**：基础燃油成本 24.70 万亿₫，油价上涨 40%，套保比例 30%
$$C_{fuel} = 24.70 \times [1 + 0.4 \times (1 - 0.3)] = 24.70 \times 1.28 = 31.62 \text{ 万亿₫}$$

---

#### 方程(2)：需求因子

票价调整通过需求弹性影响客流量：

$$D = 1 + \Delta P_{fare} \times \varepsilon$$

**约束条件**：$D \geq 0.3$（最低保留30%需求，防止极端预测导致不合理结果）

**经济含义**：
- 需求价格弹性 $\varepsilon < 0$，表示价格上涨会导致需求下降
- $\varepsilon = -0.8$ 表示票价上涨1%，需求下降0.8%
- 需求因子 $D$ 代表调整后客流量占原客流量的比例

**示例**：票价上涨 8%，需求弹性 -0.8
$$D = 1 + 0.08 \times (-0.8) = 1 - 0.064 = 0.936$$
即客流量下降至原来的 93.6%

---

#### 方程(3)：调整后收入

收入受票价和需求的双重影响：

$$R_{adj} = R_{base} \times (1 + \Delta P_{fare}) \times D$$

将需求因子代入，得展开形式：

$$R_{adj} = R_{base} \times (1 + \Delta P_{fare}) \times (1 + \Delta P_{fare} \times \varepsilon)$$

**经济含义**：
- 票价调整有直接效应（$1 + \Delta P_{fare}$）和间接效应（需求因子 $D$）
- 票价上涨虽然提高单位收入，但会抑制需求，净效应取决于两者权衡

**示例**：基础收入 64.94 万亿₫，票价上涨 8%，需求因子 0.936
$$R_{adj} = 64.94 \times 1.08 \times 0.936 = 65.74 \text{ 万亿₫}$$

---

#### 方程(4)：总边际贡献（Contribution Margin）

$$CM = R_{adj} - V_{other} - C_{fuel}$$

**经济含义**：
- 边际贡献是每单位运量对覆盖固定成本的贡献
- $CM > 0$ 是继续运营的必要条件（边际贡献为正）
- $CM \geq FC$ 是实现盈利的充分条件（边际贡献覆盖全部固定成本）

**示例**：调整后收入 65.74 万亿₫，其他变动成本 22.70 万亿₫，有效燃油成本 31.62 万亿₫
$$CM = 65.74 - 22.70 - 31.62 = 11.42 \text{ 万亿₫}$$

---

#### 方程(5)：预期运营利润

$$\pi = CM - FC$$

**经济含义**：
- $\pi > 0$ 表示运营盈利
- $\pi < 0$ 表示运营亏损

**示例**：边际贡献 11.42 万亿₫，固定成本 19.06 万亿₫
$$\pi = 11.42 - 19.06 = -7.64 \text{ 万亿₫}$$
即预期运营亏损 7.64 万亿₫

---

### 三阶决策逻辑

模型根据边际贡献（$CM$）与固定成本（$FC$）的关系，将决策状态分为三阶：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        决策状态分类                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   状态一：运营健康              状态二：现金流承压        状态三：现金流毁灭 │
│   CM ≥ FC                      0 < CM < FC              CM ≤ 0      │
│ ┌─────────────┐            ┌─────────────┐         ┌─────────────┐  │
│ │             │            │             │         │             │  │
│ │    ✅       │            │    ⚠️       │         │    🚨       │  │
│ │             │            │             │         │             │  │
│ │  γ = 0%     │            │   γ = 动态  │         │   γ = 90%   │  │
│ │             │            │             │         │             │  │
│ │  无需削减   │            │  部分削减   │         │  战略性停飞 │  │
│ └─────────────┘            └─────────────┘         └─────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 状态一：运营健康（$CM \geq FC$）

**条件**：总边际贡献大于或等于固定成本

**决策**：无需削减航班
$$\gamma = 0$$

**经济直觉**：运营可产生正向现金流或盈亏平衡，应维持或扩大运力。

---

#### 状态二：现金流承压（$0 < CM < FC$）

**条件**：边际贡献为正，但无法覆盖全部固定成本

**决策**：部分削减航班，削减比例由以下公式确定：

**步骤1**：计算固定成本覆盖率
$$\text{覆盖率} = \frac{CM}{FC}$$

**步骤2**：考虑网络骨架保留权重，调整保留比例
$$\text{保留比例} = \frac{CM}{FC} \times (1 - \alpha) + \alpha$$

**步骤3**：计算航班削减比例
$$\gamma = \max(0.05, \min(0.80, 1 - \text{保留比例}))$$

**经济直觉**：
- $CM/FC$ 是固定成本覆盖率，理论上可维持该比例的运力
- 引入权重 $\alpha$ 保护网络骨架，防止过度削减破坏枢纽结构
- 削减比例限制在 [5%, 80%] 区间内，避免极端决策

**示例**：边际贡献 11.42 万亿₫，固定成本 19.06 万亿₫，$\alpha = 0.25$
$$\text{覆盖率} = \frac{11.42}{19.06} = 0.599$$
$$\text{保留比例} = 0.599 \times 0.75 + 0.25 = 0.699$$
$$\gamma = 1 - 0.699 = 0.301$$
即建议削减 30.1% 的航班

---

#### 状态三：现金流毁灭（$CM \leq 0$）

**条件**：单班边际贡献为负或为零

**决策**：战略性停飞，仅保留10%战略骨架
$$\gamma = 0.90$$

**经济直觉**：飞一班亏一班，停飞可最小化现金流损失。保留10%航班用于维持航线权、机场时刻等战略资源。

---

### Phase 1：阈值计算与决策路径

#### 阈值1：票价盈亏平衡点

定义：在无套保保护下，使边际贡献为0所需的票价调整幅度。

求解方程：
$$R_{base}(1+f)(1+\varepsilon f) - V_{other} - V_{fuel}(1+\Delta P_{oil}) = 0$$

使用数值方法（`scipy.optimize.fsolve`）求解 $f$。

#### 阈值2：最大可承受油价涨幅

在票价调整上限 $\Delta P_{fare}^{max}$ 和套保比例上限 $h_{max}$ 下，计算可承受的最大油价涨幅：

$$\Delta P_{oil}^{max} = \frac{R_{adj}^{max} - V_{other} - V_{fuel}}{V_{fuel}(1-h_{max})}$$

其中 $R_{adj}^{max} = R_{base} \times (1 + \Delta P_{fare}^{max}) \times (1 + \varepsilon \Delta P_{fare}^{max})$

#### 阈值3：触发削班的临界套保比例

在给定油价冲击和票价调整上限下，使边际贡献刚好覆盖固定成本所需的套保比例：

$$h^* = 1 - \frac{R_{adj}^{max} - V_{other} - V_{fuel} - FC}{V_{fuel} \times \Delta P_{oil}}$$

#### 四阶段决策路径

| 阶段 | 油价范围 | 响应动作 | 紧急程度 |
|------|----------|----------|----------|
| 1 | $\le 60\%$ 油价容忍上限 | 监控 | 🟢 低 |
| 2 | 60%~85% 油价容忍上限 | 票价上调 | 🟡 中 |
| 3 | 85%~100% 油价容忍上限 | 套保加仓 + 票价 | 🟠 高 |
| 4 | > 100% 油价容忍上限 | 削班启动 | 🔴 紧急 |

---

### Phase 2：约束型动作序列优化器

#### 优化目标

在给定约束下，按优先级依次优化三个决策变量：

$$\max_{\Delta P_{fare}, h, \gamma} \quad \pi(\Delta P_{fare}, h, \gamma)$$

**约束条件**：
- $0 \le \Delta P_{fare} \le \Delta P_{fare}^{max}$（票价上限）
- $0 \le h \le h_{max}$（套保上限）
- $0 \le \gamma \le 0.9$（削班比例上限）

#### 分层优化逻辑

**Step 1：票价寻优**

$$\max_{\Delta P_{fare}} CM(\Delta P_{fare}, h=0)$$

目标函数：
$$CM(\Delta P_{fare}) = R_{base}(1+\Delta P_{fare})(1+\varepsilon \Delta P_{fare}) - V_{other} - V_{fuel}(1+\Delta P_{oil})$$

**解析解**（梯度法）：
$$\frac{\partial CM}{\partial \Delta P_{fare}} = R_{base}[(1+\varepsilon) + 2\varepsilon \Delta P_{fare}] = 0$$

$$\Delta P_{fare}^* = -\frac{1+\varepsilon}{2\varepsilon}$$

**Step 2：套保寻优**

若 $CM(\Delta P_{fare}^*) < FC$，计算所需套保比例：

$$h^* = 1 - \frac{R_{adj} - V_{other} - V_{fuel} - FC}{V_{fuel} \times \Delta P_{oil}}$$

**Step 3：削班判断**

若 $CM(\Delta P_{fare}^*, h^*) < FC$，按三阶逻辑确定削减比例。

---

### 关键推论

#### 推论1：套期保值的影响边界

套保对边际贡献的边际影响为：

$$\frac{\partial CM}{\partial h} = V_{fuel} \times \Delta P_{oil}$$

**分析**：
- 当 $\Delta P_{oil} > 0$（油价上涨）时，$\frac{\partial CM}{\partial h} > 0$，套保提高边际贡献
- 当 $\Delta P_{oil} < 0$（油价下跌）时，套保产生机会成本，反而降低边际贡献
- 套保的价值在于对冲油价上涨风险，但需承担油价下跌时的机会成本

---

#### 推论2：票价调整的盈亏平衡点

设套保 $h=0$，求解 $CM=0$ 时的票价调整幅度：

$$R_{base}(1+\Delta P_{fare})(1+\varepsilon \Delta P_{fare}) - V_{other} - V_{fuel}(1+\Delta P_{oil}) = 0$$

展开后得到关于 $\Delta P_{fare}$ 的一元二次方程：

$$R_{base} \varepsilon (\Delta P_{fare})^2 + R_{base}(1+\varepsilon)\Delta P_{fare} + (R_{base} - V_{other} - V_{fuel} - V_{fuel}\Delta P_{oil}) = 0$$

**经济含义**：给定油价冲击，存在一个票价调整阈值，低于该阈值将导致边际贡献为负。

---

#### 推论3：油价容忍度

在给定票价调整 $\Delta P_{fare}$ 和套保比例 $h$ 下，可承受的最大油价涨幅：

$$\Delta P_{oil}^{max} = \frac{R_{adj} - V_{other} - V_{fuel}}{V_{fuel}(1-h)}$$

**经济含义**：
- 该指标衡量在维持边际贡献为正的前提下，航空公司能承受的最大油价冲击
- 提高票价 $\Delta P_{fare}$ 或增加套保 $h$ 都可以提高油价容忍度

---

### 数据校准来源

| 参数 | 数值 | 数据来源 | 说明 |
|------|------|----------|------|
| 基础运营收入 | 64.94 万亿₫ | 2025财报附注28 | 剔除飞机销售、干租赁、备件销售等非航线主业收入 |
| 基础燃油成本 | 24.70 万亿₫ | 2025财报附注36 | 航油成本 |
| 其他变动成本 | 22.70 万亿₫ | 2025财报附注36 | 外部服务费、变动人工、航路起降费等 |
| 固定成本 | 19.06 万亿₫ | 2025财报附注36/31 | 租赁费、折旧、固定人工、坏账准备等 |
| 需求价格弹性 | -0.8 | 行业研究文献 | 航空业典型值 |
| 网络骨架保留权重 | 0.25 | 航空运营实践 | 防止过度削减破坏枢纽结构 |

---

## 🚀 快速开始

### 安装依赖

```bash
pip install streamlit pandas numpy scipy plotly openpyxl
```

### 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中自动打开：http://localhost:8501

---

## 📊 功能特性

### 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| **单情景分析** | 调整油价、票价、套保比例，实时查看决策结果 | ✅ |
| **多情景扫描** | 批量计算多种组合情景，导出CSV分析 | ✅ |
| **阈值分析** | 计算票价盈亏平衡点、油价容忍上限、套保触发线 | ✅ Phase 1 |
| **决策路径** | 四阶段响应路径可视化（监控→票价→套保→削班） | ✅ Phase 1 |
| **动作优化器** | 约束型动作序列优化（网格/梯度法） | ✅ Phase 2 |
| **可视化图表** | 利润热力图、航班削减图、三维决策曲面 | ✅ |
| **参数自定义** | 根据最新财报数据调整模型参数 | ✅ |

### Phase 1 新增功能

- **🎯 智能决策模式**：输入油价冲击，自动计算最优响应路径
- **📈 阈值看板**：票价盈亏平衡点、油价容忍上限、削班触发套保线
- **🚨 预警系统**：约束违规提示、风险等级标识

### Phase 2 新增功能

- **🔢 动作序列优化器**：按优先级依次优化票价→套保→削班
- **⚡ 双优化方法**：网格搜索（稳健）/ 梯度法（快速）
- **💡 推荐理由**：每步动作附带详细经济学解释
- **✅ 可行性检查**：自动检测约束违规情况

---

## 📂 项目结构

```
V_Fin_Sim/
├── vietjet_oil_model/
│   ├── __init__.py
│   ├── core_model.py              # 核心模型实现
│   ├── threshold_config.py        # Phase 1: 阈值配置
│   └── optimizer_results.py       # Phase 2: 优化结果数据类
├── static/
│   └── landing-page.html          # 落地页
├── app.py                          # Streamlit应用入口
├── 方案二.md                       # 设计方案文档
└── README.md
```

---

## 💡 使用示例

### 基础单情景测算

```python
from vietjet_oil_model import VietJetOilShockModel

# 创建模型
model = VietJetOilShockModel()

# 单情景测算
result = model.evaluate(
    oil_increase=0.4,    # 油价+40%
    fare_adj=0.08,       # 票价+8%
    hedge_ratio=0.3      # 套保30%
)

print(f"决策状态: {result.status}")
print(f"建议航班削减比例: {result.cut_ratio*100:.1f}%")
print(f"预期运营利润: {result.expected_pnl:.2f} 万亿₫")
```

### Phase 1：阈值分析

```python
# 计算决策阈值与响应路径
threshold_result = model.get_thresholds(
    oil_increase=0.4,        # 油价+40%
    fare_cap=0.20,           # 票价最多上调20%
    hedge_cap=0.80           # 套保最多80%
)

print(f"票价盈亏平衡点: +{threshold_result.fare_breakeven*100:.1f}%")
print(f"油价容忍上限: +{threshold_result.oil_tolerance*100:.1f}%")
print(f"当前阶段: {threshold_result.current_stage}")

# 查看决策路径
for step in threshold_result.decision_path:
    print(f"阶段{step['stage']}: {step['action']}")
    print(f"  触发条件: {step['trigger_value']}")
    print(f"  推荐: {step['desc']}")
```

### Phase 2：动作序列优化

```python
from vietjet_oil_model.optimizer_results import ActionType

# 约束型动作序列优化
opt_result = model.recommend_action_sequence(
    oil_increase=0.4,            # 油价+40%
    fare_cap=0.20,               # 票价最多上调20%
    hedge_cap=0.80,              # 套保最多80%
    optimization_method="grid"   # 网格搜索 / "gradient"
)

print(f"可行性: {'✅' if opt_result.is_feasible else '❌'}")
print(f"最终边际贡献: {opt_result.final_cm:.2f} 万亿₫")
print(f"预期利润: {opt_result.final_pnl:.2f} 万亿₫")

# 获取具体动作建议
fare_action = opt_result.get_action_by_type(ActionType.FARE_ADJUSTMENT)
hedge_action = opt_result.get_action_by_type(ActionType.HEDGE_POSITION)
cut_action = opt_result.get_action_by_type(ActionType.CAPACITY_REDUCTION)

print(f"\n票价调整: {fare_action.value*100:+.1f}%")
print(f"  理由: {fare_action.rationale}")

print(f"\n套保比例: {hedge_action.value*100:.1f}%")
print(f"  理由: {hedge_action.rationale}")

print(f"\n削班比例: {cut_action.value*100:.1f}%")
print(f"  理由: {cut_action.rationale}")
```

### 批量情景扫描

```python
import pandas as pd

# 批量情景扫描
df = model.scenario_sweep(
    oil_range=[0.1, 0.2, 0.3, 0.4, 0.5],
    fare_range=[0.0, 0.05, 0.10, 0.15, 0.20],
    hedge_range=[0.0, 0.3, 0.5, 0.8]
)

# 筛选健康运营的情景
healthy_scenarios = df[df['状态类型'] == 'healthy']
print(f"盈利情景数量: {len(healthy_scenarios)}")

# 导出分析结果
df.to_csv('scenario_analysis.csv', index=False)
```

---

## ⚠️ 注意事项

1. 本模型为简化分析工具，实际决策需考虑更多因素
2. 削减航班可能扩大账面亏损，但可缓解短期现金流压力
3. 套保具有双刃剑效应，油价下跌时可能产生机会成本
4. 国际航线受双边协定约束，需考虑合规性风险
5. 需求弹性假设基于行业平均值，实际弹性可能因航线、市场而异

---

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 创建 Issue
- 提交 Pull Request
