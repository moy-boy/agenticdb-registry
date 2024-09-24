import datetime
from http import HTTPStatus
from http.client import BAD_REQUEST
import json
import logging
import uuid

import openai
import yaml
from fastapi import Depends, HTTPException, APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.state import AppState, get_app_state
from app.routes.accept_type import AcceptType
from fastapi.responses import Response


router = APIRouter()


@router.post("/applications")
async def add_application(request: Request, app_state: AppState = Depends(get_app_state)):
    if app_state.applications_db is None or app_state.ratings_db is None:
        logging.error("Appications DB not initialized")
        raise HTTPException(status_code=500, detail="Appications DB not initialized")

    try:
        content_type = request.headers.get('Content-Type')
        accept_header = request.headers.get('Accept')
        raw_body = await request.body()

        if not raw_body.strip():
            logging.error("Empty or whitespace-only content received")
            raise HTTPException(status_code=400, detail="Empty or whitespace-only content received")

        content_str = raw_body.decode('utf-8').strip()

        if content_type == "application/json":
            logging.info("JSON content received")
            try:
                parsed_content = json.loads(content_str)
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON content: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid JSON content received")
        else:
            logging.error("Unsupported Content-Type")
            raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail="Unsupported Content-Type")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to read request body: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to read request body: {str(e)}")

    applications_json_object = []
    ratings_json_object = []

    for parsed_data in parsed_content:
        application_id = str(uuid.uuid4())
        ratings_id = str(uuid.uuid4())

        try:
            parsed_data['metadata']['id'] = application_id
            parsed_data['metadata']['ratings_id'] = ratings_id
        except KeyError as e:
            logging.error(f"metadata not found in content: {str(e)}")
            raise HTTPException(status_code=400, detail="Metadata not found in content")

        ratings_manifest = {
            "id": ratings_id,
            "applications_id": application_id,
            "data": {
                "score": 0,
                "samples": 0
            }
        }

        if accept_header == "application/json":
            applications_json_object.append(parsed_data)
            ratings_json_object.append(ratings_manifest)
            agent_content_str = json.dumps(parsed_data)
            ratings_content_str = json.dumps(ratings_manifest)
        else:
            raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail="Unsupported Content-Type")

        try:
            current_utc_time = datetime.datetime.now(datetime.UTC).isoformat(timespec='milliseconds') + 'Z'
            agent_docs = [agent_content_str]
            ratings_docs = [ratings_content_str]
            app_state.applications_db.add(documents=agent_docs, metadatas=[{"id": application_id, "version": 1, "timestamp": current_utc_time}], 
                                              ids=[f"{application_id}"])
            app_state.ratings_db.add(documents=ratings_docs, metadatas=[{"id": ratings_id, "version": 1, "timestamp": current_utc_time}], 
                                               ids=[f"{ratings_id}"])
            logging.info("Applications added to DBs")
        except openai.RateLimitError as e:
            logging.error(f"OpenAI rate limit error: {str(e)}")
            raise HTTPException(status_code=500, detail="OpenAI rate limit error")
        except Exception as e:
            logging.error(f"Failed to add applications to DB: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to add applications to DB")

    if accept_header == "application/json":
        return JSONResponse(content=applications_json_object)
    else:
         raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail="Unsupported Content-Type")


@router.get("/applications")
async def get_applications(query: str, request: Request, app_state: AppState = Depends(get_app_state)):
    if app_state.applications_db is None or app_state.ratings_db is None:
        logging.error("Appications DB not initialized")
        raise HTTPException(status_code=500, detail="Appications DB not initialized")
    
    try:
        accept_header = request.headers.get('Accept')

        if accept_header == "application/json":
            accept_type = AcceptType.JSON
            logging.info("Request for JSON response received")
        else:
            logging.error("Unsupported Content-Type")
            raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail="Unsupported Content-Type")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to get HTTP headers: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Failed to get HTTP headers: {str(e)}")    

    try:
        results = app_state.applications_db.query(query_texts=[query], n_results=10)
        logging.info("Similarity search query executed successfully for agents")
    except HTTPException as http_exc:
        # Handle HTTPException separately
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to execute similarity search query for agents: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to execute similarity search query for agents")


    if accept_type == AcceptType.JSON:
        json_object = []
        applications = results["documents"][0]
        for application in applications:
            app_data = json.loads(application)
            ratings_id = app_data['metadata'].get('ratings_id')
            try:
                ratings_results = app_state.ratings_db.get(ids=[f"{ratings_id}"])
                if len(ratings_results["documents"]) == 0:
                    logging.error(f"Ratings ID not found in DB: {ratings_id}")
                    raise HTTPException(status_code=404, detail="Ratings ID not found in DB")
                logging.info(f"Similarity search query executed successfully for ratings with ID: {ratings_id}")
            except HTTPException as http_exc:
                # Catch explicitly raised HTTPException and re-raise
                raise http_exc
            except Exception as e:
                logging.error(f"Failed to execute search query for ratings: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to execute search query for ratings")

            if ratings_results:
                ratings_str = ratings_results["documents"][0]
                app_data['ratings'] = json.loads(ratings_str)

            json_object.append(app_data)

        return JSONResponse(content=json_object)

