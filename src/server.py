from typing import List
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langserve import add_routes
from dotenv import load_dotenv,find_dotenv
from chain_wrapper import mychat,mychat_pure
from router_api import router
import subprocess
import threading
import webbrowser
import os
from time import sleep


def run_node_script():
    try:
        # 调用 Node.js 脚本
        result = subprocess.run(
            ['node', 'main.js', 'arg1', 'arg2'],  # 替换为实际的 Node.js 脚本路径和参数
            capture_output=True, text=True
        )
        # 输出 Node.js 的运行结果
        print("Node.js Output:", result.stdout)
        if result.stderr:
            print("Node.js Error:", result.stderr)
    except Exception as e:
        print(f"Error running Node.js script: {e}")


# 1. Create prompt template
system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages([
    ("system",system_template),
    ("user","{text}")
])

# 2 获取你的智谱 API Key
_ = load_dotenv(find_dotenv())

# 3. Create model
model = ChatOpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key="6eb9921213e82f0500f251458e6ac0f8.4BZSCuX8URbtus5C",
    model="glm-4",
)

# 4.create parser
parser = StrOutputParser()

# 5. Create chain
chain = prompt_template | model | parser

# 6. App definition
app = FastAPI(
    title="LangServe Demo",
    description="使用 LangChain 的 Runnable 接口的简单 API 服务器",
    version="0.0.1"
)

# 7. Adding chain route
add_routes(
    app,
    chain,
    path="/chain",
)


# add_routes(
#     app,
#     mychat.with_history,
#     path="/chain/mychat",
# )

# 8. Publishing static resources
app.mount("/pages",StaticFiles(directory="static"),name="pages")


# 9. cors跨域
from fastapi.middleware.cors import CORSMiddleware
# 允许所有来源访问，允许所有方法和标头
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    # allow_headers=["*"],
)

#10 get api
@app.get("/baike")
def baike(action,list,srsearch,format):
    print(action,list,srsearch,format)
    return {"query":{
        "search":[
            {"snippet":"xxxxxxx"}
        ]
    }}

#11 加载自定义路由
app.include_router(router)

if __name__ == "__main__":
    # 创建并启动线程
    node_thread = threading.Thread(target=run_node_script)
    node_thread.start()
    sleep(5)
    # 主线程继续执行其他任务
    print("Node.js 脚本在后台运行...")
    url = "http://localhost:8000/"
    webbrowser.open(url)
    uvicorn.run(app, host="0.0.0.0", port=8000)
    

"""
python serve.py

每个 LangServe 服务都带有一个简单的内置 UI，用于配置和调用应用程序，并提供流式输出和中间步骤的可见性。
前往 http://localhost:8000/chain/playground/ 试用！
传入与之前相同的输入 - {"language": "chinese", "text": "hi"} - 它应该会像以前一样做出响应。
"""