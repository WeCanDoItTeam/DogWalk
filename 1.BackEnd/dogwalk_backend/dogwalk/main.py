from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
import os

# Open API Key 불러오기
api_key = os.getenv("OPENAI_API_KEY")