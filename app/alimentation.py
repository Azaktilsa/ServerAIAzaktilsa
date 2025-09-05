import pandas as pd
from typing import Dict, List, Any, Optional
import re
import math
import json
from datetime import datetime
import numpy as np
import joblib
import requests
from decouple import config
from google.cloud import storage
from fastapi import HTTPException
from pydantic import BaseModel


# Modelos de datos para FastAPI
class PredictionRequestAlimentation(BaseModel):
    # Datos principales para el modelo (requeridos)
    finca: str
    Hectareas: float
    Piscinas: int
    Fechadesiembra: str
    Fechademuestreo: str
    Edaddelcultivo: int
    Pesoanterior: float
    Pesoactualgdia: float
    Densidadbiologoindm2: float
    AcumuladoactualLBS: float
    numeroAA: int
    Aireadores: int
    Alimentoactualkg: float

    # Datos adicionales opcionales para completar cálculos
    Pesosiembra: Optional[float] = None
    Densidadatarraya: Optional[float] = None
    TipoBalanceado: Optional[str] = None
    MarcaAA: Optional[str] = None

    # Campos calculados que pueden venir precalculados desde Flutter
    Incrementogr: Optional[float] = None
    Crecimientoactualgdia: Optional[float] = None
    Pesoproyectadogdia: Optional[float] = None
    Crecimientoesperadosem: Optional[float] = None

    # Datos de control y validación
    FechaCalculada: Optional[bool] = None
    VersionApp: Optional[str] = None
    DispositivoId: Optional[str] = None


# Rutas de los archivos (modelo y scaler por finca)
modelos = {
    'CAMANOVILLO': {
        'modelo': config('MODELO_ALIMENTATION_PATH_CAMANOVILLO'),
        'scaler': config('SCALER_ALIMENTATION_PATH_CAMANOVILLO'),
        'selector': config('SELECTOR_ALIMENTATION_PATH_CAMANOVILLO'),
        'yscalers': config('YSCALERS_ALIMENTATION_PATH_CAMANOVILLO')
    },
    'EXCANCRIGRU': {
        'modelo': config('MODELO_ALIMENTATION_PATH_EXCANCRIGRU'),
        'scaler': config('SCALER_ALIMENTATION_PATH_EXCANCRIGRU'),
        'selector': config('SELECTOR_ALIMENTATION_PATH_EXCANCRIGRU'),
        'yscalers': config('YSCALERS_ALIMENTATION_PATH_EXCANCRIGRU')
    },
    'FERTIAGRO': {
        'modelo': config('MODELO_ALIMENTATION_PATH_FERTIAGRO'),
        'scaler': config('SCALER_ALIMENTATION_PATH_FERTIAGRO'),
        'selector': config('SELECTOR_ALIMENTATION_PATH_FERTIAGRO'),
        'yscalers': config('YSCALERS_ALIMENTATION_PATH_FERTIAGRO')
    },
    'GROVITAL': {
        'modelo': config('MODELO_ALIMENTATION_PATH_GROVITAL'),
        'scaler': config('SCALER_ALIMENTATION_PATH_GROVITAL'),
        'selector': config('SELECTOR_ALIMENTATION_PATH_GROVITAL'),
        'yscalers': config('YSCALERS_ALIMENTATION_PATH_GROVITAL')
    },
    'SUFAAZA': {
        'modelo': config('MODELO_ALIMENTATION_PATH_SUFAAZA'),
        'scaler': config('SCALER_ALIMENTATION_PATH_SUFAAZA'),
        'selector': config('SELECTOR_ALIMENTATION_PATH_SUFAAZA'),
        'yscalers': config('YSCALERS_ALIMENTATION_PATH_SUFAAZA')
    },
    'TIERRAVID': {
        'modelo': config('MODELO_ALIMENTATION_PATH_TIERRAVID'),
        'scaler': config('SCALER_ALIMENTATION_PATH_TIERRAVID'),
        'selector': config('SELECTOR_ALIMENTATION_PATH_TIERRAVID'),
        'yscalers': config('YSCALERS_ALIMENTATION_PATH_TIERRAVID')
    }
}


def descargar_modelo(bucket_name, source_blob_name, destination_file_name):
    """Descarga un modelo desde Google Cloud Storage"""
    # Crear el cliente de Google Cloud Storage
    storage_client = storage.Client()

    # Referenciar el bucket
    bucket = storage_client.bucket(bucket_name)

    # Referenciar el blob (archivo dentro del bucket)
    blob = bucket.blob(source_blob_name)

    # Descargar el archivo al sistema local temporalmente
    blob.download_to_filename(destination_file_name)


def cargar_modelo_y_scaler(finca):
    """Carga el modelo y scaler para una finca específica"""
    modelo_path = modelos[finca]['modelo']
    scaler_path = modelos[finca]['scaler']
    selector_path = modelos[finca]['selector']
    yscalers_path = modelos[finca]['yscalers']

    modelo_bucket_name, modelo_blob_name = modelo_path.replace(
        "gs://", "").split("/", 1)
    scaler_bucket_name, scaler_blob_name = scaler_path.replace(
        "gs://", "").split("/", 1)
    selector_bucket_name, selector_blob_name = selector_path.replace(
        "gs://", "").split("/", 1)
    yscalers_bucket_name, yscalers_blob_name = yscalers_path.replace(
        "gs://", "").split("/", 1)

    modelo_local = f"/tmp/{finca}_modelo.pkl"
    scaler_local = f"/tmp/{finca}_scaler.pkl"
    selector_local = f"/tmp/{finca}_selector.pkl"
    yscalers_local = f"/tmp/{finca}_yscalers.pkl"

    descargar_modelo(modelo_bucket_name, modelo_blob_name, modelo_local)
    descargar_modelo(scaler_bucket_name, scaler_blob_name, scaler_local)
    descargar_modelo(selector_bucket_name, selector_blob_name, selector_local)
    descargar_modelo(yscalers_bucket_name, yscalers_blob_name, yscalers_local)

    best_model = joblib.load(modelo_local)
    scaler = joblib.load(scaler_local)
    selector = joblib.load(selector_local)
    yscalers = joblib.load(yscalers_local)

    return best_model, scaler, selector, yscalers


def procesar_prediccion_alimentation(request: PredictionRequestAlimentation):
    """Procesa la predicción para alimentación basado en los parámetros"""

    try:
        # Crear calculadora con datos reales
        calculator = AquacultureCalculator()

        # Cargar datos de referencia
        calculator.fetch_data_tabla3()

        # Datos principales para el modelo (requeridos)
        input_data = {
            "Hectareas": request.Hectareas,
            "Piscinas": request.Piscinas,
            "Fechadesiembra": request.Fechadesiembra,
            "Fechademuestreo": request.Fechademuestreo,
            "Edaddelcultivo": request.Edaddelcultivo,
            "Pesoanterior": request.Pesoanterior,
            "Pesoactualgdia": request.Pesoactualgdia,
            "Densidadbiologoindm2": request.Densidadbiologoindm2,
            "AcumuladoactualLBS": request.AcumuladoactualLBS,
            "numeroAA": request.numeroAA,
            "Aireadores": request.Aireadores,
            "Alimentoactualkg": request.Alimentoactualkg,
        }

        # Datos adicionales para completar información (opcionales)
        datos_adicionales = {
            "Pesosiembra": getattr(request, 'Pesosiembra', None),
            "Densidadatarraya": getattr(request, 'Densidadatarraya', None),
            "TipoBalanceado": getattr(request, 'TipoBalanceado', None),
            "MarcaAA": getattr(request, 'MarcaAA', None),
            "Incrementogr": getattr(request, 'Incrementogr', None),
            "Crecimientoactualgdia": getattr(request, 'Crecimientoactualgdia', None),
            "Pesoproyectadogdia": getattr(request, 'Pesoproyectadogdia', None),
            "Crecimientoesperadosem": getattr(request, 'Crecimientoesperadosem', None),
            "VersionApp": getattr(request, 'VersionApp', None),
            "DispositivoId": getattr(request, 'DispositivoId', None),
        }

        # Establecer valores principales en controladores
        calculator.set_controller_value(
            'hectareas', str(input_data['Hectareas']))
        calculator.set_controller_value(
            'piscinas', str(input_data['Piscinas']))
        calculator.set_controller_value(
            'fecha_muestreo', input_data['Fechademuestreo'])
        calculator.set_controller_value(
            'fecha_siembra', input_data['Fechadesiembra'])
        calculator.set_controller_value(
            'edad_cultivo', str(input_data['Edaddelcultivo']))
        calculator.set_controller_value(
            'peso_anterior', str(input_data['Pesoanterior']))
        calculator.set_controller_value(
            'peso_actual_gdia', str(input_data['Pesoactualgdia']))
        calculator.set_controller_value(
            'densidad_biologo_indm2', str(input_data['Densidadbiologoindm2']))
        calculator.set_controller_value(
            'acumulado_actual_lbs', str(input_data['AcumuladoactualLBS']))
        calculator.set_controller_value(
            'numero_aa', str(input_data['numeroAA']))
        calculator.set_controller_value(
            'h_aireadores_mecanicos', str(input_data['Aireadores']))
        calculator.set_controller_value(
            'alimento_actual_kg', str(input_data['Alimentoactualkg']))

        # Establecer datos adicionales si están disponibles
        if datos_adicionales['Pesosiembra'] is not None:
            calculator.set_controller_value(
                'peso_siembra', str(datos_adicionales['Pesosiembra']))

        if datos_adicionales['Densidadatarraya'] is not None:
            calculator.set_controller_value(
                'densidad_atarraya', str(datos_adicionales['Densidadatarraya']))

        # Calcular todos los valores
        calculator.calcular_todos_los_valores()

        # Generar resultados finales incluyendo datos adicionales
        resultados = calculator.generar_resultados_finales_extendidos(
            input_data, datos_adicionales)

        # Realizar análisis inteligente
        analyzer = AquacultureAnalysisEngine()
        analysis = analyzer.analyze_results(resultados)

        return {
            "finca": request.finca,
            "mensaje": "Predicción de alimentación calculada exitosamente",
            "datos_enviados": {
                "principales": input_data,
                "adicionales": datos_adicionales
            },
            "resultados": resultados,
            "analisis": analysis,
            "metadatos": {
                "version_app": datos_adicionales.get('VersionApp'),
                "dispositivo_id": datos_adicionales.get('DispositivoId'),
                "timestamp": datetime.now().isoformat(),
                "campos_calculados": calculator.get_campos_calculados(),
                "validaciones": calculator.get_validaciones()
            },
            "status": "success"
        }

    except Exception as e:
        return {
            "finca": request.finca,
            "mensaje": f"Error en el cálculo de alimentación: {str(e)}",
            "error": str(e),
            "datos_recibidos": {
                "principales": input_data if 'input_data' in locals() else None,
                "adicionales": datos_adicionales if 'datos_adicionales' in locals() else None
            },
            "status": "error"
        }
        analysis = analyzer.analyze_results(resultados)

        return {
            "finca": request.finca,
            "mensaje": "Predicción de alimentación calculada exitosamente",
            "resultados": resultados,
            "analisis": analysis,
            "status": "success"
        }

    except Exception as e:
        return {
            "finca": request.finca,
            "mensaje": f"Error en el cálculo de alimentación: {str(e)}",
            "error": str(e),
            "status": "error"
        }


# --- Datos de alimentación desde configuración ---
pesos_alimento_path = str(config("PESOS_ALIMENTATION"))


def descargar_json_desde_gcs(bucket_name: str, blob_name: str) -> dict:
    """Descarga un archivo JSON desde Google Cloud Storage"""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        # Descargar el contenido como string
        json_content = blob.download_as_text()
        return json.loads(json_content)
    except Exception as e:
        print(f"Error al descargar JSON desde GCS: {e}")
        return {}


def cargar_pesos_alimento():
    """Carga el archivo pesos_alimento desde Google Cloud Storage"""
    try:
        # Extraer bucket y blob del path GCS
        if pesos_alimento_path.startswith("gs://"):
            bucket_name, blob_name = pesos_alimento_path.replace(
                "gs://", "").split("/", 1)
            return descargar_json_desde_gcs(bucket_name, blob_name)
        else:
            # Fallback para rutas locales (desarrollo)
            with open(pesos_alimento_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error al cargar pesos_alimento: {e}")
        # Datos de respaldo
        return {
            "rows": [
                {"Pesos": 10, "BWCosechas": 1.5},
                {"Pesos": 15, "BWCosechas": 2.0},
                {"Pesos": 20, "BWCosechas": 2.5},
                {"Pesos": 25, "BWCosechas": 3.0},
                {"Pesos": 30, "BWCosechas": 3.5}
            ]
        }


class AquacultureModel:
    """Modelo para almacenar datos de acuicultura"""

    def __init__(self):
        self.piscinas_options_camanovillo: List[str] = []
        self.camanovillo_data: List[Dict[str, Any]] = []
        self.rendimiento_data: List[Dict[str, Any]] = []
        self.referencia_tabla: Dict[float, float] = {}
        self.selected_finca: Optional[str] = "CAMANOVILLO"
        self.selected_hectareas: Optional[str] = None
        self.selected_tipo_balanceado: Optional[str] = None
        self.selected_marca_aa: Optional[str] = None
        self.selected_hect_pisc: Optional[str] = None
        self.show_results: bool = False

    def update_piscinas_data(self, data):
        self.camanovillo_data = data
        self.piscinas_options_camanovillo = [
            str(item.get('Piscinas', '')) for item in data]

    def update_rendimiento_data(self, data):
        self.rendimiento_data = data

    def update_referencia_tabla(self, data):
        self.referencia_tabla = data


class AquacultureAnalysisEngine:
    """Motor de análisis inteligente para resultados de acuicultura"""

    def __init__(self, config_path: str = None):
        # Umbrales y reglas por defecto (pueden cargarse desde un archivo JSON)
        self.thresholds = {
            'growth_rate': {
                'low': 0.5,
                'optimal': 1.0,
                'high': 1.5
            },
            'fca': {
                'optimal_min': 0.8,
                'optimal_max': 1.2
            },
            'density_difference': {
                'acceptable': 15.0  # Porcentaje
            },
            'aeration_capacity': {
                'warning': 0.8,  # 80% de capacidad
                'critical': 0.9  # 90% de capacidad
            },
            'feed_ratio': {
                'optimal': 1.5  # % del peso corporal
            }
        }

        # Cargar configuración personalizada si se proporciona
        if config_path:
            self.load_configuration(config_path)

    def load_configuration(self, config_path: str):
        """Carga configuración desde un archivo JSON"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
                self.thresholds.update(custom_config.get('thresholds', {}))
        except Exception as e:
            print(f"Error al cargar configuración: {e}")

    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Analiza los resultados y genera explicaciones detalladas

        Args:
            results: Diccionario con todos los resultados del cálculo

        Returns:
            Diccionario con problemas identificados y recomendaciones
        """
        analysis = {
            'problems': [],
            'recommendations': [],
            'observations': []
        }

        # Convertir valores a float para comparaciones
        parsed_results = self._parse_results(results)

        # Ejecutar todos los análisis
        self._analyze_growth(parsed_results, analysis)
        self._analyze_fca(parsed_results, analysis)
        self._analyze_density(parsed_results, analysis)
        self._analyze_aeration(parsed_results, analysis)
        self._analyze_feeding(parsed_results, analysis)
        self._analyze_biomass(parsed_results, analysis)
        self._analyze_environmental(parsed_results, analysis)

        return analysis

    def _parse_results(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Convierte los resultados a valores numéricos para análisis"""
        parsed = {}
        for key, value in results.items():
            if isinstance(value, str):
                # Eliminar comas y convertir a float
                cleaned = value.replace(',', '').strip()
                try:
                    parsed[key] = float(cleaned) if cleaned else 0.0
                except ValueError:
                    parsed[key] = 0.0
            else:
                parsed[key] = float(value)
        return parsed

    def _analyze_growth(self, results: Dict[str, float], analysis: Dict[str, List[str]]):
        """Analiza las métricas de crecimiento"""
        growth_rate = results.get('crecim_actual_gdia', 0)
        current_weight = results.get('peso_actual_gdia', 0)
        age = results.get('edad_cultivo', 0)

        if growth_rate < self.thresholds['growth_rate']['low']:
            analysis['problems'].append(
                f"CRECIMIENTO LENTO ({growth_rate:.2f} g/día):\n"
                f"El crecimiento actual está por debajo del umbral mínimo esperado ({self.thresholds['growth_rate']['low']} g/día). "
                f"Esto puede deberse a múltiples factores:\n"
                f"- Temperatura del agua subóptima (ideal: 28-30°C)\n"
                f"- Niveles de oxígeno disuelto insuficientes (<4 mg/L)\n"
                f"- Calidad nutricional del alimento inadecuada\n"
                f"- Estrés por manejo, enfermedades o parásitos\n"
                f"- Densidad de siembra demasiado alta\n\n"
                f"El peso actual es de {current_weight:.2f} g a los {age:.0f} días, lo que representa un crecimiento "
                f"más lento de lo esperado para esta etapa."
            )

            analysis['recommendations'].append(
                f"MEJORAR TASA DE CRECIMIENTO:\n"
                f"1. Verificar y ajustar temperatura del agua (óptima: 28-30°C)\n"
                f"2. Aumentar oxigenación (mantener >5 mg/L)\n"
                f"3. Revisar calidad del alimento (proteína >35%, lípidos <10%)\n"
                f"4. Realizar muestreo de salud para descartar enfermedades\n"
                f"5. Considerar ajustar densidad si es demasiado alta\n"
                f"6. Implementar protocolos de alimentación con bandejas para monitorear consumo real"
            )

        elif growth_rate > self.thresholds['growth_rate']['high']:
            analysis['observations'].append(
                f"CRECIMIENTO ACELERADO ({growth_rate:.2f} g/día):\n"
                f"La tasa de crecimiento es superior al rango esperado. Esto puede ser positivo pero requiere monitorización "
                f"para asegurar que no hay estrés metabólico o problemas de calidad de agua."
            )

    def _analyze_fca(self, results: Dict[str, float], analysis: Dict[str, List[str]]):
        """Analiza los factores de conversión alimenticia"""
        fca_campo = results.get('fca_campo', 0)
        fca_consumo = results.get('fca_consumo', 0)
        acumulado_lbs = results.get('acumulado_actual_lbs', 0)
        libras_totales = results.get('libras_totales_campo', 0)

        # Análisis de FCA campo
        if fca_campo < self.thresholds['fca']['optimal_min']:
            analysis['observations'].append(
                f"FCA CAMPO EXCELENTE ({fca_campo:.2f}):\n"
                f"El factor de conversión alimenticia calculado por el método de campo es excelente, "
                f"indicando una alta eficiencia en la conversión del alimento a biomasa."
            )
        elif fca_campo > self.thresholds['fca']['optimal_max']:
            analysis['problems'].append(
                f"FCA CAMPO ELEVADO ({fca_campo:.2f}):\n"
                f"El factor de conversión alimenticia por campo está por encima del rango óptimo "
                f"({self.thresholds['fca']['optimal_min']}-{self.thresholds['fca']['optimal_max']}). "
                f"Esto indica ineficiencia en la conversión del alimento, que puede deberse a:\n"
                f"- Sobrealimentación\n"
                f"- Pérdida de alimento (no consumido)\n"
                f"- Condiciones ambientales subóptimas\n"
                f"- Estrés en los organismos\n\n"
                f"Se han utilizado {acumulado_lbs:.0f} lbs de alimento para producir {libras_totales:.0f} lbs de biomasa."
            )

            analysis['recommendations'].append(
                f"OPTIMIZAR FCA CAMPO:\n"
                f"1. Ajustar ración alimenticia (reducir 5-10% y monitorizar consumo)\n"
                f"2. Implementar bandejas de alimentación para verificar consumo real\n"
                f"3. Verificar calidad del alimento y condiciones de almacenamiento\n"
                f"4. Revisar parámetros de calidad de agua (oxígeno, temperatura, amonio)"
            )

        # Análisis de FCA consumo
        if fca_consumo > self.thresholds['fca']['optimal_max']:
            analysis['problems'].append(
                f"FCA CONSUMO ELEVADO ({fca_consumo:.2f}):\n"
                f"El factor de conversión alimenticia por consumo está por encima del rango óptimo, "
                f"lo que sugiere que el alimento no se está convirtiendo eficientemente en biomasa. "
                f"Posibles causas:\n"
                f"- Método de cálculo de densidad por consumo inexacto\n"
                f"- Pérdidas significativas de alimento\n"
                f"- Condiciones ambientales que afectan el metabolismo\n"
                f"- Problemas de salud en la población"
            )

    def _analyze_density(self, results: Dict[str, float], analysis: Dict[str, List[str]]):
        """Analiza las densidades y sus diferencias"""
        densidad_biologo = results.get('densidad_biologo_indm2', 0)
        densidad_consumo = results.get('densidad_consumo_im2', 0)
        diferencia = results.get('diferencia_campo_biologo', 0)

        if abs(diferencia) > self.thresholds['density_difference']['acceptable']:
            analysis['problems'].append(
                f"DIFERENCIA SIGNIFICATIVA ENTRE DENSIDADES ({diferencia:.0f}%):\n"
                f"Existe una discrepancia importante entre la densidad estimada por el biólogo "
                f"({densidad_biologo:.2f} ind/m²) y la calculada por consumo ({densidad_consumo:.2f} ind/m²).\n\n"
                f"Posibles causas:\n"
                f"1. Error en el muestreo biológico (subestimación o sobrestimación)\n"
                f"2. Cálculo incorrecto de la biomasa por consumo\n"
                f"3. Distribución desigual de la población en el estanque\n"
                f"4. Mortalidad no contabilizada\n"
                f"5. Alimento no consumido que afecta el cálculo por consumo"
            )

            analysis['recommendations'].append(
                f"VALIDAR DENSIDADES:\n"
                f"1. Realizar un nuevo muestreo biológico con metodología estandarizada\n"
                f"2. Verificar los cálculos de alimento consumido y conversión\n"
                f"3. Considerar realizar un conteo directo en áreas representativas\n"
                f"4. Revisar la uniformidad de distribución del alimento\n"
                f"5. Evaluar posibles mortalidades no registradas"
            )

    def _analyze_aeration(self, results: Dict[str, float], analysis: Dict[str, List[str]]):
        """Analiza la capacidad de aireación"""
        libras_totales = results.get('libras_totales_campo', 0)
        capacidad_carga = results.get('capacidad_carga_aireaccion', 0)
        num_aireadores = results.get('h_aireadores_mecanicos', 0)
        hectareas = results.get('hectareas', 0)

        if capacidad_carga > 0:
            ratio_carga = libras_totales / capacidad_carga

            if ratio_carga > self.thresholds['aeration_capacity']['critical']:
                analysis['problems'].append(
                    f"CAPACIDAD DE AIREACIÓN CRÍTICA ({ratio_carga*100:.1f}%):\n"
                    f"La biomasa actual ({libras_totales:.0f} lbs) está utilizando el {ratio_carga*100:.1f}% "
                    f"de la capacidad de aireación disponible ({capacidad_carga:.0f} lbs).\n\n"
                    f"Esto representa un riesgo significativo para la oxigenación del agua, especialmente "
                    f"durante la noche cuando disminuye la producción de oxígeno por fotosíntesis.\n\n"
                    f"Con {num_aireadores:.0f} aireadores en {hectareas:.2f} ha, la relación actual es de "
                    f"{num_aireadores/hectareas:.2f} aireadores por hectárea."
                )

                analysis['recommendations'].append(
                    f"MEJORAR CAPACIDAD DE AIREACIÓN:\n"
                    f"1. Añadir aireadores adicionales inmediatamente (ideal: 1-1.5 por hectárea)\n"
                    f"2. Optimizar la distribución de los aireadores existentes\n"
                    f"3. Implementar monitoreo continuo de oxígeno disuelto\n"
                    f"4. Considerar reducir la biomasa mediante cosecha parcial\n"
                    f"5. Revisar el mantenimiento y funcionamiento de los aireadores actuales"
                )

            elif ratio_carga > self.thresholds['aeration_capacity']['warning']:
                analysis['observations'].append(
                    f"CAPACIDAD DE AIREACIÓN ALERTA ({ratio_carga*100:.1f}%):\n"
                    f"La biomasa está utilizando el {ratio_carga*100:.1f}% de la capacidad de aireación. "
                    f"Se recomienda monitorizar estrechamente los niveles de oxígeno, especialmente en horas de la madrugada."
                )

    def _analyze_feeding(self, results: Dict[str, float], analysis: Dict[str, List[str]]):
        """Analiza las prácticas de alimentación"""
        alimento_actual = results.get('alimento_actual_kg', 0)
        libras_totales = results.get('libras_totales_campo', 0)
        peso_actual = results.get('peso_actual_gdia', 0)
        densidad = results.get('densidad_biologo_indm2', 0)
        hectareas = results.get('hectareas', 0)

        # Calcular porcentaje de alimentación respecto a biomasa
        if libras_totales > 0:
            biomasa_kg = libras_totales * 0.453592  # Convertir lbs a kg
            feed_ratio = (alimento_actual / biomasa_kg) * \
                100 if biomasa_kg > 0 else 0

            if feed_ratio > self.thresholds['feed_ratio']['optimal'] * 1.2:
                analysis['problems'].append(
                    f"SOBREALIMENTACIÓN DETECTADA ({feed_ratio:.1f}% de biomasa):\n"
                    f"La ración alimenticia actual representa el {feed_ratio:.1f}% de la biomasa estimada, "
                    f"lo que excede el rango recomendado (1-3% dependiendo del tamaño de los organismos).\n\n"
                    f"Para organismos de {peso_actual:.1f} g, la ración debería estar alrededor del "
                    f"{self.thresholds['feed_ratio']['optimal']}% de la biomasa.\n\n"
                    f"La sobrealimentación puede causar:\n"
                    f"- Deterioro de la calidad del agua\n"
                    f"- Aumento del FCA y costos de producción\n"
                    f"- Problemas de salud en los organismos"
                )

                analysis['recommendations'].append(
                    f"AJUSTAR ALIMENTACIÓN:\n"
                    f"1. Reducir la ración al {self.thresholds['feed_ratio']['optimal']}% de la biomasa estimada\n"
                    f"2. Implementar protocolos de alimentación con bandejas de consumo\n"
                    f"3. Ajustar frecuencia de alimentación (4-5 veces/día)\n"
                    f"4. Monitorizar consumo real y ajustar según necesidad"
                )

    def _analyze_biomass(self, results: Dict[str, float], analysis: Dict[str, List[str]]):
        """Analiza las estimaciones de biomasa"""
        biomass_campo = results.get('libras_totales_campo', 0)
        biomass_consumo = results.get('libras_totales_consumo', 0)

        if biomass_campo > 0 and biomass_consumo > 0:
            diferencia = abs(biomass_campo - biomass_consumo) / \
                biomass_campo * 100

            if diferencia > 20:
                analysis['problems'].append(
                    f"DISCREPANCIA EN ESTIMACIONES DE BIOMASA ({diferencia:.1f}%):\n"
                    f"Existe una diferencia significativa entre la biomasa estimada por campo "
                    f"({biomass_campo:.0f} lbs) y la calculada por consumo ({biomass_consumo:.0f} lbs).\n\n"
                    f"Esta discrepancia indica posibles problemas en:\n"
                    f"1. Exactitud del muestreo biológico\n"
                    f"2. Cálculo de la conversión alimenticia\n"
                    f"3. Estimación de la densidad poblacional\n"
                    f"4. Registro del alimento suministrado\n\n"
                    f"Es fundamental resolver esta discrepancia para una gestión adecuada."
                )

    def _analyze_environmental(self, results: Dict[str, float], analysis: Dict[str, List[str]]):
        """Genera observaciones generales sobre condiciones ambientales"""
        crecimiento = results.get('crecim_actual_gdia', 0)
        fca = results.get('fca_campo', 0)

        if crecimiento < self.thresholds['growth_rate']['low'] and fca > self.thresholds['fca']['optimal_max']:
            analysis['observations'].append(
                "PATRÓN DE CRECIMIENTO LENTO CON FCA ELEVADO:\n"
                "La combinación de crecimiento lento y FCA elevado sugiere fuertemente "
                "problemas ambientales o de salud que están afectando el metabolismo y "
                "la conversión alimenticia. Se recomienda realizar urgentemente:\n"
                "1. Análisis completo de calidad de agua (oxígeno, amonio, nitritos, pH, alcalinidad)\n"
                "2. Evaluación de salud de los organismos (branquias, hepatopáncreas, apéndices)\n"
                "3. Revisión del sistema de aireación y circulación de agua"
            )

    def generate_report(self, analysis: Dict[str, List[str]]) -> str:
        """Genera un reporte formateado a partir del análisis"""
        report = []

        if analysis['problems']:
            report.append("🚨 **PROBLEMAS IDENTIFICADOS:**")
            for i, problem in enumerate(analysis['problems'], 1):
                report.append(f"{i}. {problem}")

        if analysis['recommendations']:
            report.append("\n✅ **RECOMENDACIONES OPERATIVAS:**")
            for i, recommendation in enumerate(analysis['recommendations'], 1):
                report.append(f"{i}. {recommendation}")

        if analysis['observations']:
            report.append("\n🔍 **OBSERVACIONES:**")
            for i, observation in enumerate(analysis['observations'], 1):
                report.append(f"{i}. {observation}")

        return "\n\n".join(report)


class AquacultureCalculator:
    def __init__(self):
        self.controllers = {}
        self.on_state_changed = None
        self.model = AquacultureModel()
        # Cargar pesos desde configuración
        self.pesos_alimento_data = cargar_pesos_alimento()

    def get_controller_value(self, key: str) -> str:
        """Obtiene el valor de un controlador"""
        return self.controllers.get(key, '')

    def set_controller_value(self, key: str, value: str):
        """Establece el valor de un controlador"""
        self.controllers[key] = value
        if self.on_state_changed:
            self.on_state_changed()

    def parse_formatted_number(self, value_str: str) -> float:
        """Convierte una cadena formateada a número float"""
        if not value_str or value_str == '':
            return 0.0
        try:
            # Eliminar comas y convertir a float
            return float(value_str.replace(',', ''))
        except ValueError:
            return 0.0

    def format_number(self, value: float) -> str:
        """Formatea un número para mostrar"""
        return f"{value:,.2f}"

    def calcular_sacos_actuales(self):
        """Calcula los sacos actuales"""
        alimento_kg = self.parse_formatted_number(
            self.get_controller_value('alimento_actual_kg'))
        sacos = alimento_kg / 25
        self.set_controller_value('sacos_actuales', f"{sacos:.2f}")

    def calcular_edad_cultivo(self):
        """Calcula la edad del cultivo"""
        try:
            fecha_siembra_str = self.get_controller_value(
                'fecha_siembra').strip()
            fecha_muestreo_str = self.get_controller_value(
                'fecha_muestreo').strip()

            if not fecha_siembra_str or not fecha_muestreo_str:
                print("⚠️ Error: Una o ambas fechas están vacías.")
                return

            fecha_siembra = datetime.strptime(fecha_siembra_str, '%d/%m/%Y')
            fecha_muestreo = datetime.strptime(fecha_muestreo_str, '%d/%m/%Y')

            diferencia_dias = (fecha_muestreo - fecha_siembra).days

            if diferencia_dias < 0:
                print(
                    "⚠️ Error: La fecha de muestreo no puede ser anterior a la de siembra.")
                return

            mas_uno = diferencia_dias + 1
            self.set_controller_value('edad_cultivo', str(mas_uno))

            self.calcular_crecimiento_actual()
        except Exception as e:
            print(f'⚠️ Error en el cálculo de la edad del cultivo: {e}')

    def incremento_gr(self):
        """Calcula el incremento en gramos"""
        peso_actual = self.parse_formatted_number(
            self.get_controller_value('peso_actual_gdia'))
        peso_anterior = self.parse_formatted_number(
            self.get_controller_value('peso_anterior'))

        if peso_anterior == 0:
            self.set_controller_value('incremento_gr', "0.00")
            return

        incremento = peso_actual - peso_anterior
        self.set_controller_value('incremento_gr', f"{incremento:.2f}")

    def validar_y_actualizar_fecha(self, controller_key: str):
        """Valida y actualiza una fecha"""
        input_text = self.get_controller_value(controller_key).strip()
        if re.match(r'^\d{2}/\d{2}/\d{4}$', input_text):
            try:
                parsed_date = datetime.strptime(input_text, '%d/%m/%Y')
                self.set_controller_value(
                    controller_key, parsed_date.strftime('%d/%m/%Y'))
                self.calcular_edad_cultivo()
            except ValueError as e:
                print(f"Fecha inválida: {e}")

    def fetch_data(self):
        """Obtiene datos desde Terrain.json - Esta función requiere datos locales"""
        try:
            # TODO: Migrar datos de Terrain.json a Google Cloud Storage
            # Por ahora se usan datos de ejemplo
            print("⚠️ fetch_data: Usando datos de ejemplo - "
                  "migrar Terrain.json a GCS")

            # Datos de ejemplo para CAMANOVILLO
            camanovillo_data = [
                {'Piscinas': '1', 'Hectareas': '2.5'},
                {'Piscinas': '2', 'Hectareas': '3.0'},
                {'Piscinas': '3', 'Hectareas': '1.8'},
                {'Piscinas': '4', 'Hectareas': '2.2'},
                {'Piscinas': '5', 'Hectareas': '2.8'},
            ]

            rendimiento_data = [
                {'Rendimiento': '1500', 'Tipo': 'Alto'},
                {'Rendimiento': '1200', 'Tipo': 'Medio'},
                {'Rendimiento': '900', 'Tipo': 'Bajo'},
            ]

            self.model.update_piscinas_data(camanovillo_data)
            self.model.update_rendimiento_data(rendimiento_data)

            if self.model.piscinas_options_camanovillo:
                self.update_hectareas_for_piscina(
                    self.model.piscinas_options_camanovillo[0])

            self.calcular_recomendation_semana()
            print(f"✅ Datos de ejemplo cargados: "
                  f"{len(camanovillo_data)} piscinas CAMANOVILLO")
        except Exception as e:
            print(f'⚠️ Error al cargar datos: {e}')

    def fetch_data_tabla3(self):
        """Obtiene datos de la tabla 3 desde configuración"""
        try:
            referencia_tabla = {}

            if 'rows' in self.pesos_alimento_data and isinstance(
                    self.pesos_alimento_data['rows'], list):
                for row in self.pesos_alimento_data['rows']:
                    if 'Pesos' in row and 'BWCosechas' in row:
                        peso = float(row['Pesos'])
                        bw_cosechas_str = str(
                            row['BWCosechas']).replace('%', '').strip()
                        bw_cosechas = float(bw_cosechas_str)
                        referencia_tabla[peso] = bw_cosechas

            self.model.update_referencia_tabla(referencia_tabla)
            print(
                f"✅ Tabla de pesos cargada con "
                f"{len(referencia_tabla)} entradas")

        except Exception as e:
            print(f'⚠️ Error al cargar datos de tabla 3: {e}')
            self.model.update_referencia_tabla({})

    def update_hectareas_for_piscina(self, piscina: str):
        """Actualiza las hectáreas para una piscina"""
        matching_piscina = None
        for element in self.model.camanovillo_data:
            if str(element.get('Piscinas', '')) == piscina:
                matching_piscina = element
                break

        if matching_piscina:
            self.model.selected_hectareas = str(
                matching_piscina.get('Hectareas', ''))
            self.set_controller_value(
                'hectareas', self.model.selected_hectareas)
        else:
            self.model.selected_hectareas = None
            self.set_controller_value('hectareas', '')

    def calcular_crecimiento_actual(self):
        """Calcula el crecimiento actual"""
        peso_actual = self.parse_formatted_number(
            self.get_controller_value('peso_actual_gdia'))
        peso_siembra = self.parse_formatted_number(
            self.get_controller_value('peso_siembra'))
        edad_cultivo = int(self.get_controller_value('edad_cultivo') or '0')

        if edad_cultivo == 0:
            self.set_controller_value('crecim_actual_gdia', "0.00")
            return

        crecimiento = (peso_actual - peso_siembra) / edad_cultivo
        self.set_controller_value('crecim_actual_gdia', f"{crecimiento:.2f}")
        self.calcular_peso_proyectado(peso_actual)

    def calcular_peso_proyectado(self, peso_actual: float):
        """Calcula el peso proyectado"""
        incremento = 0

        if 0.001 < peso_actual < 7:
            incremento = 2.5
        elif 7 <= peso_actual < 11:
            incremento = 3
        elif peso_actual >= 11:
            incremento = 3

        peso_proyectado = peso_actual + incremento
        self.set_controller_value(
            'peso_proyectado_gdia', f"{peso_proyectado:.2f}")
        self.calcular_crecimiento_esperado(peso_proyectado)

    # --- Función calcular_densidad_consumo corregida ---
    def calcular_densidad_consumo(self):
        """Calcula la densidad de consumo"""
        try:
            alimento_actual_kg = self.parse_formatted_number(
                self.get_controller_value('alimento_actual_kg'))
            hectareas = self.parse_formatted_number(
                self.get_controller_value('hectareas'))
            peso_actual_g = self.parse_formatted_number(
                self.get_controller_value('peso_actual_gdia'))

            if hectareas == 0 or peso_actual_g == 0:
                self.set_controller_value(
                    'densidad_consumo_im2', "Datos inválidos")
                return

            if not self.model.referencia_tabla:
                self.set_controller_value(
                    'densidad_consumo_im2', "No hay datos")
                return

            peso_encontrado = 0.0
            bw_cosechas = 0.0

            # Buscar el peso más cercano (menor o igual)
            for peso, bw_value in self.model.referencia_tabla.items():
                if peso <= peso_actual_g and peso > peso_encontrado:
                    peso_encontrado = peso
                    bw_cosechas = bw_value

            # Usar bw_cosechas directamente como decimal (ya viene sin %)
            bw_cosechas_decimal = bw_cosechas

            if bw_cosechas_decimal == 0:
                self.set_controller_value(
                    'densidad_consumo_im2', "BWCosechas inválido")
                return

            densidad_consumo = (alimento_actual_kg / hectareas) * \
                10 / (peso_actual_g * bw_cosechas_decimal)
            self.set_controller_value(
                'densidad_consumo_im2', f"{densidad_consumo:.2f}")

        except Exception as e:
            print(f"Error al calcular densidad: {e}")
            self.set_controller_value('densidad_consumo_im2', "Error")

    def diferencia_campo_biologo(self):
        """Calcula la diferencia entre campo y biólogo"""
        consumo_text = self.get_controller_value(
            'densidad_consumo_im2').strip()
        biologo_text = self.get_controller_value(
            'densidad_biologo_indm2').strip()

        try:
            densidad_consumo = float(consumo_text)
            densidad_biologo = float(biologo_text)

            if densidad_biologo != 0:
                diferencia = ((densidad_consumo / densidad_biologo) - 1) * 100
                porcentaje = round(diferencia)
                self.set_controller_value(
                    'diferencia_campo_biologo', str(porcentaje))
            else:
                self.set_controller_value('diferencia_campo_biologo', "0")
        except (ValueError, TypeError):
            self.set_controller_value('diferencia_campo_biologo', "0")

    def calcular_crecimiento_esperado(self, peso_proyectado: float):
        """Calcula el crecimiento esperado"""
        try:
            peso_proyectado_val = self.parse_formatted_number(
                self.get_controller_value('peso_proyectado_gdia'))
            peso_actual_campo = self.parse_formatted_number(
                self.get_controller_value('peso_actual_gdia'))

            if peso_proyectado_val and peso_actual_campo:
                crecimiento_esperado = peso_proyectado_val - peso_actual_campo
                self.set_controller_value(
                    'crecimiento_esperado_sem', f"{crecimiento_esperado:.2f}")
            else:
                self.set_controller_value('crecimiento_esperado_sem', "0.00")
        except Exception as e:
            print(f'⚠️ Error al calcular el crecimiento esperado: {e}')
            self.set_controller_value('crecimiento_esperado_sem', "0.00")

    def calcular_kg_100mil(self):
        """Calcula kg por 100 mil"""
        alimento_kg = self.parse_formatted_number(
            self.get_controller_value('alimento_actual_kg'))
        hect = self.parse_formatted_number(
            self.get_controller_value('hectareas'))
        densidad_consumo = self.parse_formatted_number(
            self.get_controller_value('densidad_consumo_im2'))

        if hect == 0 or densidad_consumo == 0:
            self.set_controller_value('kg_100mil', "0.00")
            return

        kg_100mil = (alimento_kg / hect) / densidad_consumo * 10
        self.set_controller_value('kg_100mil', f"{kg_100mil:.2f}")

    # Métodos de cálculo para días de la semana

    def _calcular_logic(self, peso_project: float, hectareaje: float, densidad_biologo: float) -> float:
        """Lógica compartida para cálculos de días de la semana"""
        # Buscar el valor de 'BWCosechas' (VLOOKUP)
        peso_encontrado = 0.0
        bw_cosechas = 0.0

        for peso, bw_value in self.model.referencia_tabla.items():
            if peso <= peso_project and peso > peso_encontrado:
                peso_encontrado = peso
                bw_cosechas = bw_value

        if peso_encontrado == 0.0:
            raise Exception(
                "No se encontró un peso que coincida en la tabla de búsqueda.")

        if bw_cosechas == 0:
            raise Exception("Se encontró un valor 'BWCosechas' inválido.")

        # Dividir por 100 como en Dart: bwCosechasDecimal /= 100;
        bw_cosechas_decimal = bw_cosechas / 100

        # Realizar el cálculo principal
        result = ((peso_project / 1000) * ((densidad_biologo * 10000)
                                           * hectareaje)) * bw_cosechas_decimal

        # Aplicar el redondeo de "piso" (floor) como en Excel
        final_result = math.floor(result / 25) * 25

        return float(final_result)

    def calcular_lunes_dia1(self):
        """Calcula el valor para lunes día 1"""
        try:
            peso_actual_g = self.parse_formatted_number(
                self.get_controller_value('peso_actual_gdia'))
            hectareaje = self.parse_formatted_number(
                self.get_controller_value('hectareas'))
            densidad_biologo = self.parse_formatted_number(
                self.get_controller_value('densidad_biologo_indm2'))

            if peso_actual_g == 0 or hectareaje == 0 or densidad_biologo == 0:
                self.set_controller_value('lunes_dia1', "Datos inválidos")
                return

            if not self.model.referencia_tabla:
                self.set_controller_value('lunes_dia1', "No hay datos")
                return

            peso_encontrado = 0.0
            bw_cosechas = 0.0

            for peso, bw_value in self.model.referencia_tabla.items():
                if peso <= peso_actual_g and peso > peso_encontrado:
                    peso_encontrado = peso
                    bw_cosechas = bw_value

            bw_cosechas_decimal = bw_cosechas / 100

            if bw_cosechas_decimal == 0:
                self.set_controller_value('lunes_dia1', "BWCosechas inválido")
                return

            lunes_dia1 = ((peso_actual_g / 1000) * ((densidad_biologo *
                          10000) * hectareaje)) * bw_cosechas_decimal
            resultado_redondeado = round(lunes_dia1 / 25) * 25

            result_str = "25" if math.isnan(lunes_dia1) or math.isinf(
                lunes_dia1) else str(resultado_redondeado)
            self.set_controller_value('lunes_dia1', result_str)

        except Exception as e:
            print(f"Error al calcular LunesDia1: {e}")
            self.set_controller_value('lunes_dia1', "Error")

    def calcular_domingo_dia7(self):
        """Calcula el valor para domingo día 7"""
        try:
            peso_project = self.parse_formatted_number(
                self.get_controller_value('peso_proyectado_gdia'))
            hectareaje = self.parse_formatted_number(
                self.get_controller_value('hectareas'))
            densidad_biologo = self.parse_formatted_number(
                self.get_controller_value('densidad_biologo_indm2'))

            if not peso_project or not hectareaje or not densidad_biologo or peso_project <= 0 or hectareaje <= 0 or densidad_biologo <= 0:
                self.set_controller_value('domingo_dia7', "Datos inválidos")
                return

            if not self.model.referencia_tabla:
                self.set_controller_value('domingo_dia7', "No hay datos")
                return

            resultado = self._calcular_logic(
                peso_project, hectareaje, densidad_biologo)
            self.set_controller_value('domingo_dia7', str(int(resultado)))

        except Exception as e:
            print(f"Error al calcular DomingoDia7: {e}")
            self.set_controller_value('domingo_dia7', "Error")

    def calcular_martes_dia2(self):
        """Calcula martes día 2"""
        try:
            lunes_dia1c = self.parse_formatted_number(
                self.get_controller_value('lunes_dia1'))
            domingo_dia7c = self.parse_formatted_number(
                self.get_controller_value('domingo_dia7'))

            incremento_diario = (domingo_dia7c - lunes_dia1c) / 6
            martes_dia2c = lunes_dia1c + incremento_diario
            resultado_redondeado = int(round(martes_dia2c / 25)) * 25

            self.set_controller_value('martes_dia2', str(resultado_redondeado))
        except Exception:
            self.set_controller_value('martes_dia2', "Error")

    def calcular_miercoles_dia3(self):
        """Calcula miércoles día 3"""
        try:
            lunes_dia1c = self.parse_formatted_number(
                self.get_controller_value('lunes_dia1'))
            domingo_dia7c = self.parse_formatted_number(
                self.get_controller_value('domingo_dia7'))

            incremento_diario = (domingo_dia7c - lunes_dia1c) / 6 * 2
            miercoles_dia3c = lunes_dia1c + incremento_diario
            resultado_redondeado = int(round(miercoles_dia3c / 25)) * 25

            self.set_controller_value(
                'miercoles_dia3', str(resultado_redondeado))
        except Exception:
            self.set_controller_value('miercoles_dia3', "Error")

    def calcular_jueves_dia4(self):
        """Calcula jueves día 4"""
        try:
            lunes_dia1c = self.parse_formatted_number(
                self.get_controller_value('lunes_dia1'))
            domingo_dia7c = self.parse_formatted_number(
                self.get_controller_value('domingo_dia7'))

            incremento_diario = (domingo_dia7c - lunes_dia1c) / 6 * 3
            jueves_dia4c = lunes_dia1c + incremento_diario
            resultado_redondeado = int(round(jueves_dia4c / 25)) * 25

            self.set_controller_value('jueves_dia4', str(resultado_redondeado))
        except Exception:
            self.set_controller_value('jueves_dia4', "Error")

    def calcular_viernes_dia5(self):
        """Calcula viernes día 5"""
        try:
            lunes_dia1c = self.parse_formatted_number(
                self.get_controller_value('lunes_dia1'))
            domingo_dia7c = self.parse_formatted_number(
                self.get_controller_value('domingo_dia7'))

            incremento_diario = (domingo_dia7c - lunes_dia1c) / 6 * 4
            viernes_dia5c = lunes_dia1c + incremento_diario
            resultado_redondeado = int(round(viernes_dia5c / 25)) * 25

            self.set_controller_value(
                'viernes_dia5', str(resultado_redondeado))
        except Exception:
            self.set_controller_value('viernes_dia5', "Error")

    def calcular_sabado_dia6(self):
        """Calcula sábado día 6"""
        try:
            lunes_dia1c = self.parse_formatted_number(
                self.get_controller_value('lunes_dia1'))
            domingo_dia7c = self.parse_formatted_number(
                self.get_controller_value('domingo_dia7'))

            incremento_diario = (domingo_dia7c - lunes_dia1c) / 6 * 5
            sabado_dia6c = lunes_dia1c + incremento_diario
            resultado_redondeado = int(round(sabado_dia6c / 25)) * 25

            self.set_controller_value('sabado_dia6', str(resultado_redondeado))
        except Exception:
            self.set_controller_value('sabado_dia6', "Error")

    def calcular_recomendation_semana(self):
        """Calcula la recomendación semanal"""
        try:
            lunes_dia1c = self.parse_formatted_number(
                self.get_controller_value('lunes_dia1'))
            martes_dia2c = self.parse_formatted_number(
                self.get_controller_value('martes_dia2'))
            miercoles_dia3c = self.parse_formatted_number(
                self.get_controller_value('miercoles_dia3'))
            jueves_dia4c = self.parse_formatted_number(
                self.get_controller_value('jueves_dia4'))
            viernes_dia5c = self.parse_formatted_number(
                self.get_controller_value('viernes_dia5'))
            sabado_dia6c = self.parse_formatted_number(
                self.get_controller_value('sabado_dia6'))
            domingo_dia7c = self.parse_formatted_number(
                self.get_controller_value('domingo_dia7'))

            suma = lunes_dia1c + martes_dia2c + miercoles_dia3c + \
                jueves_dia4c + viernes_dia5c + sabado_dia6c + domingo_dia7c
            recomendation_semana = suma / 7

            self.set_controller_value(
                'recomendation_semana', f"{recomendation_semana:.2f}")
        except Exception:
            self.set_controller_value('recomendation_semana', "Error")

    def calcular_acumulado_semanal(self):
        """Calcula el acumulado semanal"""
        try:
            recomendation_semanal = self.parse_formatted_number(
                self.get_controller_value('recomendation_semana'))
            acumulado_semanal = recomendation_semanal * 7

            self.set_controller_value(
                'acumulado_semanal', f"{acumulado_semanal:.2f}")
        except Exception:
            self.set_controller_value('acumulado_semanal', "Error")

    def calcular_aireadores_diesel(self):
        """Calcula aireadores diesel"""
        try:
            aireadores = self.parse_formatted_number(
                self.get_controller_value('h_aireadores_mecanicos'))
            hectareas = self.parse_formatted_number(
                self.get_controller_value('hectareas'))
            aireadores_diesel = (aireadores * 3) / hectareas

            self.set_controller_value(
                'aireadores_diesel', f"{aireadores_diesel:.2f}")
        except Exception:
            self.set_controller_value('aireadores_diesel', "Error")

    def calcular_capacidad_carga_aireaccion(self):
        """Calcula la capacidad de carga de aireación"""
        try:
            aireadores_diesel = self.parse_formatted_number(
                self.get_controller_value('aireadores_diesel'))
            hectarea = self.parse_formatted_number(
                self.get_controller_value('hectareas'))

            capacidad_carga_aireaccion = (
                aireadores_diesel * 3000) + (7500 * hectarea)

            self.set_controller_value(
                'capacidad_carga_aireaccion', f"{capacidad_carga_aireaccion:.2f}")
        except Exception:
            self.set_controller_value('capacidad_carga_aireaccion', "Error")

    def libras_totales_por_aireador(self):
        """Calcula libras totales por aireador"""
        libras_totales_campo = self.parse_formatted_number(
            self.get_controller_value('libras_totales_campo'))
        aireadores_mecanicos = self.parse_formatted_number(
            self.get_controller_value('h_aireadores_mecanicos'))

        if aireadores_mecanicos == 0:
            self.set_controller_value('libras_totales_por_aireador', "0.00")
            return

        libras_totales_por_aireador = libras_totales_campo / aireadores_mecanicos
        self.set_controller_value(
            'libras_totales_por_aireador',
            self.format_number(libras_totales_por_aireador))

        print(f"Libras totales por aireador calculado: "
              f"{self.format_number(libras_totales_por_aireador)}")

    def fca_campo(self):
        """Calcula FCA Campo"""
        acumulado = self.parse_formatted_number(
            self.get_controller_value('acumulado_actual_lbs'))
        libras_totales_campo = self.parse_formatted_number(
            self.get_controller_value('libras_totales_campo'))

        if libras_totales_campo == 0 or acumulado == 0:
            self.set_controller_value('fca_campo', "0.00")
            return

        fca_campo = acumulado / libras_totales_campo
        self.set_controller_value('fca_campo', f"{fca_campo:.2f}")

    def fca_consumo(self):
        """Calcula FCA Consumo"""
        acumulado = self.parse_formatted_number(
            self.get_controller_value('acumulado_actual_lbs'))
        libras_totales_consumo = self.parse_formatted_number(
            self.get_controller_value('libras_totales_consumo'))

        if libras_totales_consumo == 0 or acumulado == 0:
            self.set_controller_value('fca_consumo', "0.00")
            return

        fca_consumo = acumulado / libras_totales_consumo
        self.set_controller_value('fca_consumo', f"{fca_consumo:.2f}")

    def calcular_rendimiento_lbs_saco(self):
        """Calcula el rendimiento en libras por saco"""
        lbs_actual_campo = self.parse_formatted_number(
            self.get_controller_value('lbs_ha_actual_campo'))
        hectareaje = self.parse_formatted_number(
            self.get_controller_value('hectareas'))
        alimento_actual_campo = self.parse_formatted_number(
            self.get_controller_value('alimento_actual_kg'))

        if alimento_actual_campo == 0:
            self.set_controller_value('rendimiento_lbs_saco', "0.00")
            return

        rendimiento_lbs_saco = (
            lbs_actual_campo * hectareaje) / (alimento_actual_campo / 25)
        self.set_controller_value(
            'rendimiento_lbs_saco', f"{rendimiento_lbs_saco:.2f}")

    def calcular_recomendacion_lbs_ha(self):
        """Calcula la recomendación en libras por hectárea"""
        try:
            capacidad = 7000
            hectareaje = self.parse_formatted_number(
                self.get_controller_value('hectareas'))
            recomendacion_lbs_ha = capacidad * hectareaje

            # Formatear el resultado si es un número grande
            self.set_controller_value(
                'recomendacion_lbs_ha', self.format_number(recomendacion_lbs_ha))

            print(f"Recomendación LBS/HA calculado: "
                  f"{self.format_number(recomendacion_lbs_ha)}")
        except Exception:
            self.set_controller_value('recomendacion_lbs_ha', "Error")

    def calcular_lbs_ha_actual_campo(self):
        """Calcula LBS/Ha actual campo"""
        try:
            densidad_biologo2 = self.parse_formatted_number(
                self.get_controller_value('densidad_biologo_indm2'))
            peso_actual_campo = self.parse_formatted_number(
                self.get_controller_value('peso_actual_gdia'))

            lbs_ha_actual_campo = densidad_biologo2 * peso_actual_campo * 22

            self.set_controller_value(
                'lbs_ha_actual_campo', f"{lbs_ha_actual_campo:.2f}")
        except Exception:
            self.set_controller_value('lbs_ha_actual_campo', "Error")

    def calcular_lbs_ha_consumo(self):
        """Calcula LBS/Ha consumo"""
        try:
            densidad_consumo = self.parse_formatted_number(
                self.get_controller_value('densidad_consumo_im2'))
            peso_actual_gdia = self.parse_formatted_number(
                self.get_controller_value('peso_actual_gdia'))
            lbs_ha_consumo = densidad_consumo * peso_actual_gdia * 22

            self.set_controller_value(
                'lbs_ha_consumo', f"{lbs_ha_consumo:.2f}")
        except Exception:
            self.set_controller_value('lbs_ha_consumo', "Error")

    def calcular_lbs_tolva_actual(self):
        """Calcula LBS TOLVA actual - Equivalente a calcularLBSTOLVAACTUAL en Dart"""
        lbs_actual_campo = self.parse_formatted_number(
            self.get_controller_value('lbs_ha_actual_campo'))
        aa_controller = self.parse_formatted_number(
            self.get_controller_value('numero_aa'))
        hectareas = self.parse_formatted_number(
            self.get_controller_value('hectareas'))

        if aa_controller == 0:
            self.set_controller_value('lbs_tolva_actual_campo', "0.00")
            return

        lbs_ha_actual_campo = (lbs_actual_campo * hectareas) / aa_controller
        self.set_controller_value(
            'lbs_tolva_actual_campo', f"{lbs_ha_actual_campo:.2f}")

    def calcular_lbs_tolva_consumo(self):
        """Calcula LBS TOLVA consumo - Equivalente a calcularLBSTOLVAConsumo en Dart"""
        try:
            aa_controller = self.parse_formatted_number(
                self.get_controller_value('numero_aa'))
            lbs_ha_consumo = self.parse_formatted_number(
                self.get_controller_value('lbs_ha_consumo'))
            hectarea = self.parse_formatted_number(
                self.get_controller_value('hectareas'))

            if aa_controller == 0:
                self.set_controller_value('lbs_tolva_segun_consumo', "0.00")
                return

            lbs_tolva_consumo = (lbs_ha_consumo * hectarea) / aa_controller

            self.set_controller_value(
                'lbs_tolva_segun_consumo', f"{lbs_tolva_consumo:.2f}")
        except Exception:
            self.set_controller_value('lbs_tolva_segun_consumo', "Error")

    def calcular_libras_totales_campo(self):
        """Calcula libras totales campo"""
        lbs_actual_campo = self.parse_formatted_number(
            self.get_controller_value('lbs_ha_actual_campo'))
        area_hectarea = self.parse_formatted_number(
            self.get_controller_value('hectareas'))
        libras_totales_campo = lbs_actual_campo * area_hectarea
        # Formatear el resultado si es un número grande
        self.set_controller_value(
            'libras_totales_campo', self.format_number(libras_totales_campo))
        print(f"Libras totales campo calculado: "
              f"{self.format_number(libras_totales_campo)}")

    def calcular_libras_totales_consumo(self):
        """Calcula libras totales consumo"""
        lbs_actual_consumo = self.parse_formatted_number(
            self.get_controller_value('lbs_ha_consumo'))
        area_hectarea = self.parse_formatted_number(
            self.get_controller_value('hectareas'))
        libras_totales_consumo = lbs_actual_consumo * area_hectarea
        # Formatear el resultado si es un número grande
        self.set_controller_value(
            'libras_totales_consumo', self.format_number(libras_totales_consumo))
        print(f"Libras totales consumo calculado: "
              f"{self.format_number(libras_totales_consumo)}")

    def calcular_hp_ha(self):
        """Calcula HP/Ha"""
        aereador_mecanico_hp = 16.00
        rendimiento_estado_y_mantenimiento = 1
        numero_aireadores_mecanicos = self.parse_formatted_number(
            self.get_controller_value('h_aireadores_mecanicos'))
        hectareaje = self.parse_formatted_number(
            self.get_controller_value('hectareas'))
        if hectareaje == 0:
            self.set_controller_value('hp_ha', "0.00")
            return
        hp_ha_value = (numero_aireadores_mecanicos * aereador_mecanico_hp) / \
            (hectareaje * rendimiento_estado_y_mantenimiento)
        self.set_controller_value('hp_ha', f"{hp_ha_value:.2f}")

    def libras_totales_consumo(self):
        """Calcula libras totales consumo"""
        lbs_actual_consumo = self.parse_formatted_number(
            self.get_controller_value('lbs_ha_consumo'))
        area_hectarea = self.parse_formatted_number(
            self.get_controller_value('hectareas'))
        libras_totales_consumo = lbs_actual_consumo * area_hectarea
        # Formatear el resultado si es un número grande
        self.set_controller_value(
            'libras_totales_consumo', self.format_number(libras_totales_consumo))
        print(f"Libras totales consumo calculado: "
              f"{self.format_number(libras_totales_consumo)}")

    def calcular_todos_los_valores(self):
        """Ejecuta todos los cálculos en el orden correcto"""
        # Cálculos básicos
        self.calcular_edad_cultivo()
        self.incremento_gr()
        self.calcular_crecimiento_actual()

        # Cálculos de densidad y alimento
        self.calcular_densidad_consumo()
        self.calcular_kg_100mil()
        self.calcular_sacos_actuales()

        # Cálculos de días de la semana
        self.calcular_lunes_dia1()
        self.calcular_domingo_dia7()
        self.calcular_martes_dia2()
        self.calcular_miercoles_dia3()
        self.calcular_jueves_dia4()
        self.calcular_viernes_dia5()
        self.calcular_sabado_dia6()

        # Cálculos semanales
        self.calcular_recomendation_semana()
        self.calcular_acumulado_semanal()

        # Cálculos de aireación
        self.calcular_aireadores_diesel()
        self.calcular_capacidad_carga_aireaccion()

        # Cálculos de libras y peso
        self.calcular_lbs_ha_actual_campo()
        self.calcular_lbs_ha_consumo()
        self.calcular_libras_totales_campo()
        self.calcular_libras_totales_consumo()
        self.calcular_lbs_tolva_actual()
        self.calcular_lbs_tolva_consumo()

        # Cálculos finales
        self.calcular_hp_ha()
        self.calcular_rendimiento_lbs_saco()
        self.calcular_recomendacion_lbs_ha()
        self.libras_totales_por_aireador()
        # self.calcular_acumulado_actual_lbs()
        self.fca_campo()
        self.fca_consumo()
        self.diferencia_campo_biologo()

    def generar_resultados_finales(self, input_data):
        """Genera el diccionario final con todos los resultados"""
        # Primero calculamos todos los valores
        self.calcular_todos_los_valores()

        # Obtenemos los valores de los controladores
        hectareas = self.parse_formatted_number(
            self.get_controller_value('hectareas'))
        edad_cultivo = self.parse_formatted_number(
            self.get_controller_value('edad_cultivo'))
        crecimiento_actual = self.parse_formatted_number(
            self.get_controller_value('crecim_actual_gdia'))
        peso_anterior = self.parse_formatted_number(
            self.get_controller_value('peso_anterior'))
        peso_actual = self.parse_formatted_number(
            self.get_controller_value('peso_actual_gdia'))
        densidad_consumo = self.parse_formatted_number(
            self.get_controller_value('densidad_consumo_im2'))
        alimento_kg = self.parse_formatted_number(
            self.get_controller_value('alimento_actual_kg'))
        sacos_actuales = self.parse_formatted_number(
            self.get_controller_value('sacos_actuales'))
        densidad_biologo = self.parse_formatted_number(
            self.get_controller_value('densidad_biologo_indm2'))
        lunes_dia1 = self.parse_formatted_number(
            self.get_controller_value('lunes_dia1'))
        martes_dia2 = self.parse_formatted_number(
            self.get_controller_value('martes_dia2'))
        miercoles_dia3 = self.parse_formatted_number(
            self.get_controller_value('miercoles_dia3'))
        jueves_dia4 = self.parse_formatted_number(
            self.get_controller_value('jueves_dia4'))
        viernes_dia5 = self.parse_formatted_number(
            self.get_controller_value('viernes_dia5'))
        sabado_dia6 = self.parse_formatted_number(
            self.get_controller_value('sabado_dia6'))
        domingo_dia7 = self.parse_formatted_number(
            self.get_controller_value('domingo_dia7'))
        recomendation_semana = self.parse_formatted_number(
            self.get_controller_value('recomendation_semana'))
        acumulado_semanal = self.parse_formatted_number(
            self.get_controller_value('acumulado_semanal'))
        numeroAA = self.parse_formatted_number(
            self.get_controller_value('numero_aa'))
        aireadores = self.parse_formatted_number(
            self.get_controller_value('h_aireadores_mecanicos'))
        LBSha_campo = self.parse_formatted_number(
            self.get_controller_value('lbs_ha_actual_campo'))
        LBSha_consumo = self.parse_formatted_number(
            self.get_controller_value('lbs_ha_consumo'))
        incremento_gr = self.parse_formatted_number(
            self.get_controller_value('incremento_gr'))
        acumulado_LBS = self.parse_formatted_number(
            self.get_controller_value('acumulado_actual_lbs'))
        libras_totales_consumo = self.parse_formatted_number(
            self.get_controller_value('libras_totales_consumo'))

        # --- Resultados finales con todas las llaves ---
        resultados_finales = {
            'hectareas': hectareas,
            'piscinas': self.get_controller_value('piscinas'),
            'fecha_siembra': input_data.get('Fechadesiembra', ''),
            'fecha_muestreo': input_data.get('Fechademuestreo', ''),
            'edad_cultivo': edad_cultivo,
            'crecim_actual_gdia': crecimiento_actual,
            'peso_siembra': self.get_controller_value('peso_siembra'),
            'peso_actual_gdia': peso_actual,
            'peso_proyectado_gdia': self.get_controller_value('peso_proyectado_gdia'),
            'crecimiento_esperado_sem': self.get_controller_value('crecimiento_esperado_sem'),
            'densidad_consumo_im2': densidad_consumo,
            'alimento_actual_kg': alimento_kg,
            'kg_100mil': self.get_controller_value('kg_100mil'),
            'sacos_actuales': sacos_actuales,
            'densidad_biologo_indm2': densidad_biologo,
            'densidad_atarraya': self.get_controller_value('densidad_atarraya'),
            'lunes_dia1': lunes_dia1,
            'martes_dia2': martes_dia2,
            'miercoles_dia3': miercoles_dia3,
            'jueves_dia4': jueves_dia4,
            'viernes_dia5': viernes_dia5,
            'sabado_dia6': sabado_dia6,
            'domingo_dia7': domingo_dia7,
            'recomendation_semana': recomendation_semana,
            'acumulado_semanal': acumulado_semanal,
            'numero_aa': numeroAA,
            'h_aireadores_mecanicos': aireadores,
            'aireadores_diesel': self.get_controller_value('aireadores_diesel'),
            'capacidad_carga_aireaccion': self.get_controller_value('capacidad_carga_aireaccion'),
            'recomendacion_lbs_ha': self.get_controller_value('recomendacion_lbs_ha'),
            'lbs_ha_actual_campo': LBSha_campo,
            'lbs_tolva_segun_consumo': self.get_controller_value('lbs_tolva_segun_consumo'),
            'lbs_ha_consumo': LBSha_consumo,
            'diferencia_campo_biologo': self.get_controller_value('diferencia_campo_biologo'),
            'peso_anterior': peso_anterior,
            'incremento_gr': incremento_gr,
            'acumulado_actual_lbs': acumulado_LBS,
            'fca_campo': self.get_controller_value('fca_campo'),
            'libras_totales_campo': self.get_controller_value('libras_totales_campo'),
            'libras_totales_consumo': libras_totales_consumo,
            'hp_ha': self.get_controller_value('hp_ha'),
            'libras_totales_por_aireador': self.get_controller_value('libras_totales_por_aireador'),
            'lbs_tolva_actual_campo': self.get_controller_value('lbs_tolva_actual_campo'),
            'fca_consumo': self.get_controller_value('fca_consumo'),
            'rendimiento_lbs_saco': self.get_controller_value('rendimiento_lbs_saco')
        }

        return resultados_finales

    def generar_resultados_finales_extendidos(self, input_data, datos_adicionales):
        """Genera el diccionario final con todos los resultados incluyendo datos adicionales"""
        # Primero calculamos todos los valores
        self.calcular_todos_los_valores()

        # Obtener resultados básicos
        resultados_base = self.generar_resultados_finales(input_data)

        # Agregar datos adicionales enviados desde Flutter
        resultados_extendidos = {
            **resultados_base,
            # Datos adicionales del request
            'peso_siembra_flutter': datos_adicionales.get('Pesosiembra'),
            'densidad_atarraya_flutter': datos_adicionales.get('Densidadatarraya'),
            'tipo_balanceado': datos_adicionales.get('TipoBalanceado'),
            'marca_aa': datos_adicionales.get('MarcaAA'),
            'incremento_gr_flutter': datos_adicionales.get('Incrementogr'),
            'crecimiento_actual_flutter': datos_adicionales.get('Crecimientoactualgdia'),
            'peso_proyectado_flutter': datos_adicionales.get('Pesoproyectadogdia'),
            'crecimiento_esperado_flutter': datos_adicionales.get('Crecimientoesperadosem'),
            # Campos calculados adicionales
            'diferencias_flutter_vs_calculado': self.calcular_diferencias_flutter(datos_adicionales),
            'validaciones_cruzadas': self.validar_datos_cruzados(input_data, datos_adicionales),
            'metricas_adicionales': self.calcular_metricas_adicionales(),
        }

        return resultados_extendidos

    def calcular_diferencias_flutter(self, datos_adicionales):
        """Calcula diferencias entre valores enviados desde Flutter y los calculados"""
        diferencias = {}

        # Comparar peso siembra si está disponible
        if datos_adicionales.get('Pesosiembra') is not None:
            peso_siembra_calculado = self.parse_formatted_number(
                self.get_controller_value('peso_siembra'))
            if peso_siembra_calculado > 0:
                diferencias['peso_siembra'] = {
                    'flutter': datos_adicionales['Pesosiembra'],
                    'calculado': peso_siembra_calculado,
                    'diferencia_abs': abs(datos_adicionales['Pesosiembra'] - peso_siembra_calculado),
                    'diferencia_porcentaje': abs(datos_adicionales['Pesosiembra'] - peso_siembra_calculado) / peso_siembra_calculado * 100 if peso_siembra_calculado > 0 else 0
                }

        # Comparar incremento en gramos
        if datos_adicionales.get('Incrementogr') is not None:
            incremento_calculado = self.parse_formatted_number(
                self.get_controller_value('incremento_gr'))
            if incremento_calculado > 0:
                diferencias['incremento_gr'] = {
                    'flutter': datos_adicionales['Incrementogr'],
                    'calculado': incremento_calculado,
                    'diferencia_abs': abs(datos_adicionales['Incrementogr'] - incremento_calculado),
                    'diferencia_porcentaje': abs(datos_adicionales['Incrementogr'] - incremento_calculado) / incremento_calculado * 100 if incremento_calculado > 0 else 0
                }

        return diferencias

    def validar_datos_cruzados(self, input_data, datos_adicionales):
        """Valida la consistencia entre datos principales y adicionales"""
        validaciones = {}

        # Validar fechas
        try:
            fecha_siembra = datetime.strptime(
                input_data['Fechadesiembra'], '%d/%m/%Y')
            fecha_muestreo = datetime.strptime(
                input_data['Fechademuestreo'], '%d/%m/%Y')
            edad_calculada = (fecha_muestreo - fecha_siembra).days + 1

            validaciones['fechas'] = {
                'edad_enviada': input_data['Edaddelcultivo'],
                'edad_calculada': edad_calculada,
                'diferencia_dias': abs(input_data['Edaddelcultivo'] - edad_calculada),
                'es_consistente': abs(input_data['Edaddelcultivo'] - edad_calculada) <= 1
            }
        except Exception as e:
            validaciones['fechas'] = {'error': str(e)}

        # Validar densidades
        if datos_adicionales.get('Densidadatarraya') is not None:
            densidad_biologo = input_data['Densidadbiologoindm2']
            densidad_atarraya = datos_adicionales['Densidadatarraya']

            validaciones['densidades'] = {
                'densidad_biologo': densidad_biologo,
                'densidad_atarraya': densidad_atarraya,
                'diferencia_abs': abs(densidad_biologo - densidad_atarraya),
                'diferencia_porcentaje': abs(densidad_biologo - densidad_atarraya) / densidad_biologo * 100 if densidad_biologo > 0 else 0,
                'diferencia_aceptable': abs(densidad_biologo - densidad_atarraya) / densidad_biologo * 100 <= 15 if densidad_biologo > 0 else False
            }

        return validaciones

    def calcular_metricas_adicionales(self):
        """Calcula métricas adicionales útiles para el análisis"""
        metricas = {}

        try:
            # Eficiencia de aireación
            libras_totales = self.parse_formatted_number(
                self.get_controller_value('libras_totales_campo'))
            aireadores = self.parse_formatted_number(
                self.get_controller_value('h_aireadores_mecanicos'))
            hectareas = self.parse_formatted_number(
                self.get_controller_value('hectareas'))

            if aireadores > 0 and hectareas > 0:
                metricas['eficiencia_aireacion'] = {
                    'libras_por_aireador': libras_totales / aireadores,
                    'aireadores_por_hectarea': aireadores / hectareas,
                    'libras_por_hectarea': libras_totales / hectareas
                }

            # Eficiencia alimenticia
            alimento_kg = self.parse_formatted_number(
                self.get_controller_value('alimento_actual_kg'))
            fca_campo = self.parse_formatted_number(
                self.get_controller_value('fca_campo'))

            if alimento_kg > 0 and libras_totales > 0:
                biomasa_kg = libras_totales * 0.453592  # lbs a kg
                metricas['eficiencia_alimenticia'] = {
                    'kg_alimento_por_kg_biomasa': alimento_kg / biomasa_kg if biomasa_kg > 0 else 0,
                    'porcentaje_biomasa_alimentacion': (alimento_kg / biomasa_kg * 100) if biomasa_kg > 0 else 0,
                    'eficiencia_conversion': 1 / fca_campo if fca_campo > 0 else 0
                }

            # Productividad por unidad de área
            peso_actual = self.parse_formatted_number(
                self.get_controller_value('peso_actual_gdia'))
            densidad = self.parse_formatted_number(
                self.get_controller_value('densidad_biologo_indm2'))

            if peso_actual > 0 and densidad > 0:
                metricas['productividad'] = {
                    'gramos_por_m2': peso_actual * densidad,
                    'kg_por_hectarea': peso_actual * densidad * 10,  # 10000 m2/ha / 1000 g/kg
                    'individuos_por_m2': densidad,
                    'peso_promedio_g': peso_actual
                }

        except Exception as e:
            metricas['error'] = str(e)

        return metricas

    def get_campos_calculados(self):
        """Retorna lista de campos que fueron calculados por el sistema"""
        campos_calculados = [
            'edad_cultivo', 'incremento_gr', 'crecim_actual_gdia',
            'peso_proyectado_gdia', 'crecimiento_esperado_sem',
            'densidad_consumo_im2', 'kg_100mil', 'sacos_actuales',
            'lunes_dia1', 'martes_dia2', 'miercoles_dia3', 'jueves_dia4',
            'viernes_dia5', 'sabado_dia6', 'domingo_dia7',
            'recomendation_semana', 'acumulado_semanal',
            'aireadores_diesel', 'capacidad_carga_aireaccion',
            'lbs_ha_actual_campo', 'lbs_ha_consumo',
            'libras_totales_campo', 'libras_totales_consumo',
            'fca_campo', 'fca_consumo', 'diferencia_campo_biologo',
            'rendimiento_lbs_saco', 'recomendacion_lbs_ha',
            'libras_totales_por_aireador'
        ]

        return {campo: self.get_controller_value(campo) for campo in campos_calculados}

    def get_validaciones(self):
        """Retorna validaciones de los datos procesados"""
        validaciones = {
            'fechas_validas': self._validar_fechas(),
            'valores_numericos_validos': self._validar_valores_numericos(),
            'rangos_aceptables': self._validar_rangos(),
            'consistencia_datos': self._validar_consistencia()
        }

        return validaciones

    def _validar_fechas(self):
        """Valida que las fechas sean coherentes"""
        try:
            fecha_siembra = self.get_controller_value('fecha_siembra')
            fecha_muestreo = self.get_controller_value('fecha_muestreo')

            if not fecha_siembra or not fecha_muestreo:
                return {'valido': False, 'error': 'Fechas faltantes'}

            fecha_s = datetime.strptime(fecha_siembra, '%d/%m/%Y')
            fecha_m = datetime.strptime(fecha_muestreo, '%d/%m/%Y')

            if fecha_m < fecha_s:
                return {'valido': False, 'error': 'Fecha muestreo anterior a siembra'}

            diferencia = (fecha_m - fecha_s).days
            if diferencia > 200:  # Ciclo muy largo
                return {'valido': False, 'advertencia': 'Ciclo excesivamente largo'}

            return {'valido': True, 'dias_cultivo': diferencia + 1}

        except Exception as e:
            return {'valido': False, 'error': f'Error en fechas: {str(e)}'}

    def _validar_valores_numericos(self):
        """Valida que los valores numéricos sean razonables"""
        validaciones = {}

        # Validar peso actual
        peso_actual = self.parse_formatted_number(
            self.get_controller_value('peso_actual_gdia'))
        validaciones['peso_actual'] = {
            'valor': peso_actual,
            'valido': 0.1 <= peso_actual <= 100,
            'rango_esperado': '0.1-100 gramos'
        }

        # Validar densidad
        densidad = self.parse_formatted_number(
            self.get_controller_value('densidad_biologo_indm2'))
        validaciones['densidad'] = {
            'valor': densidad,
            'valido': 1 <= densidad <= 50,
            'rango_esperado': '1-50 ind/m²'
        }

        # Validar FCA
        fca = self.parse_formatted_number(
            self.get_controller_value('fca_campo'))
        validaciones['fca'] = {
            'valor': fca,
            'valido': 0.5 <= fca <= 3.0,
            'rango_esperado': '0.5-3.0'
        }

        return validaciones

    def _validar_rangos(self):
        """Valida que los valores estén en rangos aceptables"""
        validaciones = {}

        # Validar crecimiento
        crecimiento = self.parse_formatted_number(
            self.get_controller_value('crecim_actual_gdia'))
        validaciones['crecimiento'] = {
            'valor': crecimiento,
            'optimo': 0.8 <= crecimiento <= 1.5,
            'aceptable': 0.5 <= crecimiento <= 2.0,
            'rango_optimo': '0.8-1.5 g/día'
        }

        return validaciones

    def _validar_consistencia(self):
        """Valida la consistencia interna de los datos"""
        validaciones = {}

        # Consistencia entre densidades
        densidad_biologo = self.parse_formatted_number(
            self.get_controller_value('densidad_biologo_indm2'))
        densidad_consumo = self.parse_formatted_number(
            self.get_controller_value('densidad_consumo_im2'))

        if densidad_biologo > 0 and densidad_consumo > 0:
            diferencia_pct = abs(densidad_biologo -
                                 densidad_consumo) / densidad_biologo * 100
            validaciones['densidades'] = {
                'diferencia_porcentaje': diferencia_pct,
                'consistente': diferencia_pct <= 20,
                'limite_aceptable': '20%'
            }

        return validaciones

    def mostrar_resultados(self, input_data):
        """Muestra los resultados en formato DataFrame"""
        resultados = self.generar_resultados_finales(input_data)

        # Mostrar en formato DataFrame vertical
        pd.set_option('display.float_format', '{:.2f}'.format)
        print("=== Variables finales con TODAS las llaves ===")
        print(pd.DataFrame(resultados, index=[0]).T)
    # Agrega estos métodos dentro de la clase AquacultureCalculator, justo después del método mostrar_resultados

    def mostrar_resultados_completos(self, input_data):
        """Muestra los resultados y el análisis completo"""
        resultados = self.generar_resultados_finales(input_data)

        # Mostrar en formato DataFrame vertical
        pd.set_option('display.float_format', '{:.2f}'.format)
        print("=== VARIABLES CALCULADAS ===")
        print(pd.DataFrame(resultados, index=[0]).T)

        # Realizar análisis inteligente
        analyzer = AquacultureAnalysisEngine()
        analysis = analyzer.analyze_results(resultados)
        report = analyzer.generate_report(analysis)

        print("\n=== ANÁLISIS INTELIGENTE ===")
        print(report)

        # Guardar análisis en archivo
        self.guardar_analisis(resultados, analysis)

        return resultados, analysis

    def guardar_analisis(self, resultados, analysis):
        """Guarda los resultados y análisis en un archivo JSON"""
        try:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analisis_acuicultura_{timestamp}.json"

            data_to_save = {
                'fecha_analisis': pd.Timestamp.now().isoformat(),
                'resultados': resultados,
                'analisis': analysis
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)

            print(f"\n📊 Análisis guardado en: {filename}")
        except Exception as e:
            print(f"Error al guardar análisis: {e}")


# Ejemplo de uso
if __name__ == "__main__":
    calculator = AquacultureCalculator()

    # Cargar datos de referencia
    calculator.fetch_data_tabla3()

    # Datos de ejemplo (debes reemplazar con tus datos reales)
    input_data = {
        "Hectareas": 7.8,
        "Piscinas": 5,
        'Fechadesiembra': '10/10/2024',
        'Fechademuestreo': '10/12/2024',
        "Edaddelcultivo": 62,
        "Pesoanterior": 23.33,
        "Pesoactualgdia": 30,
        "Densidadbiologoindm2": 11,
        "AcumuladoactualLBS": 55042,
        "numeroAA": 4,
        "Aireadores": 8,
        "Alimentoactualkg": 614,
    }

    # Establecer valores en controladores
    calculator.set_controller_value('hectareas', str(input_data['Hectareas']))
    calculator.set_controller_value('piscinas', str(input_data['Piscinas']))
    calculator.set_controller_value(
        'fecha_muestreo', input_data['Fechademuestreo'])
    calculator.set_controller_value(
        'fecha_siembra', input_data['Fechadesiembra'])
    calculator.set_controller_value(
        'edad_cultivo', str(input_data['Edaddelcultivo']))
    calculator.set_controller_value(
        'peso_anterior', str(input_data['Pesoanterior']))
    calculator.set_controller_value(
        'peso_actual_gdia', str(input_data['Pesoactualgdia']))
    calculator.set_controller_value(
        'densidad_biologo_indm2', str(input_data['Densidadbiologoindm2']))
    calculator.set_controller_value(
        'acumulado_actual_lbs', str(input_data['AcumuladoactualLBS']))
    calculator.set_controller_value('numero_aa', str(input_data['numeroAA']))
    calculator.set_controller_value(
        'h_aireadores_mecanicos', str(input_data['Aireadores']))
    calculator.set_controller_value(
        'alimento_actual_kg', str(input_data['Alimentoactualkg']))

    # Establecer valores en controladores
    for key, value in input_data.items():
        calculator.set_controller_value(key.lower(), str(value))

    # Calcular todos los valores
    calculator.calcular_todos_los_valores()

    # Mostrar resultados completos con análisis
    resultados, analisis = calculator.mostrar_resultados_completos(input_data)
