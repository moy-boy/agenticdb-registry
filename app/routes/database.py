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
        ret = app_state.db_client.delete_collection(name="agents")
        app_state.agents_db = app_state.db_client.create_collection(name="agents", metadata={"hnsw:space": "cosine"})
        results['agents'] = 0
    except Exception as e:
        results['agents'] = f"Failed to delete agents collection: {str(e)}"

    # Attempt to delete the applications collection
    try:
        ret = app_state.db_client.delete_collection(name="applications")
        app_state.applications_db = app_state.db_client.create_collection(name="applications", metadata={"hnsw:space": "cosine"})
        results['applications'] = 0
    except Exception as e:
        results['applications'] = f"Failed to delete applications collection: {str(e)}"

    # Attempt to delete the ratings collection
    try:
        ret = app_state.db_client.delete_collection(name="ratings")
        app_state.ratings_db = app_state.db_client.create_collection(name="ratings", metadata={"hnsw:space": "cosine"})
        results['ratings'] = 0
    except Exception as e:
        results['ratings'] = f"Failed to delete ratings collection: {str(e)}"  

    # Return the result of each deletion attempt
    return JSONResponse(content=results)






