#!/usr/bin/env python3
"""
PRUEBA COMPLETA Y DETALLADA DE COMPATIBILIDAD FLUTTER-PYTHON
Verificación exhaustiva de cada método paso a paso
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.alimentation import AquacultureCalculator

def test_debug_detailed():
    """Prueba detallada con debugging paso a paso"""
    print("🔍 INICIO DE PRUEBA DETALLADA CON DEBUG")
    print("=" * 70)
    
    calculator = AquacultureCalculator()
    
    # 1. Verificar carga de datos de pesos
    print("\n1️⃣ VERIFICANDO CARGA DE DATOS DE PESOS:")
    print(f"   pesos_alimento_data tipo: {type(calculator.pesos_alimento_data)}")
    print(f"   pesos_alimento_data keys: {calculator.pesos_alimento_data.keys() if isinstance(calculator.pesos_alimento_data, dict) else 'No es dict'}")
    
    if 'rows' in calculator.pesos_alimento_data:
        rows = calculator.pesos_alimento_data['rows']
        print(f"   Número de filas: {len(rows)}")
        print(f"   Primera fila: {rows[0] if rows else 'Vacío'}")
        print(f"   Última fila: {rows[-1] if rows else 'Vacío'}")
    else:
        print("   ❌ NO HAY DATOS EN 'rows'")
    
    # 2. Cargar datos de tabla 3
    print("\n2️⃣ CARGANDO DATOS DE TABLA 3:")
    calculator.fetch_data_tabla3()
    print(f"   Tabla de referencia: {len(calculator.model.referencia_tabla)} entradas")
    print(f"   Primeras entradas: {dict(list(calculator.model.referencia_tabla.items())[:3])}")
    
    # 3. Establecer datos de prueba REALES
    print("\n3️⃣ ESTABLECIENDO DATOS DE PRUEBA:")
    test_data = {
        "Hectareas": 7.8,
        "Piscinas": 5,
        'Fechadesiembra': '10/10/2024',
        'Fechademuestreo': '10/12/2024',
        "Edaddelcultivo": 62,
        "Pesoanterior": 23.33,
        "Pesoactualgdia": 30.0,  # Peso actual que debe estar en la tabla
        "Densidadbiologoindm2": 11,
        "AcumuladoactualLBS": 55042,
        "numeroAA": 4,
        "Aireadores": 8,
        "Alimentoactualkg": 614,
    }
    
    # Configurar controladores
    for key, value in test_data.items():
        if key == 'Fechadesiembra':
            calculator.set_controller_value('fecha_siembra', value)
            print(f"   fecha_siembra: {value}")
        elif key == 'Fechademuestreo':
            calculator.set_controller_value('fecha_muestreo', value)
            print(f"   fecha_muestreo: {value}")
        else:
            controller_key = key.lower()
            calculator.set_controller_value(controller_key, str(value))
            print(f"   {controller_key}: {value}")
    
    # Valores adicionales
    calculator.set_controller_value('peso_siembra', '1.0')
    calculator.set_controller_value('densidad_atarraya', '10.0')
    
    print("\n4️⃣ PROBANDO MÉTODOS INDIVIDUALES:")
    
    # Test calcular_sacos_actuales
    print("\n   📦 calcular_sacos_actuales:")
    calculator.calcular_sacos_actuales()
    sacos = calculator.get_controller_value('sacos_actuales')
    expected = 614 / 25
    print(f"      Resultado: {sacos}")
    print(f"      Esperado: {expected:.2f}")
    print(f"      ✅ OK: {abs(float(sacos) - expected) < 0.01}")
    
    # Test calcular_edad_cultivo
    print("\n   📅 calcular_edad_cultivo:")
    calculator.calcular_edad_cultivo()
    edad = calculator.get_controller_value('edad_cultivo')
    print(f"      Resultado: {edad}")
    
    # Test incremento_gr
    print("\n   📈 incremento_gr:")
    calculator.incremento_gr()
    incremento = calculator.get_controller_value('incremento_gr')
    expected_inc = 30.0 - 23.33
    print(f"      Resultado: {incremento}")
    print(f"      Esperado: {expected_inc:.2f}")
    print(f"      ✅ OK: {abs(float(incremento) - expected_inc) < 0.01}")
    
    # Test calcular_crecimiento_actual
    print("\n   🚀 calcular_crecimiento_actual:")
    calculator.calcular_crecimiento_actual()
    crecimiento = calculator.get_controller_value('crecim_actual_gdia')
    peso_proyectado = calculator.get_controller_value('peso_proyectado_gdia')
    print(f"      Crecimiento actual: {crecimiento}")
    print(f"      Peso proyectado: {peso_proyectado}")
    
    # Test calcular_densidad_consumo - ESTE ES CRÍTICO
    print("\n   🔢 calcular_densidad_consumo (CRÍTICO):")
    print("      DEBUG - Valores en el controlador:")
    print(f"         alimentoactualkg RAW: '{calculator.get_controller_value('alimentoactualkg')}'")
    print(f"         hectareas RAW: '{calculator.get_controller_value('hectareas')}'")
    print(f"         pesoactualgdia RAW: '{calculator.get_controller_value('pesoactualgdia')}'")
    
    print("      Valores de entrada procesados:")
    alimento_kg = calculator.parse_formatted_number(calculator.get_controller_value('alimentoactualkg'))
    hectareas = calculator.parse_formatted_number(calculator.get_controller_value('hectareas'))
    peso_actual = calculator.parse_formatted_number(calculator.get_controller_value('pesoactualgdia'))
    print(f"         alimento_kg: {alimento_kg}")
    print(f"         hectareas: {hectareas}")
    print(f"         peso_actual: {peso_actual}")
    
    # Verificar datos disponibles para búsqueda
    if 'rows' in calculator.pesos_alimento_data:
        data = calculator.pesos_alimento_data['rows']
        print(f"      Datos disponibles para búsqueda: {len(data)} filas")
        
        # Buscar peso manualmente para debug
        peso_encontrado = 0.0
        bw_cosechas = "0%"
        
        print("      Búsqueda manual de peso:")
        for i, row in enumerate(data):
            if "Pesos" in row and "BWCosechas" in row:
                peso = float(str(row["Pesos"]))
                print(f"         Fila {i}: Peso={peso}, BWCosechas={row['BWCosechas']}")
                if peso <= peso_actual and peso > peso_encontrado:
                    peso_encontrado = peso
                    bw_cosechas = str(row["BWCosechas"])
                    print(f"            ✅ COINCIDE: peso_encontrado={peso_encontrado}, bw_cosechas={bw_cosechas}")
        
        print(f"      Peso encontrado final: {peso_encontrado}")
        print(f"      BWCosechas final: {bw_cosechas}")
    
    calculator.calcular_densidad_consumo()
    densidad_consumo = calculator.get_controller_value('densidad_consumo_im2')
    print(f"      Resultado final: {densidad_consumo}")
    
    # Test calcular_lunes_dia1
    print("\n   📅 calcular_lunes_dia1:")
    calculator.calcular_lunes_dia1()
    lunes = calculator.get_controller_value('lunes_dia1')
    print(f"      Resultado: {lunes}")
    
    # Test calcular_domingo_dia7
    print("\n   📅 calcular_domingo_dia7:")
    calculator.calcular_domingo_dia7()
    domingo = calculator.get_controller_value('domingo_dia7')
    print(f"      Resultado: {domingo}")
    
    # Test diferencia_campo_biologo
    print("\n   ⚖️ diferencia_campo_biologo:")
    calculator.diferencia_campo_biologo()
    diferencia = calculator.get_controller_value('diferencia_campo_biologo')
    print(f"      Resultado: {diferencia}")
    
    # Test todos los días de la semana
    print("\n   📅 Calculando todos los días de la semana:")
    calculator.calcular_martes_dia2()
    calculator.calcular_miercoles_dia3()
    calculator.calcular_jueves_dia4()
    calculator.calcular_viernes_dia5()
    calculator.calcular_sabado_dia6()
    
    dias = {
        'lunes': calculator.get_controller_value('lunes_dia1'),
        'martes': calculator.get_controller_value('martes_dia2'),
        'miercoles': calculator.get_controller_value('miercoles_dia3'),
        'jueves': calculator.get_controller_value('jueves_dia4'),
        'viernes': calculator.get_controller_value('viernes_dia5'),
        'sabado': calculator.get_controller_value('sabado_dia6'),
        'domingo': calculator.get_controller_value('domingo_dia7')
    }
    
    for dia, valor in dias.items():
        print(f"      {dia.capitalize()}: {valor}")
    
    # Test recomendación semanal
    print("\n   📊 calcular_recomendation_semana:")
    calculator.calcular_recomendation_semana()
    recomendacion = calculator.get_controller_value('recomendation_semana')
    print(f"      Resultado: {recomendacion}")
    
    # Test acumulado semanal
    print("\n   📈 calcular_acumulado_semanal:")
    calculator.calcular_acumulado_semanal()
    acumulado = calculator.get_controller_value('acumulado_semanal')
    print(f"      Resultado: {acumulado}")
    
    print("\n5️⃣ EJECUTANDO CÁLCULO COMPLETO:")
    calculator.calcular_todos_los_valores()
    
    print("\n6️⃣ RESULTADOS FINALES:")
    resultados = calculator.generar_resultados_finales(test_data)
    
    campos_importantes = [
        'hectareas', 'edad_cultivo', 'crecim_actual_gdia', 'peso_proyectado_gdia',
        'densidad_consumo_im2', 'lunes_dia1', 'domingo_dia7', 'recomendation_semana',
        'acumulado_semanal', 'sacos_actuales', 'incremento_gr'
    ]
    
    for campo in campos_importantes:
        if campo in resultados:
            print(f"   {campo}: {resultados[campo]}")
    
    # 7. Diagnóstico final
    print("\n7️⃣ DIAGNÓSTICO FINAL:")
    problemas = []
    
    if densidad_consumo in ["No hay datos", "Datos inválidos", "Error"]:
        problemas.append("❌ calcular_densidad_consumo falló")
    
    if lunes in ["No hay datos", "Datos inválidos", "Error"]:
        problemas.append("❌ calcular_lunes_dia1 falló")
    
    if domingo in ["No hay datos", "Datos inválidos", "Error"]:
        problemas.append("❌ calcular_domingo_dia7 falló")
    
    if problemas:
        print("   PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"      {problema}")
    else:
        print("   ✅ TODOS LOS MÉTODOS FUNCIONARON CORRECTAMENTE")
    
    print("\n" + "=" * 70)
    print("🎯 PRUEBA DETALLADA COMPLETADA")
    
    return calculator, resultados

if __name__ == "__main__":
    print("🚀 PRUEBA DETALLADA DE COMPATIBILIDAD FLUTTER-PYTHON")
    print("🔍 Verificación exhaustiva paso a paso")
    print("=" * 70)
    
    try:
        calculator, resultados = test_debug_detailed()
        print("\n🎉 PRUEBA COMPLETADA!")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
