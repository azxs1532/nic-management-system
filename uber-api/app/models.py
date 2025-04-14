from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Date, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ✅ NIC 신규 입고 테이블
class NICIncoming(Base):
    __tablename__ = "incoming_nics"

    id = Column(Integer, primary_key=True, index=True)
    mac_address = Column(String, nullable=False)  # MAC 주소
    nic_part_number = Column(String, nullable=True)  # 닉파트넘버
    finid = Column(String, nullable=True)  # FINID
    vendor = Column(String, nullable=False)  # 벤더사
    part = Column(String, nullable=False)  # 파트
    center = Column(String, nullable=False)  # 센터
    requester = Column(String, nullable=True, default="미정")  
    work_link = Column(String, nullable=True, default="미정")
    status = Column(String, default="사용 가능")

# ✅ NIC 재고 테이블
class NICInventory(Base):
    __tablename__ = "nic_inventory"

    id = Column(Integer, primary_key=True, index=True)
    center = Column(String, nullable=False)
    vendor = Column(String, nullable=False)
    nic_type = Column(String, nullable=False)
    available = Column(Integer, default=0)
    fault = Column(Integer, default=0)
    standby = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())  
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  

# ✅ NIC 사용 이력 테이블
class UsageHistory(Base):
    __tablename__ = "usage_history"

    id = Column(Integer, primary_key=True, index=True)
    vendor = Column(String, nullable=False)
    part = Column(String, nullable=False)
    finid = Column(String, nullable=False)
    mac_address = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    center = Column(String, nullable=False)
    status = Column(String, default="사용 가능")
    date = Column(Date, server_default=func.current_date())
    model = Column(String, nullable=False)
    requester = Column(String, nullable=True, default="미정")  
    work_link = Column(String, nullable=True, default="미정")
    nic_part_number = Column(String, nullable=True)
    group_memo = Column(Text, nullable=True)
    group_id = Column(String, nullable=True)
    requested_date = Column(Date, nullable=True)
    expected_complete_date = Column(String, default="미정")

    
class RiserManagement(Base):
    __tablename__ = "riser_management"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    center = Column(String, nullable=False)  # 센터 정보
    riser_type = Column(String, nullable=False)  # Riser 종류 (예: c-riser, s2s3-riser)
    finid = Column(String, nullable=False)  # FINID
    vendor = Column(String, nullable=False)  # 벤더 정보
    total_quantity = Column(Integer, nullable=False, default=0)  # 전체 입고 수량
    available_quantity = Column(Integer, nullable=False, default=0)  # 사용 가능 수량
    reserved_quantity = Column(Integer, nullable=False, default=0)  # 예약된 수량
    used_quantity = Column(Integer, nullable=False, default=0)  # 사용된 수량
    remarks = Column(Text, nullable=True)  # ✅ 비고 (optional)
    created_at = Column(DateTime, server_default=func.now())  # 입고 날짜 및 # 업데이트 날짜
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # ✅ 수정 날짜 자동 업데이트

# ✅ Riser 사용 이력 테이블
class RiserUsage(Base):
    __tablename__ = "riser_usage"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    center = Column(String, nullable=False)  # 센터 정보
    riser_type = Column(String, nullable=False)  # Riser 종류 (예: c-riser, s2s3-riser)
    finid = Column(String, nullable=False)  # FINID
    quantity = Column(Integer, nullable=False)  # ✅ 기존 quantity → quantity_used로 통일
    vendor = Column(String, nullable=True, default="xfusion")  # ✅ Vendor 필드 추가
    requester = Column(String, nullable=True, default="미정")  # 요청자
    work_link = Column(String, nullable=True, default="미정")  # 작업 링크
    status = Column(String, default="사용 예약")  # 상태 (사용 가능, 사용 예약, 사용 완료)
    remarks = Column(Text, nullable=True, default="없음")  # ✅ 비고 컬럼 추가
    created_at = Column(DateTime, server_default=func.now())  # 생성 날짜
    updated_at = Column(DateTime, server_default=func.now(), server_onupdate=func.now())  # ✅ 업데이트 날짜 추가
