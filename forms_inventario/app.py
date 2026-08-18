import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from forms_inventario.config import settings
from forms_inventario.database import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Testar conexao com o banco
    try:
        async with engine.begin() as conn:
            await conn.execute(text('SELECT 1'))
        logger.info('Conexao com banco de dados estabelecida com sucesso.')
    except Exception as e:
        logger.error(f'Falha ao conectar no banco de dados: {e}')
        # Em producao, poderiamos falhar silenciosamente ou encerrar a app.
        # Aqui apenas logamos.
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(title='API Sistema Patrimonial', lifespan=lifespan)

# CORS
origins = [origin.strip() for origin in settings.cors_origins.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health', tags=['Health'])
async def health_check():
    """Verifica se a API e o banco estao online."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text('SELECT 1'))
        db_status = 'ok'
    except Exception:
        db_status = 'error'
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Servico indisponivel - Falha na conexao com o banco de dados.',
        )

    return {'status': 'ok', 'database': db_status}


# Registrar routers
from forms_inventario.routers import auth, registros, usuarios

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(registros.router)
