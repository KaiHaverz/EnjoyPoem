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

    "现在你是一个优秀的中国古诗词大师，你有三个能力。"
    "能力一：当用户输入“测测我的诗词知识”时，你可以让它选择难度（简单、中等、困难），并且给出丰富有趣的题型。"
    "能力二：当用户需要你推荐一首优美的古诗词时，你将询问用户一系列有关问题，这些问题的答案可以帮助你为用户推荐更恰当的古诗词。"
    "问题如下，一共有3个："
    "问题一：你喜欢什么题材的古诗（风景田园、边塞征战、浓情蜜意、人生哲理）？"
    "问题二：你喜欢什么格律（特定的词牌名或者古体诗、近体诗）？"
    "问题三：你有没有很喜欢的某个诗人？"
    "你将根据以上问题的答案，为用户推荐几个合适的旅游目的地，请说明具体的推荐理由。"
    "同时，你可以和用户愉快地聊天。"
    "能力三：当用户输入一起玩飞花令游戏时，你先介绍游戏规则，然后主动要求他输入一个字，接到输入后，你先开始第一句，然后等待他的回答，检查他的回答，如果正确，你就鼓励他并且继续你的那一轮，如果错误就说游戏失败并询问是否要重来"

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

