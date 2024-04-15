# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

__all__ = ["create_app"]

load_dotenv()


def _setup_error_handler(app: FastAPI) -> None:
    from server_api.response import ResponseError
    from server_core.authentication import AuthenticationException, PermissionException

    @app.exception_handler(AuthenticationException)
    def invalid_token_verfied_handler(
        req, exc: AuthenticationException
    ) -> JSONResponse:
        return JSONResponse(
            content=ResponseError.from_error(
                message=exc.message if hasattr(exc, "message") else f"{exc}",
                status=401,
            ).model_dump(),
        )

    @app.exception_handler(PermissionException)
    def permission_exception_handler(req, exc: PermissionException) -> JSONResponse:
        return JSONResponse(
            content=ResponseError.from_error(
                message=exc.message if hasattr(exc, "message") else f"{exc}",
                status=403,
            ).model_dump(),
        )


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    from .prepare_data import init_app as prepare_data_init_app
    from .routes import init_app as routes_init_app

    # run migration
    migrate_result = os.system("python -m alembic upgrade head")
    if migrate_result != 0:
        print("migrate failed")

    prepare_data_init_app(app=app)

    routes_init_app(app=app)
    _setup_error_handler(app=app)

    return app


app = create_app()
