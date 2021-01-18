from pydantic import BaseModel
from typing import Dict, Optional, List


class SystemInfo(BaseModel):
    model: str


class CpuFreqInfo(BaseModel):
    current: float
    min: float
    max: float


class CpuInfo(BaseModel):
    freq: List[CpuFreqInfo]
    perc: List[int]
    temp: float


class BaseMemoryInfo(BaseModel):
    total: float
    used: float
    free: float
    percent: float


class VirtualMemoryInfo(BaseMemoryInfo):
    available: float
    active: float
    inactive: float
    buffers: float
    cached: float
    shared: float
    slab: float


class SwapMemoryInfo(BaseMemoryInfo):
    sin: float
    sout: float


class MemoryInfo(BaseModel):
    virtual: VirtualMemoryInfo
    swap: SwapMemoryInfo


class DiskInfo(BaseModel):
    total: float
    used: float
    free: float
    percent: float


class StatsInfo(BaseModel):
    system: SystemInfo
    cpu: CpuInfo
    memory: MemoryInfo
    disk: Optional[Dict[str, DiskInfo]]


class SysResponse(BaseModel):
    stats: StatsInfo
