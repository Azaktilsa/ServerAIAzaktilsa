#!/bin/bash

# Script para desplegar en Cloud Run con todas las variables de entorno necesarias

echo "🚀 Desplegando aplicación en Cloud Run con todas las variables de entorno..."

gcloud run deploy azaktilsadocker \
  --image gcr.io/azaktilza-470117/azaktilsadocker:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars EMAIL_USER=terrawasuffa@gmail.com \
  --set-env-vars EMAIL_PASS=kkkgpklzlxcsgddl \
  --set-env-vars GOOGLE_CLOUD_PROJECT_ID=azaktilza-470117 \
  --set-env-vars GCS_BUCKET_NAME=azaktilsa_fincas \
  --set-env-vars ENVIRONMENT=development \
  --set-env-vars DEBUG=true \
  --set-env-vars FIREBASE_API_KEY=AIzaSyA9hinztfYgVtVs7ReqNI0kVLkPIUz3fUg \
  --set-env-vars FIREBASE_AUTH_DOMAIN=azaktilza.firebaseapp.com \
  --set-env-vars FIREBASE_DATABASE_URL=https://azaktilza-default-rtdb.firebaseio.com \
  --set-env-vars FIREBASE_PROJECT_ID=azaktilza \
  --set-env-vars FIREBASE_STORAGE_BUCKET=azaktilza.firebasestorage.app \
  --set-env-vars FIREBASE_MESSAGING_SENDER_ID=177530289587 \
  --set-env-vars FIREBASE_APP_ID=1:177530289587:web:8cafae94dee5abceb89fc6 \
  --set-env-vars FIREBASE_MEASUREMENT_ID=G-JHBH0BWS3V \
  --set-env-vars FIREBASE_CREDENTIALS_PATH=azaktilsa-firebase-adminsdk.json \
  --set-env-vars MODELO_PATH_CAMANOVILLO=gs://azaktilsa_fincas/model/modelo_CAMANOVILLO_random_forest.pkl \
  --set-env-vars SCALER_PATH_CAMANOVILLO=gs://azaktilsa_fincas/scaler/scaler_CAMANOVILLO.pkl \
  --set-env-vars MODELO_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/model/modelo_EXCANCRIGRU_random_forest.pkl \
  --set-env-vars SCALER_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/scaler/scaler_EXCANCRIGRU.pkl \
  --set-env-vars MODELO_PATH_FERTIAGRO=gs://azaktilsa_fincas/model/modelo_FERTIAGRO_random_forest.pkl \
  --set-env-vars SCALER_PATH_FERTIAGRO=gs://azaktilsa_fincas/scaler/scaler_FERTIAGRO.pkl \
  --set-env-vars MODELO_PATH_GROVITAL=gs://azaktilsa_fincas/model/modelo_GROVITAL_random_forest.pkl \
  --set-env-vars SCALER_PATH_GROVITAL=gs://azaktilsa_fincas/scaler/scaler_GROVITAL.pkl \
  --set-env-vars MODELO_PATH_SUFAAZA=gs://azaktilsa_fincas/model/modelo_SUFAAZA_random_forest.pkl \
  --set-env-vars SCALER_PATH_SUFAAZA=gs://azaktilsa_fincas/scaler/scaler_SUFAAZA.pkl \
  --set-env-vars MODELO_PATH_TIERRAVID=gs://azaktilsa_fincas/model/modelo_TIERRAVID_random_forest.pkl \
  --set-env-vars SCALER_PATH_TIERRAVID=gs://azaktilsa_fincas/scaler/scaler_TIERRAVID.pkl \
  --set-env-vars RENDIMIENTO_PATH=https://azaktilza-default-rtdb.firebaseio.com/Empresas/TerrawaSufalyng/Rendimiento.json \
  --set-env-vars PESOS_ALIMENTATION=gs://azaktilsa_fincas/Data/pesos_alimento.json \
  --set-env-vars TERRAIN=gs://azaktilsa_fincas/Data/Terrain.json \
  --set-env-vars MODELO_ALIMENTATION_PATH_CAMANOVILLO=gs://azaktilsa_fincas/modelalimentation/modelo_CAMANOVILLO_ensemble.pkl \
  --set-env-vars SCALER_ALIMENTATION_PATH_CAMANOVILLO=gs://azaktilsa_fincas/scaleralimentation/scaler_CAMANOVILLO.pkl \
  --set-env-vars SELECTOR_ALIMENTATION_PATH_CAMANOVILLO=gs://azaktilsa_fincas/selector/selector_CAMANOVILLO.pkl \
  --set-env-vars YSCALERS_ALIMENTATION_PATH_CAMANOVILLO=gs://azaktilsa_fincas/yscalers/y_scalers_CAMANOVILLO.pkl \
  --set-env-vars MODELO_ALIMENTATION_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/modelalimentation/modelo_EXCANCRIGRU_ensemble.pkl \
  --set-env-vars SCALER_ALIMENTATION_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/scaleralimentation/scaler_EXCANCRIGRU.pkl \
  --set-env-vars SELECTOR_ALIMENTATION_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/selector/selector_EXCANCRIGRU.pkl \
  --set-env-vars YSCALERS_ALIMENTATION_PATH_EXCANCRIGRU=gs://azaktilsa_fincas/yscalers/y_scalers_EXCANCRIGRU.pkl \
  --set-env-vars MODELO_ALIMENTATION_PATH_FERTIAGRO=gs://azaktilsa_fincas/modelalimentation/modelo_FERTIAGRO_ensemble.pkl \
  --set-env-vars SCALER_ALIMENTATION_PATH_FERTIAGRO=gs://azaktilsa_fincas/scaleralimentation/scaler_FERTIAGRO.pkl \
  --set-env-vars SELECTOR_ALIMENTATION_PATH_FERTIAGRO=gs://azaktilsa_fincas/selector/selector_FERTIAGRO.pkl \
  --set-env-vars YSCALERS_ALIMENTATION_PATH_FERTIAGRO=gs://azaktilsa_fincas/yscalers/y_scalers_FERTIAGRO.pkl \
  --set-env-vars MODELO_ALIMENTATION_PATH_GROVITAL=gs://azaktilsa_fincas/modelalimentation/modelo_GROVITAL_ensemble.pkl \
  --set-env-vars SCALER_ALIMENTATION_PATH_GROVITAL=gs://azaktilsa_fincas/scaleralimentation/scaler_GROVITAL.pkl \
  --set-env-vars SELECTOR_ALIMENTATION_PATH_GROVITAL=gs://azaktilsa_fincas/selector/selector_GROVITAL.pkl \
  --set-env-vars YSCALERS_ALIMENTATION_PATH_GROVITAL=gs://azaktilsa_fincas/yscalers/y_scalers_GROVITAL.pkl \
  --set-env-vars MODELO_ALIMENTATION_PATH_SUFAAZA=gs://azaktilsa_fincas/modelalimentation/modelo_SUFAAZA_ensemble.pkl \
  --set-env-vars SCALER_ALIMENTATION_PATH_SUFAAZA=gs://azaktilsa_fincas/scaleralimentation/scaler_SUFAAZA.pkl \
  --set-env-vars SELECTOR_ALIMENTATION_PATH_SUFAAZA=gs://azaktilsa_fincas/selector/selector_SUFAAZA.pkl \
  --set-env-vars YSCALERS_ALIMENTATION_PATH_SUFAAZA=gs://azaktilsa_fincas/yscalers/y_scalers_SUFAAZA.pkl \
  --set-env-vars MODELO_ALIMENTATION_PATH_TIERRAVID=gs://azaktilsa_fincas/modelalimentation/modelo_TIERRAVID_ensemble.pkl \
  --set-env-vars SCALER_ALIMENTATION_PATH_TIERRAVID=gs://azaktilsa_fincas/scaleralimentation/scaler_TIERRAVID.pkl \
  --set-env-vars SELECTOR_ALIMENTATION_PATH_TIERRAVID=gs://azaktilsa_fincas/selector/selector_TIERRAVID.pkl \
  --set-env-vars YSCALERS_ALIMENTATION_PATH_TIERRAVID=gs://azaktilsa_fincas/yscalers/y_scalers_TIERRAVID.pkl

echo "✅ Despliegue completado"
