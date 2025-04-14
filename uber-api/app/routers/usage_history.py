from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UsageHistory
from datetime import datetime
from typing import List, Dict
from app.schemas import (
    UsageHistoryResponse, AvailableNICResponse, 
    RequesterUpdateRequest, WorkLinkUpdateRequest, StatusUpdateRequest, MacAddressUpdateRequest, 
    CenterUpdateRequest, DateUpdateRequest, NewUsageEntryListRequest, NICUpdateRequest, GroupMemoUpdateRequest, UpdateFinidRequest,
    VendorUpdateRequest, UsageScheduleUpdateRequest, UsageGroupUpdateRequest, GroupResetRequest, ResetGroupRequest
)

router = APIRouter()

# ✅ NIC 사용 이력 조회 API
@router.get("/history", response_model=list[UsageHistoryResponse]) 
def get_usage_history(db: Session = Depends(get_db)):
    usage_history = db.query(UsageHistory).all()
    for entry in usage_history:
        
        if entry.nic_part_number is None:
            entry.nic_part_number = "미정"
        if entry.requester is None:
            entry.requester = "미정"
        if entry.work_link is None:
            entry.work_link = "미정"
        if entry.finid is None:
            entry.finid = "미정"
        if entry.mac_address is None:
            entry.mac_address = "미정"

    return usage_history  # ✅ NULL 값 방지 후 반환
# ✅ 사용 가능 NIC 요약 조회 API
@router.get("/nicsum", response_model=list[AvailableNICResponse])
def get_available_nic_summary(db: Session = Depends(get_db)):
    try:
        results = (
            db.query(
                UsageHistory.finid,
                UsageHistory.vendor,
                UsageHistory.nic_part_number
            )
            .filter(UsageHistory.status == "사용 가능")  
            .all()
        )
        return results  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류 발생: {str(e)}")

# ✅ 요청자(requester) 업데이트 API
@router.put("/update-requester/{id}")
def update_requester(id: int, request: RequesterUpdateRequest, db: Session = Depends(get_db)):
    print(f"📡 [DEBUG] 요청자 업데이트 요청 ID: {id}, 요청자: {request.requester}")
    nic_entry = db.query(UsageHistory).filter(UsageHistory.id == id).first()
    if not nic_entry:
        print("❌ [ERROR] NIC 사용 이력111을 찾을 수 없습니다.")
        raise HTTPException(status_code=404, detail="NIC 사용 이력을 찾을 수 없습니다.")

    nic_entry.requester = request.requester
    db.commit()
    db.refresh(nic_entry)
    print(f"✅ [SUCCESS] 요청자 업데이트 완료!2222 저장된 값: {nic_entry.requester}")
    return {"message": "요청자 업데이트 완료", "id": id, "requester": nic_entry.requester}

# ✅ 아지트 링크(work_link) 업데이트 API
@router.put("/update-worklink/{id}")
def update_work_link(id: int, request: WorkLinkUpdateRequest, db: Session = Depends(get_db)):
    nic_entry = db.query(UsageHistory).filter(UsageHistory.id == id).first()
    if not nic_entry:
        raise HTTPException(status_code=404, detail="NIC 사용 이력을 찾을 수 없습니다.")

    # ✅ work_link 변경 시 group_memo 초기화
    nic_entry.work_link = request.work_link
    nic_entry.group_memo = ""  # 기존 메모 초기화

    db.commit()
    db.refresh(nic_entry)
    return {
        "message": "아지트 링크 및 그룹 메모 초기화 완료",
        "id": id,
        "work_link": nic_entry.work_link
    }

# ✅ 상태(status) 업데이트 API
@router.put("/update-status/{id}")
def update_status(id: int, request: StatusUpdateRequest, db: Session = Depends(get_db)):
    nic_entry = db.query(UsageHistory).filter(UsageHistory.id == id).first()
    if not nic_entry:
        raise HTTPException(status_code=404, detail="NIC 사용 이력을 찾을 수 없습니다.")

    nic_entry.status = request.status
    db.commit()
    db.refresh(nic_entry)
    return {"message": "상태 업데이트 완료", "id": id, "status": nic_entry.status}

# ✅ MAC 주소 업데이트 API
@router.put("/update-mac/{id}")
def update_mac_address(id: int, request: MacAddressUpdateRequest, db: Session = Depends(get_db)):
    # 현재 NIC 조회
    nic_entry = db.query(UsageHistory).filter(UsageHistory.id == id).first()
    
    if not nic_entry:
        raise HTTPException(status_code=404, detail="NIC 사용 이력을 찾을 수 없습니다.")

    # 중복 MAC 주소 체크 (자기 자신 제외)
    duplicate = db.query(UsageHistory).filter(
        UsageHistory.mac_address == request.mac_address,
        UsageHistory.id != id  # 자기 자신은 제외
    ).first()

    if duplicate:
        raise HTTPException(status_code=400, detail="이미 존재하는 MAC 주소입니다.")

    # MAC 주소 업데이트
    nic_entry.mac_address = request.mac_address
    db.commit()
    db.refresh(nic_entry)
    
    return {"message": "MAC 주소 업데이트 완료", "id": id, "mac_address": nic_entry.mac_address}


# ✅ 센터 업데이트 API (PUT 요청)
@router.put("/update-center/{id}")
def update_center(id: int, request: CenterUpdateRequest, db: Session = Depends(get_db)):
    nic_entry = db.query(UsageHistory).filter(UsageHistory.id == id).first()

    if not nic_entry:
        raise HTTPException(status_code=404, detail="NIC 카드 정보를 찾을 수 없습니다.")

    # ✅ 센터 정보 업데이트

    nic_entry.center = request.center
    nic_entry.work_link = "미정"
    nic_entry.requester = "미정"
    db.commit()
    db.refresh(nic_entry)

    return {"message": "센터가 성공적으로 변경되었습니다.", "id": id, "center": nic_entry.center}
    
@router.put("/update-date/{finid}")
def update_finid_date(finid: str, request: DateUpdateRequest, db: Session = Depends(get_db)):
    nic_entry = db.query(UsageHistory).filter(UsageHistory.finid == finid).first()

    if not nic_entry:
        raise HTTPException(status_code=404, detail="NIC 사용 이력을 찾을 수 없습니다.")

    try:
        nic_entry.date = request.date
        db.commit()
        db.refresh(nic_entry)
        return {"message": "입고 날짜가 성공적으로 변경되었습니다.", "finid": finid, "date": nic_entry.date}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"입고 날짜 업데이트 실패: {str(e)}")

@router.post("/add-multi")
def add_multiple_usage_entries(request: NewUsageEntryListRequest, db: Session = Depends(get_db)):
    try:
        if not request.entries:
            raise HTTPException(status_code=400, detail="입력값이 없습니다.")

        # ✅ 등록 요청된 모든 work_link 모음
        requested_links = list(set([entry.work_link for entry in request.entries if entry.work_link]))

        # ✅ 이미 등록된 work_link 확인
        # existing = db.query(UsageHistory).filter(UsageHistory.work_link.in_(requested_links)).all()
        # if existing:
        #     duplicated_links = list(set([item.work_link for item in existing]))
        #     raise HTTPException(
        #         status_code=409,
        #         detail=f"❌ 이미 등록된 아지트 링크가 존재합니다: {', '.join(duplicated_links)}"
        #     )

        # ✅ 고유 group_id 생성
        group_id = f"GID_{int(datetime.now().timestamp() * 1000)}"
        new_entries = []

        for entry in request.entries:
            requested_date = entry.requested_date or date.today()
            expected_complete_date = entry.expected_complete_date or "미정"

            for _ in range(entry.quantity):
                new_entry = UsageHistory(
                    vendor=entry.vendor,
                    nic_part_number="미정",
                    center=entry.center,
                    requester=entry.requester,
                    work_link=entry.work_link,
                    status="사용 대기",
                    finid="미정",
                    mac_address="미정",
                    part=entry.part,
                    model=entry.part,
                    date=datetime.now(),
                    group_id=group_id,
                    requested_date=requested_date,
                    expected_complete_date=expected_complete_date
                )
                new_entries.append(new_entry)

        db.bulk_save_objects(new_entries)
        db.commit()

        return {"message": f"{len(new_entries)}개의 미입고 NIC 이력이 등록되었습니다."}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"NIC 사용 이력 등록 실패: {str(e)}")

@router.post("/add-multi2")
def add_multiple_usage_entries2(request: NewUsageEntryListRequest, db: Session = Depends(get_db)):
    try:
        if not request.entries:
            raise HTTPException(status_code=400, detail="입력값이 없습니다.")

        new_entries = []

        for entry in request.entries:
            group_id = entry.group_id
            requested_date = entry.requested_date or date.today()
            expected_complete_date = entry.expected_complete_date or "미정"


            for _ in range(entry.quantity):
                new_entry = UsageHistory(
                    vendor=entry.vendor,
                    nic_part_number="미정",
                    center=entry.center,
                    requester=entry.requester,
                    work_link=entry.work_link,
                    status="사용 대기",
                    finid="미정",
                    mac_address="미정",
                    part=entry.part,
                    model=entry.part,
                    date=datetime.now(),
                    group_id=group_id,
                    requested_date=requested_date,
                    expected_complete_date=expected_complete_date
                )
                new_entries.append(new_entry)

        db.bulk_save_objects(new_entries)
        db.commit()

        return {"message": f"{len(new_entries)}개의 미입고 NIC 이력이 등록되었습니다."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"NIC 사용 이력 등록 실패: {str(e)}")

@router.put("/update-nic-info")
def update_nic_info(request: List[NICUpdateRequest], db: Session = Depends(get_db)):
    """
    ✅ ID 기준으로 MAC 주소 및 NIC 파트 번호 업데이트
    ✅ 상태(status)를 "사용 예약"으로 변경
    ✅ 중복된 MAC 주소 체크
    """
    try:
        mac_addresses = [item.mac_address for item in request if item.mac_address and item.mac_address != "미정"]
        existing_macs = db.query(UsageHistory.mac_address).filter(UsageHistory.mac_address.in_(mac_addresses)).all()
        existing_macs = {mac[0] for mac in existing_macs}  # 중복 MAC 주소 집합

        duplicate_macs = [mac for mac in mac_addresses if mac in existing_macs]
        if duplicate_macs:
            raise HTTPException(status_code=400, detail=f"업데이트 실패: 중복된 MAC 주소 발견 - {', '.join(duplicate_macs)}")

        for item in request:
            nic_entry = db.query(UsageHistory).filter(UsageHistory.id == item.id).first()  # ✅ ID 기준으로 찾음
            if nic_entry:
                nic_entry.finid = item.finid  # FINID 업데이트
                nic_entry.mac_address = item.mac_address  # MAC 주소 업데이트
                nic_entry.nic_part_number = item.nic_part_number  # NIC 파트번호 업데이트
                nic_entry.status = "사용 예약"  # ✅ 상태 변경
        
        db.commit()
        return {"message": "NIC 정보 업데이트 완료"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"업데이트 실패: {str(e)}")


@router.delete("/delete-usage")
def delete_nic_usage(request_data: Dict[str, list], db: Session = Depends(get_db)):
    """
    ✅ JSON Body로 전달받아 여러 개 ID 삭제
    """
    try:
        ids = request_data.get("ids", [])
        if not ids:
            raise HTTPException(status_code=400, detail="삭제할 ID 목록이 없습니다.")

        db.query(UsageHistory).filter(UsageHistory.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
        return {"message": "NIC 사용 이력 삭제 완료"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"삭제 실패: {str(e)}")

@router.put("/update-memo/{id}")
def update_group_memo(id: int, request: GroupMemoUpdateRequest, db: Session = Depends(get_db)):
    item = db.query(UsageHistory).filter(UsageHistory.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="사용 이력을 찾을 수 없습니다.")

    if request.group_memo is not None:
        item.group_memo = request.group_memo
    if request.requested_date is not None:
        item.requested_date = request.requested_date
    if request.expected_complete_date is not None:
        item.expected_complete_date = request.expected_complete_date

    db.commit()
    return {"message": "그룹 정보가 업데이트되었습니다."}


@router.put("/update-finid")
def update_finid_batch(request: UpdateFinidRequest, db: Session = Depends(get_db)):
    for item in request.items:
        nic = db.query(UsageHistory).filter(UsageHistory.id == item.id).first()
        if nic:
            nic.finid = item.finid
    db.commit()
    return {"message": "FINID 업데이트 완료", "count": len(request.items)}

@router.put("/update-vendor-batch")
def update_vendor_batch(request: VendorUpdateRequest, db: Session = Depends(get_db)):
    for item in request.items:
        nic = db.query(UsageHistory).filter(UsageHistory.id == item.id).first()
        if nic:
            nic.vendor = item.vendor
        else:
            raise HTTPException(status_code=404, detail=f"NIC 사용 이력 ID {item.id}를 찾을 수 없습니다.")
    db.commit()
    return {"message": "✅ 벤더 일괄 수정 완료"}

@router.put("/update-schedule/{id}")
def update_usage_schedule(id: int, request: UsageScheduleUpdateRequest, db: Session = Depends(get_db)):
    nic = db.query(UsageHistory).filter(UsageHistory.id == id).first()
    if not nic:
        raise HTTPException(status_code=404, detail="NIC 사용 이력 항목을 찾을 수 없습니다.")

    if request.requested_date:
        nic.requested_date = request.requested_date
    if request.expected_complete_date:
        nic.expected_complete_date = request.expected_complete_date

    db.commit()
    db.refresh(nic)
    return {"message": "일정 업데이트 성공", "id": nic.id}


@router.put("/update-group/{id}")
def update_group_id(id: int, request: UsageGroupUpdateRequest, db: Session = Depends(get_db)):
    nic = db.query(UsageHistory).filter(UsageHistory.id == id).first()
    if not nic:
        raise HTTPException(status_code=404, detail="NIC 사용 이력 항목을 찾을 수 없습니다.")

    nic.group_id = request.group_id
    db.commit()
    db.refresh(nic)
    return {"message": "group_id 업데이트 성공", "id": nic.id}

@router.post("/reset-group")
def reset_group(request: ResetGroupRequest, db: Session = Depends(get_db)):
    try:
        for id in request.ids:
            item = db.query(UsageHistory).filter(UsageHistory.id == id).first()
            if item:
                item.status = "사용 가능"
                item.requester = "미정"
                item.work_link = "미정"
                item.group_id = None
                item.group_memo = ""
                item.requested_date = None
                item.expected_complete_date = None

        db.commit()
        return {"message": "✅ 작업이 재고 상태로 초기화되었습니다."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
