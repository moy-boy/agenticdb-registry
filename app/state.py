from pydantic import BaseModel, Field
from fastapi import Request
# from chromadb.api.models import Collection
from chromadb.types import Database, Tenant, Collection
from typing import Optional, Callable

class AppState(BaseModel):
    applications_db: Optional[Collection] = Field(None, description="Chroma DB for applications")
    agents_db: Optional[Collection] = Field(None, description="Chroma DB for agents")
    ratings_db: Optional[Collection] = Field(None, description="Chroma DB for ratings")
    text_splitter: Optional[Callable] = Field(None, description="Function or callable for text splitting")
    embedding_function: Optional[Callable] = Field(None, description="Function or callable for embedding")

    # def __init__(self):
    #     self.agents_db = None  # Initialize your Chroma DB here
    #     self.ratings_db = None  # Initialize your Chroma DB here
    #     self.text_splitter = None  # Initialize your text splitter here
    #     self.embedding_function = None  # Initialize your embedding function here


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state
