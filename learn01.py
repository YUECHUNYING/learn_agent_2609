# # 定义一个 病人 类
# class Patient:
#     # __init__ 是构造方法 创建对象时自动调用
#     def __init__(self, name, age, symptoms):
#         self.name = name
#         self.age = age
#         self.symptoms = symptoms
#     # 方法 对象能做的事情
#     def describe(self):
#         text = f"{self.name}, 年龄：{self.age}, 症状: {'~'.join(self.symptoms)}"
#         return text
#     def add_symptom(self, new_symptom):
#         self.symptoms.append(new_symptom)
#         print(f"已添加症状: {new_symptom}")

# # 使用类
# # 1.创建对象 实例化
# p = Patient("张三", 20, ["头痛", "头晕"])   
# # 2.调用方法
# print(p.describe())  # 输出: 张三, 年龄：20, 症状: 头痛~头晕
# p.add_symptom("发热")  # 输出: 已添加症状: 发热
# print(p.describe())  # 输出: 张三, 年龄：20, 症状: 头痛~头晕~发热

class Patient:
    hospital = "北京协和医院"  # 类属性，所有实例共享
    def __init__(self,name,age,symptoms):
        self.name = name
        self.age = age
        self.symptoms = symptoms
    def __str__(self):
        return f"<病人 {self.name}>"

    # 属性装饰器：让方法像属性一样访问
    @property
    def is_fever(self):
        return "发热" in self.symptoms
    # 类方法 不需要实例也能调用
    @classmethod
    def from_string(cls,line):
        parts = line.split(",")
        return cls(parts[0],int(parts[1]),parts[2:]) 

    # 静态方法 跟类相关但是不依赖实例数据
    @staticmethod
    def is_valid_age(age):
        return 0 <age <150

# 测试
print(Patient.hospital)  # 输出: 北京协和医院 
p = Patient("李四", 30, ["咳嗽", "发热"])
print(p)  # 输出: <病人 李四>
print(p.is_fever)  # 输出: True  
print(p.is_valid_age(25))  # 输出: True
print(Patient.is_valid_age(200))  # 输出: False


# 继承
class Animal:
    def __init__(self,name):
        self.name = name
    def speak(self):
        raise NotImplementedError("子类必须实现 speak 方法")
class Dog(Animal):
    def speak(self):
        return f"{self.name} 说: 汪汪"

class Cat(Animal):
    def speak(self):
        return f"{self.name} 说: 喵喵"

animals = [Dog("旺财"), Cat("咪咪")]
for animal in animals:
    print(animal.speak())  # 输出: 旺财 说: 汪汪  咪咪 说: 喵喵            


class MedicalRecord:
    def __init__(self,patient_name,doctor,diagnosis,date):
        self.patient_name = patient_name
        self.doctor = doctor
        self.diagnosis = diagnosis
        self.date = date

    def summary(self):
        return f"[{self.date}]{self.patient_name}(医生：{self.doctor}) 诊断: {self.diagnosis}"
    def save_to_file(self,filepath="records.txt"):
        try:
            with open(filepath, "a", encoding="utf-8") as f: # a 追加模式  w 写入模式 会覆盖原文件
                line = f"{self.patient_name},{self.doctor},{self.diagnosis},{self.date}\n"
                f.write(line)
            print(f"记录已保存到 {filepath}")    
        except Exception as e:
            print(f"保存记录时出错: {e}")
if __name__ == "__main__":
        record1 = MedicalRecord("张三", "李医生", "感冒", "2023-10-01")
        record2 = MedicalRecord("李四", "王医生", "发热", "2023-10-02")
        print(record1.summary())
        record1.save_to_file()
        record2.save_to_file()


# 异常处理  try-except 捕获
try:
    num = int(input("请输入一个数字: "))
    result = 100 / num
    print(f"结果是: {result}")
except ValueError:
    print("输入无效，请输入一个数字。")
except ZeroDivisionError:
    print("除数不能为零。")
except Exception as e:  # 捕获所有其他异常
    print(f"发生错误: {e}")    
else:
    print("计算成功，没有异常发生。")   
finally:
    print("程序结束。")     


import time
def call_llm_with_retry(api_func, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            return api_func()  # 假设 api_func 是调用 LLM 的函数
        except Exception as e:
            print(f"第 { attempt} 次调用失败: {e}")
            if attempt == max_retries:
                raise  # 达到最大重试次数，抛出异常
            time.sleep(2)  # 等待 2 秒后重试
        else:
            print("调用成功，没有异常发生。")   
        finally:
            print("调用结束。")        


# 装饰器 不改变函数本身的情况下 给它加功能
import time
def timer(func):
    def wrapper(*arg3,**kwargs):
        start = time.time()
        result = func(*arg3,**kwargs)
        end = time.time()   
        print(f"函数 {func.__name__} 执行时间: {(end-start):.3f} 秒")
        return result
    return wrapper
@timer
def slow_function():
    time.sleep(2)  # 模拟一个耗时操作
    return "完成"
print(slow_function())  # 输出: 函数 slow_function 执行时间: 2.000 秒  完成


# 上下文管理器 自动清理资源
# 不用with的写法（容易忘关文件）
f = open("notes.txt", "w", encoding="utf-8")
f.write("这是一些笔记内容。")
f.close()  # 如果忘记关闭文件，可能会导致资源泄漏

# 用with的写法 (自动关闭 推荐)
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("这是一些笔记内容。使用with")
# 出了with块 文件自动关闭
    

# venv与pip 管理依赖  bash
# 创建虚拟环境（隔离项目依赖，每个项目独立）
# python3 -m venv .venv

# # 激活虚拟环境  
# source .venv/bin/activate  # macOS/Linux    .venv\Scripts\activate  # Windows

# # 安装依赖包
# pip install requests python-dotenv

# # 导出依赖清单
# pip freeze > requirements.txt

# # 安装依赖清单中的包
# pip install -r requirements.txt
# # 退出虚拟环境      
# deactivate


# 作业