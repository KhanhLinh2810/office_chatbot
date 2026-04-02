from pydantic import BaseModel
from typing import Optional

class UserUpdateForUserRoleRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserUpdateForAdminRoleRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    status: Optional[int] = None
    role: Optional[int] = None
    manager_id: Optional[int] = None

class UserUpdateForSystem(BaseModel):
    google_refresh_token: Optional[str] = None
    google_access_token: Optional[str] = None

class UserUpdate(UserUpdateForUserRoleRequest, UserUpdateForAdminRoleRequest, UserUpdateForSystem):
    pass
    

