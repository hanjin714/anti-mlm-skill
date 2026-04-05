#!/usr/bin/env python3
"""
反割韭菜 - 用户画像分析模块
分析用户的历史对话习惯，判断用户特征
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter


@dataclass
class UserProfile:
    """用户画像"""
    user_id: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    traits: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    risk_tendency: str = "未知"  # 易感人群,理性用户,待观察
    analysis_complete: bool = False


@dataclass
class ConversationContext:
    """对话上下文"""
    messages: List[Dict[str, str]]  # [{"role": "user", "content": "..."}, ...]
    analyzed: bool = False
    profile: Optional[UserProfile] = None


class UserProfiler:
    """用户画像分析器"""

    # 易感人群特征词汇
    VULNERABLE_TRAITS = {
        "急切变现": [r"想赚钱", r"想副业", r"想创业", r"想翻身", r"想暴富", r"还债", r"负债"],
        "焦虑情绪": [r"焦虑", r"迷茫", r"迷茫", r"压力", r"危机", r"危机感", r"怎么办"],
        "缺乏经验": [r"新手", r"小白", r"不懂", r"不会", r"没做过", r"第一次"],
        "急于求成": [r"快速", r"捷径", r"秘诀", r"绝招", r"马上", r"立即", r"几天见效"],
    }

    # 理性用户特征
    RATIONAL_TRAITS = {
        "谨慎": [r"谨慎", r"小心", r"防止", r"避开", r"靠谱"],
        "理性": [r"分析", r"判断", r"核实", r"了解清楚", r"对比"],
        "有经验": [r"做过", r"了解", r"熟悉", r"以前", r"经验"],
        "不急切": [r"不急", r"慢慢来", r"先看看", r"观望"],
    }

    # 兴趣领域
    INTEREST_PATTERNS = {
        "副业变现": [r"副业", r"兼职", r"变现", r"赚钱", r"收入"],
        "投资理财": [r"投资", r"理财", r"股票", r"基金", r"区块链", r"数字货币"],
        "电商运营": [r"淘宝", r"京东", r"拼多多", r"电商", r"开店", r"直播带货"],
        "知识付费": [r"课程", r"培训", r"学习", r"知识", r"付费"],
        "职场发展": [r"职场", r"加薪", r"晋升", r"简历", r"面试"],
    }

    def __init__(self):
        self.conversations: Dict[str, ConversationContext] = {}

    def add_message(self, user_id: str, role: str, content: str):
        """
        添加用户消息

        Args:
            user_id: 用户ID
            role: 角色 ("user" 或 "assistant")
            content: 消息内容
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationContext(messages=[])

        self.conversations[user_id].messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def analyze_user(self, user_id: str) -> UserProfile:
        """
        分析用户画像

        Args:
            user_id: 用户ID

        Returns:
            用户画像
        """
        if user_id not in self.conversations:
            return UserProfile(user_id=user_id, analysis_complete=False)

        ctx = self.conversations[user_id]
        all_text = " ".join([m["content"] for m in ctx.messages if m["role"] == "user"])

        profile = UserProfile(user_id=user_id)

        # 分析易感特征
        vulnerable_signals = self._detect_vulnerable_traits(all_text)
        profile.traits["vulnerable_signals"] = vulnerable_signals

        # 分析理性特征
        rational_signals = self._detect_rational_traits(all_text)
        profile.traits["rational_signals"] = rational_signals

        # 分析兴趣
        profile.interests = self._detect_interests(all_text)

        # 判断风险倾向
        profile.risk_tendency = self._assess_risk_tendency(vulnerable_signals, rational_signals)

        profile.analysis_complete = True
        ctx.profile = profile

        return profile

    def _detect_vulnerable_traits(self, text: str) -> Dict[str, int]:
        """检测易感特征"""
        signals = {}
        for trait, patterns in self.VULNERABLE_TRAITS.items():
            count = sum(len(re.findall(p, text)) for p in patterns)
            if count > 0:
                signals[trait] = count
        return signals

    def _detect_rational_traits(self, text: str) -> Dict[str, int]:
        """检测理性特征"""
        signals = {}
        for trait, patterns in self.RATIONAL_TRAITS.items():
            count = sum(len(re.findall(p, text)) for p in patterns)
            if count > 0:
                signals[trait] = count
        return signals

    def _detect_interests(self, text: str) -> List[str]:
        """检测兴趣领域"""
        interests = []
        for interest, patterns in self.INTEREST_PATTERNS.items():
            if any(re.search(p, text) for p in patterns):
                interests.append(interest)
        return interests

    def _assess_risk_tendency(self, vulnerable: Dict, rational: Dict) -> str:
        """评估风险倾向"""
        v_score = sum(vulnerable.values())
        r_score = sum(rational.values())

        if v_score >= 3 and r_score <= 1:
            return "高易感性 - 容易被割韭菜话术打动"
        elif v_score >= 2 and r_score == 0:
            return "中等易感性 - 需谨慎判断"
        elif r_score >= 2 and v_score <= 1:
            return "理性用户 - 能独立判断"
        elif v_score > 0 and r_score > 0:
            return "矛盾特征 - 需具体分析"
        else:
            return "待观察 - 数据不足"

    def get_analysis_report(self, user_id: str) -> str:
        """
        生成用户分析报告

        Args:
            user_id: 用户ID

        Returns:
            报告文本
        """
        if user_id not in self.conversations:
            return "无用户数据"

        profile = self.analyze_user(user_id)

        lines = [
            f"用户ID: {user_id}",
            f"消息数量: {len(self.conversations[user_id].messages)}",
            f"风险倾向: {profile.risk_tendency}",
        ]

        if profile.interests:
            lines.append(f"兴趣领域: {', '.join(profile.interests)}")

        if profile.traits.get("vulnerable_signals"):
            lines.append(f"易感特征: {profile.traits['vulnerable_signals']}")

        if profile.traits.get("rational_signals"):
            lines.append(f"理性特征: {profile.traits['rational_signals']}")

        return "\n".join(lines)

    def get_context_for_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用于综合分析的上下文

        Args:
            user_id: 用户ID

        Returns:
            上下文数据
        """
        if user_id not in self.conversations:
            return None

        profile = self.analyze_user(user_id)

        return {
            "user_id": user_id,
            "risk_tendency": profile.risk_tendency,
            "interests": profile.interests,
            "traits": profile.traits,
            "message_count": len(self.conversations[user_id].messages),
            "analysis": self.get_analysis_report(user_id),
        }


def main():
    """测试"""
    profiler = UserProfiler()

    # 模拟用户对话
    user_id = "test_user_001"

    messages = [
        ("user", "最近想找个副业赚钱，有什么好项目吗？"),
        ("user", "看到有个课程说可以轻松月入十万，不知道是不是真的？"),
        ("user", "我是新手小白，什么都不懂"),
        ("user", "还欠了一些债，急需赚钱"),
    ]

    for role, content in messages:
        profiler.add_message(user_id, role, content)

    print("="*50)
    print("用户分析报告")
    print("="*50)
    print(profiler.get_analysis_report(user_id))

    print("\n" + "="*50)
    print("用于综合分析的上下文")
    print("="*50)
    ctx = profiler.get_context_for_analysis(user_id)
    print(f"风险倾向: {ctx['risk_tendency']}")
    print(f"兴趣领域: {ctx['interests']}")
    print(f"易感特征: {ctx['traits'].get('vulnerable_signals', {})}")
    print(f"理性特征: {ctx['traits'].get('rational_signals', {})}")


if __name__ == "__main__":
    main()