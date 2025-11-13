from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

from dotenv import load_dotenv
import os

load_dotenv()  # 프로젝트 루트의 .env 파일 읽어서 환경변수 등록

api_key = os.getenv("OPENAI_API_KEY")
print(api_key)

# LLM 설정 (클래스 또는 모듈 외부에서 한 번만 초기화)
llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 사용자와 친근하게 대화하는 AI 어시스턴트입니다."),
    # history 변수는 메시지 객체들의 리스트가 될 것이므로 MessagesPlaceholder를 사용합니다.
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# 3. 세션별 대화 기록을 저장할 임시 저장소 (실제로는 DB 등을 사용)
store = {}


# 세션 ID에 따라 대화 기록을 가져오는 함수
def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# 4. RunnableWithMessageHistory로 체인을 감싸서 메모리 기능 추가
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,       # ✅ 세션별 대화기록 가져오는 함수
    input_messages_key="input",   # 사용자의 입력을 나타내는 키
    history_messages_key="history"   # 프롬프트의 MessagesPlaceholder 변수명
)

def get_answer(user_input: str) -> str:
    """
    사용자 입력을 받아 LLM으로부터 답변을 생성하고 반환하는 함수
    
    Args:
        user_input (str): 사용자의 질문
    
    Returns:
        str: LLM의 답변
    
    Raises:
        ValueError: user_input이 비어있을 경우
    """
    if not user_input or not user_input.strip():
        raise ValueError("입력이 비어있습니다. 다시 시도해주세요.")
    
    try:
        response_a1 = chain_with_history.invoke(
            {"input": user_input.strip()},
            config={"configurable": {"session_id": "user_a"}}  # ✅ 세션 ID 지정
        )
        #result = chain.invoke({"input": user_input.strip()})
        return response_a1
    except Exception as e:
        raise Exception(f"답변 생성 중 오류 발생: {str(e)}")


def llm():
    """
    무한 루프로 사용자 입력을 받고 get_answer() 함수를 호출하는 메인 함수
    """
    print("LangChain AI Assistant에 오신 것을 환영합니다.")
    print("'quit' 또는 'exit'를 입력하여 종료할 수 있습니다.\n")
    
    while True:
        try:
            user_input = input("\n질문을 입력하세요 (종료: quit 또는 exit): ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("프로그램을 종료합니다.")
                break
            
            if not user_input:
                print("입력이 비어있습니다. 다시 시도해주세요.")
                continue
            
            # get_answer() 함수 호출
            print("\n답변:")
            answer = get_answer(user_input)
            print(answer)
            
        except KeyboardInterrupt:
            print("\n\n프로그램을 종료합니다.")
            break
        except ValueError as e:
            print(f"입력 오류: {e}")
        except Exception as e:
            print(f"오류 발생: {e}")


if __name__ == "__llm__":
    llm()