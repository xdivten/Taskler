from ..models import User


def get_user_dict(user: User):
    if user.is_authenticated:
        return {"USER_ID": user.id, "USER_NAME": user.username, "USER_EMAIL": user.email}
    return {"USER_IS_AUTHENTICATED": "false"}
