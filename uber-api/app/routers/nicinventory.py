from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import NICInventory
from app.schemas import NICInventoryResponse, NICInventoryCreate
from datetime import datetime

router = APIRouter()

# ✅ 전체 NIC 재고 조회 API
@router.get("/SaveNew", response_model=list[NICInventoryResponse])
def get_all_inventory(db: Session = Depends(get_db)):
    return db.query(NICInventory).all()

# ✅ 특정 센터의 NIC 재고 조회 API
@router.get("/SaveNew/{center}", response_model=list[NICInventoryResponse])
def get_inventory_by_center(center: str, db: Session = Depends(get_db)):
    return db.query(NICInventory).filter(NICInventory.center == center).all()

# ✅ NIC 재고 추가 API
@router.post("/SaveNew/addlist", response_model=dict)
def add_inventory(nic_data: NICInventoryCreate, db: Session = Depends(get_db)):
    try:
        # ✅ 중복된 모델인지 확인 (센터까지 포함)
        existing_nic = db.query(NICInventory).filter(
            NICInventory.center == nic_data.center,
            NICInventory.nic_type == nic_data.nic_type
        ).first()

        if existing_nic:
            raise HTTPException(status_code=400, detail="이미 존재하는 NIC 모델입니다.")

        # ✅ 새로운 NIC 재고 추가
        new_nic = NICInventory(
            center=nic_data.center,
            vendor=nic_data.vendor,
            nic_type=nic_data.nic_type,
            available=nic_data.available if nic_data.available is not None else 0,
            fault=nic_data.fault if nic_data.fault is not None else 0,
            standby=nic_data.standby if nic_data.standby is not None else 0,
            created_at=datetime.utcnow(),  # ✅ 생성 시간 저장
            updated_at=datetime.utcnow()   # ✅ 생성 시점의 업데이트 시간도 저장
        )

        db.add(new_nic)  # ✅ 데이터 추가
        db.commit()
        db.refresh(new_nic)  # ✅ 최신 데이터 반영

        return {"message": "NIC 재고 추가 완료!", "id": new_nic.id}
    
    except Exception as e:
        db.rollback()
        print(f"🚨 NIC 추가 중 오류 발생: {str(e)}")  # ✅ 콘솔에 오류 출력
        raise HTTPException(status_code=500, detail=f"NIC 추가 실패: {str(e)}")

# ✅ NIC 재고 수정 API
@router.put("/SaveNew/{id}", response_model=dict)
def update_inventory(id: int, updated_data: NICInventoryCreate, db: Session = Depends(get_db)):
    inventory_item = db.query(NICInventory).filter(NICInventory.id == id).first()
    
    if not inventory_item:
        raise HTTPException(status_code=404, detail="NIC 재고를 찾을 수 없습니다.")
    
    inventory_item.center = updated_data.center
    inventory_item.vendor = updated_data.vendor
    inventory_item.nic_type = updated_data.nic_type
    inventory_item.available = updated_data.available
    inventory_item.fault = updated_data.fault
    inventory_item.standby = updated_data.standby
    inventory_item.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(inventory_item)
    
    return {"message": "NIC 재고 수정 완료!", "id": inventory_item.id}

# ✅ NIC 재고 삭제 API
@router.delete("/SaveNew/{id}", response_model=dict)
def delete_inventory(id: int, db: Session = Depends(get_db)):
    inventory_item = db.query(NICInventory).filter(NICInventory.id == id).first()
    
    if not inventory_item:
        raise HTTPException(status_code=404, detail="NIC 재고를 찾을 수 없습니다.")

    db.delete(inventory_item)
    db.commit()

    return {"message": f"NIC 재고(ID: {id}) 삭제 완료!"}