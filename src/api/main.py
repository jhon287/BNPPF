#!/usr/bin/env python3


# from sqlalchemy import URL, Engine, create_engine, text
from fastapi import FastAPI
import uvicorn
import config
import health
import auth
import accounts


# # Database
# engine: Engine = create_engine(
#     echo=True,
#     url=URL.create(
#         drivername="mysql+mysqlconnector",
#         username=config.DB_USERNAME,
#         password=config.DB_PASSWORD,
#         host=config.DB_HOSTNAME,
#         port=config.DB_PORT,
#         database=config.DB_NAME,
#     )
# )

api: FastAPI = FastAPI(title=config.API_TITLE, version=config.API_VERSION)

api.include_router(health.router)
api.include_router(auth.router)
api.include_router(accounts.router)


# @api.head(path="/", status_code=status.HTTP_403_FORBIDDEN)
# async def head_root():
#     return "Access Denied !"

# @api.get(path="/", status_code=status.HTTP_403_FORBIDDEN,
#          response_class=PlainTextResponse)
# async def get_root():
#     return "Access Denied !"


# @api.get(path="/transactions")
# def get_transactions() -> list[dict[str, str]]:
#     transactions: list[dict[str, str]] = []
#     with engine.connect() as connection:
#         connection.execute(statement=text(
#             "CREATE TABLE example (id INTEGER, name VARCHAR(20))"
#         ))
#     return transactions

# @api.get(path="/types")
# def get_types() -> list[str]:
#     trx_types: list[str] = []
#     return trx_types


# @api.get(path="/years")
# def get_years(authorization: str | None = Header(default=None)) -> list[str]:
#     trx_years: list[str] = []
#     return trx_years


if (__name__) == "__main__":  # pragma: no cover
    uvicorn.run(  # type: ignore
        app="main:api", host=config.API_IP, port=config.API_PORT, reload=True
    )
