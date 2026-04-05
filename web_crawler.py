#!/usr/bin/env python3
"""
反割韭菜 - 网页爬虫模块
用于抓取课程宣传页面的内容
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs
import json
import time


class WebCrawler:
    """网页爬虫"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self.session = requests.Session()

    def fetch_page(self, url: str) -> Optional[str]:
        """
        获取页面HTML内容

        Args:
            url: 目标URL

        Returns:
            HTML内容或None
        """
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"获取页面失败: {e}")
            return None

    def extract_text_content(self, html: str) -> str:
        """
        从HTML中提取纯文本内容

        Args:
            html: HTML字符串

        Returns:
            纯文本内容
        """
        soup = BeautifulSoup(html, 'html.parser')

        # 移除脚本和样式
        for script in soup(["script", "style"]):
            script.decompose()

        # 获取文本
        text = soup.get_text(separator=' ', strip=True)

        # 清理多余空白
        text = re.sub(r'\s+', ' ', text)

        return text

    def extract_structured_data(self, html: str) -> Dict[str, Any]:
        """
        提取结构化数据

        Args:
            html: HTML字符串

        Returns:
            结构化数据字典
        """
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            "title": "",
            "description": "",
            "price": None,
            "images": [],
            "links": [],
            "phone": None,
            "wechat": None,
            "qr_codes": [],
        }

        # 提取标题
        title_tag = soup.find('title')
        if title_tag:
            data["title"] = title_tag.get_text(strip=True)

        # 提取meta描述
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            data["description"] = meta_desc.get('content', '')

        # 提取价格
        price_patterns = [
            r'￥(\d+(?:\.\d+)?)',
            r'¥(\d+(?:\.\d+)?)',
            r'价格[：:]?\s*(\d+(?:\.\d+)?)',
            r'原价[：:]?\s*(\d+(?:\.\d+)?)',
            r'特惠价[：:]?\s*(\d+(?:\.\d+)?)',
        ]
        text = self.extract_text_content(html)
        for pattern in price_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    data["price"] = float(match.group(1))
                    break
                except:
                    pass

        # 提取图片
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src and not src.startswith('data:'):
                data["images"].append(src)

        # 提取链接
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and href.startswith('http'):
                data["links"].append(href)

        # 提取电话
        phone_pattern = r'1[3-9]\d{9}'
        phones = re.findall(phone_pattern, text)
        if phones:
            data["phone"] = phones[0]

        # 提取微信
        wechat_pattern = r'[Vv微信][：:]?\s*([a-zA-Z][a-zA-Z0-9_-]{5,})'
        wechat_match = re.search(wechat_pattern, text)
        if wechat_match:
            data["wechat"] = wechat_match.group(1)

        return data

    def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        综合分析URL

        Args:
            url: 目标URL

        Returns:
            分析结果
        """
        result = {
            "url": url,
            "domain": "",
            "domain_risk": "未知",
            "page_content": "",
            "structured_data": {},
            "risk_signals": [],
            "success": False,
        }

        # 解析域名
        parsed = urlparse(url)
        result["domain"] = parsed.netloc
        result["domain_risk"] = self._analyze_domain_risk(parsed.netloc)

        # 获取页面内容
        html = self.fetch_page(url)
        if not html:
            result["error"] = "无法获取页面内容"
            return result

        result["success"] = True

        # 提取纯文本
        result["page_content"] = self.extract_text_content(html)

        # 提取结构化数据
        result["structured_data"] = self.extract_structured_data(html)

        # 检测风险信号
        result["risk_signals"] = self._detect_risk_signals(result["page_content"], result["structured_data"])

        return result

    def _analyze_domain_risk(self, domain: str) -> str:
        """分析域名风险"""
        domain_lower = domain.lower()

        # 高风险域名模式
        suspicious_patterns = [
            (r'taobao|1688|tmall', "电商平台页面，可能存在虚假宣传"),
            (r'weixin|wechat|mp\.weixin', "微信生态，难以追溯责任"),
            (r'long省市\.com|nanyue', "疑似传销/诈骗常用域名"),
            (r'^[a-z]-{5,}\.com$', "随机生成的低信任度域名"),
            (r'pinjie|cuxiao|mianfei', "促销/免费噱头页面"),
        ]

        for pattern, desc in suspicious_patterns:
            if re.search(pattern, domain_lower):
                return f"可疑 - {desc}"

        # 可信域名
        trusted_patterns = [
            r'bilibili|zhihu|baidu|tencent',
            r'youtube|twitter|facebook',
            r'microsoft|apple|google|amazon',
            r'tencent|alibaba|baidu|bytedance',
            r'imooc|coursera|udemy|ted',
        ]

        for pattern in trusted_patterns:
            if re.search(pattern, domain_lower):
                return "较可信 - 知名平台"

        return "一般 - 需进一步验证"

    def _detect_risk_signals(self, text: str, data: Dict) -> List[str]:
        """检测页面中的风险信号"""
        signals = []

        # 稀缺性词汇
        scarcity_words = ["限量", "限时", "名额有限", "即将涨价", "错过等一年", "仅此一次"]
        for word in scarcity_words:
            if word in text:
                signals.append(f"使用稀缺性营销: {word}")

        # 成功承诺
        promise_words = ["日入", "月入", "躺赚", "财富自由", "稳赚", "保证赚钱"]
        for word in promise_words:
            if word in text:
                signals.append(f"使用成功承诺: {word}")

        # 身份包装
        identity_words = ["大师", "创始人", "领袖", "传奇", "神话"]
        for word in identity_words:
            if word in text:
                signals.append(f"过度身份包装: {word}")

        # 价格异常
        if data.get("price"):
            if data["price"] > 10000:
                signals.append(f"价格较高: {data['price']}元")
            elif data["price"] < 1:
                signals.append(f"价格可疑: {data['price']}元")

        return signals


def main():
    """测试"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python web_crawler.py <URL>")
        sys.exit(1)

    crawler = WebCrawler()
    result = crawler.analyze_url(sys.argv[1])

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()