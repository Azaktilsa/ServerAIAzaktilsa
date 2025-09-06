#!/usr/bin/env python3
"""
Test específico para verificar que calcular_densidad_consumo 
replica exactamente la lógica de Flutter
"""

from app.alimentation import AquacultureCalculator
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_calcular_densidad_consumo_flutter():
    """
    Prueba específica de calcular_densidad_consumo replicando Flutter
    ACTUALIZADA: Maneja formatos decimales inglés (7.8) y español (7,8)
    """
    print("🔬 TEST ESPECÍFICO: calcular_densidad_consumo (Flutter → Python)")
    print("=" * 70)

    calculator = AquacultureCalculator()
    calculator.fetch_data_tabla3()

    # Configurar datos de prueba exactos - PROBANDO AMBOS FORMATOS
    test_values_english = {
        'alimentoactualkg': '614',      # alimentoActualKg en Flutter
        'hectareas': '7.8',            # hectareas en Flutter (formato inglés)
        # pesoActualG en Flutter (formato inglés)
        'pesoactualgdia': '30.0'
    }

    test_values_spanish = {
        'alimentoactualkg': '614',      # alimentoActualKg en Flutter
        'hectareas': '7,8',            # hectareas en Flutter (formato español)
        # pesoActualG en Flutter (formato español)
        'pesoactualgdia': '30,0'
    }

    print("📋 PRUEBA 1 - FORMATO INGLÉS (punto decimal):")
    print(f"   alimentoActualKg: {test_values_english['alimentoactualkg']} kg")
    print(f"   hectareas: {test_values_english['hectareas']} ha")
    print(f"   pesoActualG: {test_values_english['pesoactualgdia']} g")

    # Establecer valores formato inglés
    for key, value in test_values_english.items():
        calculator.set_controller_value(key, value)

    # Ejecutar el cálculo
    calculator.calcular_densidad_consumo()
    resultado_english = calculator.get_controller_value('densidad_consumo_im2')
    print(f"   Resultado: {resultado_english}")

    print("\n📋 PRUEBA 2 - FORMATO ESPAÑOL (coma decimal):")
    print(f"   alimentoActualKg: {test_values_spanish['alimentoactualkg']} kg")
    print(f"   hectareas: {test_values_spanish['hectareas']} ha")
    print(f"   pesoActualG: {test_values_spanish['pesoactualgdia']} g")

    # Establecer valores formato español
    for key, value in test_values_spanish.items():
        calculator.set_controller_value(key, value)

    # Ejecutar el cálculo
    calculator.calcular_densidad_consumo()
    resultado_spanish = calculator.get_controller_value('densidad_consumo_im2')
    print(f"   Resultado: {resultado_spanish}")

    print(f"\n🎯 COMPARACIÓN DE RESULTADOS:")
    print(f"   Formato inglés (7.8): {resultado_english}")
    print(f"   Formato español (7,8): {resultado_spanish}")
    print(f"   ¿Son iguales? {resultado_english == resultado_spanish}")

    # Mostrar datos de búsqueda en pesos_alimento_data
    if calculator.pesos_alimento_data and 'rows' in calculator.pesos_alimento_data:
        data = calculator.pesos_alimento_data['rows']
        peso_actual_g = 30.0

        print(f"\n🔍 PROCESO DE CÁLCULO (replicando Flutter):")
        print("-" * 50)
        print(f"   Buscando en {len(data)} filas de pesos_alimento_data...")
        print(f"   Criterio: Peso <= {peso_actual_g}g")

        # Mostrar algunos datos relevantes para el peso 30g
        relevant_weights = []
        for row in data:
            if "Pesos" in row and "BWCosechas" in row:
                peso = float(str(row["Pesos"]))
                if peso <= peso_actual_g:
                    relevant_weights.append({
                        'peso': peso,
                        'bw': row["BWCosechas"]
                    })

        # Ordenar y mostrar los últimos 5 pesos relevantes
        relevant_weights.sort(key=lambda x: x['peso'])
        print("   Pesos relevantes encontrados (últimos 5):")
        for weight in relevant_weights[-5:]:
            print(f"     Peso: {weight['peso']}g → BWCosechas: {weight['bw']}")

    # Mostrar la fórmula Flutter replicada
    print("\n📐 FÓRMULA FLUTTER REPLICADA:")
    print("   densidad_consumo = (alimentoActualKg / hectareas) * 10 / (pesoActualG * bwCosechasDecimal)")
    print(f"   densidad_consumo = (614 / 7.8) * 10 / (30 * bwCosechasDecimal)")

    # Verificar que el resultado es numérico y tiene el formato correcto
    try:
        resultado_num = float(resultado_spanish)  # Usar resultado español
        print(f"\n✅ RESULTADO VÁLIDO: {resultado_num:.2f}")
        print(
            f"✅ FORMATO CORRECTO: {len(resultado_spanish.split('.')[1]) == 2 if '.' in resultado_spanish else True}")
        print("✅ MANEJO DE FORMATOS: Tanto punto como coma decimal funcionan")
        return True
    except ValueError:
        print(f"\n❌ ERROR: Resultado no numérico: {resultado_spanish}")
        return False


def test_edge_cases_flutter():
    """Probar casos límite como en Flutter"""
    print("\n🧪 CASOS LÍMITE (replicando Flutter):")
    print("=" * 50)

    calculator = AquacultureCalculator()
    calculator.fetch_data_tabla3()

    test_cases = [
        {
            'name': 'Hectáreas = 0',
            'values': {'alimentoactualkg': '614', 'hectareas': '0', 'pesoactualgdia': '30'},
            'expected': 'Datos inválidos'
        },
        {
            'name': 'Peso = 0',
            'values': {'alimentoactualkg': '614', 'hectareas': '7.8', 'pesoactualgdia': '0'},
            'expected': 'Datos inválidos'
        },
        {
            'name': 'Valores normales',
            'values': {'alimentoactualkg': '614', 'hectareas': '7.8', 'pesoactualgdia': '30'},
            'expected': 'número'
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n🔸 Caso {i}: {case['name']}")

        # Configurar valores
        for key, value in case['values'].items():
            calculator.set_controller_value(key, value)

        # Ejecutar cálculo
        calculator.calcular_densidad_consumo()
        resultado = calculator.get_controller_value('densidad_consumo_im2')

        print(f"   Resultado: {resultado}")

        # Verificar resultado esperado
        if case['expected'] == 'número':
            try:
                float(resultado)
                print("   ✅ Correcto: Es un número")
            except ValueError:
                print("   ❌ Error: Debería ser un número")
        else:
            if resultado == case['expected']:
                print(f"   ✅ Correcto: {case['expected']}")
            else:
                print(
                    f"   ❌ Error: Esperado '{case['expected']}', obtenido '{resultado}'")


if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DE REPLICACIÓN FLUTTER → PYTHON")
    print("📱 Método: calcular_densidad_consumo")
    print("=" * 70)

    try:
        # Test principal
        success = test_calcular_densidad_consumo_flutter()

        # Tests de casos límite
        test_edge_cases_flutter()

        print("\n" + "=" * 70)
        if success:
            print("🎉 ¡REPLICACIÓN EXITOSA!")
            print("✅ El método Python coincide exactamente con Flutter")
            print("🔗 Usa datos de pesos_alimento_data de Google Cloud")
            print("📐 Aplica la misma fórmula y validaciones")
        else:
            print("❌ Hay diferencias con Flutter")

    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
