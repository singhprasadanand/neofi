def get_user_role(user_id: int, event) -> str:
    for perm in event.permissions:
        if perm.user_id == user_id:
            return perm.role
    return ""

def can_view(role: str) -> bool:
    return role in ["owner", "editor", "viewer"]

def can_edit(role: str) -> bool:
    return role in ["owner", "editor"]

def can_delete(role: str) -> bool:
    return role == "owner"

def can_share(role: str) -> bool:
    return role == "owner"