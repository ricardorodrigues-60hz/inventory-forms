import logging
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from forms_inventario.database import engine
from forms_inventario.routers import auth, registros, usuarios
from forms_inventario.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        async with engine.begin() as conn:
            await conn.execute(text('SELECT 1'))
        logger.info('Conexao com banco de dados estabelecida com sucesso.')
    except Exception as e:
        logger.error(f'Falha ao conectar no banco de dados: {e}')

    yield

    await engine.dispose()


app = FastAPI(title='API Sistema Patrimonial', lifespan=lifespan)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(registros.router)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health', tags=['Health'])
async def health_check():

    try:
        async with engine.begin() as conn:
            await conn.execute(text('SELECT 1'))
        db_status = 'ok'
    except Exception:
        db_status = 'error'
        raise HTTPException(
            status_code=HTTPStatus.SERVICE_UNAVAILABLE,
            detail='Falha na conexao com o banco de dados.',
        )

    return {'status': 'ok', 'database': db_status}
