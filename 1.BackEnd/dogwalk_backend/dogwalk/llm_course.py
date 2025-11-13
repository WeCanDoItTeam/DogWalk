# TODO: 1. 기능구현<< 2. 리펙토링 3. 예외처리 

import os
import json
import redis
import time
from fastapi import FastAPI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Optional, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser

#======== [ 상수 선언 ] ========

REDIS_HOST = "192.168.0.76"
REDIS_PORT = 6379

MODEL_GPT_4O_MINI = "gpt-4o-mini" # 테스트용. 싸다
MODEL_GPT_4 = "gpt-4" # 실전용. 비싸다

POI_CULTURE = "culture" # 문화
POI_EAT = "eat" # 식당
POI_WALK = "walk" # 산책
POI_HOSPITAL = "hospital" # 병원
POI_TRIP = "trip" # 여행
POI_SERVICE = "service" # 미용
POI_SHOP = "shop" # 동물샵

GEO_CULTURE = "culture_geo" # 문화
GEO_EAT = "eat_geo" # 식당
GEO_WALK = "walk_geo" # 산책
GEO_HOSPITAL = "hospital_geo" # 병원
GEO_TRIP = "trip_geo" # 여행
GEO_SERVICE = "service_geo" # 미용
GEO_SHOP = "shop_geo" # 동물샵

#======== [ 환경변수 가져오기 (.env) ] ========

load_dotenv()

#======== [ Data Class ] ========

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

# 산책 시간 및 강도 추천
class WalkRecommendationData(BaseModel):
    duration_min: int = Field(description="추천 산책 시간(분)")
    intensity: int = Field(ge=1, le=3, description="산책 강도 (1=평지 및 건물 내, 2=약간의 경사로, 3=심한 경사로)")
    
class POIData(BaseModel):
    # MGMT_ID: int = Field(description="테이블 고유 ID")
    category: str = Field(description="카테고리 7개 (문화/식당/산책/병원/서비스/숙박/여행)")
    place_nm: str = Field(description="장소 명")
    latitude: float = Field(description="위도")
    longitude: float = Field(description="경도")
    land_address: str = Field(description="주소")
    cours_dc: Optional[str] = Field(default= None, description="산책로일 시 경로 표기")
    # lvl: int = Field(description="산책 강도 (1=평지 및 건물 내, 2=약간의 경사로, 3=심한 경사로)")
    poi_title: Optional[str] = Field(default= None, description="추천 아이템 제목")

class POIData_List(BaseModel):
    poi: List[POIData] = Field(description="선택된 장소 리스트")

class POIRecommendationData(BaseModel):
    radius: float = Field(description="반경 (km)") # 소수점 주의!!!!!!!!!!!!!!!!!
    poi: List[POIData] = Field(default_factory=list, description="POI 리스트")

class POIPLaceViewRequest(BaseModel):
    category: str = Field(description="카테고리: culture / eat / walk / hospital / trip / service / shop")
    radius: float = Field(description="반경 (km)")
    user_pos: UserPosData # 사용자 위치 정보

#======== [ Fast API (차후 들어낼 예정) ] ========

# Fast API 사용하기
app = FastAPI(title="DogWalk")

# Fast API 메서드
# 기본 endpoint
@app.get("/")
def root():
    return {"message": "Hello, DogWalk BackEnd Server!!"}

## LangChain 파이프라인 엔드포인트
@app.post("/course_recommend")
def course_recommend(request: CourseRcommendRequest):
    walk = walk_recommend(request.dog_info)
    poi = poi_recommend(walk, request.user_pos)
    result = title_recommend(poi)
    return result

#======== [ OpenAI ] ========

# Open API Key 불러오기
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

# LLM 가져오기
llm_low = ChatOpenAI(model=MODEL_GPT_4O_MINI, temperature=0, openai_api_key=openai_api_key)
llm_high = ChatOpenAI(model=MODEL_GPT_4, temperature=0, openai_api_key=openai_api_key)

#======== [ Redis ] ========

# Redis 연결
connect_redis = True
if connect_redis:
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        
        r.ping()
        print("Redis 연결 성공")
    except Exception as e:
        print("Redis 연결 실패 : ", e)

#======== [ Method ] ========

# 1. LLM 산책 시간과 강도 설정
# 입력: 강아지 정보(json), 사용자 위치(위도,경도)
# 출력: 추천 산책 시간, 강도(1~3)
def walk_recommend(dog_info: DogInfoData):
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

    chain = prompt | llm_low | parser

    input_data = dog_info.model_dump()
    result = chain.invoke(input_data)
    print("1. walk_recommend : ", result)
    return result

# 2. 산책시간 기반 반경 계산 (시속 사람기준 0.4)
# - 사용자 위도경도 기준 반경으로 해당 범위 계산 
# - 해당 강도 이하 난이도 찾도록 검색
# - Redis에서 해당되는 범위 POI가져오기
# - llm 선별
# 입력: 추천 산책 시간(분), 강도(1~3)
# 출력: POI N개
def poi_recommend(walk_data:WalkRecommendationData, user_pos:UserPosData):
    max_level = walk_data.intensity # 산책 강도
    speed_kmh = 4 # 속도 (성인 기준 평균 속도 4km/h)
    radius = min(2,speed_kmh * (walk_data.duration_min / 60)) # 최대 이동 거리 계산 (최대 반경 2km 제한)
    
    categories = [GEO_WALK, GEO_CULTURE, GEO_EAT]
    filtered_values = []

    for cat in categories:
        nearby = r.georadius(cat, user_pos.user_lon, user_pos.user_lat, radius, unit="km")
        if nearby:
            filtered_values.extend([r.hgetall(v) for v in nearby if int(r.hgetall(v).get('lvl', 99)) <= max_level])

    prompt_template = """
    당신은 반려견과 함께 산책 겸 나들이를 계획하는 사람입니다.
    각 장소는 카테고리(category), 이름(place_nm), 난이도(lvl) 등의 정보를 포함합니다.

    목표: 아래 조건을 고려하여 반려견과 함께 가기 좋은 장소 3곳을 선택하세요.
    - lvl 값이 낮을수록 초보자에게 쉬운 코스입니다.
    - category 값이 다양할수록 좋습니다 (walk, culture, eat 등).

    출력에는 반드시 아래 필드만 포함하세요:
    - category
    - place_nm
    - latitude
    - longitude
    - land_address
    - cours_dc

    입력 데이터 (JSON 리스트 형식): {filtered_values}

    출력은 반드시 JSON 형식으로, 데이터를 변경하지 않고, 선택한 3개의 장소를 아래 구조로 반환하세요:
    {{ 'poi':
        [
            {{
                "category": str,
                "place_nm": str,
                "latitude": float,
                "longitude": float,
                "land_address": str,
                "cours_dc": str
            }},
            ...
        ]
    }}
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    parser = PydanticOutputParser(pydantic_object=POIData_List)

    chain = prompt | llm_low | parser
    input_data = {"filtered_values": filtered_values}
    poi_recommendation = chain.invoke(input_data)
    
    result = POIRecommendationData(radius=radius, poi=poi_recommendation.poi)
    print("2. poi_recommend : ", result)
    return result

# 3. POI에 대한 짧은 제목
# 입력: POI N개
# 출력: 반경, {POI, 각 소개글}
def title_recommend(poi_data:POIRecommendationData):
    prompt_template = """
        당신은 반려견과 함께 나들이할 장소를 소개하는 작가입니다.
        아래는 장소 정보 데이터입니다.
        각 장소의 'place_nm', 'category', 그리고 'cours_dc'(있을 경우)를 참고하여
        짧고 자연스러운 소개 문장(poi_title)을 작성하세요.

        **주의**:
        - 'place_nm'은 **출력 문장에서 반드시 원문 그대로 포함**해야 합니다. 
        - 공백, 철자, 순서, 구두점을 포함하여 **입력된 문자열을 그대로 복사**하세요.
        - 'place_nm'은 수정, 번역, 변형 절대 금지입니다. (예: 띄어쓰기 변경, 오타 교정 금지)

        - 문체: 따뜻하고 자연스럽게
        - 길이: 1문장 (15자 내외)
        - 예시:
            - "도심 속 반려견 산책 명소, place_nm"
            - "완만한 코스로 편히 걷는 place_nm"

        입력 데이터(JSON 리스트): {poi_data}

        **출력 형식** (JSON 문자열 리스트), 반드시 아래 구조로 반환하세요:
        [
            "도심 속 반려견 산책 명소, 고래의모험",
            "문화 공연을 즐길 수 있는 경기아트센터",
            "휴식하기 좋은 펫프렌들리 카페, 유폴24시 애견셀프목욕 무인카페"
        ]
    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    parser = StrOutputParser()

    chain = prompt | llm_high | parser

    input_data = {"poi_data": json.dumps([{"category": p.category, "place_nm": p.place_nm} for p in poi_data.poi])}
    title_list = json.loads(chain.invoke(input_data))

    for base, new_title in zip(poi_data.poi, title_list):
        base.poi_title = new_title  # title만 업데이트
    
    print("3. title_recommend : ", poi_data)
    return poi_data # 제목만 업데이트 해서 반환

#=========== [ POI 요청 메서드 ] =============

# 입력: 카테고리, 반경, 위치
# 출력: 카테고리 별 반경 내 모든 poi
poi_list = [POI_CULTURE, POI_EAT, POI_WALK, POI_HOSPITAL, POI_TRIP, POI_SERVICE, POI_SHOP]
def poi_placeview(data:POIPLaceViewRequest):
    # 카테고리 키 검증
    if data.category in poi_list:
        nearby = r.georadius(data.category, data.user_pos.user_lon, data.user_pos.user_lat, data.radius, unit="km")
        filtered_values: list[POIData] = []
        if nearby:
            filtered_values.extend([r.hgetall(v) for v in nearby])

        # if nearby:
        #     for v in nearby:
        #         poi_dict = r.hgetall(v)
        #         decoded = {k.decode(): v.decode() for k, v in poi_dict.items()}
        #         poi_obj = POIData(**decoded)
        #         filtered_values.append(poi_obj)
        
        return filtered_values
    else:
        print(f"잘못된 카테고리: {data.category}")

#=========== [ 테스트 코드 (차후 삭제) ] =============

start = time.time()
print("🚀 실행 시작")

dog = DogInfoData(age=3, breed="보더콜리",gender=0,weight=4.2)
user = UserPosData(user_lat=37.2498756, user_lon=127.0080277)

data = CourseRcommendRequest(dog_info=dog, user_pos=user)
result = course_recommend(data)
print("4. result : ", result)

end = time.time()
print(f"✅ 실행 완료 (총 {end - start:.2f}초 소요)")
