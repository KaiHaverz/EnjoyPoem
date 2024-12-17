from fastapi import APIRouter
from starlette.responses import StreamingResponse
from pydantic import BaseModel
from chain_wrapper import mychat
from langchain_core.messages import AIMessageChunk, HumanMessage
from fastapi import HTTPException
from chain_wrapper import mychat_pure
from pydantic import BaseModel
#import mysql.connector
import hashlib

def get_db_connection():
    # return mysql.connector.connect(
    #     host="localhost",
    #     user="root",  
    #     password="080608",  
    #     database="user_info",
    #     charset='utf8'
    # )
    return
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Item(BaseModel):
    content: str

class Param(BaseModel):
    content: str
    userId: str
    a: str
    session_id: str

router = APIRouter()
  
async def generate_response(content, target_chain, session_id):
    target_chain.config["configurable"]["session_id"] = session_id
    print(target_chain.config)
    
    async for message_chunk in target_chain.with_message_history.astream(
        {"input": content},
        config=target_chain.config
    ):
        if isinstance(message_chunk, AIMessageChunk):
            message_str = str(message_chunk.content)
        else:
            message_str = message_chunk.content
        
        yield message_str.encode('utf-8')
    target_chain.save_history_to_file(target_chain.store, target_chain.history_file_path)

@router.post("/api/mychat")
async def chat(item: Param):
    print("传输的参数为：", item.content, item.userId, item.a, item.session_id)
    return StreamingResponse(generate_response(item.content, mychat, item.session_id), media_type="text/event-stream")

@router.post("/api/mychat_pure")
async def chat(item: Param):
    print("传输的参数为：", item.content, item.userId, item.a, item.session_id)
    return StreamingResponse(generate_response(item.content, mychat_pure, item.session_id), media_type="text/event-stream")

