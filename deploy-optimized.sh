#!/bin/bash

# Script de despliegue optimizado para Azaktilsa en GCP...
# Mantiene consistencia con la URL actual: https://azaktilsadocker-1032463379361.us-central1.run.app/

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Desplegando Azaktilsa en GCP...${NC}"
echo "========================================="

# Configuración
PROJECT_ID="azaktilza-470117"
IMAGE_NAME="azaktilsadocker"
SERVICE_NAME="azaktilsadocker"
REGION="us-central1"
BUCKET_NAME="azaktilsa_fincas"

echo -e "${YELLOW}📋 Configuración del despliegue:${NC}"
echo "   Proyecto: $PROJECT_ID"
echo "   Imagen: gcr.io/$PROJECT_ID/$IMAGE_NAME:latest"
echo "   Servicio: $SERVICE_NAME"
echo "   Región: $REGION"
echo "   Bucket: $BUCKET_NAME"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ ERROR: No se encuentra main.py. Ejecuta desde el directorio del servidor.${NC}"
    exit 1
fi

# Paso 1: Construir la imagen
echo -e "${BLUE}🔨 Paso 1: Construyendo imagen Docker...${NC}"
docker buildx build --platform linux/amd64 -t gcr.io/$PROJECT_ID/$IMAGE_NAME:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Imagen construida exitosamente${NC}"
else
    echo -e "${RED}❌ Error construyendo la imagen${NC}"
    exit 1
fi

# Paso 2: Empujar la imagen
echo -e "${BLUE}📤 Paso 2: Empujando imagen a Google Container Registry...${NC}"
docker push gcr.io/$PROJECT_ID/$IMAGE_NAME:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Imagen empujada exitosamente${NC}"
else
    echo -e "${RED}❌ Error empujando la imagen${NC}"
    exit 1
fi

# Paso 3: Desplegar en Cloud Run
echo -e "${BLUE}🚀 Paso 3: Desplegando en Google Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$IMAGE_NAME:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="GCS_BUCKET_NAME=$BUCKET_NAME,GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production,DEBUG=false,MODELO_PATH_CAMANOVILLO=gs://azaktilsa_fincas/model/modelo_CAMANOVILLO_random_forest.pkl,SCALER_PATH_CAMANOVILLO=gs://azaktilsa_fincas/scaler/scaler_CAMANOVILLO.pkl,MODELO_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/model/modelo_EXCANCRIGRU_random_forest.pkl,SCALER_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/scaler/scaler_EXCANCRIGRU.pkl,MODELO_PATH_FERTIAGRO=gs://azaktilsa_fincas/model/modelo_FERTIAGRO_random_forest.pkl,SCALER_PATH_FERTIAGRO=gs://azaktilsa_fincas/scaler/scaler_FERTIAGRO.pkl,MODELO_PATH_GROVITAL=gs://azaktilsa_fincas/model/modelo_GROVITAL_random_forest.pkl,SCALER_PATH_GROVITAL=gs://azaktilsa_fincas/scaler/scaler_GROVITAL.pkl,MODELO_PATH_SUFAAZA=gs://azaktilsa_fincas/model/modelo_SUFAAZA_random_forest.pkl,SCALER_PATH_SUFAAZA=gs://azaktilsa_fincas/scaler/scaler_SUFAAZA.pkl,MODELO_PATH_TIERRAVID=gs://azaktilsa_fincas/model/modelo_TIERRAVID_random_forest.pkl,SCALER_PATH_TIERRAVID=gs://azaktilsa_fincas/scaler/scaler_TIERRAVID.pkl,RENDIMIENTO_PATH=https://azaktilza-default-rtdb.firebaseio.com/Empresas/TerrawaSufalyng/Rendimiento.json,PESOS_ALIMENTATION=gs://azaktilsa_fincas/Data/pesos_alimento.json,MODELO_ALIMENTATION_PATH_CAMANOVILLO=gs://azaktilsa_fincas/modelalimentation/modelo_CAMANOVILLO_ensemble.pkl,SCALER_ALIMENTATION_PATH_CAMANOVILLO=gs://azaktilsa_fincas/scaleralimentation/scaler_CAMANOVILLO.pkl,SELECTOR_ALIMENTATION_PATH_CAMANOVILLO=gs://azaktilsa_fincas/selector/selector_CAMANOVILLO.pkl,YSCALERS_ALIMENTATION_PATH_CAMANOVILLO=gs://azaktilsa_fincas/yscalers/y_scalers_CAMANOVILLO.pkl,MODELO_ALIMENTATION_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/modelalimentation/modelo_EXCANCRIGRU_ensemble.pkl,SCALER_ALIMENTATION_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/scaleralimentation/scaler_EXCANCRIGRU.pkl,SELECTOR_ALIMENTATION_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/selector/selector_EXCANCRIGRU.pkl,YSCALERS_ALIMENTATION_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/yscalers/y_scalers_EXCANCRIGRU.pkl,MODELO_ALIMENTATION_PATH_FERTIAGRO=gs://azaktilsa_fincas/modelalimentation/modelo_FERTIAGRO_ensemble.pkl,SCALER_ALIMENTATION_PATH_FERTIAGRO=gs://azaktilsa_fincas/scaleralimentation/scaler_FERTIAGRO.pkl,SELECTOR_ALIMENTATION_PATH_FERTIAGRO=gs://azaktilsa_fincas/selector/selector_FERTIAGRO.pkl,YSCALERS_ALIMENTATION_PATH_FERTIAGRO=gs://azaktilsa_fincas/yscalers/y_scalers_FERTIAGRO.pkl,MODELO_ALIMENTATION_PATH_GROVITAL=gs://azaktilsa_fincas/modelalimentation/modelo_GROVITAL_ensemble.pkl,SCALER_ALIMENTATION_PATH_GROVITAL=gs://azaktilsa_fincas/scaleralimentation/scaler_GROVITAL.pkl,SELECTOR_ALIMENTATION_PATH_GROVITAL=gs://azaktilsa_fincas/selector/selector_GROVITAL.pkl,YSCALERS_ALIMENTATION_PATH_GROVITAL=gs://azaktilsa_fincas/yscalers/y_scalers_GROVITAL.pkl,MODELO_ALIMENTATION_PATH_SUFAAZA=gs://azaktilsa_fincas/modelalimentation/modelo_SUFAAZA_ensemble.pkl,SCALER_ALIMENTATION_PATH_SUFAAZA=gs://azaktilsa_fincas/scaleralimentation/scaler_SUFAAZA.pkl,SELECTOR_ALIMENTATION_PATH_SUFAAZA=gs://azaktilsa_fincas/selector/selector_SUFAAZA.pkl,YSCALERS_ALIMENTATION_PATH_SUFAAZA=gs://azaktilsa_fincas/yscalers/y_scalers_SUFAAZA.pkl,MODELO_ALIMENTATION_PATH_TIERRAVID=gs://azaktilsa_fincas/modelalimentation/modelo_TIERRAVID_ensemble.pkl,SCALER_ALIMENTATION_PATH_TIERRAVID=gs://azaktilsa_fincas/scaleralimentation/scaler_TIERRAVID.pkl,SELECTOR_ALIMENTATION_PATH_TIERRAVID=gs://azaktilsa_fincas/selector/selector_TIERRAVID.pkl,YSCALERS_ALIMENTATION_PATH_TIERRAVID=gs://azaktilsa_fincas/yscalers/y_scalers_TIERRAVID.pkl" \
  --port=8080 \
  --max-instances=10 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Despliegue exitoso${NC}"
else
    echo -e "${RED}❌ Error en el despliegue${NC}"
    exit 1
fi

# Obtener la URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform=managed --region=$REGION --format='value(status.url)')

echo ""
echo -e "${GREEN}🎉 ¡DESPLIEGUE COMPLETADO!${NC}"
echo "========================================="
echo -e "${YELLOW}📍 URL del servicio:${NC} $SERVICE_URL"
echo -e "${YELLOW}🩺 Health check:${NC} $SERVICE_URL/api/system/health"
echo -e "${YELLOW}👩‍💼 Panel Admin:${NC} $SERVICE_URL/admin"
echo -e "${YELLOW}📚 API Docs:${NC} $SERVICE_URL/docs"
echo ""
echo -e "${BLUE}🔍 Para verificar el estado:${NC}"
echo "   gcloud run services list --region=$REGION"
echo ""
echo -e "${BLUE}📊 Para ver logs:${NC}"
echo "   gcloud logs tail --follow --service=$SERVICE_NAME"