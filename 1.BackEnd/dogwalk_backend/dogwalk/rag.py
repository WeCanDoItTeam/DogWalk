import os
from pathlib import Path
from dotenv import load_dotenv

# LangChain 임포트 (올바른 버전)
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 환경 변수 설정
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# ============================================================================
# 1단계: PDF 문서 로드
# ============================================================================
data_path = Path("data")
pdf_files = list(data_path.glob("*.pdf"))

all_documents = []

for pdf_file in pdf_files:
    print(f"불러오는 중: {pdf_file}")
    loader = PyMuPDFLoader(str(pdf_file))
    documents = loader.load()
    all_documents.extend(documents)

print(f"총 {len(all_documents)}개 문서 로드 완료")

# ============================================================================
# 2단계: 텍스트 분할 (청크 생성)
# ============================================================================
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""]
)

chunks = text_splitter.split_documents(all_documents)
print(f"총 {len(chunks)}개 청크 생성 완료")

# ============================================================================
# 3단계: 임베딩 및 벡터 스토어 생성
# ============================================================================
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="chroma_db"
)

print("벡터 스토어 생성 및 저장 완료")

# ============================================================================
# 4단계: Retriever 설정
# ============================================================================
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# ============================================================================
# 5단계: LLM 및 프롬프트 설정
# ============================================================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 반려견 산책로 추천용 프롬프트
template = """다음 문맥을 사용하여 질문에 답하세요. 문맥에서 답을 찾을 수 없다면, 모른다고 말하세요.

문맥:
{context}

질문: {input}

답변: 위의 문맥을 바탕으로 질문에 대해 자세하고 정확한 답변을 한국어로 제공해주세요."""

prompt = ChatPromptTemplate.from_template(template)

# ============================================================================
# 6단계: RAG 체인 구성 (최신 방식)
# ============================================================================
# 방법 1: create_stuff_documents_chain + create_retrieval_chain 사용
combine_docs_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

# ============================================================================
# 7단계: 질의 및 응답
# ============================================================================
def get_dog_walking_recommendation(question: str):
    """범고래 관련 질문"""
    result = rag_chain.invoke({"input": question})
    return result["answer"]

# 테스트
if __name__ == "__main__":
    # 질문 예시
    queries = [
        "범고래의 먹이는 무엇인가요?"
    ]
    
    for query in queries:
        print(f"\n질문: {query}")
        answer = get_dog_walking_recommendation(query)
        print(f"답변: {answer}\n")
