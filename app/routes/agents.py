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


@router.post("/agents")
async def add_agent(request: Request, app_state: AppState = Depends(get_app_state)):
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
            parsed_yamls = list(yaml.safe_load_all(yaml_content_str))
            if not parsed_yamls:
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

    response = []

    for parsed_yaml in parsed_yamls:
        # Generate UUIDs for the agent and its ratings
        agent_id = str(uuid.uuid4())
        ratings_id = str(uuid.uuid4())

        try:
            parsed_yaml['metadata']['id'] = agent_id
            parsed_yaml['metadata']['ratings_id'] = ratings_id
        except KeyError as e:
            logging.error(f"metadata not found in YAML content: {str(e)}")
            raise HTTPException(status_code=400, detail="Metadata not found in YAML content")

        # Create the ratings manifest
        ratings_manifest = {
            "id": ratings_id,
            "agent_id": agent_id,
            "data": {
                "score": 0,
                "samples": 0
            }
        }

        # Convert the updated parsed content and ratings manifest back to YAML strings
        agent_yaml_content_str = yaml.dump(parsed_yaml, sort_keys=False)
        ratings_yaml_content_str = yaml.dump(ratings_manifest, sort_keys=False)

        # Split the YAML content into documents
        try:
            # Generate the current UTC time down to milliseconds
            current_utc_time = datetime.datetime.now(datetime.UTC).isoformat(timespec='milliseconds') + 'Z'
            agent_docs = app_state.text_splitter.create_documents(texts=[agent_yaml_content_str],
                                                                  metadatas=[{"id": agent_id, "version": 1,
                                                                              "timestamp": current_utc_time}])
            ratings_docs = app_state.text_splitter.create_documents(texts=[ratings_yaml_content_str],
                                                                    metadatas=[{"id": ratings_id, "version": 1,
                                                                                "timestamp": current_utc_time}])
            logging.info("YAML content split into documents")
        except Exception as e:
            logging.error(f"Failed to split YAML content: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to split YAML content")

        try:
            # Insert documents into the respective Chroma databases
            app_state.agents_db.add_documents(agent_docs, ids=[agent_id])
            app_state.ratings_db.add_documents(ratings_docs, ids=[ratings_id])
            logging.info("Documents added to Chroma DBs")
        except openai.RateLimitError as e:
            logging.error(f"OpenAI rate limit error: {str(e)}")
            raise HTTPException(status_code=500, detail="OpenAI rate limit error")
        except Exception as e:
            logging.error(f"Failed to add documents to Chroma DB: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to add documents to Chroma DB")

        response.append({
            "agent_manifest": parsed_yaml,
            "ratings_manifest": ratings_manifest
        })

    return response


@router.get("/agents")
async def get_agents(query: str, app_state: AppState = Depends(get_app_state)):
    if app_state.agents_db is None or app_state.ratings_db is None:
        logging.error("Chroma DB not initialized")
        raise HTTPException(status_code=500, detail="Chroma DB not initialized")

    try:
        results = app_state.agents_db.similarity_search(query)
        logging.info("Similarity search query executed successfully for agents")
    except HTTPException as http_exc:
        # Handle HTTPException separately
        raise http_exc
    except Exception as e:
        logging.error(f"Failed to execute similarity search query for agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute similarity search query for agents")

    concatenated_yaml = "---\n"
    for result in results:
        agent_content = result.page_content.strip()
        agent_data = yaml.safe_load(agent_content)
        ratings_id = agent_data['metadata'].get('ratings')

        try:
            ratings_results = app_state.ratings_db.get(ratings_id)
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
            ratings_dict = yaml.safe_load(ratings_str)
            agent_data['ratings'] = ratings_dict

        agent_yaml_content_str = yaml.dump(agent_data, sort_keys=False)
        concatenated_yaml += agent_yaml_content_str + "\n---\n"

    # Remove the last separator if it exists
    if concatenated_yaml.endswith("\n---\n"):
        concatenated_yaml = concatenated_yaml[:-5]

    return JSONResponse(content={"agents": concatenated_yaml.strip()})
