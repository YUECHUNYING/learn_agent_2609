"""
信息提取器（规则版 / "裸手版"）
目标：从一段患者描述中提取 姓名、年龄、症状列表、病史，输出 JSON。

这是 LangChain 结构化提取的"裸手版"——先不用大模型，
用 Python 正则表达式和字符串处理理解底层原理。

知识点：
- 正则表达式 re 模块
- 字典 / JSON 输出
- 类的封装
"""

import re
import json


class GetInfo:
    """从患者描述中提取结构化信息"""

    def getInfo(self, desc: str) -> dict:
        """
        主入口：传入患者描述字符串，返回 JSON 字典
        """
        return {
            "name": self._extract_name(desc),
            "age": self._extract_age(desc),
            "symptoms": self._extract_symptoms(desc),
            "history": self._extract_history(desc),
        }

    def _extract_name(self, desc: str) -> str | None:
        """提取姓名"""
        patterns = [
            r"姓名[：:]\s*([\u4e00-\u9fa5]{2,4})",   # 姓名：张三
            r"我叫([\u4e00-\u9fa5]{2,4})",             # 我叫张三
            r"患者([\u4e00-\u9fa5]{2,4})",            # 患者张三
            r"([\u4e00-\u9fa5]{2,4})，\s*(?:男|女)", # 张三，男/女
        ]
        return self._first_match(desc, patterns)

    def _extract_age(self, desc: str) -> int | None:
        """提取年龄，返回整数"""
        patterns = [
            r"年龄[：:]\s*(\d+)",   # 年龄：45
            r"(\d+)\s*岁",          # 45岁、今年32岁
        ]
        match = self._first_match(desc, patterns)
        return int(match) if match else None

    def _extract_symptoms(self, desc: str) -> list:
        """提取症状列表"""
        # 先匹配"症状：..."
        m = re.search(r"症状[：:]\s*([^。；\n]+)", desc)
        if not m:
            # 匹配"症状包括..."，但要在"没有/无/病史/既往"之前截断
            m = re.search(r"症状包括\s*(.+?)(?=，\s*(?:没有|无|病史|既往)|[。；\n]|$)", desc)

        if m:
            text = m.group(1)
            # 按顿号、逗号、分号分隔，去掉空项
            items = [s.strip() for s in re.split(r"[、，,；;]", text) if s.strip()]
            # 过滤掉明显不是症状的干扰词
            noise = {"没有", "无", "否认", "既往"}
            return [item for item in items if item not in noise and not item.endswith("病史")]
        return []

    def _extract_history(self, desc: str) -> list:
        """提取病史列表"""
        m = re.search(r"病史[：:]\s*([^。；\n]+)", desc)
        if not m:
            # 兼容"既往病史：..."
            m = re.search(r"既往病史[：:]\s*([^。；\n]+)", desc)

        if m:
            text = m.group(1)
            # 如果写的是"无"/"没有"，返回空列表
            if re.search(r"^(无|没有|否认)", text.strip()):
                return []
            return [s.strip() for s in re.split(r"[、，,；;]", text) if s.strip()]
        return []

    def _first_match(self, desc: str, patterns: list) -> str | None:
        """依次尝试多个正则，返回第一个匹配结果"""
        for p in patterns:
            m = re.search(p, desc)
            if m:
                return m.group(1)
        return None


if __name__ == "__main__":
    # 测试样本：覆盖不同写法
    samples = [
        "患者张三，年龄：45岁。症状：头痛、恶心、视力模糊。病史：高血压、糖尿病。",
        "我叫李四，今年32岁，症状包括胸痛、呼吸困难，没有既往病史。",
        "王五，男，28岁。症状：发热、咳嗽。病史：无。",
    ]

    extractor = GetInfo()
    print("=" * 50)
    for desc in samples:
        result = extractor.getInfo(desc)
        print(f"\n原始描述：{desc}")
        print("提取结果：")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # 保存到文件
    all_results = []
    for desc in samples:
        all_results.append({"desc": desc, "extracted": extractor.getInfo(desc)})

    try:
        with open("info_extractor_results.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print("\n✅ 结果已保存到 info_extractor_results.json")
    except PermissionError:
        print("\n⚠️ 无法写入文件，可能是权限限制。终端输出已包含完整结果。")
