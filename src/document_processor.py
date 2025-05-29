import json
import os
from typing import Dict, List, Tuple

import aiohttp
import docx
import PyPDF2
from paddleocr import PaddleOCR


class DocumentProcessor:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base = "https://api.deepseek.com/v1"

    async def process_document(self, file, standard_name: str) -> Dict:
        """统一文档处理接口"""
        # 提取文档内容
        if file.name.endswith(".pdf"):
            text = await self._extract_pdf_content(file)
        elif file.name.endswith((".docx", ".doc")):
            text = await self._extract_word_content(file)
        else:
            raise ValueError("不支持的文件格式")

        # LLM知识抽取
        knowledge = await self._extract_knowledge_with_llm(text, standard_name)
        return knowledge

    async def _extract_pdf_content(self, file) -> str:
        """PDF内容提取（支持扫描版）"""
        try:
            # 尝试文本提取
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            if len(text.strip()) < 100:  # 可能是扫描版
                # 使用OCR
                text = await self._ocr_extract(file)

            return text
        except Exception as e:
            # 回退到OCR
            return await self._ocr_extract(file)

    async def _extract_word_content(self, file) -> str:
        """Word文档内容提取"""
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    async def _extract_knowledge_with_llm(self, text: str, standard_name: str) -> Dict:
        """使用DeepSeek API进行知识抽取"""

        prompt = f"""你是EMC标准专家，请从以下文档中抽取结构化知识：

标准名称：{standard_name}
文档内容：{text[:8000]}

请识别并输出JSON格式：
{{
    "entities": [
        {{"id": "实体ID", "name": "实体名称", "type": "实体类型", "attributes": {{"属性": "值"}}}}
    ],
    "relations": [
        {{"source": "源实体ID", "target": "目标实体ID", "type": "关系类型", "confidence": 0.9}}
    ]
}}

实体类型包括：standard, organization, test_method, test_environment, vehicle_type, frequency_range
关系类型包括：develops, includes, applies_to, uses, references, covers
"""

        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 4000,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/chat/completions", headers=headers, json=payload
            ) as response:
                result = await response.json()

        # 解析LLM输出
        content = result["choices"][0]["message"]["content"]
        try:
            knowledge = json.loads(content)
            return self._validate_knowledge(knowledge)
        except json.JSONDecodeError:
            # 容错处理
            return self._extract_json_from_text(content)
