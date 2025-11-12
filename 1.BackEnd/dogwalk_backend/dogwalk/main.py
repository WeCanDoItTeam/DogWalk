import os
import json
import redis
from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableMap
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser

REDIS_HOST = "192.168.0.76"
REDIS_PORT = 6379

MODEL_GPT_4O_MINI = "gpt-4o-mini" # 테스트용. 싸다
MODEL_GPT_4 = "gpt-4" # 실전용. 비싸다

load_dotenv()

# Fast API 사용하기
app = FastAPI(title="DogWalk")

# Open API Key 불러오기
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

# LLM 가져오기
llm = ChatOpenAI(model=MODEL_GPT_4O_MINI, temperature=0, openai_api_key=openai_api_key)

# Redis 연결
connect_redis = True
if connect_redis:
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        
        r.ping()
        print("Redis 연결 성공")
    except Exception as e:
        print("Redis 연결 실패 : ", e)

# 클래스 (pydantic 사용)
# 강아지 정보
class DogInfoData(BaseModel):
    age: int = Field(gt=0, description="나이 (0살일 경우 1살 미만으로 간주)")
    breed: str  = Field(min_length=1, max_length=20, description="견종명 (예: 말티즈, 푸들 등)")
    gender: int = Field(ge=0, le=1, description="성별 (0=수컷, 1=암컷)")
    weight: float = Field(gt=0, description="몸무게(kg), 0<만 가능")
    
# 사용자 위치 정보
class UserPosData(BaseModel):
    user_lat: float = Field(description="사용자의 현재 GPS 위도")
    user_lon: float = Field(description="사용자의 현재 GPS 경도")

class CourseRcommendRequest(BaseModel):
    dog_info: DogInfoData # 강아지 정보
    user_pos: UserPosData # 사용자 위치 정보

class WalkRecommendationData(BaseModel):
    duration_min: int = Field(description="추천 산책 시간(분)")
    intensity: int = Field(ge=1, le=3, description="산책 강도 (1=평지 및 건물 내, 2=약간의 경사로, 3=심한 경사로")
    

# TODO: 1. 기능구현  2. 예외처리 3. 리펙토링

# Fast API 메서드
# 기본 endpoint
@app.get("/")
def root():
    return {"message": "Hello, DogWalk BackEnd Server!!"}

class PromptRequest(BaseModel):
    user_input: str

@app.post("/testllm")
def testllm(request: PromptRequest):
    prompt = ChatPromptTemplate.from_template("주어진 문제를 풀기 위하여 계획을 세우고 단계에 따라 차근차근 문제를 푸세요. <Question>: {input}")
    try:
        chain = prompt | llm | StrOutputParser()
        result = chain.invoke({"input":request.user_input})
    except Exception as e:
        # 에러 내용 확인
        print("Error:", e)
        return {"error": str(e)}
    return result

## LangChain 파이프라인 엔드포인트
@app.post("/course_recommend")
def course_recommend(request: CourseRcommendRequest):
    recommendation = recommend_walk(request.dog_info)
    eee = get_poi(recommendation, request.user_pos)
    return eee


## POI 요청 엔드포인트
## 챗봇 엔드포인트

# 입력 프롬프트 생성 => LLM => 반경계산, POI 가져오기, 프롬프트 => LLM => 제목 프롬프트 생성 => LLM => 아웃풋
# LangChain 파이프라인
# 입력: 강아지 정보(json), 사용자 위치(위도,경도)
# 1. LLM 산책 시간과 강도 설정
# - 프롬프트 챗
# 출력: 추천 산책 시간, 강도(1~3)
def recommend_walk(dog_info: DogInfoData):
    prompt_template = """
    당신은 강아지 훈련사입니다.
    다음 강아지 정보를 참고하여 권장 산책 시간과 강도를 추천해주세요.
    - 강아지 종류: {breed}
    - 나이: {age}살 (0살일 경우 1살 미만으로 간주)
    - 성별: {gender} (0=수컷, 1=암컷)
    - 몸무게: {weight}kg 
    
    intensity 기준:
    - 견종 평균 몸무게와 비교, 비만 시 활동량 낮춤
    1 = 활동량 적음 (<20분) 
    2 = 활동량 중간 (<60분)
    3 = 활동량 많음 (60분<)
    위를 기준으로 intensity 설정하세요.
    
    출력은 반드시 JSON 형식으로, duration_min(분), intensity(1~3)만 포함하세요.
    {{
        "duration_min": int,
        "intensity": int
    }}
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    parser = PydanticOutputParser(pydantic_object=WalkRecommendationData)

    chain = prompt | llm | parser

    input_data = dog_info.model_dump()
    recommendation = chain.invoke(input_data)
    
    return recommendation

# 입력: 추천 산책 시간(분), 강도(1~3)
# 2. 산책시간 기반 반경 계산 (시속 사람기준 0.4)
# - 사용자 위도경도 기준 반경으로 해당 범위 계산 
# - 해당 강도 이하 난이도 찾도록
# - Redis에서 해당되는 범위 POI가져오기
# - llm 선별 부탁
# 출력: POI N개
def get_poi(recommendation:WalkRecommendationData, user_pos:UserPosData):

    radius = 2

    # 문화 식당 병원 여행 산택 미용 동물샵
    nearby_walks = r.georadius("walk_geo", user_pos.user_lon, user_pos.user_lat, radius, unit="km")
    print("nearby_walks : ", nearby_walks)
    if nearby_walks:
        walk_values = r.hmget(nearby_walks)
        print("walk_values : ", walk_values)
    else:
        walk_data_list = []

    #print("반경 2km 내 walk 데이터:", walk_data_list)

# 입력: POI N개
# 3. POI에 대한 짧은 제목
# - POI에 설명 추가
# 출력: 반경, {POI, 각 소개글}




# dog_info = DogInfoData(
#     age=3,
#     breed="말티즈",
#     gender=0,
#     weight=4.5
# )

# result = recommend_walk(dog_info)

# print(type(result))

test = WalkRecommendationData(duration_min=20, intensity=2)
pos = UserPosData(user_lon=127.0080277,user_lat=37.2598756)
eee = get_poi(test,pos)
print(eee)

# POI 요청 메서드


# 챗봇 메서드
# 입력 : 사용자 인풋 (str)
# llm 챗봇 기능 : "role" : "프롬프트..."