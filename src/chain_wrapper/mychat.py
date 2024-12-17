from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv, find_dotenv
#from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import time
import json
import os

# Load environment variables
_ = load_dotenv(find_dotenv())

# Initialize model
model = ChatOpenAI(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key="6eb9921213e82f0500f251458e6ac0f8.4BZSCuX8URbtus5C",
    model="glm-4",
)

# File path to save and load chat history
history_file_path = "chat_history.json"

# Function to load chat history from a file
def load_history_from_file(file_path: str) -> dict:
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            history = {}
            for k, v in data.items():
                messages = []
                for msg in v:
                    if msg['type'] == 'human':
                        messages.append(HumanMessage(content=msg['content']))
                    else:
                        messages.append(AIMessage(content=msg['content']))
                chat_history = ChatMessageHistory()  # Initialize empty ChatMessageHistory
                chat_history.messages = messages   # Set the messages attribute
                history[k] = chat_history
            return history
    return {}

# Function to save chat history to a file
def save_history_to_file(history: dict, file_path: str):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({k: [msg.__dict__ for msg in v.messages] for k, v in history.items()}, f, ensure_ascii=False, indent=4)

# Load existing chat history
store = load_history_from_file(history_file_path)

# Function to get session history
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Define the system message for the prompt
system_message = (
     """
现在你是一个精通中国古诗词的文学大师，拥有三个专业能力，能为用户提供互动的古诗词知识测试、精确的诗词推荐以及有趣的飞花令游戏体验。

能力一：诗词知识测试
当用户输入“测测我的诗词知识”时，你将引导用户选择难度等级（简单、中等、困难），并且准备包含多种题型的测验。例如：

选择题：给出一个诗句，要求用户选出正确的下一句。
填空题：给出诗句的一部分，让用户填写缺失的字词。
诗人和作品匹配题：让用户匹配诗句与对应的诗人或作品。
确保题目丰富有趣、符合用户选择的难度等级，并在答题过程中提供鼓励性反馈（如“答对了！继续加油！”）或正确答案的解释，以帮助用户更好地理解和记忆古诗词。

能力二：诗词推荐
当用户请求推荐一首优美的古诗词时，你将引导用户回答三个问题，以便为其推荐更贴切的作品。这些问题包括：

题材偏好：用户喜欢的诗词题材（如风景田园、边塞征战、浓情蜜意、人生哲理）。
格律偏好：用户偏爱的诗词格式（如特定的词牌名、古体诗、近体诗）。
诗人喜好：用户特别喜爱的诗人。
根据用户的答案，你不仅会推荐适合的诗词作品，还会结合诗句的意境和情感，为用户推荐相关的旅游目的地，并提供具体推荐理由。例如：

针对喜欢风景田园诗的用户，可以推荐苏州、杭州等历史悠久的园林风光地，并结合诗句中的意境解释推荐理由。
针对喜欢边塞征战题材的用户，可以推荐如敦煌、张掖等边疆之地，讲述这些地方的文化底蕴与诗歌意境的关系。
能力三：飞花令游戏
当用户输入“一起玩飞花令游戏”时，你将向用户介绍游戏规则：

飞花令是一种古典诗词游戏，通常以一个字或一个主题作为关键词，双方交替吟诵含有该字的诗句，直至一方无法继续。
你会主动邀请用户选择一个字作为游戏主题，并引导用户输入第一句含该字的诗句。如果用户要求你先开始，你可以主动开始并期待用户回应。每轮游戏中，你会检查用户的回答：

正确时：鼓励用户，并继续给出下一句诗。
错误时：告知用户“游戏失败”，并询问是否要重来。
此外，你会在游戏中适当加入鼓励性或互动性语言，使用户获得愉快的游戏体验。

额外能力：古诗词文化互动
你可以根据用户的兴趣，通过与用户轻松愉快的聊天，分享更多关于诗词文化的知识，如典故、诗词的历史背景、与诗人相关的趣闻等，让用户在互动中获得对中国古诗词更深层的理解。
    """
)

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    MessagesPlaceholder("chat_history"),
    ("user", "{input}")
])

# Create the answer chain
answer_chain = prompt | model

# Create a runnable with message history
with_message_history = RunnableWithMessageHistory(
    answer_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Config for session
config = {
    "configurable": {
        "session_id": str(time.time())  # Ensure session_id is a string
    }
}

# Output parser
parser = StrOutputParser()

"""# Save chat history to file after the response
save_history_to_file(store, history_file_path)"""

