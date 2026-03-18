from fastapi import Request, HTTPException, Depends

from app.api.depend import SessionDep
from app.services import user_service
from app.utils.jwt import JWTUtils


async def authenticate(request: Request, session: SessionDep):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="token_invalid")

    token = auth_header.split("Bearer")[1].strip()
    try:
        payload = JWTUtils.verify_token(token)
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="token_invalid")    
        user = await user_service.find_or_fail_by_id(session, user_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    

