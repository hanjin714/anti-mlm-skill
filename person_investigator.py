#!/usr/bin/env python3
"""
反割韭菜 - 人物背景调查模块
查询课程讲师/创始人等人物的背景、资质、真实成绩
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class PersonProfile:
    """人物画像"""
    name: str
    titles: List[str] = field(default_factory=list)
    claimed_achievements: List[str] = field(default_factory=list)
    verified_achievements: List[str] = field(default_factory=list)
    controversies: List[str] = field(default_factory=list)
    verified: bool = False
    risk_level: str = "未知"
    search_urls: Dict[str, str] = field(default_factory=dict)


class PersonInvestigator:
    """人物背景调查器"""

    # 讲师常用包装词汇（可疑）
    SUSPICIOUS_TITLES = [
        "大师", "教父", "之神", "第一人", "创始之神",
        "传奇", "领袖", "大咖", "大牛", "大神",
        "顶级", "天花板", "鼻祖", "之父",
    ]

    # 声称成绩的可疑模式
    SUSPICIOUS_CLAIMS = [
        r"(?:帮助|带领)\s*(\d+[万+])\s*(?:学员|人|代理)",
        r"(?:学员|人)\s*(?:月入|日入|年收入)\s*(\d+[万+]?)",
        r"(?:团队|业绩)\s*(?:突破|达到|超过)\s*(\d+[万+]?)",
        r"(?:年入|身家)\s*(\d+[万+]?)",
    ]

    # 常见黑历史关键词
    BLACKLIST_KEYWORDS = [
        "骗局", "诈骗", "传销", "割韭菜", "维权",
        "退款", "上当", "欺骗", "虚假宣传", "投诉",
    ]

    def __init__(self):
        self.cache = {}

    def extract_person_info(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取人物信息

        Args:
            text: 输入文本

        Returns:
            人物信息列表
        """
        persons = []

        # 提取人物名称（常见模式）
        name_patterns = [
            r'([A-Za-z·\u4e00-\u9fa5]{2,5})\s*(?:导师|讲师|创始人|CEO|创始人)',
            r'([A-Za-z·\u4e00-\u9fa5]{2,5})\s*(?:老师|大师|专家|达人)',
            r'讲师\s*([A-Za-z·\u4e00-\u9fa5]{2,5})',
            r'导师\s*([A-Za-z·\u4e00-\u9fa5]{2,5})',
        ]

        names_found = set()
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            for name in matches:
                if len(name) >= 2 and len(name) <= 6:
                    names_found.add(name)

        # 提取声称的头衔
        for name in names_found:
            person_data = {
                "name": name,
                "titles": self._extract_titles(text, name),
                "claimed_achievements": self._extract_claims(text, name),
                "risk_signals": self._analyze_person_risk(name, text),
            }
            persons.append(person_data)

        return persons

    def _extract_titles(self, text: str, name: str) -> List[str]:
        """提取人物头衔"""
        titles = []

        # 查找人物附近的词汇
        patterns = [
            rf'{name}\s*([^\s]*(?:导师|讲师|创始人|CEO|老师|大师|专家)[^\s]*)',
            rf'([^\s]*(?:导师|讲师|创始人|CEO|老师|大师|专家)[^\s]*)\s*{name}',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            titles.extend(matches)

        # 检测可疑头衔
        suspicious = []
        for title in titles:
            for sus in self.SUSPICIOUS_TITLES:
                if sus in title:
                    suspicious.append(f"可疑头衔: {title}")

        return suspicious if suspicious else list(set(titles))

    def _extract_claims(self, text: str, name: str) -> List[str]:
        """提取声称的成绩"""
        claims = []

        for pattern in self.SUSPICIOUS_CLAIMS:
            matches = re.findall(pattern, text)
            claims.extend([f"声称: {m}" for m in matches])

        return claims

    def _analyze_person_risk(self, name: str, text: str) -> List[str]:
        """分析人物风险"""
        risks = []

        # 检查头衔是否夸大
        for sus in self.SUSPICIOUS_TITLES:
            if sus in text:
                risks.append(f"使用夸大头衔: {sus}")

        # 检查是否有过负面
        for keyword in self.BLACKLIST_KEYWORDS:
            # 简单检查人物名附近是否有黑词
            pattern = rf'{name}.{{0,20}}{keyword}|{keyword}.{{0,20}}{name}'
            if re.search(pattern, text):
                risks.append(f"存在负面关联: {keyword}")

        return risks

    def investigate_person(self, name: str) -> Dict[str, Any]:
        """
        调查人物背景

        Args:
            name: 人物姓名

        Returns:
            调查报告
        """
        result = {
            "name": name,
            "verified": False,
            "risk_level": "低风险",
            "risk_signals": [],
            "recommendations": [],
            "search_urls": self._generate_search_urls(name),
            "analysis": "",
        }

        # 基础分析
        risk_signals = self._analyze_name_risk(name)
        result["risk_signals"] = risk_signals

        if risk_signals:
            result["risk_level"] = "中高风险"
            result["analysis"] = "该人物存在多个风险特征"
        else:
            result["analysis"] = "未发现明显风险特征"

        # 建议
        result["recommendations"] = [
            f"建议搜索「{name} 骗子」查看是否有负面新闻",
            f"建议搜索「{name} 骗局」核实是否有曝光",
            f"建议核实该人物的真实资质和背景",
        ]

        return result

    def _analyze_name_risk(self, name: str) -> List[str]:
        """分析姓名风险"""
        risks = []

        # 检测是否使用洋名/假名
        if re.match(r'^[A-Za-z]+$', name):
            risks.append("使用英文名，可信度降低")

        # 检测是否过于夸张
        if any(char in name for char in ["神", "圣", "仙", "帝", "王"]):
            risks.append("姓名含有夸张字眼")

        return risks

    def _generate_search_urls(self, name: str) -> Dict[str, str]:
        """生成搜索链接"""
        import urllib.parse
        encoded = urllib.parse.quote(name)

        return {
            "百度搜索": f"https://www.baidu.com/s?wd={encoded}",
            "微博": f"https://s.weibo.com/weibo?q={encoded}",
            "知乎": f"https://www.zhihu.com/search?type=people&q={encoded}",
            "天眼查": f"https://www.tianyancha.com/search?key={encoded}",
            "搜索负面": f"https://www.baidu.com/s?wd={encoded}+骗子+骗局",
        }

    def analyze_instructor_from_page(self, page_data: Dict) -> Dict[str, Any]:
        """
        分析页面中的讲师信息

        Args:
            page_data: 页面数据

        Returns:
            分析结果
        """
        result = {
            "persons_found": [],
            "total_risk_level": "未知",
            "recommendations": [],
        }

        # 提取所有文本
        all_text = ""
        if page_data.get("structured_data"):
            all_text += page_data["structured_data"].get("title", "")
            all_text += page_data["structured_data"].get("description", "")

        if page_data.get("page_content"):
            all_text += page_data["page_content"]

        if not all_text:
            return result

        # 提取人物信息
        persons = self.extract_person_info(all_text)
        result["persons_found"] = persons

        # 风险评估
        high_risk_count = sum(1 for p in persons if len(p.get("risk_signals", [])) > 0)
        if high_risk_count > 0:
            result["total_risk_level"] = f"中高风险 - 发现{high_risk_count}个可疑人物"
            result["recommendations"].append("建议核实所有讲师的真实背景")
        else:
            result["total_risk_level"] = "未发现明显异常"

        return result


def main():
    """测试"""
    investigator = PersonInvestigator()

    test_texts = [
        "某大师带你躺赚，月入十万！张老师是知名创业导师，已帮助10000+学员实现财富自由。",
        "李明老师，资深Python讲师，某互联网公司CTO。",
        "王大师创立财富自由训练营，声称已带领团队月入500万。",
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\n{'='*50}")
        print(f"测试案例 {i}")
        print("="*50)

        persons = investigator.extract_person_info(text)
        for person in persons:
            print(f"\n人物: {person['name']}")
            print(f"可疑头衔: {person['titles']}")
            print(f"声称成绩: {person['claimed_achievements']}")
            print(f"风险信号: {person['risk_signals']}")

        print("\n详细调查:")
        for person in persons:
            result = investigator.investigate_person(person['name'])
            print(f"  {person['name']}: {result['risk_level']}")


if __name__ == "__main__":
    main()