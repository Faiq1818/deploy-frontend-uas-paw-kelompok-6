from pyramid.response import Response
from pyramid.view import view_config
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
import bcrypt
from db import Session
from enum import Enum
import jwt
from models.user_model import User


class UserRole(str, Enum):
    agent = "agent"
    tourist = "tourist"


class FromRequest(BaseModel):
    email: str
    password: str
    role: UserRole


@view_config(route_name="login", request_method="POST", renderer="json")
def login(request):
    # request validation
    try:
        req_data = FromRequest(**request.json_body)
    except ValidationError as err:
        return Response(json_body={"error": str(err.errors())}, status=400)

    with Session() as session:
        stmt = select(User).where(User.email == req_data.email)
        try:
            result = session.execute(stmt).scalars().one()
        except:
            return Response(json_body={"error"}, status=409)

    # check the password with the hash in the db
    bytes = req_data.password.encode("utf-8")
    is_valid = bcrypt.checkpw(bytes, result.password_hash.encode("utf-8"))

    if is_valid == True:
        # making jwt token
        encoded = jwt.encode(
            {"name": result.name, "email": result.email, "role": result.role},
            "secret",
            algorithm="HS256",
        )
        return {
            "message": "User login",
            "user": {
                "id": str(result.id),
                "name": result.name,
                "email": result.email,
                "role": result.role,
            },
            "token": encoded,
        }

    return {"message": "Password salah"}
