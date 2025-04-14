# NIC Management System (NIC 재고/사용 이력 관리 웹)

FastAPI + React 기반의 NIC(네트워크 인터페이스 카드) 입고, 재고, 사용 이력을 통합 관리하는 내부망용 웹 시스템입니다.

## 🧩 주요 기술 스택

- Frontend: **React**, Bootstrap
- Backend: **FastAPI**, PostgreSQL
- DB 마이그레이션: Alembic
- 배포 환경: Ubuntu 내부망 서버 (인터넷 미연결)
- 기타: Axios, Excel 업로드 지원, 수동 작업 추적

---

## 📁 프로젝트 구조

```
uber-api/               # FastAPI 백엔드
├── app/
│   ├── database.py     # DB 연결
│   ├── main.py         # FastAPI 실행 진입점
│   ├── models.py       # SQLAlchemy 모델
│   ├── schemas.py      # Pydantic 스키마
│   └── routers/        # 입고, 재고, 사용 이력 API

uber-frontend/          # React 프론트엔드
├── src/
│   ├── components/     # NIC 관련 UI 컴포넌트
│   ├── pages/          # 입고/재고/사용 페이지
│   └── App.js          # 라우팅
```

---

## 💡 주요 기능

- ✅ NIC 입고 등록 (엑셀 업로드 지원)
- ✅ 재고 수량 상태 관리 (활용가능 / 대기 / 장애대처)
- ✅ 사용 이력 등록 및 상태 변경 (예약 / 완료 등)
- ✅ 센터별 필터, 벤더 필터
- ✅ 사용 그룹 관리 및 FINID 기반 정리
- ✅ 장애 시 교체 기능 및 이력 추적
- ✅ 작업 예약 → 실사용 → 완료까지 전체 흐름 기록

---

## ⚙️ 실행 방법

### 1. 백엔드 실행 (FastAPI)

```bash
cd uber-api
uvicorn app.main:app --reload
```

### 2. 프론트엔드 실행 (React)

```bash
cd uber-frontend
npm install
npm start
```

> `.env` 파일에 백엔드 API 주소를 `REACT_APP_API_URL`로 설정

---

## 🔐 주의 사항

- 내부망 운영 환경 기준으로 제작됨 (인터넷 연결 없이 배포됨)
- PostgreSQL DB는 `uber_nic_db`, 계정: `uber_admin`
- `.env`는 Git에 포함되지 않도록 주의 (보안정보 포함)

---

## ✨ 만든 이유

데이터센터에서 NIC 사용 흐름을 실시간으로 관리하고,  
수작업 오류를 줄이기 위한 내부 자동화 프로젝트로 시작되었습니다.  
운영자 중심 UX, 명확한 상태 전환, 실시간 이력 파악을 목표로 개발했습니다.
