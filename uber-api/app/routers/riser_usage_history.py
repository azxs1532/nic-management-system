from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models import RiserUsage, RiserManagement  # ✅ 추가됨: RiserManagement import
from app.schemas import RiserStatusUpdateRequest,RiserRemarksUpdateRequest,RiserWorkLinkUpdateRequest, RiserRequesterUpdateRequest, RiserUsageCreate, RiserUsageResponse, RiserManagementCreate, RiserManagementResponse  # ✅ 추가됨: 관련된 스키마 import

import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# ✅ Riser 사용 이력 조회 API
@router.get("/history", response_model=List[RiserUsageResponse])
def fetch_riser_usage_history(db: Session = Depends(get_db)):
    try:
        riser_usage_entries = db.query(RiserUsage).all()
        
        if not riser_usage_entries:
            logger.warning("⚠️ Riser 사용 이력이 존재하지 않습니다.")
            return []

        logger.info(f"✅ {len(riser_usage_entries)}개의 Riser 사용 이력 조회 성공")
        return riser_usage_entries
    
    except Exception as e:
        logger.error(f"🚨 Riser 사용 이력 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="Riser 사용 이력 조회 중 서버 오류가 발생했습니다.")

# ✅ Riser 신규 입고 API (중복 FINID 체크 후 처리)
@router.post("/register", response_model=RiserManagementResponse)
def register_riser(data: RiserManagementCreate, db: Session = Depends(get_db)):
    try:
        # 🔍 기존 FINID가 존재하는지 확인
        existing_riser = db.query(RiserManagement).filter(
            RiserManagement.finid == data.finid,
            RiserManagement.center == data.center
        ).first()

        if existing_riser:
            # ✅ 기존 데이터가 있으면 재고 업데이트
            existing_riser.total_quantity += data.total_quantity
            existing_riser.available_quantity += data.available_quantity
            db.commit()
            db.refresh(existing_riser)
            return {"message": "✅ 기존 FINID의 재고가 업데이트되었습니다.", "finid": data.finid}

        else:
            # ✅ 새로운 FINID면 신규 데이터 삽입
            new_riser = RiserManagement(**data.dict())
            db.add(new_riser)
            db.commit()
            db.refresh(new_riser)
            return {"message": "✅ 새로운 Riser 데이터가 등록되었습니다.", "finid": data.finid}

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="⚠ FINID가 이미 존재합니다. 중복 등록 불가.")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"🚨 서버 오류 발생: {str(e)}")



# ✅ Riser 사용 이력 등록 API (사용 후 재고 차감) ✅ 추가됨
@router.post("/update/register", response_model=RiserUsageResponse)
def register_riser_usage(data: RiserUsageCreate, db: Session = Depends(get_db)):
    try:
        # 🔍 사용하려는 FINID + 모델명 + 센터가 재고에 있는지 확인
        riser_stock = db.query(RiserManagement).filter(
            RiserManagement.finid == data.finid,
            RiserManagement.riser_type == data.riser_type,  # ✅ 모델명 추가
            RiserManagement.center == data.center
        ).first()

        if not riser_stock:
            raise HTTPException(status_code=404, detail="❌ 해당 모델과 FINID의 Riser 재고가 존재하지 않습니다.")

        if riser_stock.available_quantity < data.quantity:
            raise HTTPException(status_code=400, detail="❌ 남은 수량보다 많은 수량을 사용할 수 없습니다.")

        # ✅ 사용한 만큼 재고 차감
        riser_stock.available_quantity -= data.quantity

        # ✅ 새로운 사용 이력 등록
        new_riser_usage = RiserUsage(**data.dict())
        db.add(new_riser_usage)
        db.commit()
        db.refresh(new_riser_usage)

        return new_riser_usage

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"🚨 Riser 사용 이력 등록 중 오류 발생: {str(e)}")


# ✅ 요청자(requester) 업데이트 API
@router.put("/update-requester/{id}")
def update_riser_requester(id: int, request: RiserRequesterUpdateRequest, db: Session = Depends(get_db)):
    print(f"📡 [DEBUG] 요청자 업데이트 요청 ID: {id}, 요청자: {request.requester}")
    riser_entry = db.query(UsageHistory).filter(UsageHistory.id == id).first()
    if not riser_entry:
        print("❌ [ERROR] NIC 사용 이력111을 찾을 수 없습니다.")
        raise HTTPException(status_code=404, detail="NIC 사용 이력을 찾을 수 없습니다.")

    riser_entry.requester = request.requester
    db.commit()
    db.refresh(riser_entry)
    print(f"✅ [SUCCESS] 요청자 업데이트 완료!2222 저장된 값: {riser_entry.requester}")
    return {"message": "요청자 업데이트 완료", "id": id, "requester": riser_entry.requester}

# ✅ 아지트 링크(work_link) 업데이트 API
@router.put("/update-worklink/{id}")
def update_riser_work_link(id: int, request: RiserWorkLinkUpdateRequest, db: Session = Depends(get_db)):
    riser_entry = db.query(UsageHistory).filter(UsageHistory.id == id).first()
    if not riser_entry:
        raise HTTPException(status_code=404, detail="NIC 사용 이력을 찾을 수 없습니다.")

    riser_entry.work_link = request.work_link
    db.commit()
    db.refresh(riser_entry)
    return {"message": "아지트 링크 업데이트 완료", "id": id, "work_link": riser_entry.work_link}


# ✅ Riser 사용 이력 상태 업데이트 API
@router.put("/update-status/{id}")
def update_riser_status(id: int, request: RiserStatusUpdateRequest, db: Session = Depends(get_db)):
    riser_entry = db.query(RiserUsage).filter(RiserUsage.id == id).first()
    if not riser_entry:
        raise HTTPException(status_code=404, detail=f"ID {id}에 대한 Riser 사용 이력이 없습니다.")

    riser_entry.status = request.status
    db.commit()
    db.refresh(riser_entry)
    return {"message": "✅ Riser 사용 이력 상태 업데이트 완료", "id": id}


# ✅ Riser 사용 이력 비고(remarks) 업데이트 API
@router.put("/update-remarks/{id}")
def update_riser_remarks(id: int, request: RiserRemarksUpdateRequest, db: Session = Depends(get_db)):
    riser_entry = db.query(RiserUsage).filter(RiserUsage.id == id).first()
    if not riser_entry:
        raise HTTPException(status_code=404, detail=f"ID {id}에 대한 Riser 사용 이력이 없습니다.")

   
    riser_entry.remarks = request.remarks

    db.commit()
    db.refresh(riser_entry)
    return {"message": "✅ Riser 비고 업데이트 완료", "id": id}


@router.delete("/delete/{id}")
def delete_riser_usage(id: int, db: Session = Depends(get_db)):
    riser_entry = db.query(RiserUsage).filter(RiserUsage.id == id).first()
    if not riser_entry:
        raise HTTPException(status_code=404, detail=f"ID {id}에 대한 Riser 사용 이력이 없습니다.")

    # 🔍 사용 이력 삭제 시 재고 복구 (FINID + 모델명 + 센터 비교)
    riser_stock = db.query(RiserManagement).filter(
        RiserManagement.finid == riser_entry.finid,
        RiserManagement.riser_type == riser_entry.riser_type,  # ✅ 모델명 추가
        RiserManagement.center == riser_entry.center
    ).first()

    if riser_stock:
        # ✅ 재고 복구 전, available_quantity가 None이 아닌지 체크
        if riser_stock.available_quantity is not None:
            riser_stock.available_quantity += riser_entry.quantity
        else:
            riser_stock.available_quantity = riser_entry.quantity  # 만약 None이면 기본값 설정

    # ✅ 사용 이력 삭제
    db.delete(riser_entry)
    db.commit()
    
    return {"message": "✅ Riser 사용 이력 삭제 완료 및 재고 복구", "id": id}

