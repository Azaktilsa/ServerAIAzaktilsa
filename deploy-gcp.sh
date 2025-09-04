#!/bin/bash

# Script para desplegar en Google Cloud Run
set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Desplegando El Gringo Auto Taller en Google Cloud Run${NC}"

# Verificar variables requeridas
if [ -z "$GOOGLE_CLOUD_PROJECT_ID" ]; then
    echo -e "${RED}❌ ERROR: Variable GOOGLE_CLOUD_PROJECT_ID no configurada${NC}"
    echo "Ejecutar: export GOOGLE_CLOUD_PROJECT_ID=elgringoautorepuesto"
    exit 1
fi

if [ -z "$GCS_BUCKET_NAME" ]; then
    echo -e "${RED}❌ ERROR: Variable GCS_BUCKET_NAME no configurada${NC}"
    echo "Ejecutar: export GCS_BUCKET_NAME=repogalleryautorepuesto"
    exit 1
fi

PROJECT_ID="$GOOGLE_CLOUD_PROJECT_ID"
IMAGE_NAME="azaktilsa_image"
SERVICE_NAME="azaktilsa_image"
REGION="us-central1"

echo -e "${YELLOW}📋 Configuración del despliegue:${NC}"
echo "   Proyecto: $PROJECT_ID"
echo "   Imagen: $IMAGE_NAME"
echo "   Servicio: $SERVICE_NAME"
echo "   Región: $REGION"
echo "   Bucket: $GCS_BUCKET_NAME"
echo ""

# Verificar que gcloud esté instalado y autenticado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ ERROR: gcloud CLI no está instalado${NC}"
    echo "Instalar desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar autenticación
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    echo -e "${RED}❌ ERROR: No hay usuario autenticado en gcloud${NC}"
    echo "Ejecutar: gcloud auth login"
    exit 1
fi

# Configurar proyecto
echo -e "${BLUE}🔧 Configurando proyecto...${NC}"
gcloud config set project $PROJECT_ID

# Habilitar APIs necesarias
echo -e "${BLUE}🔌 Habilitando APIs necesarias...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com

# Construir imagen en Cloud Build
echo -e "${BLUE}🏗️  Construyendo imagen en Cloud Build...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$IMAGE_NAME

# Crear secretos para credenciales de email (si no existen)
echo -e "${BLUE}🔐 Configurando secretos...${NC}"
if [ ! -z "$EMAIL_USER" ] && [ ! -z "$EMAIL_PASS" ]; then
    # Crear secreto para EMAIL_USER
    if ! gcloud secrets describe email-user >/dev/null 2>&1; then
        echo -e "${YELLOW}📝 Creando secreto para EMAIL_USER...${NC}"
        echo -n "$EMAIL_USER" | gcloud secrets create email-user --data-file=-
    else
        echo -e "${GREEN}✅ Secreto email-user ya existe${NC}"
    fi
    
    # Crear secreto para EMAIL_PASS
    if ! gcloud secrets describe email-pass >/dev/null 2>&1; then
        echo -e "${YELLOW}📝 Creando secreto para EMAIL_PASS...${NC}"
        echo -n "$EMAIL_PASS" | gcloud secrets create email-pass --data-file=-
    else
        echo -e "${GREEN}✅ Secreto email-pass ya existe${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Variables EMAIL_USER y EMAIL_PASS no configuradas${NC}"
    echo "   El envío de emails no funcionará"
fi

# Desplegar en Cloud Run
echo -e "${BLUE}🚀 Desplegando en Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="GCS_BUCKET_NAME=$GCS_BUCKET_NAME,GOOGLE_CLOUD_PROJECT_ID=$PROJECT_ID,ENVIRONMENT=production,DEBUG=false" \
    --set-secrets="EMAIL_USER=email-user:latest,EMAIL_PASS=email-pass:latest" \
    --memory 512Mi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0

# Obtener URL del servicio
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo -e "${GREEN}✅ Despliegue completado exitosamente!${NC}"
echo ""
echo -e "${BLUE}📱 URLs del servicio:${NC}"
echo "   🏠 Página principal: $SERVICE_URL"
echo "   🎛️  Panel de administración: $SERVICE_URL/admin"
echo "   📚 Documentación API: $SERVICE_URL/docs"
echo "   🩺 Health check: $SERVICE_URL/api/system/health"
echo ""
echo -e "${YELLOW}🔧 Para actualizar el servicio:${NC}"
echo "   ./deploy-gcp.sh"
echo ""
echo -e "${YELLOW}📋 Para ver logs:${NC}"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION"