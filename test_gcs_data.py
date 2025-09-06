#!/usr/bin/env python3
"""
Test para verificar que se cargan datos correctos desde Google Cloud Storage
"""

from app.alimentation import cargar_pesos_alimento, AquacultureCalculator
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    print("🔍 Probando carga de datos desde Google Cloud Storage...")

    # Cargar datos desde GCS
    pesos_data = cargar_pesos_alimento()

    if not pesos_data or 'rows' not in pesos_data:
        print("❌ Error: No se pudieron cargar los datos")
        return

    print(f"📊 Total de registros: {len(pesos_data['rows'])}")

    # Buscar el registro para peso 30.0
    peso_30_record = None
    for row in pesos_data['rows']:
        if row.get('Pesos') == 30.0 or row.get('Pesos') == 30:
            peso_30_record = row
            break

    if peso_30_record:
        print(f"✅ Registro para Peso 30.0 encontrado:")
        print(f"   BWCosechas: {peso_30_record['BWCosechas']}")
        print(f"   Pesos: {peso_30_record['Pesos']}")

        # Verificar que sea el valor correcto
        expected_bw = "2.58516749708439%"
        if peso_30_record['BWCosechas'] == expected_bw:
            print(f"✅ BWCosechas correcto: {expected_bw}")
        else:
            print(
                f"❌ BWCosechas incorrecto. Esperado: {expected_bw}, Encontrado: {peso_30_record['BWCosechas']}")
    else:
        print("❌ No se encontró registro para Peso 30.0")
        # Mostrar algunos registros para debuggear
        print("📋 Primeros 5 registros:")
        for i, row in enumerate(pesos_data['rows'][:5]):
            print(
                f"   {i+1}. Pesos: {row.get('Pesos')}, BWCosechas: {row.get('BWCosechas')}")

    print("\n🧮 Probando cálculo de densidad de consumo...")

    # Crear calculadora y probar el cálculo
    calculator = AquacultureCalculator()

    # Configurar valores de prueba
    calculator.set_controller_value('alimento_actual_kg', '614')
    calculator.set_controller_value('hectareas', '7,8')  # Formato español
    calculator.set_controller_value(
        'peso_actual_gdia', '30,0')  # Formato español

    # Cargar datos de pesos
    calculator.pesos_alimento_data = pesos_data

    # Calcular densidad de consumo
    resultado = calculator.calcular_densidad_consumo()

    print(f"📊 Resultado de densidad de consumo: {resultado}")
    print(f"🎯 Esperado: 10.15")

    if resultado and abs(float(resultado) - 10.15) < 0.1:
        print("✅ ¡Cálculo correcto! El resultado coincide con Excel")
    else:
        print("❌ El resultado no coincide con el valor esperado de Excel")


if __name__ == "__main__":
    main()
