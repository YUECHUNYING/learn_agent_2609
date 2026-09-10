# git命令 
# git add  
# git commit
# git push


# linux命令与效率工具
# pwd 我在哪
# ls -la 有什么文件（ -la显示隐藏文件）
# cd 目录名  （进入目录）
# cat file.txt (查看文件内容)
# head -20 file (看前20行)
# grep "关键字" file （搜索）
# curl https:// (发起HTTP请求)
# python -m http.server 8000 (快速起一个静态文件服务器)


# bash 
import os
# .env文件里的内容不会自动变成系统环境变量。还需要一个加载器 python-dotenv
from dotenv import load_dotenv

#先加载 .env文件到环境变量
load_dotenv()

# 加载好之后才能读到
api_key = os.getenv("ZHIPU_API_KEY")

# print(api_key)
if api_key:
    print("已经读到api_key", len(api_key))
else:
    print("没有读到api_key,检查.env文件")
        




# curl -X POST  https://open.bigmodel.cn/api/paas/v4/chat/completions \ 
#      -H "Authorization: Bearer b699989772764e15a34b8453387a532a.m1AdprvWjYFv6HPx" \
#      -H "Content-Type: application/json" \
#      -d '{"model":"glm-4-flash", "messages":[{"role":"user","content":"你好"}]}'