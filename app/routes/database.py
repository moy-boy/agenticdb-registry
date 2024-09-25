from http import HTTPStatus
import json
import logging

from fastapi import Depends, HTTPException, APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.state import AppState, get_app_state
from app.routes.accept_type import AcceptType
from fastapi.responses import Response


from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request

database = APIRouter()

@database.delete("/collections")
async def delete_all_collections(app_state: AppState = Depends(get_app_state)):
    results = {}
    
    # Attempt to delete the agents collection
    try:
        app_state.agents_db.delete()
        results['agents'] = "Successfully deleted agents collection"
    except Exception as e:
        results['agents'] = f"Failed to delete agents collection: {str(e)}"

    # Attempt to delete the applications collection
    try:
        app_state.applications_db.delete()
        results['applications'] = "Successfully deleted applications collection"
    except Exception as e:
        results['applications'] = f"Failed to delete applications collection: {str(e)}"

    # Attempt to delete the ratings collection
    try:
        app_state.ratings_db.delete()
        results['ratings'] = "Successfully deleted ratings collection"
    except Exception as e:
        results['ratings'] = f"Failed to delete ratings collection: {str(e)}"

    # Return the result of each deletion attempt
    return JSONResponse(content=results)






