#!/usr/bin/env python3
"""
反割韭菜Skill - 增强版主入口
整合文本分析、网页爬取、企业查询、人物调查、用户画像
"""

import sys
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

# 导入各模块
from analyzer import AntiMlmAnalyzer, AnalysisResult
from web_crawler import WebCrawler
from image_ocr import ImageOCRProcessor
from company_checker import CompanyChecker
from person_investigator import PersonInvestigator
from user_profiler import UserProfiler


class AntiMlmSkill:
    """反割韭菜综合技能"""

    def __init__(self):
        self.analyzer = AntiMlmAnalyzer()
        self.crawler = WebCrawler()
        self.ocr = ImageOCRProcessor()
        self.company_checker = CompanyChecker()
        self.person_investigator = PersonInvestigator()
        self.user_profiler = UserProfiler()

    def analyze(
        self,
        content: str,
        content_type: str = "text",
        user_id: str = "default",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        综合分析入口

        Args:
            content: 分析内容（文本、URL或图片路径）
            content_type: 内容类型 ("text", "url", "image")
            user_id: 用户ID（用于用户画像）
            context: 额外的上下文信息

        Returns:
            综合分析报告
        """
        report = {
            "status": "success",
            "content_type": content_type,
            "content": content[:200] + "..." if len(content) > 200 else content,
            "timestamp": self._get_timestamp(),
        }

        # 1. 基础文本分析
        if content_type == "text":
            text_analysis = self.analyzer.analyze_text(content)
            report["text_analysis"] = self._format_text_analysis(text_analysis)

        elif content_type == "url":
            report["url_analysis"] = self._analyze_url(content)

        elif content_type == "image":
            report["image_analysis"] = self._analyze_image(content)

        # 2. 用户画像分析
        self.user_profiler.add_message(user_id, "user", content)
        user_context = self.user_profiler.get_context_for_analysis(user_id)
        report["user_context"] = user_context

        # 3. 综合评估
        report["final_assessment"] = self._calculate_final_assessment(report)

        # 4. 决策建议
        report["decision_support"] = self._generate_decision_support(report)

        return report

    def _analyze_url(self, url: str) -> Dict[str, Any]:
        """分析URL"""
        result = {
            "url": url,
            "page_data": None,
            "company_analysis": None,
            "person_analysis": None,
        }

        # 抓取页面
        page_data = self.crawler.analyze_url(url)
        result["page_data"] = {
            "success": page_data.get("success", False),
            "domain": page_data.get("domain", ""),
            "domain_risk": page_data.get("domain_risk", ""),
            "title": page_data.get("structured_data", {}).get("title", ""),
            "risk_signals": page_data.get("risk_signals", []),
            "content_preview": page_data.get("page_content", "")[:500] + "..." if len(page_data.get("page_content", "")) > 500 else page_data.get("page_content", ""),
        }

        # 文本分析
        if page_data.get("page_content"):
            text_analysis = self.analyzer.analyze_text(page_data["page_content"])
            result["text_analysis"] = self._format_text_analysis(text_analysis)

        # 企业分析
        if page_data.get("page_content"):
            result["company_analysis"] = self.company_checker.analyze_courses_from_page(page_data)

        # 人物分析
        result["person_analysis"] = self.person_investigator.analyze_instructor_from_page(page_data)

        return result

    def _analyze_image(self, image_path: str) -> Dict[str, Any]:
        """分析图片"""
        result = {
            "image_path": image_path,
            "ocr_available": self.ocr.available,
        }

        if not self.ocr.available:
            result["warning"] = "OCR引擎未安装，无法分析图片内容"
            result["recommendation"] = "请安装: pip install paddleocr paddlepaddle"
            return result

        # OCR分析
        ocr_result = self.ocr.analyze_poster(image_path)
        result["ocr"] = ocr_result

        # 文本分析（如果OCR成功）
        if ocr_result.get("ocr_result", {}).get("text"):
            text = ocr_result["ocr_result"]["text"]
            text_analysis = self.analyzer.analyze_text(text)
            result["text_analysis"] = self._format_text_analysis(text_analysis)

        # 企业分析
        if ocr_result.get("ocr_result", {}).get("text"):
            text = ocr_result["ocr_result"]["text"]
            page_data = {"page_content": text, "structured_data": {}}
            result["company_analysis"] = self.company_checker.analyze_courses_from_page(page_data)

        # 人物分析
        if ocr_result.get("ocr_result", {}).get("text"):
            text = ocr_result["ocr_result"]["text"]
            page_data = {"page_content": text, "structured_data": {}}
            result["person_analysis"] = self.person_investigator.analyze_instructor_from_page(page_data)

        return result

    def _format_text_analysis(self, result: AnalysisResult) -> Dict[str, Any]:
        """格式化文本分析结果"""
        return {
            "risk_score": result.risk_score,
            "risk_level": result.risk_level.value,
            "summary": result.summary,
            "high_risk_keywords": result.high_risk_keywords,
            "medium_risk_keywords": result.medium_risk_keywords,
            "suspicious_tactics": result.suspicious_tactics,
            "red_flags": result.red_flags,
            "recommendations": result.recommendations,
            "details": result.details,
        }

    def _calculate_final_assessment(self, report: Dict) -> Dict[str, Any]:
        """计算最终评估"""
        base_score = 0
        source_bonus = 0
        sources = []

        # 文本分析基础分
        if "text_analysis" in report:
            base_score = report["text_analysis"]["risk_score"]
            sources.append(f"文本风险: {base_score}")

        # URL域名风险
        if "url_analysis" in report and report["url_analysis"].get("page_data"):
            domain_risk = report["url_analysis"]["page_data"].get("domain_risk", "")
            if "可疑" in domain_risk:
                base_score += 15
                sources.append("域名风险: +15")
            elif "可信" in domain_risk:
                base_score -= 10
                sources.append("可信域名: -10")

        # 用户画像调整
        if report.get("user_context"):
            tendency = report["user_context"].get("risk_tendency", "")
            if "易感" in tendency:
                base_score += 10
                sources.append("用户易感: +10")

        # 企业/人物验证
        if "url_analysis" in report:
            company = report["url_analysis"].get("company_analysis", {})
            if company.get("overall_risk") and "异常" not in company["overall_risk"]:
                base_score -= 5
                sources.append("企业核查: -5")

        final_score = min(100, max(0, base_score))

        # 确定最终等级
        if final_score >= 75:
            level = "极高风险 - 极可能是割韭菜"
        elif final_score >= 50:
            level = "高风险 - 很可能是割韭菜"
        elif final_score >= 25:
            level = "中等风险 - 需谨慎判断"
        else:
            level = "较低风险 - 可理性对待"

        return {
            "final_score": final_score,
            "level": level,
            "score_sources": sources,
        }

    def _generate_decision_support(self, report: Dict) -> Dict[str, Any]:
        """生成决策支持"""
        final = report.get("final_assessment", {})
        score = final.get("final_score", 0)

        if score >= 75:
            decision = "强烈建议远离"
            reasons = [
                "检测到典型割韭菜特征",
                "存在虚假宣传嫌疑",
                "可能导致经济损失",
            ]
        elif score >= 50:
            decision = "建议谨慎考虑"
            reasons = [
                "存在多项可疑特征",
                "建议进一步核实",
                "做好风险评估",
            ]
        elif score >= 25:
            decision = "可考虑但需核实"
            reasons = [
                "未发现明显欺诈特征",
                "建议核实课程内容",
                "了解退款政策",
            ]
        else:
            decision = "可理性对待"
            reasons = [
                "未检测到明显风险",
                "仍需保持理性判断",
                "核实讲师资质",
            ]

        # 添加用户画像相关的建议
        user_ctx = report.get("user_context", {})
        if "易感" in user_ctx.get("risk_tendency", ""):
            reasons.append("注意：您可能属于易感人群，建议找信任的人帮忙判断")

        return {
            "decision": decision,
            "reasons": reasons,
        }

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def print_report(report: Dict):
    """格式化打印报告"""
    print("\n" + "="*70)
    print("🔍 反割韭菜综合分析报告")
    print("="*70)

    # 内容类型
    print(f"\n📌 分析类型: {report['content_type']}")
    print(f"⏰ 分析时间: {report['timestamp']}")

    # 文本分析
    if "text_analysis" in report:
        ta = report["text_analysis"]
        print(f"\n📊 风险评分: {ta['risk_score']}/100")
        print(f"⚠️  风险等级: {ta['risk_level']}")
        print(f"📝 摘要: {ta['summary']}")

        if ta["high_risk_keywords"]:
            print(f"\n🔴 高风险词汇: {', '.join(ta['high_risk_keywords'][:5])}")
        if ta["medium_risk_keywords"]:
            print(f"🟡 中风险词汇: {', '.join(ta['medium_risk_keywords'][:5])}")
        if ta["suspicious_tactics"]:
            print(f"🎭 可疑套路: {', '.join(ta['suspicious_tactics'])}")
        if ta["red_flags"]:
            print(f"🚩 红旗信号: {', '.join(ta['red_flags'])}")

    # URL分析
    if "url_analysis" in report:
        ua = report["url_analysis"]
        print(f"\n🌐 URL分析: {ua['url']}")
        if ua.get("page_data"):
            pd = ua["page_data"]
            print(f"   域名: {pd['domain']}")
            print(f"   域名风险: {pd['domain_risk']}")
            if pd.get("risk_signals"):
                print(f"   页面风险: {', '.join(pd['risk_signals'][:3])}")

        if ua.get("company_analysis"):
            ca = ua["company_analysis"]
            print(f"\n🏢 企业分析: {ca.get('overall_risk', '未知')}")

        if ua.get("person_analysis"):
            pa = ua["person_analysis"]
            print(f"\n👤 人物分析: {pa.get('total_risk_level', '未知')}")

    # 图片分析
    if "image_analysis" in report:
        ia = report["image_analysis"]
        print(f"\n🖼️ 图片分析: {ia['image_path']}")
        if not ia.get("ocr_available"):
            print(f"   ⚠️ {ia.get('warning', 'OCR不可用')}")
        elif ia.get("ocr", {}).get("ocr_result", {}).get("text"):
            ocr_text = ia["ocr"]["ocr_result"]["text"][:200]
            print(f"   识别文字: {ocr_text}...")

    # 用户画像
    if report.get("user_context"):
        uc = report["user_context"]
        print(f"\n👤 用户画像: {uc.get('risk_tendency', '未知')}")
        if uc.get("interests"):
            print(f"   兴趣领域: {', '.join(uc['interests'])}")

    # 最终评估
    final = report.get("final_assessment", {})
    print(f"\n{'='*70}")
    print(f"🎯 最终评分: {final.get('final_score', 0)}/100")
    print(f"📍 最终等级: {final.get('level', '未知')}")
    if final.get("score_sources"):
        print(f"   评分来源: {'; '.join(final['score_sources'])}")

    # 决策支持
    ds = report.get("decision_support", {})
    print(f"\n💡 决策建议: {ds.get('decision', '未知')}")
    for reason in ds.get("reasons", []):
        print(f"   • {reason}")

    print("\n" + "="*70)


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python enhanced_main.py text <文本内容>")
        print("  python enhanced_main.py url <URL>")
        print("  python enhanced_main.py image <图片路径>")
        print("\n示例:")
        print("  python enhanced_main.py text '好消息！某导师带你躺赚，月入十万...'")
        print("  python enhanced_main.py url 'https://example.com/course'")
        print("  python enhanced_main.py image './poster.jpg'")
        sys.exit(1)

    content_type = sys.argv[1]
    content = sys.argv[2] if len(sys.argv) > 2 else ""

    if not content:
        print("错误: 未提供分析内容")
        sys.exit(1)

    skill = AntiMlmSkill()
    report = skill.analyze(content, content_type)
    print_report(report)

    # 返回码
    score = report.get("final_assessment", {}).get("final_score", 0)
    if score >= 75:
        sys.exit(3)
    elif score >= 50:
        sys.exit(2)
    elif score >= 25:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()