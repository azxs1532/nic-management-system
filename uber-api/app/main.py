from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import incoming, usage_history, riser_management, riser_usage_history 
import logging

# ✅ FastAPI 인스턴스 생성
app = FastAPI(title="NIC Management API", description="NIC 입고, 사용 대기, 사용 이력 관리 API")

# ✅ 로깅 설정 (FastAPI 실행 로그 출력 - 상세 로그 포맷 추가)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ✅ CORS 설정 (보안 고려하여 특정 도메인 허용)
origins = [
    "http://localhost:3000",  # ✅ 로컬 프론트엔드
    "http://127.0.0.1:3000",  # ✅ 로컬 IP 프론트엔드
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

# ✅ 데이터베이스 초기화
@app.on_event("startup")
def startup():
    logger.info("🚀 FastAPI 서버 시작됨: NIC Management API")
    init_db()

# ✅ API 라우터 등록
app.include_router(incoming.router, prefix="/nic/inventory", tags=["NIC 신규 입고"])

# ✅ 기존 "NIC 재고 관리"는 주석 처리
# app.include_router(nicinventory.router, prefix="/nic/nicinventory", tags=["NIC 재고 관리"])

# ✅ 사용 이력 라우터
app.include_router(usage_history.router, prefix="/nic/usage", tags=["NIC 사용 이력"])

# ✅ Riser 관련 라우터 추가
app.include_router(riser_management.router, prefix="/riser/management", tags=["Riser 관리"])
app.include_router(riser_usage_history.router, prefix="/riser/usage", tags=["Riser 사용 이력"])

# ✅ 기본 엔드포인트 (FastAPI 상태 체크)
@app.get("/")
def root():
    return {"message": "NIC Management API is running"}

# ✅ FastAPI 상태 확인 (서버 헬스 체크)
@app.get("/health")
def health_check():
    return {"status": "OK", "message": "FastAPI is healthy"}
