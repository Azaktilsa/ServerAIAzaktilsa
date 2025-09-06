#!/usr/bin/env python3
"""
Script para probar el endpoint de alimentación con los datos reales de Flutter
"""

import requests
import json

# URL del endpoint local (ajustar según tu configuración)
url = "http://localhost:8080/predict_alimentation"

# Datos exactos de la request que diste
data = {
    "finca": "CAMANOVILLO",
    "Hectareas": 7.8,
    "Piscinas": 5,
    "Fechadesiembra": "10/10/2024",
    "Fechademuestreo": "10/12/2024",
    "Edaddelcultivo": 62,
    "Pesoanterior": 23.33,
    "Pesoactualgdia": 30,
    "Densidadbiologoindm2": 11,
    "AcumuladoactualLBS": 55042,
    "numeroAA": 4,
    "Aireadores": 8,
    "Alimentoactualkg": 614,
    "Pesosiembra": 1.32,
    "Densidadatarraya": 10.6,
    "TipoBalanceado": "Aqua 1,2",
    "MarcaAA": "AQ1",
    "Incrementogr": 6.67,
    "Pesoproyectadogdia": 0,
    "FechaCalculada": True,
    "VersionApp": "1.0.0",
    "DispositivoId": "WEB-1757182202192"
}

print("=== PROBANDO ENDPOINT DE ALIMENTACIÓN ===")
print(f"URL: {url}")
print(f"Datos enviados:")
print(json.dumps(data, indent=2))

try:
    response = requests.post(url, json=data, timeout=30)
    
    print(f"\n=== RESPUESTA ===")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        # Extraer los valores clave para verificar
        resultados = result.get('resultados', {})
        
        print(f"\n=== VALORES CALCULADOS CLAVE ===")
        print(f"incremento_gr: {resultados.get('incremento_gr')}")
        print(f"crecim_actual_gdia: {resultados.get('crecim_actual_gdia')}")
        print(f"peso_proyectado_gdia: {resultados.get('peso_proyectado_gdia')}")
        print(f"edad_cultivo: {resultados.get('edad_cultivo')}")
        print(f"densidad_consumo_im2: {resultados.get('densidad_consumo_im2')}")
        
        # Verificar si los valores son los esperados
        incremento = resultados.get('incremento_gr')
        crecimiento = resultados.get('crecim_actual_gdia') 
        peso_proyectado = resultados.get('peso_proyectado_gdia')
        
        print(f"\n=== VERIFICACIÓN ===")
        print(f"Incremento esperado: 6.67, obtenido: {incremento} {'✅' if abs(float(incremento) - 6.67) < 0.01 else '❌'}")
        print(f"Crecimiento esperado: ~0.46, obtenido: {crecimiento} {'✅' if abs(float(crecimiento) - 0.46) < 0.01 else '❌'}")
        print(f"Peso proyectado esperado: 33.00, obtenido: {peso_proyectado} {'✅' if abs(float(peso_proyectado) - 33.0) < 0.01 else '❌'}")
        
        print(f"\n=== RESPUESTA COMPLETA ===")
        print(json.dumps(result, indent=2))
        
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Error de conexión: {e}")
    print("\nAsegúrate de que el servidor esté corriendo en el puerto 8080")
    print("Para iniciar el servidor: uvicorn main:app --host 0.0.0.0 --port 8080")
except Exception as e:
    print(f"Error inesperado: {e}")
