# 🚀 NIC Management System 배포 가이드

이 문서는 FastAPI + React 기반 NIC 관리 시스템의 **내부망 서버 배포 절차**를 설명합니다.

---

## ✅ 1. 서버 준비 (Ubuntu 기준)

```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql
```

---

## ✅ 2. PostgreSQL 설정

```bash
sudo -u postgres psql
CREATE USER uber_admin WITH PASSWORD 'dkadmin1';
CREATE DATABASE uber_nic_db OWNER uber_admin;
```

---

## ✅ 3. 백엔드 실행 (FastAPI)

```bash
cd uber-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## ✅ 4. 프론트엔드 빌드 (React)

```bash
cd uber-frontend
npm install
npm run build
```

빌드된 정적 파일을 Nginx 또는 내부 static 웹서버에 배포합니다.

---

## ✅ 5. .env 설정 예시

```env
# 백엔드 .env
DB_URL=postgresql://uber_admin:dkadmin1@localhost/uber_nic_db

# 프론트엔드 .env
REACT_APP_API_URL=http://localhost:8000
```

---

## 🧩 기타

- 외부망 차단된 환경에서 npm, pip 패키지 미리 옮겨둘 것
- `rsync`, `scp` 등으로 내부망 서버로 코드 이관 가능
