#!/usr/bin/env python3
"""
Script de prueba para verificar las correcciones de alimentation.py
"""

import sys
import traceback
from app.alimentation import (
    PredictionRequestAlimentation, 
    procesar_prediccion_alimentation,
    AquacultureCalculator
)

def test_parse_formatted_number():
    """Prueba la función parse_formatted_number con diferentes tipos de entrada"""
    print("=== Prueba parse_formatted_number ===")
    
    calculator = AquacultureCalculator()
    
    # Casos de prueba
    test_cases = [
        (None, 0.0),
        ("", 0.0),
        ("10.5", 10.5),
        ("1,234.56", 1234.56),
        (10, 10.0),
        (10.5, 10.5),
        ("invalid", 0.0),
    ]
    
    for input_val, expected in test_cases:
        try:
            result = calculator.parse_formatted_number(input_val)
            status = "✓" if result == expected else "✗"
            print(f"{status} Input: {input_val} -> Output: {result} (Expected: {expected})")
        except Exception as e:
            print(f"✗ Input: {input_val} -> Error: {e}")

def test_controller_values():
    """Prueba el manejo de valores None en controladores"""
    print("\n=== Prueba controller values ===")
    
    calculator = AquacultureCalculator()
    
    # Probar get_controller_value con claves que no existen
    value = calculator.get_controller_value('non_existent_key')
    print(f"Controller value for non-existent key: '{value}' (type: {type(value)})")
    
    # Probar diferencia_campo_biologo con valores None
    try:
        calculator.diferencia_campo_biologo()
        diferencia = calculator.get_controller_value('diferencia_campo_biologo')
        print(f"✓ diferencia_campo_biologo with None values: {diferencia}")
    except Exception as e:
        print(f"✗ diferencia_campo_biologo failed: {e}")

def test_prediction_request():
    """Prueba completa de procesar_prediccion_alimentation"""
    print("\n=== Prueba completa de predicción ===")
    
    # Datos de prueba basados en el error original
    request_data = {
        "finca": "CAMANOVILLO",
        "Hectareas": 8.3,
        "Piscinas": 1,
        "Fechadesiembra": "10/10/2024",
        "Fechademuestreo": "10/12/2024",
        "Edaddelcultivo": 62,
        "Pesoanterior": 23.33,
        "Pesoactualgdia": 30,
        "Densidadbiologoindm2": 10,
        "AcumuladoactualLBS": 55042,
        "numeroAA": 4,
        "Aireadores": 8,
        "Alimentoactualkg": 614,
        "Pesosiembra": 1.32,
        "Densidadatarraya": 10,
        "TipoBalanceado": "Haid",
        "MarcaAA": "AQ1",
        "Incrementogr": 6.67,
        "Pesoproyectadogdia": 0,
        "FechaCalculada": True,
        "VersionApp": "1.0.0",
        "DispositivoId": "WEB-1757110356977"
    }
    
    try:
        # Crear request object
        request = PredictionRequestAlimentation(**request_data)
        print(f"✓ Request object created successfully")
        
        # Procesar predicción
        result = procesar_prediccion_alimentation(request)
        print(f"✓ Prediction processed successfully")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Message: {result.get('mensaje', 'No message')}")
        
        if result.get('status') == 'success':
            print("✓ Test passed - no NoneType errors!")
            # Mostrar algunos resultados clave
            resultados = result.get('resultados', {})
            print(f"Sample results:")
            print(f"  - FCA Campo: {resultados.get('fca_campo', 'N/A')}")
            print(f"  - Libras Totales Campo: {resultados.get('libras_totales_campo', 'N/A')}")
            print(f"  - Diferencia Campo-Biólogo: {resultados.get('diferencia_campo_biologo', 'N/A')}")
        else:
            print(f"✗ Test failed with error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        traceback.print_exc()

def main():
    """Función principal de prueba"""
    print("Probando correcciones de alimentation.py")
    print("=" * 50)
    
    test_parse_formatted_number()
    test_controller_values()
    test_prediction_request()
    
    print("\n" + "=" * 50)
    print("Pruebas completadas")

if __name__ == "__main__":
    main()
