import os
import json
import redis
from fastapi import FastAPI
from pydantic import BaseModel
from llm import get_answer

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# Open API Key 불러오기
# os.getenv("OPENAI_API_KEY")

# 클래스 (pydantic 사용)


# Fast API 메서드
app = FastAPI(
    title="LangChain Chatbot API",
    description="사용자 입력을 받아 LangChain LLM 응답을 반환하는 FastAPI 서버",
    version="1.0.0",
)
# Pydantic 모델 정의
class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    answer: str
# API 엔드포인트
# -------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    LangChain LLM을 사용해 사용자 질문에 대한 답변을 반환합니다.
    """
    user_input = request.user_input.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="입력이 비어 있습니다.")

    try:
        response_text = get_answer(user_input)
        return ChatResponse(answer=response_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"응답 생성 중 오류 발생: {str(e)}")
# 6. 루트 엔드포인트
# -------------------------------
@app.get("/")
async def root():
    return {"message": "LangChain Chatbot API에 오신 것을 환영합니다."}


## LangChain 파이프라인 엔드포인트
## POI 요청 엔드포인트
## 챗봇 엔드포인트

# LangChain 파이프라인


# POI 요청 메서드


# 챗봇 메서드
# 입력 : 사용자 인풋 (str)
# llm 챗봇 기능 : "role" : "프롬프트..."
