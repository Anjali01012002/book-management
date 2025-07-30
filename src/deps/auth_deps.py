from fastapi import Depends, HTTPException, status
from src.api.users import get_current_user
from src.models.user import User

def check_role(required_role: str):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in ['admin', required_role]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires role '{required_role}' or 'admin'"
            )
        return user
    return role_checker
