import datetime
import logging
import uuid

import openai
import yaml
from fastapi import Depends, HTTPException, APIRouter
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.state import AppState, get_app_state

router = APIRouter()


@router.post("/ratings")
async def add_ratings(request: Request, app_state: AppState = Depends(get_app_state)):
    if app_state.agents_db is None or app_state.ratings_db is None:
        logging.error("Chroma DB not initialized")
        raise HTTPException(status_code=500, detail="Chroma DB not initialized")
    try:
        # Read the raw YAML content from the request body
        yaml_content_str = await request.body()
        if not yaml_content_str.strip():
            logging.error("Empty or whitespace-only YAML content received")
            raise HTTPException(status_code=400, detail="Empty or whitespace-only YAML content received")

        yaml_content_str = yaml_content_str.decode('utf-8').strip()
        logging.info("YAML content received")

        # Attempt to parse the YAML content to check for validity
        try:
            parsed_yaml = yaml.safe_load(yaml_content_str)
            if parsed_yaml is None:
                raise ValueError("YAML content is empty after parsing")
        except yaml.YAMLError as e:
            logging.error(f"Invalid YAML content: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid YAML content received")

    except HTTPException as http_exc:
        # Catch explicitly raised HTTPException and re-raise
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to read request body: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to read request body: {str(e)}")

    try:
        updated_ratings = parsed_yaml.get("ratings")
        ratings_id = updated_ratings.get("id")
    except KeyError as e:
        logging.error(f"Ratings ID not found in YAML content: {str(e)}")
        raise HTTPException(status_code=400, detail="Ratings ID not found in YAML content")

    # Get existing document from Chroma DB
    try:
        results = app_state.ratings_db.get(ratings_id)
        if len(results["documents"]) == 0:
            logging.error(f"Ratings ID not found in Chroma DB: {ratings_id}")
            raise HTTPException(status_code=404, detail="Ratings ID not found in Chroma DB")
        ratings_str = results["documents"][0]
        ratings_dict = yaml.safe_load(ratings_str)
        logging.info(f"Search query executed successfully for ratings ID: {ratings_id}")
    except HTTPException as http_exc:
        # Handle HTTPException separately
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to execute search query for ratings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute search query for ratings")

    # Update the ratings
    ratings_dict["data"]["samples"] = ratings_dict.get("data").get("samples") + 1
    ratings_dict["data"]["score"] = round(
        (ratings_dict.get("data").get("score") +
         updated_ratings.get("data").get("score")) / ratings_dict["data"]["samples"],
        2
    )
    # convert back to YAML
    ratings_yaml_content_str = yaml.dump(ratings_dict, sort_keys=False)
    # # Split the YAML content into documents but carry metadata from before
    # try:
    #     ratings_docs = app_state.text_splitter.create_documents([ratings_yaml_content_str],
    #                                                             metadatas=results["metadatas"])
    #     logging.info("YAML content split into documents")
    # except Exception as e:
    #     logging.error(f"Failed to split YAML content: {str(e)}")
    #     raise HTTPException(status_code=500, detail="Failed to split YAML content")

    try:
        # Update document
        ratings_docs = [ratings_yaml_content_str]
        app_state.ratings_db.update(ids=[ratings_id], documents=ratings_docs)
        logging.info("Update document in Chroma DBs")
    except openai.RateLimitError as e:
        logging.error(f"OpenAI rate limit error: {str(e)}")
        raise HTTPException(status_code=500, detail="OpenAI rate limit error")
    except Exception as e:
        logging.error(f"Failed to update documents in Chroma DB: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add documents to Chroma DB")

    return JSONResponse(content={"ratings": ratings_dict})


@router.get("/ratings")
async def get_ratings(ratings_id: str, app_state: AppState = Depends(get_app_state)):
    if app_state.agents_db is None or app_state.ratings_db is None:
        logging.error("Chroma DB not initialized")
        raise HTTPException(status_code=500, detail="Chroma DB not initialized")
    try:
        results = app_state.ratings_db.get(ratings_id)
        ratings_str = results["documents"][0]
        ratings_dict = yaml.safe_load(ratings_str)
        logging.info(f"Search query executed successfully for ratings ID: {ratings_id}")
    except HTTPException as http_exc:
        # Handle HTTPException separately
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to execute similarity search query for ratings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute similarity search query for ratings")

    return JSONResponse(content=ratings_dict)
