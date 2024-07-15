import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict

import openai
import yaml
from dotenv import load_dotenv, find_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langserve import add_routes


def load_env_file():
    # Try to find and load the default .env file first
    env_path = find_dotenv()
    if env_path != "":
        load_dotenv(dotenv_path=env_path, override=True)
        logging.info(f"Loaded environment variables from {env_path}")
    else:
        # If the default .env file is not found, try to find and load .env.azure
        env_azure_path = find_dotenv(".env.azure")
        if env_azure_path:
            load_dotenv(dotenv_path=env_azure_path, override=True)
            logging.info(f"Loaded environment variables from {env_azure_path}")
        else:
            logging.error("Neither .env nor .env.azure files were found")
            raise FileNotFoundError("Neither .env nor .env.azure files were found")


def get_text_splitter():
    return RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
        separators=[
            "\n\n",
            "\n",
        ],
    )


def get_embedding_function():
    return OpenAIEmbeddings(model="text-embedding-3-large")


class AppState:
    def __init__(self):
        self.chroma_db = None
        self.text_splitter = None
        self.embedding_function = None


class YAMLContent(BaseModel):
    original_content: str
    parsed_content: Dict[str, Any]

    @field_validator('parsed_content', mode='before')
    def parse_yaml(cls, v, values):
        try:
            return yaml.safe_load(values['original_content'])
        except yaml.YAMLError as e:
            logging.error(f"Failed to parse YAML content: {str(e)}")
            raise ValueError(f"Invalid YAML content: {str(e)}")


def get_app_state(fast_app: FastAPI) -> AppState:
    return fast_app.state.app_state


def add_agent_routes(fast_app: FastAPI):
    chat_model = ChatOpenAI(model=os.getenv("OPENAI_MODEL_NAME")),
    chat_prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
    add_routes(
        app=fast_app,
        runnable=chat_prompt | chat_model[0],
        path="/joke",
    )


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    try:
        load_env_file()
        add_agent_routes(fast_app)
        fast_app.state.app_state = AppState()
        fast_app.state.app_state.text_splitter = get_text_splitter()
        fast_app.state.app_state.embedding_function = get_embedding_function()
        fast_app.state.app_state.chroma_db = Chroma(embedding_function=fast_app.state.app_state.embedding_function)
        logging.info("App state initialized successfully")
        yield
    except Exception as e:
        logging.error(f"Error during app initialization: {str(e)}")
        raise
    finally:
        # Perform any necessary cleanup here
        logging.info("App shutdown")


app = FastAPI(lifespan=lifespan, title="Agentic DB API", description="API for managing Agentic DB",
              version="0.1.0")

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@app.get("/")
async def root():
    logging.info("Root endpoint called")
    return {"message": "Hello World"}


@app.post("/agent")
async def parse_yaml(request: Request, app_state: AppState = Depends(lambda: get_app_state(app))):
    if app_state.chroma_db is None:
        logging.error("Chroma DB not initialized")
        raise HTTPException(status_code=500, detail="Chroma DB not initialized")

    # Read the raw YAML content from the request body
    try:
        yaml_content_str = await request.body()
        yaml_content_str = yaml_content_str.decode('utf-8')
        logging.info("YAML content received")
    except Exception as e:
        logging.error(f"Failed to read request body: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to read request body")

    try:
        parsed_content = yaml.safe_load(yaml_content_str)
        logging.info("YAML content parsed successfully")
    except yaml.YAMLError as e:
        logging.error(f"Invalid YAML content: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid YAML content: {str(e)}")

    # Generate a UUID and add it to the parsed content
    agent_id = str(uuid.uuid4())
    parsed_content['metadata']['id'] = agent_id

    # Convert the updated parsed content back to a YAML string
    yaml_content_str = yaml.dump(parsed_content)

    # Split the YAML content into documents
    try:
        docs = app_state.text_splitter.create_documents([yaml_content_str])
        logging.info("YAML content split into documents")
    except Exception as e:
        logging.error(f"Failed to split YAML content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to split YAML content")

    try:
        # Insert documents into the Chroma database
        app_state.chroma_db.add_documents(docs)
        logging.info("Documents added to Chroma DB")
    except openai.RateLimitError as e:
        logging.error(f"OpenAI rate limit error: {str(e)}")
        raise HTTPException(status_code=500, detail="OpenAI rate limit error")
    except Exception as e:
        logging.error(f"Failed to add documents to Chroma DB: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add documents to Chroma DB")

    # Query example (replace with actual queries as needed)
    query = "Which agents have a category of Natural Language?"
    try:
        results = app_state.chroma_db.similarity_search(query)
        logging.info("Similarity search query executed successfully")
    except Exception as e:
        logging.error(f"Failed to execute similarity search query: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute similarity search query")

    return {
        "original_content": yaml_content_str,
        "parsed_content": parsed_content,
        "query_results": results,
        "agent_id": agent_id
    }


if __name__ == "__main__":
    import uvicorn

    logging.info("Starting Agentic DB API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    logging.info("Application shutdown")
