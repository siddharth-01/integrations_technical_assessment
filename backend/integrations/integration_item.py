from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class IntegrationItem(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    directory: bool = False
    parent_path_or_name: Optional[str] = None
    parent_id: Optional[str] = None
    name: Optional[str] = None
    creation_time: Optional[datetime] = None
    last_modified_time: Optional[datetime] = None
    url: Optional[str] = None
    children: Optional[List[str]] = None
    mime_type: Optional[str] = None
    delta: Optional[str] = None
    drive_id: Optional[str] = None
    visibility: Optional[bool] = True

    # New Fields for Contact Information from HubSpot
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None

    class Config:
        orm_mode = True

    class Config:
        orm_mode = True
