import json
import zipfile
from pathlib import Path
from langchain_core.documents import Document
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
import shutil

# 환경 변수 설정
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
data_path = Path("data/labeling")

def load_json_from_zip(zip_path, content_key="disease"):
    # print("2")
    docs = []
    with zipfile.ZipFile(zip_path, 'r') as z:
        for filename in z.namelist():
            if filename.endswith(".json"):
                with z.open(filename) as f:
                    data = json.load(f)
                    # print("1")
                    # 문서 전체를 하나의 덩어리로 구성
                    text = (
                        f"[meta]\n"
                        f"lifeCycle: {data['meta']['lifeCycle']}\n"
                        f"department: {data['meta']['department']}\n"
                        f"disease: {data['meta']['disease']}\n\n"
                        f"[instruction]\n{data['qa']['instruction']}\n\n"
                        f"[question]\n{data['qa']['input']}\n\n"
                        f"[answer]\n{data['qa']['output']}"
                    )

                    # 문서 생성
                    docs.append({
                        "text": text,
                        "metadata": data["meta"]     # 검색 필터에 유용
                    })

    return docs

def load_all_zips(zip_folder, content_key):
    # print("1-1")
    zip_files = list(zip_folder.glob("*.zip"))
    all_docs = []
    # print(zip_files)
    for zip_file in zip_files:
        # print("2-2")
        docs = load_json_from_zip(zip_file, content_key)
        all_docs.extend(docs)
    return all_docs

all_doc_text = load_all_zips(data_path,"disease")

# from pathlib import Path

# # 현재 작업 디렉토리 확인
# print(f"현재 디렉토리: {Path.cwd()}")

# # data_path 확인
# print(f"경로: {data_path}")
# print(f"경로 존재: {data_path.exists()}")
# print(f"폴더 내 모든 파일:")
# for item in data_path.iterdir():
#     print(f"  {item.name} {'(DIR)' if item.is_dir() else ''}")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200000,
    chunk_overlap=0,
    separators=["\n\n", "\n", ".", " ", ""]
)

# chunks = text_splitter.split_documents(all_doc_text)
#print(f"총 {len(chunks)}개 청크 생성 완료")
final_docs = []
for doc in all_doc_text:
    # 사실상 chunks는 항상 1개
    chunks = text_splitter.split_text(doc["text"])
    final_docs.append({
        "text": chunks[0],
        "metadata": doc["metadata"]
    })

print(f"총 {len(final_docs)}개 문서 준비 완료")

# ============================================================================
# 3단계: 임베딩 및 벡터 스토어 생성
# ============================================================================
embeddings = OpenAIEmbeddings(model="text-embedding-3-small",chunk_size=10)

db_dir = "chroma_db_dog_qa"
# 문자열 dict → Document 객체로 변환
document_list = [
    Document(page_content=d["text"], metadata=d["metadata"])
    for d in final_docs
]


# 기존 DB가 있으면 로드
if Path(db_dir).exists():
    print(f"기존 {db_dir}에서 로드")
    vectorstore = Chroma(
        persist_directory=db_dir,
        embedding_function=embeddings
    )
else:
    print("새로운 벡터 스토어 생성")
    vectorstore = Chroma.from_documents(
        documents=document_list,
        embedding=embeddings,
        persist_directory=db_dir
    )
    
vectorstore.persist()  # 명시적 저장 (선택사항)
print(f"벡터 스토어 준비 완료")

# ============================================================================
# 4단계: Retriever 설정
# ============================================================================
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)


# ============================================================================
# 5단계: LLM 및 프롬프트 설정
# ============================================================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 강아지 질병 프롬프트 템플릿
template = """너는 반려견의 건강 상담을 제공하는 수의사야. 보호자의 궁금한 점을 해결해줘.
다음 문맥을 사용하여 질문에 답하세요. 문맥에서 답을 찾을 수 없다면, 모른다고 말하세요.

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
def get_dog_disease_recommendation(question: str):
    """강아지 질병"""
    result = rag_chain.invoke({"input": question})
    return result["answer"]

# 테스트
if __name__ == "__main__":
    # 질문 예시
    queries = [
        "강아지의 눈에 충혈이 조금 있습니다. 무슨 질환이 의심되나요? 생활에서 주의할 점도 알려주세요."
    ]
    
    for query in queries:
        print(f"\n질문: {query}")
        answer = get_dog_disease_recommendation(query)
        print(f"답변: {answer}\n")
