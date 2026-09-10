# LLM API 深入
# 1.多轮对话 messages结构

messages = [
    {"role": "system", "content": "你是一位耐心的医学知识助手"},
    {"role": "user", "content": "我最近总是头痛,是什么原因？"},
    {"role": "assistant", "content": "头痛的原因有很多种：紧张性头痛、偏头痛、睡眠不足...请问头痛是持续性的还是阵发性的？"},
    {"role": "user", "content": "是阵发性的,主要在太阳穴位置"}
]

# 关键理解 LLM本身没有记忆 列表发给模型 它就知道上下文了

# 2.JSON模式输出（结构化输出）
payload = {
    "model": "glm-4-flash",
    "messages": [
        {"role": "system", "content": "你是信息提取助手，只能输出JSON格式"},
        {"role": "user", "content": "张三，35岁，最近三天反复发烧，伴随咳嗽和乏力"},
    ],
    "response_format": {"type": "json_object"}  # 强制JSON输出
}

# 3.动手练习：信息提取器
# 从一段患者描述中提取：姓名、年龄、症状列表、病史，输出JSON.这是 LangChain结构化提取的“裸手版”,理解底层原理很重要

import re
import json


class GetInfo:
    def getInfo(self, desc: str) -> dict:
        return {
            "name": self._extract_name(desc),
            "age": self._extract_age(desc),
            "symptoms": self._extract_symptoms(desc),
            "history": self._extract_history(desc)
        }

    def _extract_name(self, desc: str) -> str | None:
        """提取姓名"""
        patterns = [
            r"姓名[:：]\s*([\u4e00-\u9fa5]{2,4})",
            r"我叫([\u4e00-\u9fa5]{2,4})",
            r"患者([\u4e00-\u9fa5]{2,4})",
            r"([\u4e00-\u9fa5]{2,4})[，,]\s*(?:男|女)"
        ]
        return self._first_match(desc, patterns)

    def _extract_age(self, desc: str) -> int | None:
        """提取年龄 返回整数"""
        patterns = [
            r"年龄[:：]\s*(\d+)",
            r"(\d+)\s*岁"
        ]
        match = self._first_match(desc, patterns)
        return int(match) if match else None

    def _extract_symptoms(self, desc: str) -> list:
        """先匹配症状"""
        m = re.search(r"症状[:：]\s*([^。；\n]+)", desc)
        if not m:
            m = re.search(r"症状包括\s*(.+?)(?=[,，]\s*(?:没有|无|病史|既往)|[。；\n]|$)", desc)
        if m:
            text = m.group(1)
            # 按顿号、逗号、分号分割 去掉空项
            items = [s.strip() for s in re.split(r"[、，,；;]", text) if s.strip()]
            # 过滤掉明显不是症状的干扰词
            noise = {"没有", "无", "否认", "既往"}
            return [item for item in items if item not in noise and not item.endswith("病史")]
        return []

    def _extract_history(self, desc: str) -> list:
        """提取病史列表"""
        m = re.search(r"病史[:：]\s*([^。；\n]+)", desc)
        if not m:
            # 兼容 既往病史
            m = re.search(r"既往病史[:：]\s*([^。；\n]+)", desc)
        if m:
            text = m.group(1)
            if re.search(r"^(无|没有|否认)", text.strip()):
                return []
            return [s.strip() for s in re.split(r"[、，,;；]", text) if s.strip()]
        return []

    def _first_match(self, desc: str, patterns: list) -> str | None:
        """一次尝试多个正则，返回第一个匹配结果"""
        for p in patterns:
            m = re.search(p, desc)
            if m:
                return m.group(1)
        return None


if __name__ == "__main__":
    # 测试样本 覆盖不同写法
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

    # 保存文件
    all_results = []
    for desc in samples:
        all_results.append({"desc": desc, "extracted": extractor.getInfo(desc)})

    try:
        with open("info_result_day4.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print("\n✅ 结果已保存到 info_result_day4.json")
    except PermissionError:
        print("\n无法写入文件，可能是权限限制，终端输出已经包含完整结果")
