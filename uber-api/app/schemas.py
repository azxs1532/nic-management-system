from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

# ✅ NIC 신규 입고 스키마
class NICIncomingCreate(BaseModel):
    mac_address: str
    nic_part_number: str
    finid: str
    vendor: str
    part: str
    center: str
    requester: Optional[str] = "미정"  # ✅ 요청자가 없을 경우 "미정" 기본값
    work_link: Optional[str] = "미정"  # ✅ 아지트 링크 없을 경우 "미정"
    status: Optional[str] = "사용 가능"  # ✅ 기본 상태 설정

# ✅ 여러 개의 NIC 입고 요청을 처리할 수 있도록 리스트 형태로 감싸줌
class NICRequest(BaseModel):
    records: List[NICIncomingCreate]

# ✅ NIC 입고 목록을 응답할 때 사용할 스키마
class NICIncomingResponse(BaseModel):
    mac_address: str
    nic_part_number: str
    finid: str
    vendor: str
    part: str
    center: str

    class Config:
        orm_mode = True  # ✅ SQLAlchemy 모델과 Pydantic 변환 가능하도록 설정


# ✅ 사용 이력 공통 속성
class UsageHistoryBase(BaseModel):
    vendor: str
    part: str
    finid: str
    mac_address: str
    quantity: int
    requester: str
    work_link: str
    status: str
    date: datetime
    center: str
    model: str  
    nic_part_number: str
    group_id: Optional[str] = None
    requested_date: Optional[date] = None
    expected_complete_date: Optional[str] = "미정"

class GroupMemoUpdateRequest(BaseModel):
    group_memo: Optional[str] = None
    requested_date: Optional[str] = None
    expected_complete_date: Optional[str] = None

class ResetGroupRequest(BaseModel):
    ids: List[int]


# ✅ 사용 이력 상태 업데이트 스키마 (부분 수정 가능)
class UsageHistoryUpdate(BaseModel):  
    status: Optional[str] = None  

# ✅ 사용 이력 생성 요청 스키마
class UsageHistoryCreate(UsageHistoryBase):
    pass

# ✅ 사용 이력 응답 스키마
class UsageHistoryResponse(UsageHistoryBase):
    id: int
    vendor: str
    nic_part_number: Optional[str] = "미정" 
    center: str
    requester: Optional[str] = "미정"
    work_link: Optional[str] = "미정"
    status: str
    finid: Optional[str] = "미정"
    mac_address: Optional[str] = "미정"
    quantity: int
    model: str
    part: Optional[str] = "미정"  
    date: datetime
    group_memo: Optional[str] = None
    group_id: Optional[str] = None
    requested_date: Optional[date] = None
    expected_complete_date: Optional[str] = "미정"

    class Config:
        from_attributes = True  # ✅ SQLAlchemy 모델과 변환 가능하도록 설정

# ✅ NIC 재고 조회용 응답 스키마
class AvailableNICResponse(BaseModel):
    finid: str
    vendor: str
    nic_part_number: str

# ✅ 닉 개별 속성 업데이트 요청 스키마
class RequesterUpdateRequest(BaseModel):
    requester: str  # 🔥 요청자 업데이트 스키마 추가

class WorkLinkUpdateRequest(BaseModel):
    work_link: str  # 🔥 아지트 링크 업데이트 스키마 추가

class StatusUpdateRequest(BaseModel):
    status: str  # 🔥 상태 변경 스키마 추가

class MacAddressUpdateRequest(BaseModel):
    mac_address: str  # 🔥 MAC 주소 업데이트 스키마 추가

class CenterUpdateRequest(BaseModel):
    center: str  # 🔥 센터 정보 업데이트 스키마 추가
    work_link: str = "미정"
    requester: str = "미정"
class DateUpdateRequest(BaseModel):
    date: date  # ✅ 입고 날짜 업데이트 요청 스키마

class NewUsageEntryItem(BaseModel):
    vendor: str
    part: str
    center: str
    requester: str
    work_link: str
    quantity: int
    group_id: Optional[str] = None
    requested_date: Optional[date] = None
    expected_complete_date: Optional[str] = None

class NewUsageEntryListRequest(BaseModel):
    entries: List[NewUsageEntryItem]

# ✅ 요청 스키마
class NICUpdateRequest(BaseModel):
    id: int  # ✅ PK 기반 업데이트
    finid: str
    mac_address: str
    nic_part_number: str

class UpdateFinidPayload(BaseModel):
    id: int
    finid: str

class UpdateFinidRequest(BaseModel):
    items: List[UpdateFinidPayload]

class VendorUpdateItem(BaseModel):
    id: int
    vendor: str

class VendorUpdateRequest(BaseModel):
    items: List[VendorUpdateItem]

class UsageScheduleUpdateRequest(BaseModel):
    requested_date: Optional[str] = None
    expected_complete_date: Optional[str] = "미정"

class UsageGroupUpdateRequest(BaseModel):
    group_id: str

class GroupResetRequest(BaseModel):
    ids: list[int] 




# Riser 관리 (입고 및 재고 통합)
class RiserManagementBase(BaseModel):
    center: str
    riser_type: str
    finid: str
    vendor: str
    total_quantity: int
    available_quantity: int
    reserved_quantity: int
    used_quantity: int
    remarks: Optional[str] = None 

class RiserManagementCreate(RiserManagementBase):
    pass

class RiserManagementResponse(RiserManagementBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  

# ✅ Riser 사용 이력 스키마
class RiserUsageBase(BaseModel):
    center: str
    riser_type: str
    finid: str
    quantity: int  
    vendor: Optional[str] = "xfusion"
    total_quantity: int = 0
    available_quantity: int = 0
    reserved_quantity: int = 0
    used_quantity: int = 0
    requester: Optional[str] = "미정"
    work_link: str = "미정"
    status: Optional[str] = "사용 가능" 
    remarks: Optional[str] = "없음"

class RiserUsageCreate(BaseModel):
    center: str
    riser_type: str
    finid: str
    quantity: int  
    vendor: Optional[str] = "xfusion"
    requester: Optional[str] = "미정"
    work_link: Optional[str] = "미정"
    remarks: Optional[str] = "없음"
    status: Optional[str] = "사용 예약" 

class RiserUsageResponse(RiserUsageBase):
    id: int
    updated_at: datetime  

    class Config:
        from_attributes = True

# ✅ 라이저 개별 속성 업데이트 요청 스키마 (선택적 업데이트)
class RiserRequesterUpdateRequest(BaseModel):
    requester: Optional[str] = None

class RiserWorkLinkUpdateRequest(BaseModel):
    work_link: Optional[str] = None

class RiserStatusUpdateRequest(BaseModel):
    status: Optional[str] = None

class RiserRemarksUpdateRequest(BaseModel):
    remarks: Optional[str] = None
    
# ✅ 수량 변경 요청 (파트 추가 / 파트 회수)
class RiserUpdateRequest(BaseModel):
    quantity: int  # 변경할 수량
    status: str  # "파트 추가" 또는 "파트 회수"
    remarks: Optional[str] = None  # 변경 사유

# ✅ 타센터 이동 요청
class RiserTransferRequest(BaseModel):
    finid: str  # 이동할 Riser의 FINID
    source_center: str  # 출발 센터
    target_center: str  # 도착 센터
    quantity: int  # 이동할 수량

#----------------------------------------------------------------
# ✅ NIC 재고 추가 요청 스키마
class NICInventoryCreate(BaseModel):
    center: str
    vendor: str
    nic_type: str
    available: Optional[int] = 0
    fault: Optional[int] = 0
    standby: Optional[int] = 0
    created_at: Optional[datetime] = None  # ✅ 자동 설정을 위해 Optional 처리
    updated_at: Optional[datetime] = None  # ✅ 자동 설정을 위해 Optional 처리
    
# ✅ NIC 재고 조회 응답 스키마
class NICInventoryResponse(NICInventoryCreate):
    id: int  # ✅ 조회 시에만 ID 포함
    class Config:
        from_attributes = True  # ✅ SQLAlchemy ORM과 호환