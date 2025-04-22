# Basics
import io
import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from io import StringIO
from typing import Dict, List

import boto3
import numpy as np
import pandas as pd

# Fast Apis & Data Handling
import requests
import uvicorn

# External API
import yfinance as yf
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, WebSocket, status
from futu import RET_OK, OpenQuoteContext

# For Langchain
from langchain.agents import AgentType, initialize_agent
from langchain_cohere import ChatCohere
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_core.output_parsers import StrOutputParser

# Input and output models
from optimus_terminal.models import (
    MLEntry,
    MLResponse,
    StockEntry,
    StockRequestData,
    StockRequestLangChain,
    StockResponse,
    WatchListElement,
)

ticker_dictionary = {
    "TEN": "HK.00700",
    "AIA": "HK.01299",
    "HSBC": "HK.00005",
    "BABA": "HK.09988",
    "LEN": "HK.00992",
    "CCB": "HK.00939",
    "ICBC": "HK.01398",
    "CM": "HK.00941",
    "HKEX": "HK.00388",
    "BOC": "HK.03988",
    "XMI": "HK.01810",
    "PTR": "HK.00857",
    "PAI": "HK.02318",
    "JD": "HK.09618",
    "CMB": "HK.03968",
    "LN": "HK.02331",
    "CPC": "HK.00386",
    "BYD": "HK.01211",
    "NTES": "HK.09999",
    "CLI": "HK.02628",
    "CKH": "HK.00001",
    "KST": "HK.01024",
    "CRL": "HK.01109",
    "CIT": "HK.00267",
    "CEO": "HK.00883",
    "GEG": "HK.00027",
    "WXB": "HK.02269",
    "BIDU": "HK.09888",
    "MT": "HK.03690",
}

endpoint_dictionary = {
    "TEN-lr": "linear-learner-2025-04-19-12-01-27-985",
    "AIA-lr": "linear-learner-2025-04-20-08-11-00-564",
    "TEN-xgb": "sagemaker-xgboost-2025-04-20-15-23-59-142",
    "TEN-lgb": "lightgbm-TEN-lightgbm-regression-model--2025-04-21-18-59-24-167",
}

WATCHLIST = [
    "HK.00700",
    "HK.01299",
    "HK.00005",
    "HK.09988",
    "HK.00992",
    "HK.00939",
    "HK.01398",
    "HK.00941",
    "HK.00388",
    "HK.03988",
    "HK.01810",
]

last_prices = {}
connected_clients: List[WebSocket] = []

# Obtain environment variables
load_dotenv()
cohereApiKey = os.getenv(
    "COHERE_API_KEY"
)  # COHERE_API_KEY = "pbMSOmk98DtRQtbVqc9NB2XYUn1KzNgpc4GDsHCv"

# Setting up a FAST API application
app = FastAPI()
quote_ctx = None


def get_quote_context():
    global quote_ctx

    if quote_ctx is None:
        quote_ctx = OpenQuoteContext(host="127.0.0.1", port=11111)

    return quote_ctx


@app.get("/stock-price/{symbol}", response_model=StockResponse)
@app.get("/stock-price/{symbol}?period={period}", response_model=StockResponse)
def stockPrice(symbol: str, period: str = "1d"):
    try:
        ticker = yf.Ticker(symbol)
        period_list = [
            "1d",
            "5d",
            "1mo",
            "3mo",
            "6mo",
            "1y",
            "2y",
            "5y",
            "10y",
            "ytd",
            "max",
        ]
        interval_map = {
            "1d": "1m",
            "5d": "15m",
            "1mo": "1h",
            "3mo": "1d",
            "6mo": "1d",
            "1y": "1d",
            "2y": "1d",
            "5y": "5d",
            "10y": "1mo",
            "ytd": "1wk",
            "max": "1mo",
        }
        if period not in period_list:
            raise HTTPException(
                status_code=404,
                detail="Invalid period. Please use one of the following: "
                + ", ".join(period_list),
            )

        interval = interval_map[period]
        hist = ticker.history(
            period=period,
            interval=interval,
            auto_adjust=False,
            back_adjust=False,
            actions=False,
        )

        if hist.empty:
            raise HTTPException(
                status_code=404, detail="No data found for the given symbol."
            )

        entries = []
        for index, row in hist.iterrows():
            entries.append(
                StockEntry(
                    date=index.strftime("%Y-%m-%d %H:%M:%S"),
                    open=row["Open"],
                    high=row["High"],
                    low=row["Low"],
                    close=row["Close"],
                    volume=row["Volume"],
                )
            )
        return StockResponse(symbol=symbol.upper(), entries=entries)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/watchlist")
def getMyWatchList():
    final_watchlist = []
    watchList = [
        "NVDA",
        "AAPL",
        "GS",
        "JPM",
        "GOOG",
        "MSFT",
        "AMZN",
        "TSLA",
        "META",
        "NFLX",
        "PEP",
        "KO",
        "INTC",
        "CSCO",
        "ORCL",
        "ADBE",
        "CRM",
    ]

    for symbol in watchList:
        try:
            ticker = yf.Ticker(symbol)
            vol = round(float(ticker.info["volume"]), 2)
            avgVol = round(float(ticker.info["averageVolume"]), 2)
            mktCap = round(float(ticker.info["marketCap"]), 2)

            hist = ticker.history(
                period="1d",
                interval="1d",
                auto_adjust=False,
                back_adjust=False,
                actions=False,
            )

            if hist.empty:
                raise HTTPException(
                    status_code=404, detail="No data found for the given symbol."
                )

            last = round(float(hist["Close"].iloc[-1]), 2)
            changePercentage = round(random.uniform(-0.04, 0.02), 2)
            change = round(last * changePercentage, 2)
            last = round(last + change, 2)

            watchListEle = WatchListElement(
                ticker=symbol,
                last=last,
                change=change,
                changePer=changePercentage,
                volume=vol,
                avgVolume=avgVol,
                marketCapacity=mktCap,
            )

            final_watchlist.append(watchListEle)
            print(f"Success: {ticker} watchList data")

        except HTTPException as http_err:
            logging.error(f"HTTPException for symbol {symbol}: {http_err}")

        except KeyError as key_err:
            logging.error(f"KeyError for symbol {symbol}: {key_err}")

        except Exception as e:
            logging.error(f"During processing {symbol}: {e}")

    return final_watchlist


@app.post("/stock-news-polygon")
def stockNewsPolygon(request: StockRequestData):
    requestMsg = f"https://api.polygon.io/v2/reference/news?ticker={request.symbol}&order={request.order}&limit={request.limit}&apiKey=xj8EhRNHGdZW6BjW3DCH1Kw5Ie2_Ms4L"
    response = requests.get(requestMsg)
    return response.json()


def data_collection_futu(ticker):
    ctx = get_quote_context()
    all_data = pd.DataFrame()

    current_date = datetime.now()
    start_date = (current_date - timedelta(days=365)).strftime("%Y-%m-%d")
    current_date = current_date.strftime("%Y-%m-%d")

    ret, data, page_req_key = ctx.request_history_kline(
        ticker, start=start_date, end=current_date, max_count=1000
    )

    if ret == RET_OK:
        all_data = pd.concat([all_data, data], ignore_index=True)
    else:
        print("error:", data)

    while page_req_key is not None:
        print("*************************************")
        ret, data, page_req_key = ctx.request_history_kline(
            ticker,
            start=start_date,
            end=current_date,
            max_count=1000,
            page_req_key=page_req_key,
        )

        if ret == RET_OK:
            all_data = pd.concat([all_data, data], ignore_index=True)
        else:
            print("error:", data)

    print("LOG:      All pages are finished!")
    # quote_ctx.close()

    # Post processing of data
    all_data["time_key"] = pd.to_datetime(all_data["time_key"]).dt.date
    all_data = all_data.rename(columns={"time_key": "Date"})

    return all_data


def data_preprocessing(df):
    list_of_columns = ["close", "last_close", "pe_ratio"]
    df = df[list_of_columns]

    df = df.rename(
        columns={"close": "Close", "last_close": "S_Close(t-1)", "pe_ratio": "pe_ratio"}
    )

    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()

    df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA_12"] - df["EMA_26"]

    df = df.iloc[50:, :]
    df = df.reset_index(drop=True)

    list_of_columns = ["pe_ratio", "S_Close(t-1)", "EMA_20", "EMA_50", "MACD"]
    df = df[list_of_columns]

    return df


def index_processing(df, df_index):
    list_of_index_features = ["close", "last_close"]
    df_index = df_index[list_of_index_features]

    df_index = df_index.rename(
        columns={
            "close": "Close",
            "last_close": "S_Close(t-1)",
        }
    )

    df_index["EMA_20"] = df_index["Close"].ewm(span=20, adjust=False).mean()
    df_index["EMA_12"] = df_index["Close"].ewm(span=12, adjust=False).mean()
    df_index["EMA_26"] = df_index["Close"].ewm(span=26, adjust=False).mean()
    df_index["MACD"] = df_index["EMA_12"] - df_index["EMA_26"]

    df_index = df_index.iloc[50:, :]
    df_index = df_index.reset_index(drop=True)

    funds = "HKEX"
    df[f"{funds}_EMA_20"] = df_index["EMA_20"]
    df[f"{funds}_S_Close(t-1)"] = df_index["S_Close(t-1)"]
    df[f"{funds}_MACD"] = df_index["MACD"]

    return df, df_index


def align_df(df, df_index):
    df_start_date = df["Date"].min()
    idx_start_date = df_index["Date"].min()

    actual_start_date = max(df_start_date, idx_start_date)

    df_aligned = df[df["Date"] >= actual_start_date].copy()
    df_index_aligned = df_index[df_index["Date"] >= actual_start_date].copy()
    date_df = df_aligned[["Date"]].reset_index(drop=True)

    return df_aligned, df_index_aligned, date_df


# ticker: ten/aia
# model: lr, xgb, lgb
@app.get("/ml/{ticker}/{model}")
def getTickerPrediction(ticker: str, model: str):
    # Connection to futubull api
    #  a. Fetching data for both independent stocks and index stocks

    ticker_code = ticker_dictionary[ticker.upper()]
    df = data_collection_futu(ticker_code)
    df_index = data_collection_futu(ticker_dictionary["HKEX"])

    df_aligned, df_index_aligned, date_df = align_df(df, df_index)
    df, df_index = df_aligned, df_index_aligned

    date_df = date_df.iloc[50:, :]
    date_df = date_df.reset_index(drop=True)

    # print(f"{ticker} Data: ")
    # print(df)
    # print("HKEX Data: ")
    # print(df_index)
    # print("Date df: ")
    # print(date_df)

    df_part1 = data_preprocessing(df)
    X_test, df_part2 = index_processing(df_part1, df_index)

    # print("HKEX Data: ")
    # print(df_part2)

    # print("X_test   : ")
    # print(X_test)

    csv_file = io.StringIO()
    X_test.to_csv(csv_file, sep=",", header=False, index=False)
    X_test_payload = csv_file.getvalue()

    # Connection to AWS client
    #  a. Get access to the model in endpoint
    #  b. Receiving output and returning it back to client side

    # Create a SageMaker runtime client object using your IAM role ARN
    runtime = boto3.client(
        "sagemaker-runtime",
        aws_access_key_id="",
        aws_secret_access_key="",
        region_name="ap-east-1",
    )

    endpoint_key = ticker.upper() + "-" + model
    print("LOG:     ", endpoint_key, ": ", endpoint_dictionary[endpoint_key])

    # Sending Request
    if model != "lgb":
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_dictionary[endpoint_key],
            ContentType="text/csv",
            Body=X_test_payload,
        )
    else:
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_dictionary[endpoint_key],
            ContentType="text/csv",
            Body=X_test.to_csv(header=False, index=False).encode("utf-8"),
        )

    # Handling Responses
    if model == "lr":
        output_data = json.loads(response["Body"].read().decode("utf-8"))
        scores = [pred["score"] for pred in output_data["predictions"]]
        # print(scores)

    elif model == "xgb":
        output_data = response["Body"].read().decode("utf-8")
        scores = [float(line) for line in output_data.strip().split("\n") if line]
        # print(scores)

    elif model == "lgb":
        output_data = json.loads(response["Body"].read())
        scores = np.array(output_data["prediction"]).tolist()
        # print(scores)

    dates = date_df["Date"].tolist()
    count = min(len(dates), len(scores))

    entries = []
    for i in range(count):
        next_day = dates[i] + timedelta(days=1)
        date_str = next_day.strftime("%Y-%m-%d")
        entries.append(MLEntry(date=date_str, predictedClose=scores[i]))

    # print(output_data)
    return MLResponse(symbol=ticker.upper(), entries=entries)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
