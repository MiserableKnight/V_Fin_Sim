# -*- coding: utf-8 -*-
"""
动作序列优化结果数据结构
Action Sequence Optimization Result Data Structures

Phase 2 优化：约束型动作序列优化器
Phase 2 Optimization: Constrained Action Sequence Optimizer
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class ActionStatus(Enum):
    """动作状态枚举 / Action Status Enumeration"""
    OPTIMIZED = "optimized"       # 已优化到最优值
    SKIPPED = "skipped"           # 跳过（无需执行）
    TRIGGERED = "triggered"       # 已触发
    NOT_TRIGGERED = "not_triggered"  # 未触发
    CAP_EXCEEDED = "cap_exceeded"  # 触及上限


class ActionType(Enum):
    """动作类型枚举 / Action Type Enumeration"""
    FARE_ADJUSTMENT = "fare"      # 票价调整
    HEDGE_POSITION = "hedge"      # 套保建仓
    CAPACITY_REDUCTION = "cut"    # 削班


@dataclass
class ActionStep:
    """
    单个动作步骤 / Single Action Step

    封装优化过程中每个动作的详细信息
    """
    type: ActionType                      # 动作类型
    value: float                          # 动作值（如票价+0.12，套保0.35）
    status: ActionStatus                  # 动作状态
    description: str                      # 动作描述
    rationale: str                        # 推荐理由
    priority: int = 1                     # 优先级（1=最高）

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 / Convert to dictionary format"""
        return {
            "type": self.type.value,
            "value": self.value,
            "status": self.status.value,
            "description": self.description,
            "rationale": self.rationale,
            "priority": self.priority
        }


@dataclass
class OptimizationResult:
    """
    优化结果总览 / Optimization Result Summary

    包含动作序列优化器的完整输出
    """
    triggered_by: str                     # 触发原因（如"油价+40%"）
    actions: List[ActionStep]             # 动作序列（按优先级排序）
    final_cm: float                       # 最终边际贡献
    final_pnl: float                      # 最终预期利润
    constraints_violated: List[str]       # 违反的约束列表
    is_feasible: bool                     # 是否找到可行解
    optimization_summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式 / Convert to dictionary format"""
        return {
            "triggered_by": self.triggered_by,
            "actions": [action.to_dict() for action in self.actions],
            "final_cm": self.final_cm,
            "final_pnl": self.final_pnl,
            "constraints_violated": self.constraints_violated,
            "is_feasible": self.is_feasible,
            "optimization_summary": self.optimization_summary
        }

    def get_action_by_type(self, action_type: ActionType) -> Optional[ActionStep]:
        """根据类型获取动作 / Get action by type"""
        for action in self.actions:
            if action.type == action_type:
                return action
        return None

    def get_summary_text(self) -> str:
        """获取优化结果摘要文本 / Get optimization summary text"""
        lines = [
            f"触发原因: {self.triggered_by}",
            f"可行性: {'✅ 可行' if self.is_feasible else '❌ 不可行'}",
            f"最终边际贡献: {self.final_cm:.2f} 万亿₫",
            f"预期利润: {self.final_pnl:.2f} 万亿₫"
        ]

        if self.constraints_violated:
            lines.append("\n约束违规:")
            for violation in self.constraints_violated:
                lines.append(f"  - {violation}")

        lines.append("\n推荐动作序列:")
        for action in self.actions:
            status_icon = {
                ActionStatus.OPTIMIZED: "🟢",
                ActionStatus.SKIPPED: "⚪",
                ActionStatus.TRIGGERED: "🔴",
                ActionStatus.NOT_TRIGGERED: "⚪",
                ActionStatus.CAP_EXCEEDED: "🟠"
            }.get(action.status, "⚪")

            lines.append(f"  {status_icon} {action.description} - {action.rationale}")

        return "\n".join(lines)
