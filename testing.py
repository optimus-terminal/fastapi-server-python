# For os and environment variables for Langchain OpenAI and langchain agent

import os 
from dotenv import load_dotenv


from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool

load_dotenv()
cohereApiKey = os.getenv("COHERE_API_KEY")

tool = YahooFinanceNewsTool()
llm = ChatCohere(cohere_api_key="pbMSOmk98DtRQtbVqc9NB2XYUn1KzNgpc4GDsHCv")
output = StrOutputParser()

chain = tool | llm | output
result = chain.invoke(f"Tell me about todays news about AAPL?")

print(result)