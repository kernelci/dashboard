from typing import Optional

from pydantic import BaseModel


class HardwareRegistryNamedLink(BaseModel):
    id: str
    url: Optional[str] = None
    form_factor: Optional[str] = None


class HardwareRegistryProcessorInfo(BaseModel):
    id: str
    architecture: Optional[str] = None
    cores: Optional[int] = None
    max_clock_speed_mhz: Optional[int] = None
    url: Optional[str] = None
    description: Optional[str] = None


class HardwareRegistryInfo(BaseModel):
    platform_id: str
    board_type: Optional[str] = None
    form_factor: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    vendor: Optional[HardwareRegistryNamedLink] = None
    silicon_vendor: Optional[HardwareRegistryNamedLink] = None
    system_module: Optional[HardwareRegistryNamedLink] = None
    processor: Optional[HardwareRegistryProcessorInfo] = None
