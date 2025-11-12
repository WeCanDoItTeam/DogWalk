import os
import json
import redis
from fastapi import FastAPI
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

# Open API Key 불러오기
os.getenv("OPENAI_API_KEY")

# 클래스 (pydantic 사용)


# Fast API 메서드
## LangChain 파이프라인 엔드포인트
## POI 요청 엔드포인트
## 챗봇 엔드포인트

# LangChain 파이프라인


# POI 요청 메서드


# 챗봇 메서드
# 입력 : 사용자 인풋 (str)
# llm 챗봇 기능 : "role" : "프롬프트..."