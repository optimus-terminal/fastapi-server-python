python_source(
    name="main",
    source="main.py",
    dependencies=[
        "//:reqs#fastapi",
        "//:reqs#langchain",
        "//:reqs#langchain-cohere",
        "//:reqs#langchain-community",
        "//:reqs#langchain-core",
        "//:reqs#python-dotenv",
        "//:reqs#requests",
        "//:reqs#types-requests",
        "//:reqs#uvicorn",
        "//:reqs#yfinance",
        "//:reqs#futu-api",
    ],
)

pex_binary(name="server_run", entry_point="main.py")
