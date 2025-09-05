# Parte Inicial, Configuración del servidor

## Activar entorno

Python 3.10.16

### En macOS/Linux

source .venv/bin/activate

### En Windows

.venv\Scripts\activate

## Instalar las dependencias

pip install -r requirements.txt

## Parte 1: Construir la Imagen Docker

docker build --platform linux/amd64 -t gcr.io/azaktilza-470117/azaktilsadocker:latest .

## Parte 2: Subir la Imagen Docker a Google Container Registry (GCR)

gcloud auth login
gcloud auth configure-docker

## Parte 3: Empujar la imagen Docker al Container Registry

docker tag gcr.io/azaktilza-470117/azaktilsadocker:latest azaktilza-470117/azaktilsadocker:latest

docker push gcr.io/azaktilza-470117/azaktilsadocker:latest

## Parte 4: Subir la Imagen Docker al Bucket de Google Cloud Storage

gsutil cp azaktilsadocker.tar gs://azaktilsa-docker-images/

docker save azaktilza-470117/azaktilsadocker:latest > azaktilsadocker.tar

## Parte 5: Desplegar la Imagen Docker en Google Cloud

gcloud run deploy --image gcr.io/azaktilza-470117/azaktilsadocker:latest --platform managed --region us-central1 --allow-unauthenticated

## Parte 6: Verificación

gcloud run services list

## PASOS CORTOS PARA ACTUALIZACIÓN EN EL SERVIDOR

## 1. Construir la imagen en amd64

docker buildx build --platform linux/amd64 -t gcr.io/azaktilza-470117/azaktilsadocker:latest .

## 🔄 2. Empujar la imagen corregida a GCR

docker push gcr.io/azaktilza-470117/azaktilsadocker:latest

## 🚀 3. Desplegar en Google Cloud Run

gcloud run deploy --image gcr.io/azaktilza-470117/azaktilsadocker:latest --platform managed --region us-central1 --allow-unauthenticated

## Nombre para el servicio en Google Cloud Run

azaktilsadocker

## Si nada de lo anterior funciona utilizar esto para regenerar la imagen Docker y volverla a desplegar

    ´´´
    docker build -t gcr.io/azaktilza-470117/azaktilsadocker:latest .

    docker push gcr.io/azaktilza-470117/azaktilsadocker:latest
    ´´´

## Run Server

python app.py

## Config emergencia

    ´´´
    gcloud run deploy azaktilsadocker \
    --image gcr.io/azaktilza-470117/azaktilsadocker:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars GCS_BUCKET_NAME=azaktilsa_docker,GOOGLE_CLOUD_PROJECT_ID=azaktilsa,EMAIL_USER=terrawasuffa@gmail.com,EMAIL_PASS=kkkgpklzlxcsgddl,ENVIRONMENT=development,DEBUG=true
    ´´´

## Server live

uvicorn main:app --reload --host 0.0.0.0 --port 8080
