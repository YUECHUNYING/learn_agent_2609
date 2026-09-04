# 练习使用prompt
"""
工程基础练习 
目标：用同一个 LLMClient对比不同 Prompt写法的效果

练习内容：
1、zero-shot：直接提问 不给任何提示
2、few-shot: 给几个输入-输出的例子，让模型按照固定格式回答
3、temperature对比： 同一个问题 分别用0 / 0.5 / 0.7 看回答的差异 (temperature 控制生成的随机性)
"""

from day3 import LLMClient

client = LLMClient(provider="zhipu", temperature=0.7)

#三个医学问题
QUESTIONS = [
    "什么是双肺支气管炎 支气管肺炎?",
    "纵隔及肺门多发淋巴结是什么意思？",
    "冠状动脉硬化是什么意思？"
]
def run_zero_shot(questions, temperature=0.7):
    """zero-shot 直接提问 不加任何示例"""
    print("\n" + "=" * 60)
    print("【Part 1】Zero-shot 直接提问")
    print("="* 60)
    result = []
    for q in questions:
       print(f"\n问题{q}")
       ans = client.chat_single(q,temperature=temperature)
       print(f"回答：\n {ans} \n")
       result.append(("zero-shot",q,ans))
    return result

def run_few_shot(questions, temperature=0.7):
    """
    few-shot:给出示例 要求按照固定格式回答
    """   
    print("\n"+"="*60)
    print("【Part2】few-shot 给出示例引导")
    print("=" * 60)

    # 构造示例前缀 （prompt的开头部分）
    few_shot_prefix = """
    请用以下固定格式回答医学问题：
    问题：{用户问题}
    简要回答：{用一句话概括}
    详细解释：{3-5句话概括} 

    示例 1:
    问题：什么是糖尿病？
    简要回答：糖尿病是一种血糖长期过高的代谢性疾病。
    详细解释：胰岛素分泌不足或作用异常导致血糖无法被有效利用，长期高血糖会损害血管、神经和多个器官。

    示例 2:
    问题：为什么会发烧？
    简要回答：发烧是身体免疫系统对抗感染的反应。
    详细解释：病原体入侵后，免疫细胞释放致热因子，使体温调定点升高，帮助抑制病原体繁殖。

    现在请回答：
    """
    results = []
    for q in questions:
        prompt = few_shot_prefix + q
        print(f"\n问题：{q}")
        ans = client.chat_single(prompt, temperature=temperature)
        print(f"回答：\n{ans}\n")
        results.append(("few-shot", q, ans))
    return results  
  
def run_temperature_comparison(question, temperatures=(0,0.5,1.0)):
    """
    同一个问题 用不同temperature跑，观察差异
    注意： 智谱 GLM-4-Flash的temperature合法范围是[0,1],
    """
    print("\n"+"="*60)
    print(f"【Part 3】 Temperature对比 -- 问题：{question}")
    print("=" * 60)

    results = []
    for temp in temperatures:
        ans = client.chat_single(question,temperature = temp)
        print(f"\n [temperature]={temp}\n {ans} \n")
        results.append((f"temperature={temp}", question, ans))
    return results

def save_report(all_results,filename="prompt_report_day3.md"):
    """
    把结果保存成Markdow，方便查看和提交
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# Prompt 工程练习报告\n\n")
            f.write("练习目标：对比zero-sho、few-shot、不同temperature的效果。\n\n")
            for tag,q,ans in all_results:
                f.write(f"## {tag}\n\n")
                f.write(f"**问题**{q}\n\n")
                f.write(f"**回答**\n\n {ans} \n\n")
        print(f"\n报告已经保存到 {filename}")        

    except PermissionError:
        print(f"无法写入文件{filename},可能是权限限制，请手动保存")   


if __name__ == "__main__":
    all_results = []

    # 1.zero-shot
    all_results.extend(run_zero_shot(QUESTIONS, temperature=0.7))
    
    # 2.few-shot
    all_results.extend(run_few_shot(QUESTIONS,temperature=0.7))

    # 3.temperature对比 用第一个问题
    all_results.extend(run_temperature_comparison(QUESTIONS[0]))

    #保存报告
    save_report(all_results)