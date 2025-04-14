from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import RiserManagement
from app.schemas import RiserManagementCreate, RiserManagementResponse

router = APIRouter()

# ✅ Riser 전체 목록 조회 API
@router.get("/list", response_model=List[RiserManagementResponse])
def get_all_riser_management(db: Session = Depends(get_db)):
    risers = db.query(RiserManagement).all()
    return risers

# ✅ 특정 FINID의 Riser 데이터 조회 API
@router.get("/list/{finid}", response_model=List[RiserManagementResponse])
def get_riser_by_finid(finid: str, db: Session = Depends(get_db)):
    riser_entries = db.query(RiserManagement).filter(RiserManagement.finid == finid).all()
    if not riser_entries:
        raise HTTPException(status_code=404, detail="해당 FINID의 Riser 데이터가 없습니다.")
    return riser_entries

# ✅ Riser 신규 입고 API
@router.post("/register", response_model=RiserManagementResponse)
def register_riser(data: RiserManagementCreate, db: Session = Depends(get_db)):
    riser_entry = RiserManagement(**data.dict())
    db.add(riser_entry)
    db.commit()
    db.refresh(riser_entry)
    return riser_entry

# ✅ Riser 데이터 수정 API
@router.put("/update/{id}")
def update_riser(id: int, data: RiserManagementCreate, db: Session = Depends(get_db)):
    riser_entry = db.query(RiserManagement).filter(RiserManagement.id == id).first()
    if not riser_entry:
        raise HTTPException(status_code=404, detail="해당 ID의 Riser 데이터가 없습니다.")

    for key, value in data.dict().items():
        setattr(riser_entry, key, value)

    db.commit()
    db.refresh(riser_entry)
    return {"message": "Riser 데이터 수정 완료", "id": id}

# ✅ Riser 데이터 삭제 API
@router.delete("/delete/{id}")
def delete_riser(id: int, db: Session = Depends(get_db)):
    riser_entry = db.query(RiserManagement).filter(RiserManagement.id == id).first()
    if not riser_entry:
        raise HTTPException(status_code=404, detail="해당 ID의 Riser 데이터가 없습니다.")

    db.delete(riser_entry)
    db.commit()
    return {"message": "Riser 데이터 삭제 완료", "id": id}

