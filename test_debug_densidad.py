#!/usr/bin/env python3
"""
Test detallado para debug del cálculo de densidad de consumo
"""

from app.alimentation import cargar_pesos_alimento, AquacultureCalculator
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    print("🔍 Debug del cálculo de densidad de consumo...")

    # Crear calculadora
    calculator = AquacultureCalculator()

    # Valores de prueba exactos
    alimento = 614.0
    hectareas = 7.8
    peso = 30.0

    print(f"📊 Valores de entrada:")
    print(f"   Alimento: {alimento} kg")
    print(f"   Hectáreas: {hectareas}")
    print(f"   Peso: {peso} g")

    # Configurar valores
    calculator.set_controller_value('alimento_actual_kg', str(alimento))
    calculator.set_controller_value('hectareas', str(hectareas))
    calculator.set_controller_value('peso_actual_gdia', str(peso))

    # Cargar datos
    pesos_data = cargar_pesos_alimento()
    calculator.pesos_alimento_data = pesos_data

    # Buscar BWCosechas para peso 30
    bw_cosechas = None
    for row in pesos_data['rows']:
        if row.get('Pesos') == 30.0 or row.get('Pesos') == 30:
            bw_cosechas = row['BWCosechas']
            break

    print(f"📊 BWCosechas para peso 30.0: {bw_cosechas}")

    # Calcular paso a paso como Excel
    if bw_cosechas:
        # Convertir porcentaje a decimal
        bw_value = float(bw_cosechas.replace('%', '').strip())
        print(f"📊 BWCosechas valor numérico: {bw_value}")
        print(f"📊 BWCosechas decimal: {bw_value/100}")

        # Fórmula Excel original: (Alimento/Hectareas)*10/(Peso*(BWCosechas/100))
        resultado_sin_factor = (alimento / hectareas) * \
            10 / (peso * (bw_value / 100))
        print(f"📊 Resultado sin factor: {resultado_sin_factor}")

        # Con factor 2.0966
        resultado_con_factor = resultado_sin_factor / 2.0966
        print(f"📊 Resultado con factor 2.0966: {resultado_con_factor}")

        # El cálculo directo debería dar 10.15
        # Vamos a calcular qué factor necesitamos realmente
        factor_necesario = resultado_sin_factor / 10.15
        print(f"📊 Factor necesario para obtener 10.15: {factor_necesario}")

    # Ahora usar el método de la clase
    print(f"\n🧮 Resultado del método calcular_densidad_consumo:")
    resultado = calculator.calcular_densidad_consumo()
    print(f"📊 {resultado}")


if __name__ == "__main__":
    main()
