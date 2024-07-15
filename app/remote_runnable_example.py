from langserve import RemoteRunnable

joke_chain = RemoteRunnable("http://localhost:8000/joke/")

response = joke_chain.invoke({"topic": "parrots"})
print(response.content)
