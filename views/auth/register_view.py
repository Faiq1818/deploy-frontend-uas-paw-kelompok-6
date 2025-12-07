from pyramid.response import Response
from pyramid.view import view_config
from pydantic import BaseModel
import bcrypt
import json
from db import Session

from models.user_model import User


class FromRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str


@view_config(route_name="register", request_method="POST", renderer="json")
def register(request):
    # request validation
    try:
        req_data = FromRequest(**request.json_body)
    except:
        return Response("Body harus berupa JSON valid", status=400)

    # hash the password
    bytes = req_data.password.encode("utf-8")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)

    with Session() as session:
        new_user = User(
            name=req_data.name,
            email=req_data.email,
            password_hash=hash,
            role=req_data.role,
        )

        session.add(new_user)
        session.commit()

    return {
        "message": "User registered",
        "user": {
            "name": req_data.name,
            "email": req_data.email,
            "role": req_data.role,
            "token": str(hash)
        },
        "success": True,
    }
