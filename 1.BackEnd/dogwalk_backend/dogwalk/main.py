from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()  # 프로젝트 루트의 .env 파일 읽어서 환경변수 등록

api_key = os.getenv("OPENAI_API_KEY")
print(api_key)
