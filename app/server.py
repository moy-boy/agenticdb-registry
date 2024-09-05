import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

import yaml
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langserve import add_routes

from app.routes.agents import router as agents_router
from app.routes.ratings import router as ratings_router
from app.state import AppState


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
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
        separators=[
            "\n\n",
            "\n",
        ],
    )


def get_embedding_function():
    return OpenAIEmbeddingFunction(api_key=os.environ.get('OPENAI_API_KEY'), model_name="text-embedding-3-small")
    # return OpenAIEmbeddings(model="text-embedding-3-small")


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


def add_joke_agent_route(fast_app: FastAPI):
    chat_model = ChatOpenAI(model=os.getenv("OPENAI_MODEL_NAME")),
    chat_prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
    add_routes(
        app=fast_app,
        runnable=chat_prompt | chat_model[0],
        path="/joke",
    )


def cascade_invoke(input_data: Any = "what is 3 + 4?") -> Any:
    import requests
    # inspect the sample inference data and update with your own fields
    sample = dict()
    sample["input"] = input_data
    headers = {"Authorization": "Bearer " + os.getenv("CASCADE_TOKEN")}
    # invoke the agent
    url = os.getenv("CASCADE_AGENT_URL")
    response = requests.post(url, headers=headers, json=sample)
    return response.json()


def add_cascade_agent_route(fast_app: FastAPI):
    add_routes(
        app=fast_app,
        runnable=RunnableLambda(cascade_invoke),
        path="/cascade",
    )


@asynccontextmanager
async def lifespan(fast_app: FastAPI):
    try:
        load_env_file()
        add_joke_agent_route(fast_app)
        add_cascade_agent_route(fast_app)
        routes = [route.path for route in fast_app.router.routes]
        logging.info(f"Available routes: {routes}")

        fast_app.state.app_state = AppState()
        fast_app.state.app_state.text_splitter = get_text_splitter()
        fast_app.state.app_state.embedding_function = get_embedding_function()

        chroma_client = chromadb.Client()

        # Initialize ChromaDB for agents
        if "agents" in [c.name for c in chroma_client.list_collections()]:
            chroma_client.delete_collection(name="agents")
        if "ratings" in [c.name for c in chroma_client.list_collections()]:
            chroma_client.delete_collection(name="ratings")
        fast_app.state.app_state.agents_db = chroma_client.create_collection(name="agents",
                                                    embedding_function=fast_app.state.app_state.embedding_function)
        # Initialize ChromaDB for ratings
        fast_app.state.app_state.ratings_db = chroma_client.create_collection(name="ratings",
                                                     embedding_function=fast_app.state.app_state.embedding_function)

        logging.info("App state initialized successfully")
        yield
    except Exception as e:
        logging.error(f"Error during app initialization: {str(e)}")
        raise
    finally:
        logging.info("App shutdown")


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Determine the absolute path to the 'static' directory
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
static_directory = os.path.join(current_dir, '..', 'static')


# Serve the static files


def add_handlers(app: FastAPI):
    @app.get("/", response_class=FileResponse)
    async def read_root():
        return os.path.join(static_directory, "index.html")


def create_app():
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

    app.mount("/static", StaticFiles(directory=static_directory), name="static")
    add_handlers(app)
    app.include_router(ratings_router)
    app.include_router(agents_router)

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    logging.info("Starting Agentic DB API...")
    uvicorn.run(app, host="localhost", port=8000)
    logging.info("Application shutdown")
