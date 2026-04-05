#!/usr/bin/env python3
"""
反割韭菜Skill - CLI入口
"""

import sys
import json
from analyzer import AntiMlmAnalyzer


def print_report(report: dict):
    """格式化打印报告"""
    print("\n" + "="*60)
    print("🔍 反割韭菜分析报告")
    print("="*60)

    # 风险评估
    risk = report["risk_assessment"]
    print(f"\n📊 风险评分: {risk['score']}/100")
    print(f"⚠️  风险等级: {risk['level']}")
    print(f"📝 风险概述: {risk['summary']}")

    # 警告信号
    warnings = report["warning_signs"]
    if warnings["high_risk_keywords"]:
        print(f"\n🔴 高风险词汇: {', '.join(warnings['high_risk_keywords'])}")
    if warnings["medium_risk_keywords"]:
        print(f"🟡 中风险词汇: {', '.join(warnings['medium_risk_keywords'])}")
    if warnings["manipulation_tactics"]:
        print(f"🎭 可疑营销套路: {', '.join(warnings['manipulation_tactics'])}")

    # 决策支持
    support = report["decision_support"]
    print(f"\n💡 价格评估: {support['price_reasonableness']}")
    print(f"📋 承诺可信度: {support['claims_verifiability']}")
    print(f"⚡ 风险因素: {support['risk_factors']}")

    # 建议
    print("\n📌 建议:")
    for rec in report["recommendations"]:
        print(f"   • {rec}")

    print("\n" + "="*60)


def main():
    if len(sys.argv) < 2:
        print("用法: python main.py <分析内容>")
        print("示例: python main.py '好消息！某导师亲授，普通人也能轻松月入十万...'")
        sys.exit(1)

    content = " ".join(sys.argv[1:])
    analyzer = AntiMlmAnalyzer()
    report = analyzer.analyze(content, "text")
    print_report(report)

    # 返回退出码（高风险返回1）
    if report["risk_assessment"]["score"] >= 60:
        sys.exit(1)
    elif report["risk_assessment"]["score"] >= 30:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()