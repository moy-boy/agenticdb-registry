import datetime
from http import HTTPStatus
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


@router.post("/agents")
async def add_agent(request: Request, app_state: AppState = Depends(get_app_state)):
    if app_state.agents_db is None or app_state.ratings_db is None:
        logging.error("Chroma DB not initialized")
        raise HTTPException(status_code=500, detail="Chroma DB not initialized")

    try:
        content_type = request.headers.get('Content-Type')
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
        elif content_type == "application/x-yaml" or content_type == "text/yaml":
            logging.info("YAML content received")
            try:
                parsed_content = list(yaml.safe_load_all(content_str))
                if not parsed_content:
                    raise ValueError("YAML content is empty after parsing")
            except yaml.YAMLError as e:
                logging.error(f"Invalid YAML content: {str(e)}")
                raise HTTPException(status_code=400, detail="Invalid YAML content received")
        else:
            logging.error("Unsupported Content-Type")
            raise HTTPException(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, detail="Unsupported Content-Type")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to read request body: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to read request body: {str(e)}")

    response = []

    for parsed_data in parsed_content:
        agent_id = str(uuid.uuid4())
        ratings_id = str(uuid.uuid4())

        try:
            parsed_data['metadata']['id'] = agent_id
            parsed_data['metadata']['ratings_id'] = ratings_id
        except KeyError as e:
            logging.error(f"metadata not found in content: {str(e)}")
            raise HTTPException(status_code=400, detail="Metadata not found in content")

        ratings_manifest = {
            "id": ratings_id,
            "agent_id": agent_id,
            "data": {
                "score": 0,
                "samples": 0
            }
        }

        if content_type == "application/json":
            agent_content_str = json.dumps(parsed_data)
            ratings_content_str = json.dumps(ratings_manifest)
        else:  # Assume YAML
            agent_content_str = yaml.dump(parsed_data, sort_keys=False)
            ratings_content_str = yaml.dump(ratings_manifest, sort_keys=False)

        try:
            current_utc_time = datetime.datetime.now(datetime.UTC).isoformat(timespec='milliseconds') + 'Z'
            agent_docs = [agent_content_str]
            ratings_docs = [ratings_content_str]
            app_state.agents_db.add(documents=agent_docs, metadatas=[{"id": agent_id, "version": 1, "timestamp": current_utc_time}], 
                                              ids=[f"{agent_id}"])
            app_state.ratings_db.add(documents=ratings_docs, metadatas=[{"id": ratings_id, "version": 1, "timestamp": current_utc_time}], 
                                               ids=[f"{ratings_id}"])
            logging.info("Documents added to Chroma DBs")
        except openai.RateLimitError as e:
            logging.error(f"OpenAI rate limit error: {str(e)}")
            raise HTTPException(status_code=500, detail="OpenAI rate limit error")
        except Exception as e:
            logging.error(f"Failed to add documents to Chroma DB: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to add documents to Chroma DB")

        response.append({
            "agent_manifest": parsed_data,
            "ratings_manifest": ratings_manifest
        })

    return response


@router.get("/agents")
async def get_agents(query: str, request: Request, app_state: AppState = Depends(get_app_state)):
    if app_state.agents_db is None or app_state.ratings_db is None:
        logging.error("Chroma DB not initialized")
        raise HTTPException(status_code=500, detail="Chroma DB not initialized")
    
    try:
        accept_header = request.headers.get('Accept')

        if accept_header == "application/json":
            accept_type = AcceptType.JSON
            logging.info("Request for JSON response received")
        elif accept_header == "application/x-yaml" or accept_header == "text/yaml":
            accept_type = AcceptType.YAML
            logging.info("Request for JSON response received")
        else:
            logging.error("Unsupported Content-Type")
            raise HTTPException(status_code=415, detail="Unsupported Content-Type")

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to get HTTP headers: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to get HTTP headers: {str(e)}")    

    try:
        results = app_state.agents_db.query(query_texts=[query], n_results=10)
        logging.info("Similarity search query executed successfully for agents")
    except HTTPException as http_exc:
        # Handle HTTPException separately
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to execute similarity search query for agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute similarity search query for agents")

    if accept_type == AcceptType.YAML:

        concatenated_yaml = "---\n"
        agents = results["documents"][0]
        for agent in agents:
            agent_data = yaml.safe_load(agent)
            ratings_id = agent_data['metadata'].get('ratings_id')

            try:
                ratings_results = app_state.ratings_db.get(ids=[f"{ratings_id}"])
                if len(ratings_results["documents"]) == 0:
                    logging.error(f"Ratings ID not found in Chroma DB: {ratings_id}")
                    raise HTTPException(status_code=404, detail="Ratings ID not found in Chroma DB")
                logging.info(f"Similarity search query executed successfully for ratings with ID: {ratings_id}")
            except HTTPException as http_exc:
                # Catch explicitly raised HTTPException and re-raise
                raise http_exc
            except Exception as e:
                logging.error(f"Failed to execute search query for ratings: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to execute search query for ratings")

            if ratings_results:
                ratings_str = ratings_results["documents"][0] 
                agent_data['ratings'] = yaml.safe_load(ratings_str)

            agent_yaml_content_str = yaml.dump(agent_data, sort_keys=False)
            concatenated_yaml += agent_yaml_content_str + "\n---\n"

        # Remove the last separator if it exists
        if concatenated_yaml.endswith("\n---\n"):
            concatenated_yaml = concatenated_yaml[:-5]

        return Response(content=concatenated_yaml.strip(), media_type="application/x-yaml")
        # return JSONResponse(content={"agents": concatenated_yaml.strip()})

    if accept_type == AcceptType.JSON:
        json_object = []
        agents = results["documents"][0]
        for agent in agents:
            agent_data = json.loads(agent)
            ratings_id = agent_data['metadata'].get('ratings_id')
            try:
                ratings_results = app_state.ratings_db.get(ids=[f"{ratings_id}"])
                if len(ratings_results["documents"]) == 0:
                    logging.error(f"Ratings ID not found in Chroma DB: {ratings_id}")
                    raise HTTPException(status_code=404, detail="Ratings ID not found in Chroma DB")
                logging.info(f"Similarity search query executed successfully for ratings with ID: {ratings_id}")
            except HTTPException as http_exc:
                # Catch explicitly raised HTTPException and re-raise
                raise http_exc
            except Exception as e:
                logging.error(f"Failed to execute search query for ratings: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to execute search query for ratings")

            if ratings_results:
                ratings_str = ratings_results["documents"][0]
                agent_data['ratings'] = json.loads(ratings_str)

            json_object.append(agent_data)

        return JSONResponse(content=json_object)

