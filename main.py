from dotenv import load_dotenv
import warnings
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.routes import router as main_router
from app.stats import stats_manager
from app.animal import PredictionRequest, procesar_prediccion_animal
from app.alimentation import PredictionRequestAlimentation, procesar_prediccion_alimentation

warnings.filterwarnings(
    "ignore", message="Skipping variable loading for optimizer")

app = FastAPI(
    title="Azaktilza S.A",
    description="Sistema CRUD con Google Cloud Storage para "
                "Alimentación del camarón",
    version="1.0.0"
)

load_dotenv()
# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia por dominio real en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Motor de plantillas
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Endpoint simple de health check para contenedores"""
    return {"status": "healthy", "message": "API funcionando correctamente"}


@app.get("/api/system/health")
async def system_health_check():
    """Endpoint de health check del sistema para contenedores"""
    return {"status": "healthy", "message": "Sistema funcionando"}


@app.get("/stats")
async def get_stats():
    """Endpoint para obtener estadísticas de la aplicación"""
    return stats_manager.get_all_stats()


@app.post("/predict")
async def predict(request: PredictionRequest):
    # Incrementar contador de solicitudes totales
    stats_manager.increment_total_requests()

    try:
        # Procesar la predicción usando el módulo animal
        resultado = procesar_prediccion_animal(request)

        # Incrementar contador de solicitudes exitosas
        stats_manager.increment_successful_requests(request.finca)

        return resultado

    except HTTPException:
        # Incrementar contador de solicitudes fallidas
        stats_manager.increment_failed_requests()
        raise
    except Exception as e:
        # Incrementar contador de solicitudes fallidas
        stats_manager.increment_failed_requests()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alimentation")
async def alimentation(request: PredictionRequestAlimentation):
    # Incrementar contador de solicitudes totales
    stats_manager.increment_total_requests()

    try:
        # Procesar la predicción usando el módulo alimentation
        resultado = procesar_prediccion_alimentation(request)

        # Incrementar contador de solicitudes exitosas
        stats_manager.increment_successful_requests(request.finca)

        return resultado

    except HTTPException:
        # Incrementar contador de solicitudes fallidas
        stats_manager.increment_failed_requests()
        raise
    except Exception as e:
        # Incrementar contador de solicitudes fallidas
        stats_manager.increment_failed_requests()
        raise HTTPException(status_code=500, detail=str(e))


# Incluir otras rutas
app.include_router(main_router)
