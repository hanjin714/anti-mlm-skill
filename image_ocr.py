#!/usr/bin/env python3
"""
反割韭菜 - 图片OCR识别模块
从课程海报/截图中提取文字信息
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import base64
import io


@dataclass
class OCRResult:
    """OCR识别结果"""
    full_text: str
    blocks: List[Dict[str, Any]]
    detected_language: str = "zh"
    confidence: float = 0.0


class ImageOCRProcessor:
    """图片OCR处理"""

    # 关键词提取模式
    KEYWORD_PATTERNS = {
        "价格相关": [
            r'￥\s*(\d+(?:\.\d+)?)',
            r'¥\s*(\d+(?:\.\d+)?)',
            r'原价[：:]\s*(\d+(?:\.\d+)?)',
            r'现价[：:]\s*(\d+(?:\.\d+)?)',
            r'特惠价[：:]\s*(\d+(?:\.\d+)?)',
            r'价格[：:]\s*(\d+(?:\.\d+)?)',
            r'(\d+)\s*元',
        ],
        "联系方式": [
            r'1[3-9]\d{9}',  # 手机号
            r'微信[：:]\s*([a-zA-Z][a-zA-Z0-9_-]{5,})',
            r'[Vv][：:]\s*([a-zA-Z][a-zA-Z0-9_-]{5,})',
            r'电话[：:]\s*(\d+)',
        ],
        "时间相关": [
            r'(\d{4})[年](\d{1,2})[月](\d{1,2})[日]?',
            r'(\d{1,2})[/月](\d{1,2})',
            r'20\d{2}-\d{2}-\d{2}',
        ],
        "课程名称": [
            r'《([^》]+)》',
            r'「([^」]+)」',
            r'课程[：:]\s*([^<\n]+)',
            r'训练营[：:]\s*([^<\n]+)',
        ],
    }

    def __init__(self):
        self.available = False
        self.engine = None

        # 尝试导入OCR引擎
        self._init_ocr_engine()

    def _init_ocr_engine(self):
        """初始化OCR引擎"""
        # 优先尝试PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self.engine = "paddleocr"
            self.available = True
            print("使用 PaddleOCR 引擎")
            return
        except ImportError:
            pass

        # 尝试EasyOCR
        try:
            import easyocr
            self.engine = "easyocr"
            self.available = True
            print("使用 EasyOCR 引擎")
            return
        except ImportError:
            pass

        # 尝试Tesseract
        try:
            import pytesseract
            self.engine = "tesseract"
            self.available = True
            print("使用 Tesseract OCR 引擎")
            return
        except ImportError:
            pass

        print("警告: 未安装OCR引擎，图片分析功能将受限")

    def process_image(self, image_path: str) -> OCRResult:
        """
        处理单张图片

        Args:
            image_path: 图片路径或URL

        Returns:
            OCRResult对象
        """
        if not self.available:
            return self._fallback_result()

        try:
            if self.engine == "paddleocr":
                return self._process_paddleocr(image_path)
            elif self.engine == "easyocr":
                return self._process_easyocr(image_path)
            elif self.engine == "tesseract":
                return self._process_tesseract(image_path)
        except Exception as e:
            print(f"OCR处理失败: {e}")

        return self._fallback_result()

    def _process_paddleocr(self, image_path: str) -> OCRResult:
        """使用PaddleOCR处理"""
        from paddleocr import PaddleOCR

        ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        result = ocr.ocr(image_path, cls=True)

        full_text = ""
        blocks = []

        if result and result[0]:
            for line in result[0]:
                if line:
                    text = line[1][0]
                    confidence = line[1][1]
                    full_text += text + "\n"
                    blocks.append({
                        "text": text,
                        "confidence": confidence,
                        "position": line[0] if len(line) > 0 else None
                    })

        return OCRResult(
            full_text=full_text.strip(),
            blocks=blocks,
            confidence=sum(b["confidence"] for b in blocks) / len(blocks) if blocks else 0
        )

    def _process_easyocr(self, image_path: str) -> OCRResult:
        """使用EasyOCR处理"""
        import easyocr

        reader = easyocr.Reader(['ch_sim', 'en'])
        result = reader.readtext(image_path)

        full_text = ""
        blocks = []

        for item in result:
            text = item[1]
            confidence = item[2]
            full_text += text + "\n"
            blocks.append({
                "text": text,
                "confidence": confidence,
                "position": item[0]
            })

        return OCRResult(
            full_text=full_text.strip(),
            blocks=blocks,
            confidence=sum(b["confidence"] for b in blocks) / len(blocks) if blocks else 0
        )

    def _process_tesseract(self, image_path: str) -> OCRResult:
        """使用Tesseract处理"""
        import pytesseract
        from PIL import Image

        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')

        blocks = [{"text": line, "confidence": 0.8} for line in text.split('\n') if line.strip()]

        return OCRResult(
            full_text=text.strip(),
            blocks=blocks,
            confidence=0.8
        )

    def _fallback_result(self) -> OCRResult:
        """OCR不可用时的降级结果"""
        return OCRResult(
            full_text="",
            blocks=[],
            confidence=0.0
        )

    def extract_keywords(self, text: str) -> Dict[str, List[str]]:
        """从文本中提取关键词"""
        extracted = {}

        for category, patterns in self.KEYWORD_PATTERNS.items():
            extracted[category] = []
            for pattern in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    # 如果匹配是元组，取第一个元素
                    for match in matches:
                        if isinstance(match, tuple):
                            match = match[0]
                        if match not in extracted[category]:
                            extracted[category].append(str(match))

        return extracted

    def analyze_poster(self, image_path: str) -> Dict[str, Any]:
        """
        分析课程海报

        Args:
            image_path: 图片路径

        Returns:
            分析结果
        """
        ocr_result = self.process_image(image_path)
        keywords = self.extract_keywords(ocr_result.full_text)

        return {
            "ocr_result": {
                "text": ocr_result.full_text,
                "blocks": ocr_result.blocks,
                "confidence": ocr_result.confidence,
            },
            "extracted_info": keywords,
            "analysis": self._analyze_extracted_info(keywords),
        }

    def _analyze_extracted_info(self, keywords: Dict[str, List[str]]) -> Dict[str, Any]:
        """分析提取的信息"""
        analysis = {
            "price_detected": False,
            "price_value": None,
            "contact_detected": False,
            "contact_info": [],
            "date_detected": False,
            "course_name_detected": False,
            "course_name": None,
            "suspicious_elements": [],
        }

        # 价格
        if keywords.get("价格相关"):
            analysis["price_detected"] = True
            try:
                prices = [float(re.findall(r'\d+(?:\.\d+)?', p)[0]) for p in keywords["价格相关"] if re.findall(r'\d+(?:\.\d+)?', p)]
                if prices:
                    analysis["price_value"] = max(prices)
                    if analysis["price_value"] > 5000:
                        analysis["suspicious_elements"].append("价格偏高(>5000元)")
            except:
                pass

        # 联系方式
        if keywords.get("联系方式"):
            analysis["contact_detected"] = True
            analysis["contact_info"] = keywords["联系方式"]
            if len(keywords["联系方式"]) > 2:
                analysis["suspicious_elements"].append("联系方式过多")

        # 课程名称
        if keywords.get("课程名称"):
            analysis["course_name_detected"] = True
            analysis["course_name"] = keywords["课程名称"][0]

        return analysis


def main():
    """测试"""
    import sys
    import json

    if len(sys.argv) < 2:
        print("用法: python image_ocr.py <图片路径>")
        sys.exit(1)

    processor = ImageOCRProcessor()

    if not processor.available:
        print("警告: OCR引擎未安装，图片分析功能不可用")
        print("安装方式:")
        print("  pip install paddleocr paddlepaddle")
        print("或")
        print("  pip install easyocr")
        print("或")
        print("  pip install pytesseract pillow && brew install tesseract")
        sys.exit(1)

    result = processor.analyze_poster(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()