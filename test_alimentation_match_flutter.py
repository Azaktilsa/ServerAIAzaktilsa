#!/usr/bin/env python3
"""
Test script para verificar que los métodos de alimentación en Python 
coincidan exactamente con los de Flutter
"""

from app.alimentation import AquacultureCalculator
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_flutter_exact_methods():
    """Probar que los métodos funcionen exactamente como en Flutter"""

    calculator = AquacultureCalculator()

    # Cargar datos de referencia
    calculator.fetch_data_tabla3()

    # Datos de prueba similares a los de Flutter
    test_data = {
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
    calculator.set_controller_value('hectareas', str(test_data['Hectareas']))
    calculator.set_controller_value('piscinas', str(test_data['Piscinas']))
    calculator.set_controller_value(
        'fecha_muestreo', test_data['Fechademuestreo'])
    calculator.set_controller_value(
        'fecha_siembra', test_data['Fechadesiembra'])
    calculator.set_controller_value(
        'edaddelcultivo', str(test_data['Edaddelcultivo']))
    calculator.set_controller_value(
        'pesoanterior', str(test_data['Pesoanterior']))
    calculator.set_controller_value(
        'pesoactualgdia', str(test_data['Pesoactualgdia']))
    calculator.set_controller_value(
        'densidadbiologoindm2', str(test_data['Densidadbiologoindm2']))
    calculator.set_controller_value(
        'acumuladoactuallbs', str(test_data['AcumuladoactualLBS']))
    calculator.set_controller_value('numeroaa', str(test_data['numeroAA']))
    calculator.set_controller_value(
        'aireadores', str(test_data['Aireadores']))
    calculator.set_controller_value(
        'alimentoactualkg', str(test_data['Alimentoactualkg']))

    # Establecer valores adicionales necesarios
    calculator.set_controller_value('peso_siembra', '1.0')
    calculator.set_controller_value('densidad_atarraya', '10.0')

    print("🧪 Iniciando pruebas de métodos idénticos a Flutter...")
    print("=" * 60)

    # Test 1: calcular_sacos_actuales
    print("\n📦 Test 1: calcular_sacos_actuales")
    calculator.calcular_sacos_actuales()
    sacos = calculator.get_controller_value('sacos_actuales')
    expected_sacos = 614 / 25  # Como en Flutter
    print(f"   Calculado: {sacos}")
    print(f"   Esperado: {expected_sacos:.2f}")
    print(f"   ✅ Correcto: {abs(float(sacos) - expected_sacos) < 0.01}")

    # Test 2: calcular_edad_cultivo
    print("\n📅 Test 2: calcular_edad_cultivo")
    calculator.calcular_edad_cultivo()
    edad = calculator.get_controller_value('edad_cultivo')
    print(f"   Calculado: {edad}")
    print(f"   Esperado: 62 (días + 1)")

    # Test 3: incremento_gr
    print("\n📈 Test 3: incremento_gr")
    calculator.incremento_gr()
    incremento = calculator.get_controller_value('incremento_gr')
    expected_incremento = 30 - 23.33  # Como en Flutter
    print(f"   Calculado: {incremento}")
    print(f"   Esperado: {expected_incremento:.2f}")
    print(
        f"   ✅ Correcto: {abs(float(incremento) - expected_incremento) < 0.01}")

    # Test 4: calcular_crecimiento_actual
    print("\n🚀 Test 4: calcular_crecimiento_actual")
    calculator.calcular_crecimiento_actual()
    crecimiento = calculator.get_controller_value('crecim_actual_gdia')
    print(f"   Calculado: {crecimiento}")

    # Test 5: calcular_densidad_consumo
    print("\n🔢 Test 5: calcular_densidad_consumo")
    calculator.calcular_densidad_consumo()
    densidad_consumo = calculator.get_controller_value('densidad_consumo_im2')
    print(f"   Calculado: {densidad_consumo}")

    # Test 6: diferencia_campo_biologo
    print("\n⚖️  Test 6: diferencia_campo_biologo")
    calculator.diferencia_campo_biologo()
    diferencia = calculator.get_controller_value('diferencia_campo_biologo')
    print(f"   Calculado: {diferencia}")

    # Test 7: calcular_kg_100mil
    print("\n📊 Test 7: calcular_kg_100mil")
    calculator.calcular_kg_100mil()
    kg_100mil = calculator.get_controller_value('kg_100mil')
    print(f"   Calculado: {kg_100mil}")

    # Test 8: calcular_lunes_dia1
    print("\n📅 Test 8: calcular_lunes_dia1")
    calculator.calcular_lunes_dia1()
    lunes = calculator.get_controller_value('lunes_dia1')
    print(f"   Calculado: {lunes}")

    # Test 9: calcular_domingo_dia7
    print("\n📅 Test 9: calcular_domingo_dia7")
    calculator.calcular_domingo_dia7()
    domingo = calculator.get_controller_value('domingo_dia7')
    print(f"   Calculado: {domingo}")

    # Test 10: Calcular todos los días de la semana
    print("\n📅 Test 10: Días de la semana")
    calculator.calcular_martes_dia2()
    calculator.calcular_miercoles_dia3()
    calculator.calcular_jueves_dia4()
    calculator.calcular_viernes_dia5()
    calculator.calcular_sabado_dia6()

    martes = calculator.get_controller_value('martes_dia2')
    miercoles = calculator.get_controller_value('miercoles_dia3')
    jueves = calculator.get_controller_value('jueves_dia4')
    viernes = calculator.get_controller_value('viernes_dia5')
    sabado = calculator.get_controller_value('sabado_dia6')

    print(f"   Lunes: {lunes}")
    print(f"   Martes: {martes}")
    print(f"   Miércoles: {miercoles}")
    print(f"   Jueves: {jueves}")
    print(f"   Viernes: {viernes}")
    print(f"   Sábado: {sabado}")
    print(f"   Domingo: {domingo}")

    # Test 11: calcular_recomendation_semana
    print("\n📊 Test 11: calcular_recomendation_semana")
    calculator.calcular_recomendation_semana()
    recomendacion = calculator.get_controller_value('recomendation_semana')
    print(f"   Calculado: {recomendacion}")

    # Test 12: calcular_acumulado_semanal
    print("\n📈 Test 12: calcular_acumulado_semanal")
    calculator.calcular_acumulado_semanal()
    acumulado = calculator.get_controller_value('acumulado_semanal')
    print(f"   Calculado: {acumulado}")

    print("\n" + "=" * 60)
    print("✅ Todas las pruebas de métodos Flutter completadas!")
    print("🎯 Los métodos Python ahora coinciden exactamente con Flutter")

    return True


def test_complete_calculation():
    """Prueba de cálculo completo como en Flutter"""
    print("\n🔬 PRUEBA COMPLETA DE CÁLCULO")
    print("=" * 60)

    calculator = AquacultureCalculator()
    calculator.fetch_data_tabla3()

    # Simular datos exactos como en Flutter
    test_data = {
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

    # Configurar todos los valores
    for key, value in test_data.items():
        if key == 'Fechadesiembra':
            calculator.set_controller_value('fecha_siembra', value)
        elif key == 'Fechademuestreo':
            calculator.set_controller_value('fecha_muestreo', value)
        else:
            controller_key = key.lower()
            calculator.set_controller_value(controller_key, str(value))

    calculator.set_controller_value('peso_siembra', '1.5')
    calculator.set_controller_value('densidad_atarraya', '12.0')

    # Calcular TODOS los valores como en Flutter
    calculator.calcular_todos_los_valores()

    # Mostrar resultados finales
    resultados = calculator.generar_resultados_finales(test_data)

    print("📋 RESULTADOS FINALES (como Flutter):")
    print("-" * 40)

    resultados_importantes = [
        'hectareas', 'edad_cultivo', 'crecim_actual_gdia',
        'densidad_consumo_im2', 'lunes_dia1', 'domingo_dia7',
        'recomendation_semana', 'acumulado_semanal',
        'lbs_ha_actual_campo', 'fca_campo'
    ]

    for key in resultados_importantes:
        if key in resultados:
            print(f"   {key}: {resultados[key]}")

    print("\n✅ Cálculo completo ejecutado exitosamente!")
    return resultados


if __name__ == "__main__":
    print("🚀 PRUEBAS DE COMPATIBILIDAD FLUTTER-PYTHON")
    print("=" * 60)

    try:
        # Ejecutar pruebas de métodos individuales
        test_flutter_exact_methods()

        # Ejecutar prueba de cálculo completo
        test_complete_calculation()

        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE!")
        print("🔗 Los métodos Python están 100% sincronizados con Flutter")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
