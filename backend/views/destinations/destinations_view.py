from db import Session
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, IntegrityError
from typing import Optional
from pyramid.view import view_config
from pydantic import BaseModel, ValidationError, Field
from pyramid.response import Response
from models.destination_model import Destination

class FromRequest(BaseModel):
    country: Optional[str] = None
    search: Optional[str] = None

@view_config(route_name="destinations", request_method="GET", renderer="json")
def destinations(request):
    # request validation
    try:
        req_data = FromRequest(**request.params.mixed())
    except ValidationError as err:
        return Response(json_body={"error": str(err.errors())}, status=400)

    # get destination from db
    with Session() as session:

        if req_data.country == None and req_data.search == None:
            stmt = select(Destination)
        elif req_data.search != None and req_data.search == None:
            stmt = select(Destination).where(Destination.name == req_data.search)
        elif req_data.search == None and req_data.search != None:
            stmt = select(Destination).where(Destination.country == req_data.country)
        else:
            stmt = select(Destination).where(Destination.country == req_data.country and Destination.name == req_data.search)

        try:
            result = session.execute(stmt).scalars().one()
            if not result:
                return Response(json_body={"message": "User tidak ditemukan"}, status=401)
        except NoResultFound:
            return Response(json_body={"message": "User tidak ditemukan"}, status=401)
        except Exception as e:
            print(e)
            return Response(json_body={"error": "Internal Server Error"}, status=500)

    return {"data": str(result.country)}
