from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()  # 프로젝트 루트의 .env 파일 읽어서 환경변수 등록

api_key = os.getenv("OPENAI_API_KEY")
print(api_key)

# model 선택
llm = ChatOpenAI(model="gpt-4o-mini")

# prompt + model + output parser
prompt = ChatPromptTemplate.from_template("주어진 문제를 풀기 위하여 계획을 세우고 단계에 따라 차근차근 문제를 푸세요. <Question>: {input}")
output_parser = StrOutputParser()

# LCEL 체인 구성 (프롬프트 → 모델 → 출력 파서)
# LCEL chaining
chain = prompt | llm | output_parser       # 프롬프트 ↦ 모델 ↦ 파서 체인

# 무한 루프: 사용자 입력 받기
while True:
    try:
        user_input = input("\n질문을 입력하세요 (종료: quit 또는 exit): ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("프로그램을 종료합니다.")
            break
        
        if not user_input:
            print("입력이 비어있습니다. 다시 시도해주세요.")
            continue
        
        # chain 호출 및 결과 출력
        print("\n답변:")
        result = chain.invoke({"input": user_input})
        print(result)
        
    except KeyboardInterrupt:
        print("\n\n프로그램을 종료합니다.")
        break