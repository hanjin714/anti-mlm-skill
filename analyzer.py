#!/usr/bin/env python3
"""
反割韭菜分析器 - 核心引擎
分析课程海报、宣传词汇，判断是否为割韭菜课程
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = "较低风险"
    MEDIUM = "中等风险"
    HIGH = "高风险"
    VERY_HIGH = "极高风险"


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    risk_score: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    high_risk_keywords: List[str] = field(default_factory=list)
    medium_risk_keywords: List[str] = field(default_factory=list)
    suspicious_tactics: List[str] = field(default_factory=list)
    red_flags: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    summary: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


class TextAnalyzer:
    """文本分析器"""

    # 高风险关键词（强烈暗示割韭菜）
    HIGH_RISK_PATTERNS = [
        r"躺赚", r"日入过万", r"财富自由", r"月入\s*\d+[万kK]", r"快速致富",
        r"稳赚不赔", r"100%赚钱", r"内部消息", r"限量名额",
        r"限时特价", r"错过等一年", r"名额有限", r"即将涨价",
        r"普通人也能", r"轻松月入", r"在家赚钱", r"副业刚需",
        r"睡后收入", r"被动收入", r"实现财务自由", r"逆袭人生",
        r"改变命运", r"低成本高回报", r"一本万利",
        r"轻松赚钱", r"快速变现", r"日赚", r"月赚",
        r"创业导师", r"财富密码", r"盈利模式", r"暴利",
        r"零风险", r"无风险", r"包赚钱", r"一定赚",
    ]

    # 中风险关键词（需要警惕）
    MEDIUM_RISK_PATTERNS = [
        r"导师", r"教练", r"大师", r"创始人", r"CEO",
        r"成功案例", r"学员见证", r"逆袭", r"蜕变",
        r"干货", r"秘籍", r"绝招", r"杀手锏",
        r"带你", r"教你", r"训练营", r"密训",
        r"变现", r"副业", r"斜杠", r"第二收入",
        r"提升", r"成长", r"突破", r"进阶",
        r"大咖", r"名师", r"专家", r"权威",
    ]

    # 可疑营销套路
    SUSPICIOUS_TACTICS = {
        "制造焦虑": r"(焦虑|危机|被淘汰|不转型|跟不上|来不及|后悔|错过)",
        "虚假稀缺": r"(只剩|仅限|最后|紧急|限时|错过|停止招募|名额不多了)",
        "夸大宣传": r"(最[佳棒厉害牛]|[的]第[一一个]|唯一|首创|颠覆|革命性|爆炸性)",
        "情感绑架": r"(对不起|对不起家人|让孩子|让父母|后悔一辈子|别让孩子输)",
        "截图诱导": r"(收入截图|转账截图|聊天截图|学员反馈|晒单|提现截图)",
        "身份包装": r"(资深|资深导师|知名|著名|明星|网红|大V|第一人)",
        "保证承诺": r"(保证|承诺|100%|一定|绝对|必定|稳赚)",
    }

    # 红旗信号（严重警告）
    RED_FLAGS = [
        r"拉人头", r"发展下线", r"分销", r"代理", r"层级",
        r"返利", r"佣金", r"团队计酬", r"缴纳\d+[万块]",
        r"入门费", r"加盟费", r"保证金", r"会员费",
    ]

    def __init__(self):
        self.text = ""

    def analyze(self, text: str) -> AnalysisResult:
        """分析文本内容"""
        self.text = text
        result = AnalysisResult()

        # 提取所有风险关键词
        result.high_risk_keywords = self._extract_keywords(self.HIGH_RISK_PATTERNS)
        result.medium_risk_keywords = self._extract_keywords(self.MEDIUM_RISK_PATTERNS)
        result.suspicious_tactics = self._detect_tactics()
        result.red_flags = self._detect_red_flags()

        # 计算风险评分
        result.risk_score = self._calculate_risk_score(result)
        result.risk_level = self._determine_risk_level(result.risk_score)

        # 生成摘要和建议
        result.summary = self._generate_summary(result)
        result.recommendations = self._generate_recommendations(result)
        result.details = self._generate_details(result)

        return result

    def _extract_keywords(self, patterns: List[str]) -> List[str]:
        """提取匹配的关键词"""
        found = []
        for pattern in patterns:
            if re.search(pattern, self.text):
                # 提取匹配的部分
                match = re.search(pattern, self.text)
                if match:
                    found.append(match.group())
        return list(set(found))

    def _detect_tactics(self) -> List[str]:
        """检测可疑营销套路"""
        detected = []
        for tactic_name, pattern in self.SUSPICIOUS_TACTICS.items():
            if re.search(pattern, self.text):
                detected.append(tactic_name)
        return detected

    def _detect_red_flags(self) -> List[str]:
        """检测红旗信号"""
        detected = []
        for pattern in self.RED_FLAGS:
            if re.search(pattern, self.text):
                match = re.search(pattern, self.text)
                if match:
                    detected.append(match.group())
        return list(set(detected))

    def _calculate_risk_score(self, result: AnalysisResult) -> int:
        """计算风险评分"""
        score = 0

        # 高风险词每个15分
        score += len(result.high_risk_keywords) * 15

        # 中风险词每个5分
        score += len(result.medium_risk_keywords) * 5

        # 可疑套路每个加20分
        score += len(result.suspicious_tactics) * 20

        # 红旗信号每个加30分
        score += len(result.red_flags) * 30

        return min(100, score)

    def _determine_risk_level(self, score: int) -> RiskLevel:
        """确定风险等级"""
        if score >= 75:
            return RiskLevel.VERY_HIGH
        elif score >= 50:
            return RiskLevel.HIGH
        elif score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _generate_summary(self, result: AnalysisResult) -> str:
        """生成风险概述"""
        if result.risk_level == RiskLevel.VERY_HIGH:
            return "检测到多项严重高风险特征，几乎可以确定为割韭菜课程，建议立即远离"
        elif result.risk_level == RiskLevel.HIGH:
            return "检测到多项高风险特征，存在明显的割韭菜嫌疑，建议高度警惕"
        elif result.risk_level == RiskLevel.MEDIUM:
            return "检测到一些可疑特征，建议进一步核实课程内容和讲师资质"
        else:
            return "未检测到明显的割韭菜特征，但仍需保持理性判断"

    def _generate_recommendations(self, result: AnalysisResult) -> List[str]:
        """生成建议"""
        recommendations = []

        if result.risk_level in [RiskLevel.VERY_HIGH, RiskLevel.HIGH]:
            recommendations = [
                "强烈建议不要冲动报名，立即远离",
                "这类课程通常涉嫌虚假宣传",
                "如已付款，建议保留证据并考虑报警",
                "可以向消费者协会或市场监管部门举报",
            ]
        elif result.risk_level == RiskLevel.MEDIUM:
            recommendations = [
                "建议多方核实后再做决定",
                "查看课程大纲，判断内容是否值这个价",
                "搜索讲师真实评价（不只是他们展示的）",
                "考虑是否有更靠谱的学习渠道",
                "核实企业和讲师的真实背景",
            ]
        else:
            recommendations = [
                "保持理性判断",
                "仔细阅读课程合同条款",
                "了解退款政策",
            ]

        # 如果有红旗信号，添加特殊警告
        if result.red_flags:
            recommendations.insert(0, "⚠️ 检测到涉嫌传销/拉人头的特征，务必警惕！")

        return recommendations

    def _generate_details(self, result: AnalysisResult) -> Dict[str, Any]:
        """生成详细信息"""
        return {
            "total_high_risk": len(result.high_risk_keywords),
            "total_medium_risk": len(result.medium_risk_keywords),
            "total_tactics": len(result.suspicious_tactics),
            "total_red_flags": len(result.red_flags),
            "price_assessment": self._assess_price(result),
            "credibility_assessment": self._assess_credibility(result),
        }

    def _assess_price(self, result: AnalysisResult) -> str:
        """评估价格"""
        # 尝试提取价格
        price_pattern = r"(\d+)[元万块]"
        prices = re.findall(price_pattern, self.text)

        if not prices:
            return "未检测到明确价格信息"

        max_price = max(int(p) for p in prices)

        if result.risk_level in [RiskLevel.VERY_HIGH, RiskLevel.HIGH]:
            if max_price >= 1000:
                return f"检测到价格{max_price}元，结合高风险特征，价格通常虚高"
            else:
                return f"检测到价格{max_price}元，虽不高但风险特征明显"
        elif result.risk_level == RiskLevel.MEDIUM:
            return f"检测到价格{max_price}元，需结合课程内容综合判断"
        else:
            return f"检测到价格{max_price}元，价格相对合理"

    def _assess_credibility(self, result: AnalysisResult) -> str:
        """评估可信度"""
        if result.red_flags:
            return "极低 - 存在涉嫌违法风险"
        elif result.risk_level == RiskLevel.HIGH:
            return "低 - 宣传内容可信度存疑"
        elif result.risk_level == RiskLevel.MEDIUM:
            return "中等 - 承诺内容需自行核实"
        else:
            return "较高 - 未发现明显虚假宣传"


class AntiMlmAnalyzer:
    """反割韭菜综合分析器"""

    def __init__(self):
        self.text_analyzer = TextAnalyzer()
        self.sources_analyzed = []

    def analyze_text(self, text: str) -> AnalysisResult:
        """分析纯文本"""
        return self.text_analyzer.analyze(text)

    def analyze_with_context(
        self,
        text: str,
        source_url: Optional[str] = None,
        company_info: Optional[Dict] = None,
        person_info: Optional[Dict] = None,
        user_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        带上下文的综合分析

        Args:
            text: 分析文本
            source_url: 来源链接
            company_info: 企业信息
            person_info: 人物信息
            user_profile: 用户画像

        Returns:
            综合分析报告
        """
        # 基础文本分析
        text_result = self.text_analyzer.analyze(text)

        # 构建综合报告
        report = {
            "risk_assessment": {
                "score": text_result.risk_score,
                "level": text_result.risk_level.value,
                "summary": text_result.summary,
                "details": text_result.details,
            },
            "warning_signals": {
                "high_risk_keywords": text_result.high_risk_keywords,
                "medium_risk_keywords": text_result.medium_risk_keywords,
                "suspicious_tactics": text_result.suspicious_tactics,
                "red_flags": text_result.red_flags,
            },
            "recommendations": text_result.recommendations,
            "source_verification": self._verify_source(source_url),
            "company_check": company_info or {},
            "person_check": person_info or {},
            "user_context": self._analyze_user_context(user_profile),
        }

        # 综合评分调整
        report["final_assessment"] = self._calculate_final_assessment(report)

        return report

    def _verify_source(self, url: Optional[str]) -> Dict[str, Any]:
        """验证来源"""
        if not url:
            return {"verified": False, "reason": "未提供来源链接"}

        # 基本的URL分析
        suspicious_domains = ["taobao.com", "weipin.cn", "cdnniao.cn", "xxzy.com"]
        verified = not any(d in url.lower() for d in suspicious_domains)

        return {
            "verified": verified,
            "url": url,
            "domain_analysis": self._analyze_domain(url),
        }

    def _analyze_domain(self, url: str) -> str:
        """分析域名"""
        try:
            if "taobao" in url or "1688" in url:
                return "电商平台页面，可信度较低"
            elif "weixin" in url or "wechat" in url:
                return "微信生态内容，难以追溯"
            elif "toutiao" in url or "byte" in url:
                return "字节系内容平台"
            else:
                return "需进一步验证域名真实性"
        except:
            return "无法分析域名"

    def _analyze_user_context(self, profile: Optional[Dict]) -> Dict[str, Any]:
        """分析用户上下文"""
        if not profile:
            return {"analyzed": False}

        return {
            "analyzed": True,
            "profile": profile,
            "context_awareness": "已结合用户画像进行分析",
        }

    def _calculate_final_assessment(self, report: Dict) -> Dict[str, Any]:
        """计算最终评估"""
        base_score = report["risk_assessment"]["score"]

        # 根据各维度调整分数
        adjustments = []

        # 来源验证调整
        if not report["source_verification"].get("verified", True):
            base_score += 10
            adjustments.append("来源不可信 +10")

        # 企业信息调整
        company = report.get("company_check", {})
        if company.get("verified") == False:
            base_score += 15
            adjustments.append("企业不可信 +15")
        elif company.get("verified") == True:
            base_score -= 10
            adjustments.append("企业可信 -10")

        # 人物信息调整
        person = report.get("person_check", {})
        if person.get("verified") == False:
            base_score += 15
            adjustments.append("人物不可信 +15")
        elif person.get("verified") == True:
            base_score -= 10
            adjustments.append("人物可信 -10")

        final_score = min(100, max(0, base_score))

        return {
            "final_score": final_score,
            "adjustments": adjustments,
            "adjusted_level": self._score_to_level(final_score),
        }

    def _score_to_level(self, score: int) -> str:
        """分数转等级"""
        if score >= 75:
            return "极高风险"
        elif score >= 50:
            return "高风险"
        elif score >= 25:
            return "中等风险"
        else:
            return "较低风险"


def main():
    """测试"""
    import json

    analyzer = AntiMlmAnalyzer()

    test_cases = [
        "好消息！某导师亲授，普通人也能轻松月入十万，限时特价只要999，名额有限，错过等一年！",
        "Python编程基础课程，系统化学习，适合零基础学员，提供课后答疑服务。",
        "【内部消息】某大师带你躺赚，日入过万不是梦！限量名额，仅限前100名，错过等一年！还等什么？赶紧扫码加入！",
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试案例 {i}")
        print("="*60)
        result = analyzer.analyze_text(text)

        print(f"\n风险评分: {result.risk_score}/100")
        print(f"风险等级: {result.risk_level.value}")
        print(f"摘要: {result.summary}")
        print(f"\n高风险词: {result.high_risk_keywords}")
        print(f"中风险词: {result.medium_risk_keywords}")
        print(f"可疑套路: {result.suspicious_tactics}")
        print(f"红旗信号: {result.red_flags}")
        print(f"\n建议: {result.recommendations}")


if __name__ == "__main__":
    main()