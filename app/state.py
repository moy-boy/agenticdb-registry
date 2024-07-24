from fastapi import Request


class AppState:
    def __init__(self):
        self.agents_db = None  # Initialize your Chroma DB here
        self.ratings_db = None  # Initialize your Chroma DB here
        self.text_splitter = None  # Initialize your text splitter here
        self.embedding_function = None  # Initialize your embedding function here


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state
