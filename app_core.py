# =====================
# 🔐 仮ログイン（復旧用）
# =====================
USERS = {
    "test": {
        "password": "1234",
        "nickname": "はは"
    }
}

def verify_login(login_id, password):
    user = USERS.get(login_id)
    if user and user["password"] == password:
        return {
            "user_id": login_id,
            "nickname": user["nickname"]
        }
    return None

def create_user(login_id, password, nickname, birth_date):
    USERS[login_id] = {
        "password": password,
        "nickname": nickname
    }
    return {"user_id": login_id, "nickname": nickname}

def reset_password(login_id, new_password):
    if login_id in USERS:
        USERS[login_id]["password"] = new_password
        return True
    return False
