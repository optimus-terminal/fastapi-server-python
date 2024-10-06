# For FASTAPI and API requests
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
import requests

# For os and environment variables for Langchain OpenAI and langchain agent
import os 
from dotenv import load_dotenv

# For Langchain
from langchain.agents import AgentType, initialize_agent
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_cohere import ChatCohere
from langchain_core.output_parsers import StrOutputParser

# Obtain environment variables
load_dotenv()
cohereApiKey = os.getenv("COHERE_API_KEY") # COHERE_API_KEY = "pbMSOmk98DtRQtbVqc9NB2XYUn1KzNgpc4GDsHCv"

# Setting up a FAST API application
app = FastAPI()

# Inputs for two APIs
class StockRequestData(BaseModel):
    symbol: str                         # Symbol of the Stock
    order: Optional[str] = "asc"        # Order: asc/desc
    limit: Optional[str] = "5"          # Limit: E.g. 10

class StockRequestLangChain(BaseModel):
    symbol: str                         # Symbol of the Stock

# Actual implementation of APIs
@app.post("/stock-news-polygon")
def stockNewsPolygon(request: StockRequestData):

    requestMsg = f"https://api.polygon.io/v2/reference/news?ticker={request.symbol}&order={request.order}&limit={request.limit}&apiKey=xj8EhRNHGdZW6BjW3DCH1Kw5Ie2_Ms4L"
    response = requests.get(requestMsg)
    return response.json()

@app.post("/stock-news-langchain")
def stockNewsLangChain(request: StockRequestLangChain):

    tool = YahooFinanceNewsTool()
    llm = ChatCohere(cohere_api_key=cohereApiKey)
    output = StrOutputParser()

    chain = tool | llm | output
    result = chain.invoke(f"Tell me about today's news about {request.symbol}?")
    
    return {"result": str(result)}