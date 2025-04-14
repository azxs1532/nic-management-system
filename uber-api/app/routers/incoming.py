from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from datetime import date
from app.models import UsageHistory  
from app.schemas import NICRequest, NICIncomingResponse

router = APIRouter()

# ✅ NIC 신규 입고 데이터 등록 API (UsageHistory에만 저장)
@router.post("/incoming/register", response_model=dict)
def register_nic(nic_data: NICRequest, db: Session = Depends(get_db)):
    try:
        usage_history_entries = []
        skipped_entries = 0

        for record in nic_data.records:
            # 중복된 MAC 주소 체크 (UsageHistory에서만 체크)
            if db.query(UsageHistory).filter_by(mac_address=record.mac_address).first():
                skipped_entries += 1
                continue

            # 사용 이력 테이블에 데이터 저장
            usage_history_entries.append(UsageHistory(
                vendor=record.vendor,
                part=record.part,
                finid=record.finid,
                mac_address=record.mac_address,
                quantity=1,
                center=record.center,
                status="사용 가능",
                date=date.today(),
                model=record.part,
                requester=record.requester if record.requester else "미정",
                work_link=record.work_link if record.work_link else "미정",
                nic_part_number=record.nic_part_number
            ))

        # 데이터 저장
        if usage_history_entries:
            db.add_all(usage_history_entries)

        db.commit()

        return {
            "message": f"{len(usage_history_entries)}개의 NIC 사용 이력이 성공적으로 등록되었습니다!",
            "skipped_count": skipped_entries,
            "skipped": f"{skipped_entries}개의 중복된 MAC 주소는 등록되지 않았습니다."
        }

    except Exception as e:
        db.rollback()
        print("🚨 서버 오류 발생:", str(e))  # 로그 출력
        raise HTTPException(status_code=500, detail=f"서버 오류 발생: {str(e)}")

# ✅ NIC 입고 목록 조회 API (UsageHistory에서만 조회)
@router.get("/incoming/list", response_model=list[NICIncomingResponse])
def get_incoming_nics(db: Session = Depends(get_db)):
    nic_list = db.query(UsageHistory).all()  # ✅ NICInventory 제거, UsageHistory에서 조회
    return nic_list

# ✅ 특정 MAC 주소로 NIC 삭제 API (UsageHistory에서 삭제)
@router.delete("/incoming/delete/{mac}", response_model=dict)
async def delete_nic(mac: str, db: Session = Depends(get_db)):
    nic_entry = db.query(UsageHistory).filter_by(mac_address=mac).first()
    if not nic_entry:
        raise HTTPException(status_code=404, detail="해당 MAC 주소의 NIC를 찾을 수 없습니다.")

    db.delete(nic_entry)
    db.commit()
    return {"message": f"NIC({mac})가 삭제되었습니다."}

# ✅ NIC 전체 삭제 API (입고 + 사용이력 전부 삭제)
@router.delete("/incoming/delete-all", response_model=dict)
async def delete_all_nics(db: Session = Depends(get_db)):
    try:
        if not db.query(UsageHistory).first():
            raise HTTPException(status_code=404, detail="삭제할 데이터가 없습니다.")

        db.query(UsageHistory).delete(synchronize_session=False)
        db.commit()
        return {"message": "전체 NIC 사용 이력 삭제 완료!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"삭제 중 오류 발생: {str(e)}")
