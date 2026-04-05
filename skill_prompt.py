#!/usr/bin/env python3
"""
反割韭菜Skill - Prompt框架 v2.2
为多模态模型提供分析框架和判断逻辑
覆盖12大割韭菜场景 + 用户经济匹配 + 免费资源推荐
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    VERY_HIGH = "极高风险"
    HIGH = "高风险"
    MEDIUM = "中等风险"
    LOW = "较低风险"
    UNKNOWN = "未知"


# ============================================================
# 免费优质课程资源库
# ============================================================

FREE_COURSES = {
    # ===== 编程开发类 =====
    "编程开发": {
        "Python": [
            {"name": "Python入门", "platform": "慕课网", "url": "https://www.imooc.com/learn/98", "price": "免费", "level": "入门"},
            {"name": "Python基础教程", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=Python%E5%85%A5%E9%97%A8", "price": "免费", "level": "入门"},
            {"name": "廖雪峰Python教程", "platform": "官网", "url": "https://www.liaoxuefeng.com/wiki/1016959663602400", "price": "免费", "level": "入门到进阶"},
            {"name": "Python官方文档", "platform": "官网", "url": "https://docs.python.org/zh-cn/3/tutorial/", "price": "免费", "level": "官方教程"},
        ],
        "Java": [
            {"name": "Java基础入门", "platform": "慕课网", "url": "https://www.imooc.com/learn/85", "price": "免费", "level": "入门"},
            {"name": "Java学习路线", "platform": "阿里云开发者社区", "url": "https://developer.aliyun.com/roadmap/java", "price": "免费", "level": "完整学习路线"},
        ],
        "Web前端": [
            {"name": "前端入门", "platform": "慕课网", "url": "https://www.imooc.com/learn/300", "price": "免费", "level": "入门"},
            {"name": "Web前端学习路线", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=%E5%89%8D%E7%AB%AF%E5%85%A5%E9%97%A8", "price": "免费", "level": "完整路线"},
        ],
        "全栈": [
            {"name": "Web全栈开发", "platform": "Coursera", "url": "https://www.coursera.org/specializations/full-stack", "price": "免费旁听", "level": "进阶"},
        ],
    },

    # ===== 数据科学类 =====
    "数据科学": {
        "数据分析": [
            {"name": "数据分析与可视化", "platform": "学习强国", "url": "https://www.xuexi.cn/", "price": "免费", "level": "入门"},
            {"name": "Python数据分析", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=Python%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90", "price": "免费", "level": "入门到进阶"},
            {"name": "SQL基础", "platform": "LeetCode", "url": "https://leetcode.cn/leetbook/detail/sql/", "price": "免费", "level": "入门"},
        ],
        "人工智能": [
            {"name": "机器学习", "platform": "吴恩达 Coursera", "url": "https://www.coursera.org/learn/machine-learning", "price": "免费旁听", "level": "经典课程"},
            {"name": "深度学习", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=%E6%B7%B1%E5%BA%A6%E5%AD%A6%E4%B9%A0", "price": "免费", "level": "入门到进阶"},
        ],
        "大数据": [
            {"name": "大数据学习路线", "platform": "阿里云开发者社区", "url": "https://developer.aliyun.com/roadmap/bigdata", "price": "免费", "level": "完整路线"},
        ],
    },

    # ===== 设计类 =====
    "设计类": {
        "UI设计": [
            {"name": "UI设计基础", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=UI%E8%AE%BE%E8%AE%A1%E5%85%A5%E9%97%A8", "price": "免费", "level": "入门"},
            {"name": "设计基础理论", "platform": "网易公开课", "url": "https://open.163.com/newview/mic-course/", "price": "免费", "level": "理论"},
        ],
        "平面设计": [
            {"name": "PS教程", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=PS%E6%95%99%E7%A8%8B", "price": "免费", "level": "入门"},
            {"name": "设计原理", "platform": "网易公开课", "url": "https://open.163.com/newview/mic-course/", "price": "免费", "level": "理论"},
        ],
        "视频剪辑": [
            {"name": "PR剪辑教程", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=PR%E5%89%AA%E8%BE%91%E6%95%99%E7%A8%8B", "price": "免费", "level": "入门"},
            {"name": "剪映教程", "platform": "抖音创作课堂", "url": "https://creator.douyin.com/college", "price": "免费", "level": "入门"},
        ],
    },

    # ===== 营销运营类 =====
    "营销运营": {
        "短视频运营": [
            {"name": "抖音创作者学院", "platform": "抖音", "url": "https://creator.douyin.com/college", "price": "免费", "level": "官方教程"},
            {"name": "快手光合学院", "platform": "快手", "url": "https://guanghe.kuaishou.com/", "price": "免费", "level": "官方教程"},
            {"name": "B站创作中心", "platform": "B站", "url": "https://member.bilibili.com/", "price": "免费", "level": "官方教程"},
            {"name": "小红书博主学院", "platform": "小红书", "url": "https://creator.xiaohongshu.com/", "price": "免费", "level": "官方教程"},
        ],
        "电商运营": [
            {"name": "淘宝大学", "platform": "淘宝", "url": "https://daxue.taobao.com/", "price": "免费", "level": "官方教程"},
            {"name": "京东商家学习中心", "platform": "京东", "url": "https://school.jd.com/", "price": "免费", "level": "官方教程"},
        ],
        "新媒体运营": [
            {"name": "微信公开课", "platform": "微信", "url": "https://open.weixin.qq.com/", "price": "免费", "level": "官方教程"},
        ],
    },

    # ===== 投资理财类 =====
    "投资理财": {
        "股票": [
            {"name": "证监会投资者教育", "platform": "证监会", "url": "https://www.csrc.gov.cn/pub/csrc_jyzx/", "price": "免费", "level": "官方教育"},
            {"name": "上交所投教专区", "platform": "上交所", "url": "https://edu.sse.com.cn/", "price": "免费", "level": "官方教程"},
            {"name": "深交所投教专区", "platform": "深交所", "url": "https://www.szse.cn/education/", "price": "免费", "level": "官方教程"},
        ],
        "基金": [
            {"name": "天天基金网学院", "platform": "天天基金", "url": "https://fund.eastmoney.com/college.html", "price": "免费", "level": "基金知识"},
        ],
        "理财基础": [
            {"name": "理财小知识", "platform": "学习强国", "url": "https://www.xuexi.cn/", "price": "免费", "level": "入门"},
            {"name": "金融知识普及", "platform": "中国人民银行", "url": "http://www.pbc.gov.cn/", "price": "免费", "level": "官方教育"},
        ],
    },

    # ===== 副业技能类 =====
    "副业技能": {
        "写作变现": [
            {"name": "写作基础", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=%E5%86%99%E4%BD%9C%E5%85%A5%E9%97%A8", "price": "免费", "level": "入门"},
            {"name": "知乎写作课", "platform": "知乎", "url": "https://www.zhihu.com/", "price": "免费内容", "level": "平台规则"},
        ],
        "配音兼职": [
            {"name": "配音基础教程", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=%E9%85%8D%E9%9F%B3%E5%85%A5%E9%97%A8", "price": "免费", "level": "入门"},
        ],
        "摄影": [
            {"name": "摄影基础", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=%E6%91%84%E5%BD%B1%E5%85%A5%E9%97%A8", "price": "免费", "level": "入门"},
        ],
    },

    # ===== 健康类 =====
    "健康": {
        "减肥健身": [
            {"name": "健身教程", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=%E5%81%A5%E8%BA%AB%E5%85%A5%E9%97%A8", "price": "免费", "level": "入门"},
            {"name": "keep教程", "platform": "Keep", "url": "https://www.gotokeep.com/", "price": "免费基础", "level": "入门"},
        ],
    },

    # ===== 求职就业类 =====
    "求职就业": {
        "简历面试": [
            {"name": "简历写法", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=%E7%AE%80%E5%8E%9%E8%AF%BB%E6%B3%95", "price": "免费", "level": "技巧"},
            {"name": "面试技巧", "platform": "B站", "url": "https://search.bilibili.com/all?keyword=%E9%9D%A2%E8%AF%95%E6%8A%80%E5%B7%A7", "price": "免费", "level": "技巧"},
        ],
        "职业规划": [
            {"name": "职业规划", "platform": "学习强国", "url": "https://www.xuexi.cn/", "price": "免费", "level": "职业发展"},
        ],
    },
}


# ============================================================
# 优质平台白名单（官方免费资源）
# ============================================================

TRUSTED_PLATFORMS = {
    "学习强国": {"url": "https://www.xuexi.cn/", "type": "官方综合学习", "reliability": 10},
    "中国大学MOOC": {"url": "https://www.icourse163.org/", "type": "高校课程", "reliability": 10},
    "慕课网": {"url": "https://www.imooc.com/", "type": "IT技能课程", "reliability": 8},
    "B站": {"url": "https://www.bilibili.com/", "type": "综合学习", "reliability": 7},
    "网易公开课": {"url": "https://open.163.com/", "type": "名校公开课", "reliability": 9},
    "网易云课堂": {"url": "https://study.163.com/", "type": "职业技能", "reliability": 8},
    "Coursera": {"url": "https://www.coursera.org/", "type": "国际名校课程", "reliability": 9},
    "腾讯课堂": {"url": "https://ke.qq.com/", "type": "综合课程", "reliability": 7},
    "知乎": {"url": "https://www.zhihu.com/", "type": "知识分享", "reliability": 6},
    "阿里云开发者社区": {"url": "https://developer.aliyun.com/", "type": "技术学习", "reliability": 9},
    "抖音创作者学院": {"url": "https://creator.douyin.com/college", "type": "短视频运营", "reliability": 9},
    "快手光合学院": {"url": "https://guanghe.kuaishou.com/", "type": "短视频运营", "reliability": 9},
    "小红书创作学院": {"url": "https://creator.xiaohongshu.com/", "type": "内容创作", "reliability": 8},
    "淘宝大学": {"url": "https://daxue.taobao.com/", "type": "电商运营", "reliability": 9},
    "京东商家学习中心": {"url": "https://school.jd.com/", "type": "电商运营", "reliability": 9},
    "证监会投资者教育": {"url": "https://www.csrc.gov.cn/pub/csrc_jyzx/", "type": "投资教育", "reliability": 10},
    "上交所投教专区": {"url": "https://edu.sse.com.cn/", "type": "股票投资", "reliability": 10},
    "深交所投教专区": {"url": "https://www.szse.cn/education/", "type": "股票投资", "reliability": 10},
}


# ============================================================
# 割韭菜场景分类 - 12大高发场景
# ============================================================

SCAM_SCENARIOS = {
    "课程培训": {
        "keywords": ["课程", "培训", "训练营", "大师课", "实战班"],
        "high_risk": ["轻松月入", "年薪百万", "财富自由"],
        "examples": ["Python入门课", "短视频运营课", "写作变现课"],
    },
    "投资理财": {
        "keywords": ["投资", "理财", "炒股", "基金", "股票", "收益率"],
        "high_risk": ["稳赚不赔", "内幕消息", "保本", "日赚", "月收益"],
        "warning": "正规投资不会承诺收益",
    },
    "电商创业": {
        "keywords": ["电商", "开店", "淘宝", "拼多多", "直播带货", "抖音变现"],
        "high_risk": ["日出千单", "月入过万", "无货源", "一件代发"],
        "warning": "电商需要真实运营能力，非暴富途径",
    },
    "副业兼职": {
        "keywords": ["副业", "兼职", "在家赚钱", "打字员", "快递录入"],
        "high_risk": ["简单高薪", "日结", "现结", "适合宝妈", "轻松自由"],
        "warning": "高薪兼职往往存在陷阱",
    },
    "健康减肥": {
        "keywords": ["减肥", "瘦身", "健身", "美容", "保健品", "养生"],
        "high_risk": ["一周瘦十斤", "不节食不运动", "纯天然", "无效退款"],
        "warning": "健康产品需谨慎，避免三无产品",
    },
    "情感挽回": {
        "keywords": ["挽回", "复合", "恋爱", "脱单", "PUA", "撩妹"],
        "high_risk": ["100%挽回", "包成功", "私密教学", "导师1对1"],
        "warning": "情感课程往往利用焦虑营销",
    },
    "学历考证": {
        "keywords": ["学历", "考证", "包过", "代考", "VIP班", "保过"],
        "high_risk": ["不过退款", "内部渠道", "名额有限", "最后机会"],
        "warning": "学历提升无捷径，正规渠道最可靠",
    },
    "创业孵化": {
        "keywords": ["创业", "加盟", "招商", "代理", "合伙人", "联创"],
        "high_risk": ["小投资大回报", "总部扶持", "轻松当老板", "年入百万"],
        "warning": "创业有风险，加盟需核实特许经营资质",
    },
    "求职就业": {
        "keywords": ["求职", "简历", "面试", "内推", "offer", "猎头"],
        "high_risk": ["保offer", "不过退款", "内部推荐", "年薪翻倍"],
        "warning": "正规求职不收费，收费的往往是骗局",
    },
    "传销拉人头": {
        "keywords": ["拉人头", "发展下线", "团队计酬", "分销", "代理", "层级"],
        "high_risk": ["躺赚", "管道收入", "被动收益", "裂变", "躺赢"],
        "warning": "拉人头模式涉嫌违法，务必远离",
    },
    "数字货币": {
        "keywords": ["区块链", "虚拟货币", "数字资产", "BTC", "ETH", "炒币"],
        "high_risk": ["百倍币", "ICO", "IEO", "私募", "埋伏", "一级市场"],
        "warning": "虚拟货币风险极高，很多是资金盘",
    },
    "风水玄学": {
        "keywords": ["风水", "算命", "易经", "起名", "改运", "化解"],
        "high_risk": ["大师", "高人", "密传", "开光", "转运", "招财"],
        "warning": "封建迷信不可取，理性对待命运",
    },
}


# ============================================================
# 课程价格数据库 - 市场参考价
# ============================================================

COURSE_PRICE_BENCHMARKS = {
    # 技能培训类
    "编程开发": {
        "beginner": {"min": 0, "max": 2000, "reasonable": (500, 1500), "description": "入门课程"},
        "intermediate": {"min": 1000, "max": 5000, "reasonable": (2000, 4000), "description": "进阶课程"},
        "advanced": {"min": 3000, "max": 15000, "reasonable": (5000, 10000), "description": "高级课程"},
    },
    "数据科学": {
        "beginner": {"min": 0, "max": 2000, "reasonable": (500, 1500), "description": "入门课程"},
        "intermediate": {"min": 1500, "max": 6000, "reasonable": (3000, 5000), "description": "进阶课程"},
        "advanced": {"min": 5000, "max": 20000, "reasonable": (8000, 15000), "description": "高级课程"},
    },
    "设计类": {
        "beginner": {"min": 0, "max": 1500, "reasonable": (300, 1000), "description": "入门课程"},
        "intermediate": {"min": 1000, "max": 4000, "reasonable": (1500, 3000), "description": "进阶课程"},
        "advanced": {"min": 3000, "max": 10000, "reasonable": (5000, 8000), "description": "高级课程"},
    },
    "营销运营": {
        "beginner": {"min": 0, "max": 1000, "reasonable": (200, 800), "description": "入门课程"},
        "intermediate": {"min": 800, "max": 3000, "reasonable": (1000, 2500), "description": "进阶课程"},
        "advanced": {"min": 2000, "max": 8000, "reasonable": (3000, 6000), "description": "高级课程"},
    },
    "短视频/直播": {
        "beginner": {"min": 0, "max": 800, "reasonable": (1, 500), "description": "入门课程"},
        "intermediate": {"min": 500, "max": 3000, "reasonable": (800, 2000), "description": "进阶课程"},
        "advanced": {"min": 2000, "max": 10000, "reasonable": (3000, 6000), "description": "高级课程"},
    },
    "写作变现": {
        "beginner": {"min": 0, "max": 500, "reasonable": (1, 300), "description": "入门课程"},
        "intermediate": {"min": 300, "max": 2000, "reasonable": (500, 1500), "description": "进阶课程"},
        "advanced": {"min": 1500, "max": 5000, "reasonable": (2000, 4000), "description": "高级课程"},
    },
    "电商运营": {
        "beginner": {"min": 0, "max": 1000, "reasonable": (200, 800), "description": "入门课程"},
        "intermediate": {"min": 800, "max": 4000, "reasonable": (1500, 3000), "description": "进阶课程"},
        "advanced": {"min": 3000, "max": 10000, "reasonable": (4000, 7000), "description": "高级课程"},
    },
    # 投资理财类
    "股票投资": {
        "beginner": {"min": 0, "max": 3000, "reasonable": (500, 2000), "description": "入门课程"},
        "intermediate": {"min": 2000, "max": 10000, "reasonable": (3000, 6000), "description": "进阶课程"},
        "advanced": {"min": 5000, "max": 30000, "reasonable": (8000, 20000), "description": "高级课程"},
    },
    "基金理财": {
        "beginner": {"min": 0, "max": 1000, "reasonable": (1, 500), "description": "入门课程"},
        "intermediate": {"min": 500, "max": 3000, "reasonable": (800, 2000), "description": "进阶课程"},
        "advanced": {"min": 2000, "max": 8000, "reasonable": (3000, 6000), "description": "高级课程"},
    },
    # 副业技能类
    "配音兼职": {
        "beginner": {"min": 0, "max": 2000, "reasonable": (300, 1000), "description": "入门课程"},
        "intermediate": {"min": 1000, "max": 5000, "reasonable": (2000, 4000), "description": "进阶课程"},
        "advanced": {"min": 3000, "max": 10000, "reasonable": (5000, 8000), "description": "高级课程"},
    },
    "摄影视频": {
        "beginner": {"min": 0, "max": 1500, "reasonable": (300, 800), "description": "入门课程"},
        "intermediate": {"min": 800, "max": 4000, "reasonable": (1500, 3000), "description": "进阶课程"},
        "advanced": {"min": 3000, "max": 15000, "reasonable": (5000, 10000), "description": "高级课程"},
    },
    # 健康类
    "减肥健身": {
        "beginner": {"min": 0, "max": 2000, "reasonable": (500, 1500), "description": "入门课程"},
        "intermediate": {"min": 1500, "max": 5000, "reasonable": (2000, 4000), "description": "进阶课程"},
        "advanced": {"min": 4000, "max": 15000, "reasonable": (5000, 10000), "description": "高级课程"},
    },
    # 默认值
    "default": {
        "beginner": {"min": 0, "max": 1000, "reasonable": (200, 800), "description": "入门课程"},
        "intermediate": {"min": 800, "max": 3000, "reasonable": (1500, 2500), "description": "进阶课程"},
        "advanced": {"min": 2500, "max": 10000, "reasonable": (4000, 7000), "description": "高级课程"},
    },
}


# ============================================================
# 收入分层与消费能力
# ============================================================

INCOME_TIERS = {
    "低收入": {
        "monthly_income": (0, 3000),
        "annual_income": (0, 36000),
        "description": "月薪3K以下",
        "course_affordability": {
            "low_risk_max": 500,       # 课程价格上限
            "medium_risk_max": 1500,   # 超过此价需谨慎
            "high_risk_min": 2000,     # 超过此价基本是割韭菜
        },
        "warning": "谨慎消费，优先选择免费或低价资源",
    },
    "中低收入": {
        "monthly_income": (3000, 6000),
        "annual_income": (36000, 72000),
        "description": "月薪3K-6K",
        "course_affordability": {
            "low_risk_max": 1000,
            "medium_risk_max": 3000,
            "high_risk_min": 5000,
        },
        "warning": "理性消费，不建议贷款学习",
    },
    "中等收入": {
        "monthly_income": (6000, 12000),
        "annual_income": (72000, 144000),
        "description": "月薪6K-12K",
        "course_affordability": {
            "low_risk_max": 2000,
            "medium_risk_max": 5000,
            "high_risk_min": 10000,
        },
        "warning": "可以适度投资自己，但需核实课程质量",
    },
    "中等偏高": {
        "monthly_income": (12000, 25000),
        "annual_income": (144000, 300000),
        "description": "月薪12K-25K",
        "course_affordability": {
            "low_risk_max": 5000,
            "medium_risk_max": 15000,
            "high_risk_min": 25000,
        },
        "warning": "投资自己需关注性价比",
    },
    "高收入": {
        "monthly_income": (25000, 50000),
        "annual_income": (300000, 600000),
        "description": "月薪25K-50K",
        "course_affordability": {
            "low_risk_max": 10000,
            "medium_risk_max": 30000,
            "high_risk_min": 50000,
        },
        "warning": "高端课程也需核实质量",
    },
    "高净值": {
        "monthly_income": (50000, float('inf')),
        "annual_income": (600000, float('inf')),
        "description": "月薪50K以上",
        "course_affordability": {
            "low_risk_max": 50000,
            "medium_risk_max": 100000,
            "high_risk_min": 100000,
        },
        "warning": "高端课程更需关注实质内容",
    },
}


# ============================================================
# 风险关键词库
# ============================================================

class RiskKeywords:
    """风险关键词库"""

    # 收益承诺类（极高风险）
    INCOME_PROMISE = [
        "躺赚", "日入过万", "月入十万", "年薪百万", "财富自由",
        "稳赚不赔", "100%赚钱", "保赚", "一定赚", "日赚", "月赚",
        "睡后收入", "被动收入", "快速致富", "一本万利", "低成本高回报",
    ]

    # 稀缺营销类（高风险）
    SCARCITY_MARKETING = [
        "限时特价", "名额有限", "错过等一年", "即将涨价", "限量名额",
        "仅限今天", "最后机会", "紧急招募", "停止招生", "恢复原价",
    ]

    # 身份包装类（中高风险）
    IDENTITY_PACKAGING = [
        "大师", "教父", "之神", "第一人", "创始之神", "领袖",
        "传奇", "顶级", "天花板", "鼻祖", "之父", "大咖",
    ]

    # 焦虑制造类（高风险）
    ANXIETY_CREATION = [
        "普通人也能", "改变命运", "逆袭人生", "不学习就被淘汰",
        "跟不上时代", "即将失业", "被同龄人抛弃", "别让孩子输",
        "对不起家人", "阶层固化",
    ]

    # 截图诱导类（高风险）
    SCREENSHOT_INDUCTION = [
        "收入截图", "转账截图", "聊天截图", "学员反馈", "提现截图",
        "晒单", "战绩", "喜报", "成交记录",
    ]

    # 拉人头/传销类（极高风险）
    PYRAMID_SCHEME = [
        "拉人头", "发展下线", "团队计酬", "层级", "分销",
        "代理", "加盟", "合伙人", "联创", "推荐奖励", "邀请返利",
    ]

    # 入门费用类（红旗）
    ENTRY_FEE = [
        "入门费", "加盟费", "保证金", "会员费", "代理费",
        "培训费", "资料费", "激活费", "认证费", "年费",
    ]


# ============================================================
# 分析框架 Prompt
# ============================================================

ANALYSIS_PROMPT_TEMPLATE = """
# 反割韭菜分析框架 v2.1

你是一个专业的反割韭菜分析助手。请对用户提供的课程宣传内容进行多维度综合分析。

## 核心分析理念

**同样是4999元的课程：**
- 对月薪3万的人：可能是合理投资
- 对月薪5千的人：可能是割韭菜
- 对欠债累累的人：绝对是割韭菜

**因此，分析必须结合用户的经济情况！**

---

## 一、识别割韭菜场景

请先判断属于以下哪个场景（可能多个）：
{scam_scenarios}

---

## 二、文本风险分析

### 2.1 高风险关键词检测

**收益承诺类（极高风险-权重20）：**
躺赚、日入过万、月入十万、年薪百万、财富自由、稳赚不赔、100%赚钱、保赚、快速致富

**拉人头/传销类（极高风险-权重30）：**
拉人头、发展下线、团队计酬、层级、分销、代理、加盟、合伙人、联创、推荐奖励

**入门费用类（红旗-权重25）：**
入门费、加盟费、保证金、会员费、代理费、培训费、资料费、激活费

**焦虑制造类（高风险-权重15）：**
普通人也能、改变命运、逆袭人生、不学习就被淘汰、被同龄人抛弃

**截图诱导类（高风险-权重15）：**
收入截图、转账截图、聊天截图、学员反馈、提现截图、晒单

**稀缺营销类（中高风险-权重10）：**
限时特价、名额有限、错过等一年、仅限今天、最后机会

**身份包装类（中高风险-权重5）：**
大师、教父、之神、第一人、领袖、传奇、天花板

### 2.2 可疑营销套路

- 制造焦虑、虚假稀缺、夸大宣传
- 情感绑架、截图诱导、饥饿营销
- 权威背书、社会证明

### 2.3 红旗信号

以下任一特征出现 = 极高风险/骗局：
1. 拉人头、发展下线、层层返利
2. 收取入门费、加盟费
3. 承诺躺赚、日入过万
4. 内部消息、特殊渠道

---

## 三、价格合理性分析

### 3.1 提取课程价格

从文本中提取价格信息（单位：元）

### 3.2 市场参考价对比

| 课程类型 | 入门价 | 合理价 | 进阶层 | 高级课 |
|---------|--------|--------|--------|--------|
| 编程开发 | 0-2K | 500-1.5K | 2K-4K | 5K-1万 |
| 短视频运营 | 0-1K | 200-800 | 800-2K | 3K-6K |
| 电商创业 | 0-1K | 200-800 | 1.5K-3K | 4K-7K |
| 股票投资 | 0-3K | 500-2K | 3K-6K | 8K-2万 |
| 写作变现 | 0-500 | 1-300 | 500-1.5K | 2K-4K |

**价格虚高判断：**
- 入门课 > 2000元：价格偏高
- 入门课 > 5000元：几乎肯定是割韭菜
- 承诺暴富的课程无论价格都是割韭菜

### 3.3 用户消费能力匹配

**收入分层（可主动询问用户）：**

| 收入层级 | 月薪范围 | 建议课程上限 |
|---------|---------|-------------|
| 低收入 | 0-3K | 500元以下 |
| 中低收入 | 3K-6K | 1000元以下 |
| 中等收入 | 6K-12K | 2000元以下 |
| 中高收入 | 12K-25K | 5000元以下 |
| 高收入 | 25K-50K | 1万元以下 |
| 高净值 | 50K+ | 根据课程质量判断 |

**价格与收入匹配原则：**
- 课程价格 > 月收入的30%：需谨慎
- 课程价格 > 月收入的50%：几乎都是割韭菜
- 课程价格 > 月收入：基本是骗局

---

## 四、免费优质资源推荐（重要！）

**当检测到用户想学习某个技能时，必须主动推荐免费资源！**

### 4.1 优质免费平台白名单

| 平台 | 类型 | 可靠性 | 说明 |
|------|------|--------|------|
| 学习强国 | 官方综合 | ⭐⭐⭐⭐⭐ | 时政、法律、职业技能全免费 |
| 中国大学MOOC | 高校课程 | ⭐⭐⭐⭐⭐ | 985/211高校课程，含证书 |
| 慕课网 | IT技能 | ⭐⭐⭐⭐ | 程序员职业技能课程 |
| B站 | 综合学习 | ⭐⭐⭐⭐ | 各领域教程丰富 |
| 网易公开课 | 名校公开 | ⭐⭐⭐⭐⭐ | TED、国内外名校课程 |
| 网易云课堂 | 职业技能 | ⭐⭐⭐⭐ | 实用技能课程 |
| Coursera | 国际课程 | ⭐⭐⭐⭐⭐ | 斯坦福/耶鲁等名校课程 |
| 证监会投教 | 投资教育 | ⭐⭐⭐⭐⭐ | 官方证券投资知识 |
| 抖音创作者学院 | 短视频 | ⭐⭐⭐⭐⭐ | 官方免费短视频教程 |
| 快手光合学院 | 短视频 | ⭐⭐⭐⭐⭐ | 官方免费直播/运营教程 |

### 4.2 主题匹配推荐

根据用户想学的内容，自动匹配免费资源：

| 用户想学 | 免费资源 |
|---------|---------|
| Python/编程 | 廖雪峰Python教程(免费)、慕课网Python课 |
| 短视频/直播 | 抖音创作者学院、快手光合学院(全免费) |
| 电商运营 | 淘宝大学、京东商家学习中心(官方免费) |
| 数据分析 | B站SQL/Python教程、Coursera旁听 |
| 机器学习/AI | 吴恩达机器学习(Coursera免费旁听) |
| 写作变现 | B站写作教程、知乎免费内容 |
| 投资理财 | 证监会投教、上交所/深交所投教专区 |
| 求职面试 | B站简历/面试教程 |
| 设计/剪辑 | B站PS/PR/剪映教程(海量免费) |
| 健身减肥 | Keep(基础课程免费)、B站健身教程 |

### 4.3 推荐原则

**必须遵循：**
1. 优先推荐**官方免费资源**（学习强国、官方学院）
2. 推荐**权威平台**的高质量内容
3. 提供具体的**课程名称和链接**
4. 说明**免费原因**（官方补贴/平台推广/引流）
5. 即使付费课程，也要先推荐免费替代方案

**话术模板：**
- "其实这个内容有很好的免费学习渠道，推荐您先看这些："
- "不必花冤枉钱，B站/慕课上有非常系统的免费教程："
- "官方出了免费课程，比这个靠谱多了："

---

## 五、用户画像分析

### 5.1 主动询问（必要时）

在分析时可询问用户：
1. "您的月收入大概是多少？"
2. "您目前有负债吗？"
3. "您为什么想学这个课程？"
4. "您之前了解过这方面的知识吗？"

### 5.2 易感人群特征

**高易感性（需特别警惕）：**
- 急切想赚钱/还债
- 缺乏相关经验
- 急于求成
- 表现出焦虑
- 之前被割过韭菜

**低易感性：**
- 理性分析
- 有相关经验
- 不急切
- 谨慎询问

---

## 六、综合评估

### 6.1 评分标准

**基础风险分（文本分析）：**
- 高风险词 × 15分
- 拉人头/传销词 × 30分
- 入门费词 × 25分
- 焦虑制造 × 15分
- 截图诱导 × 15分
- 稀缺营销 × 10分
- 身份包装 × 5分

**价格虚高加分：**
- 价格超出市场合理价3倍 +20分
- 价格超出用户承受范围 +15分

**最终等级：**
- ≥75分 或 检测到传销特征：极高风险
- 50-74分：高风险
- 25-49分：中等风险
- <25分：较低风险

### 6.2 个性化建议

根据用户收入和课程价格，给出具体建议：
- "以您的收入，这个课程价格偏高，建议先看免费资源"
- "这个课程对您来说在承受范围内，但需核实课程质量"
- "建议不要贷款学习这类课程"

---

## 七、输出格式

```json
{{
  "status": "success",
  "scam_scenario": ["识别到的场景"],
  "risk_assessment": {{
    "score": 0-100,
    "level": "极高风险/高风险/中等风险/较低风险",
    "summary": "一句话总结"
  }},
  "price_analysis": {{
    "detected_price": "检测到的价格",
    "market_price": "市场参考价",
    "price_ratio": "溢价倍数",
    "is_overpriced": true/false,
    "overprice_reason": "溢价原因"
  }},
  "free_alternatives": {{
    "recommended": true/false,
    "platforms": ["推荐平台列表"],
    "courses": [{{ "name": "课程名", "platform": "平台", "url": "链接", "price": "免费" }}],
    "reason": "为什么推荐这些"
  }},
  "user_matching": {{
    "user_income_tier": "用户收入层级（如果已知）",
    "affordability": "可承受性评估",
    "recommendation": "针对该用户的具体建议"
  }},
  "warning_signals": {{
    "high_risk_keywords": [],
    "suspicious_tactics": [],
    "red_flags": []
  }},
  "decision_support": {{
    "decision": "强烈远离/高度警惕/谨慎考虑/可理性对待",
    "reasons": [],
    "personalized_advice": "针对该用户的个性化建议"
  }}
}}
```

---

## 七、分析流程建议

1. **接收用户输入** → 提取文本、识别场景
2. **文本风险分析** → 检测关键词、计算基础分
3. **价格分析** → 提取价格、对比市场价
4. **询问用户情况**（如需要）→ 了解收入、学习目的
5. **综合评估** → 结合价格+收入给出个性化建议
6. **输出报告** → JSON格式 + 口语化解释

---

## 八、关键提醒

1. **价格不是唯一标准**：低价课也可能割韭菜（收入门费、卖资料）
2. **收入影响判断**：同一个课程，对不同收入的人建议不同
3. **场景化分析**：投资理财类课程的"合理价格"比技能课高
4. **红旗优先**：一旦发现传销特征，立即警告
5. **保护弱势用户**：对低收入/欠债用户更加谨慎
"""


# ============================================================
# 风险评分引擎
# ============================================================

class RiskScorer:
    """风险评分器"""

    def __init__(self):
        self.patterns = {
            "income_promise": RiskKeywords.INCOME_PROMISE,
            "scarcity_marketing": RiskKeywords.SCARCITY_MARKETING,
            "identity_packaging": RiskKeywords.IDENTITY_PACKAGING,
            "anxiety_creation": RiskKeywords.ANXIETY_CREATION,
            "screenshot_induction": RiskKeywords.SCREENSHOT_INDUCTION,
            "pyramid_scheme": RiskKeywords.PYRAMID_SCHEME,
            "entry_fee": RiskKeywords.ENTRY_FEE,
        }

    def score_text(self, text: str) -> Dict[str, Any]:
        """对文本进行风险评分"""
        import re

        findings = {k: [] for k in self.patterns}

        # 检测各类关键词
        for category, keywords in self.patterns.items():
            for keyword in keywords:
                if keyword in text:
                    findings[category].append(keyword)

        # 去重
        for k in findings:
            findings[k] = list(set(findings[k]))

        # 计算分数
        score = 0
        score += len(findings["income_promise"]) * 20
        score += len(findings["scarcity_marketing"]) * 10
        score += len(findings["identity_packaging"]) * 5
        score += len(findings["anxiety_creation"]) * 15
        score += len(findings["screenshot_induction"]) * 15
        score += len(findings["pyramid_scheme"]) * 30
        score += len(findings["entry_fee"]) * 25
        score = min(100, score)

        # 确定等级
        if score >= 75 or findings["pyramid_scheme"]:
            level = RiskLevel.VERY_HIGH
        elif score >= 50:
            level = RiskLevel.HIGH
        elif score >= 25:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        # 红旗
        red_flags = []
        if findings["pyramid_scheme"]:
            red_flags.append("涉嫌传销/拉人头模式")
        if findings["entry_fee"]:
            red_flags.append("收取各种入门费用")
        if len(findings["income_promise"]) >= 3:
            red_flags.append("过度承诺收益")

        return {
            "score": score,
            "level": level.value,
            "findings": findings,
            "red_flags": red_flags,
        }


# ============================================================
# 免费资源推荐引擎
# ============================================================

class FreeResourceRecommender:
    """免费资源推荐引擎"""

    def __init__(self):
        self.courses = FREE_COURSES
        self.trusted_platforms = TRUSTED_PLATFORMS

    def detect_topic(self, text: str) -> List[str]:
        """检测用户想学的主题"""
        topics = []

        topic_keywords = {
            "Python": ["python", "Python", "爬虫", "数据分析"],
            "Java": ["java", "Java", "后端"],
            "Web前端": ["前端", "html", "css", "js", "javascript", "vue", "react"],
            "全栈": ["全栈", "web开发"],
            "数据分析": ["数据分析", "数据科学", "sql", "tableau"],
            "人工智能": ["人工智能", "AI", "机器学习", "深度学习", "神经网络"],
            "大数据": ["大数据", "hadoop", "spark"],
            "UI设计": ["UI", "ui设计", "界面设计"],
            "平面设计": ["平面设计", "PS", "photoshop", "ai", "illustrator"],
            "视频剪辑": ["视频剪辑", "PR", "premiere", "剪辑", "AE", "after effects"],
            "短视频运营": ["短视频", "抖音", "快手", "小红书", "直播", "自媒体", "带货"],
            "电商运营": ["电商", "淘宝", "拼多多", "京东", "开店", "跨境电商"],
            "新媒体运营": ["新媒体", "运营", "公众号", "微信运营"],
            "股票": ["股票", "炒股", "A股", "K线"],
            "基金": ["基金", "公募基金", "私募基金"],
            "理财基础": ["理财", "投资", "财务规划"],
            "写作变现": ["写作", "写文章", "投稿", "文案", "内容创作"],
            "配音兼职": ["配音", "声音", "音频"],
            "摄影": ["摄影", "拍照", "相机"],
            "健身": ["健身", "减肥", "瘦身", "增肌", "体态"],
            "简历面试": ["简历", "面试", "求职", "找工作"],
            "职业规划": ["职业规划", "职业发展", "职场"],
        }

        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if topic not in topics:
                        topics.append(topic)
                    break

        return topics

    def recommend(self, text: str, max_results: int = 5) -> Dict[str, Any]:
        """推荐免费资源"""
        topics = self.detect_topic(text)

        if not topics:
            return {
                "recommended": False,
                "reason": "未识别到学习主题",
                "courses": []
            }

        results = []

        for topic in topics:
            # 遍历FREE_COURSES中的所有主类别和子类别来匹配
            for category, subcats in self.courses.items():
                for subcat_name, courses in subcats.items():
                    # 检查topic是否匹配类别名或子类别名
                    if topic in category or topic in subcat_name:
                        for course in courses:
                            if len(results) < max_results:
                                results.append(course)

        if results:
            return {
                "recommended": True,
                "detected_topics": topics,
                "reason": f"检测到您想学习 {', '.join(topics)}，以下是免费优质资源：",
                "courses": results,
                "total_count": len(results),
            }

        return {
            "recommended": False,
            "reason": "未找到相关免费资源",
            "courses": []
        }

    def get_trusted_platforms(self) -> List[Dict]:
        """获取可信平台列表"""
        return [
            {"name": name, "url": info["url"], "type": info["type"]}
            for name, info in self.trusted_platforms.items()
        ]

    def format_recommendation_message(self, recommendation: Dict) -> str:
        """格式化推荐消息"""
        if not recommendation["recommended"]:
            return ""

        lines = [
            "\n💡 其实您有很好的免费学习选择：",
        ]

        for course in recommendation["courses"]:
            lines.append(f"  • {course['name']} ({course['level']}) - {course['platform']}")
            lines.append(f"    {course['url']}")

        lines.append("\n这些平台都是官方或权威机构提供的免费课程，比付费课程靠谱多了！")

        return "\n".join(lines)


# ============================================================
# 价格分析引擎
# ============================================================

class PriceAnalyzer:
    """价格分析器"""

    def __init__(self):
        self.benchmarks = COURSE_PRICE_BENCHMARKS
        self.income_tiers = INCOME_TIERS

    def extract_price(self, text: str) -> Optional[float]:
        """从文本中提取价格"""
        import re
        patterns = [
            r'￥\s*(\d+(?:\.\d+)?)',
            r'¥\s*(\d+(?:\.\d+)?)',
            r'原价[：:]\s*(\d+(?:\.\d+)?)',
            r'现价[：:]\s*(\d+(?:\.\d+)?)',
            r'特惠价[：:]\s*(\d+(?:\.\d+)?)',
            r'价格[：:]\s*(\d+(?:\.\d+)?)',
            r'(\d+)\s*元',
            r'(\d+)\s*万',  # 万
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match:
                    try:
                        price = float(match)
                        # 如果匹配到"万"，乘以10000
                        if '万' in pattern and '万' in text[text.find(match)-1:text.find(match)+2]:
                            price *= 10000
                        return price
                    except:
                        pass
        return None

    def analyze_price(
        self,
        price: float,
        course_type: str = "default",
        level: str = "beginner"
    ) -> Dict[str, Any]:
        """分析价格合理性"""
        benchmark = self.benchmarks.get(course_type, self.benchmarks["default"])
        level_data = benchmark.get(level, benchmark["beginner"])

        min_price = level_data["min"]
        max_price = level_data["max"]
        reasonable_min = level_data["reasonable"][0]
        reasonable_max = level_data["reasonable"][1]

        # 计算溢价
        if price > reasonable_max:
            ratio = price / reasonable_max
        elif price < reasonable_min:
            ratio = price / reasonable_min if reasonable_min > 0 else 0
        else:
            ratio = 1.0

        # 判断是否虚高
        is_overpriced = price > reasonable_max * 3
        is_suspiciously_cheap = price < reasonable_min * 0.1 and price > 0

        return {
            "price": price,
            "course_type": course_type,
            "level": level,
            "market_range": f"{reasonable_min}-{reasonable_max}元",
            "ratio": ratio,
            "is_overpriced": is_overpriced,
            "is_suspiciously_cheap": is_suspiciously_cheap,
            "assessment": self._get_assessment(price, reasonable_min, reasonable_max, is_overpriced),
        }

    def _get_assessment(self, price: float, r_min: int, r_max: int, is_overpriced: bool) -> str:
        """获取评估"""
        if price < r_min * 0.5 and price > 0:
            return "价格过低，可能存在其他收费陷阱"
        elif price < r_min:
            return "价格偏低，较为合理"
        elif price <= r_max:
            return "价格在合理范围内"
        elif price <= r_max * 2:
            return "价格偏高，需核实课程质量"
        elif price <= r_max * 3:
            return "价格明显偏高，可能是割韭菜"
        else:
            return "价格严重虚高，极可能是割韭菜"

    def match_user_affordability(
        self,
        price: float,
        monthly_income: Optional[float] = None,
        income_tier: Optional[str] = None
    ) -> Dict[str, Any]:
        """匹配用户消费能力"""
        if income_tier and income_tier in self.income_tiers:
            tier = self.income_tiers[income_tier]
        elif monthly_income:
            tier = self._get_tier_by_income(monthly_income)
        else:
            return {"match": "unknown", "reason": "收入信息不足"}

        affordability = tier["course_affordability"]

        if price <= affordability["low_risk_max"]:
            match = "可承受"
            advice = f"价格在您的承受范围内"
        elif price <= affordability["medium_risk_max"]:
            match = "需谨慎"
            advice = f"课程价格占月收入比例较高，建议慎重考虑"
        elif price <= affordability["high_risk_min"]:
            match = "超出承受范围"
            advice = f"以您目前的收入，这个课程价格偏高，建议选择更便宜的替代方案"
        else:
            match = "严重超出"
            advice = f"这个课程价格对您来说过高，不建议购买"

        # 计算占收入比
        monthly = tier["monthly_income"][0]
        ratio = (price / monthly * 100) if monthly > 0 else 0

        return {
            "match": match,
            "income_tier": tier["description"],
            "price_to_income_ratio": f"{ratio:.1f}%",
            "advice": advice,
            "warning": tier["warning"] if match != "可承受" else None,
        }

    def _get_tier_by_income(self, monthly_income: float) -> Dict:
        """根据月收入确定层级"""
        for tier_name, tier_data in self.income_tiers.items():
            min_inc, max_inc = tier_data["monthly_income"]
            if min_inc <= monthly_income < max_inc:
                return tier_data
        return self.income_tiers["高净值"]


def main():
    """测试"""
    print("=" * 70)
    print("反割韭菜Skill - Prompt框架 v2.1 价格分析测试")
    print("=" * 70)

    price_analyzer = PriceAnalyzer()

    test_prices = [
        ("Python入门课", 499, "编程开发", "beginner"),
        ("Python入门课", 9999, "编程开发", "beginner"),
        ("短视频课程", 299, "短视频/直播", "beginner"),
        ("短视频课程", 3999, "短视频/直播", "beginner"),
        ("股票课程", 1999, "股票投资", "beginner"),
        ("股票课程", 19999, "股票投资", "beginner"),
    ]

    print("\n📊 价格分析测试：")
    print("-" * 60)
    for name, price, course_type, level in test_prices:
        result = price_analyzer.analyze_price(price, course_type, level)
        print(f"{name} ({price}元)")
        print(f"  市场价: {result['market_range']}")
        print(f"  评估: {result['assessment']}")
        print()

    print("\n💰 用户消费能力匹配测试：")
    print("-" * 60)

    income_levels = [
        ("低收入", 2500),
        ("中低收入", 4500),
        ("中等收入", 9000),
        ("中高收入", 20000),
    ]

    test_price = 4999
    print(f"课程价格: {test_price}元\n")

    for tier_name, monthly_income in income_levels:
        result = price_analyzer.match_user_affordability(test_price, monthly_income=monthly_income)
        print(f"{tier_name} (月薪{monthly_income}元)")
        print(f"  承受评估: {result['match']}")
        print(f"  占收入比: {result['price_to_income_ratio']}")
        print(f"  建议: {result['advice']}")
        if result.get("warning"):
            print(f"  ⚠️ {result['warning']}")
        print()

    print("\n📝 风险评分测试：")
    print("-" * 60)
    scorer = RiskScorer()

    tests = [
        "拉人头发展下线，团队计酬，月入百万！",
        "某大师带你日入过万，限时特价只要9999！",
        "Python课程，系统学习，课后答疑，价4999",
    ]

    for t in tests:
        r = scorer.score_text(t)
        print(f"文本: {t[:40]}...")
        print(f"评分: {r['score']} - {r['level']}")
        if r['red_flags']:
            print(f"🚩 红旗: {r['red_flags']}")
        print()


if __name__ == "__main__":
    main()