from rest_framework_jwt.utils import jwt_payload_handler

def jwt_response_payload_handler(token, user=None, request=None):

    return  {
        "username":user.username,
        "user_id": user.id,
        "token": token
        }


def jwt_my_handler(user):

    payload = jwt_payload_handler(user)

    # 接收到的payload是一个字典
    # 删除email属性
    del payload["email"]
    # 增加mobile属性
    payload["mobile"]=user.mobile

    return payload
