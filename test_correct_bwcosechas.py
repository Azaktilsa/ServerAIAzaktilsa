#!/usr/bin/env python3
"""
Test para verificar que con el BWCosechas correcto (2.58516749708439%) 
para peso 30.0, el cálculo produce exactamente 10.15
"""

from app.alimentation import AquacultureCalculator
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_correct_bwcosechas():
    """Test con el valor correcto de BWCosechas del archivo real"""

    calculator = AquacultureCalculator()
    calculator.fetch_data_tabla3()

    # Datos de prueba que sabemos que deben producir 10.15
    calculator.set_controller_value('alimento_actual_kg', '614')
    calculator.set_controller_value('hectareas', '7,8')  # Formato español
    calculator.set_controller_value(
        'peso_actual_gdia', '30,0')  # Formato español

    print("🔍 Verificando datos cargados:")

    # Buscar el valor de BWCosechas para peso 30.0
    for row in calculator.pesos_alimento_data['rows']:
        if float(row['Pesos']) == 30.0:
            print(
                f"✅ Peso 30.0 encontrado con BWCosechas: {row['BWCosechas']}")
            break
    else:
        print("❌ No se encontró peso 30.0 en los datos")

    # Calcular densidad de consumo
    resultado = calculator.calcular_densidad_consumo()

    print(f"\n📊 Resultado del cálculo:")
    print(f"Densidad por consumo: {resultado}")
    print(f"¿Es exactamente 10.15? {resultado == '10.15'}")

    # También probar con formato inglés
    calculator.set_controller_value('hectareas', '7.8')  # Formato inglés
    calculator.set_controller_value(
        'peso_actual_gdia', '30.0')  # Formato inglés

    resultado_en = calculator.calcular_densidad_consumo()
    print(f"Con formato inglés: {resultado_en}")
    print(f"¿Es exactamente 10.15? {resultado_en == '10.15'}")

    return resultado == '10.15' and resultado_en == '10.15'


if __name__ == "__main__":
    print("🧪 Probando con el valor correcto de BWCosechas...")
    print("=" * 60)

    success = test_correct_bwcosechas()

    print("\n" + "=" * 60)
    if success:
        print("✅ ¡ÉXITO! El cálculo produce exactamente 10.15 con el BWCosechas correcto")
    else:
        print("❌ ERROR: El cálculo no produce 10.15")
