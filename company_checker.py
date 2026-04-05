#!/usr/bin/env python3
"""
反割韭菜 - 企业信息查询模块
查询企业/公司是否存在、资质是否合法
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CompanyInfo:
    """企业信息"""
    name: str
    unified_credit_code: Optional[str] = None
    legal_representative: Optional[str] = None
    registered_capital: Optional[str] = None
    establishment_date: Optional[str] = None
    business_status: Optional[str] = None
    registered_address: Optional[str] = None
    business_scope: Optional[str] = None
    verified: bool = False
    risk_signals: List[str] = None

    def __post_init__(self):
        if self.risk_signals is None:
            self.risk_signals = []


class CompanyChecker:
    """企业信息查询器"""

    # 企业风险关键词
    RISK_KEYWORDS = [
        "培训", "教育咨询", "科技", "传媒", "商务信息",
        "网络科技", "信息科技", "文化传播", "广告",
    ]

    # 可疑经营异常
    RISK_STATUS = [
        "吊销", "注销", "清算", "破产", "经营异常",
        "严重违法", "失信被执行人",
    ]

    def __init__(self):
        self.cache = {}

    def extract_company_names(self, text: str) -> List[str]:
        """
        从文本中提取公司名称

        Args:
            text: 输入文本

        Returns:
            公司名称列表
        """
        companies = []

        # 提取模式
        patterns = [
            r'([^（(,，、\s]{5,30})(?:有限公司|有限责任公司|Co\.,?\s*Ltd)',
            r'([^（(,，、\s]{5,30})(?:股份公司|股份有限公司)',
            r'([^（(,，、\s]{5,30})(?:集团|研究院|工作室)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            companies.extend(matches)

        # 去重
        return list(set(companies))

    def check_company(self, company_name: str) -> Dict[str, Any]:
        """
        查询企业信息

        Args:
            company_name: 企业名称

        Returns:
            查询结果
        """
        result = {
            "company_name": company_name,
            "verified": False,
            "info": {},
            "risk_signals": [],
            "search_urls": self._generate_search_urls(company_name),
            "analysis": "未完成验证",
        }

        # 基础验证
        if self._basic_validation(company_name):
            result["verified"] = True
            result["analysis"] = "公司名称格式正常"
        else:
            result["risk_signals"].append("公司名称格式异常")
            result["analysis"] = "公司名称格式可疑"

        # 检测虚假宣传风险
        result["risk_signals"].extend(self._detect_risk_features(company_name))

        # 生成详细报告
        result["report"] = self._generate_report(result)

        return result

    def _basic_validation(self, name: str) -> bool:
        """基础验证"""
        if not name or len(name) < 4:
            return False
        if not re.search(r'公司|企业|集团|Co|Ltd', name):
            return False
        return True

    def _detect_risk_features(self, name: str) -> List[str]:
        """检测风险特征"""
        risks = []

        # 夸大宣传类词汇
        hype_words = ["第一", "最大", "最佳", "最强", "全球", "国际", "中华", "中国"]
        for word in hype_words:
            if word in name:
                risks.append(f"公司名称含夸大宣传词汇: {word}")

        # 蹭知名企业
        famous_companies = ["阿里", "腾讯", "百度", "字节", "京东", "华为", "小米"]
        for famous in famous_companies:
            if famous in name and famous not in ["阿里巴巴", "腾讯", "京东"]:
                risks.append(f"疑似蹭知名企业热度: {famous}")

        return risks

    def _generate_search_urls(self, company_name: str) -> Dict[str, str]:
        """生成查询链接"""
        import urllib.parse
        encoded = urllib.parse.quote(company_name)

        return {
            "天眼查": f"https://www.tianyancha.com/search?key={encoded}",
            "企查查": f"https://www.qcc.com/web/search?key={encoded}",
            "爱企查": f"https://aiqicha.baidu.com/s?q={encoded}",
            "国家企业信用": f"https://www.gsxt.gov.cn/corp-query-search-info.html?keyword={encoded}",
            "百度搜索": f"https://www.baidu.com/s?wd={encoded}+公司",
        }

    def _generate_report(self, result: Dict) -> str:
        """生成分析报告"""
        report_lines = [
            f"企业名称: {result['company_name']}",
            f"验证状态: {'已验证' if result['verified'] else '未验证'}",
        ]

        if result['risk_signals']:
            report_lines.append(f"风险信号: {'; '.join(result['risk_signals'])}")

        report_lines.append(f"查询建议: 请通过上方链接核实企业信息")

        return "\n".join(report_lines)

    def batch_check(self, text: str) -> List[Dict[str, Any]]:
        """
        批量检查文本中提到的企业

        Args:
            text: 输入文本

        Returns:
            检查结果列表
        """
        companies = self.extract_company_names(text)
        results = []

        for company in companies:
            if company not in self.cache:
                self.cache[company] = self.check_company(company)
            results.append(self.cache[company])

        return results

    def analyze_courses_from_page(self, page_data: Dict) -> Dict[str, Any]:
        """
        分析页面中的课程相关企业信息

        Args:
            page_data: 页面结构化数据

        Returns:
            分析结果
        """
        result = {
            "companies_mentioned": [],
            "company_checks": [],
            "overall_risk": "未知",
            "recommendations": [],
        }

        # 提取公司名称
        all_text = ""
        if page_data.get("structured_data"):
            all_text += page_data["structured_data"].get("title", "")
            all_text += page_data["structured_data"].get("description", "")

        if page_data.get("page_content"):
            all_text += page_data["page_content"]

        # 批量检查
        company_checks = self.batch_check(all_text)
        result["company_checks"] = company_checks

        # 统计风险
        risk_count = sum(1 for c in company_checks if c["risk_signals"])
        if risk_count > 0:
            result["overall_risk"] = f"发现{risk_count}个可疑企业"
            result["recommendations"].append("建议核实所有提及企业的真实资质")
        else:
            result["overall_risk"] = "未发现明显异常"

        return result


def main():
    """测试"""
    checker = CompanyChecker()

    test_cases = [
        "某科技有限公司",
        "阿里云计算有限公司",
        "最强国际集团有限公司",
        "某大师创立的财富自由训练营",
    ]

    for company in test_cases:
        print(f"\n{'='*50}")
        print(f"检查: {company}")
        print('='*50)
        result = checker.check_company(company)
        print(f"验证状态: {result['verified']}")
        print(f"风险信号: {result['risk_signals']}")
        print(f"分析: {result['analysis']}")
        print(f"\n查询链接:")
        for name, url in result['search_urls'].items():
            print(f"  {name}: {url}")


if __name__ == "__main__":
    main()