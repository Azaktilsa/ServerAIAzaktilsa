#!/usr/bin/env python3
"""
Test para verificar el cálculo de densidad de consumo con diferentes formatos decimales
y comparar con el resultado esperado de Excel
"""

from app.alimentation import AquacultureCalculator
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_calculo_paso_a_paso():
    """Mostrar el cálculo paso a paso para depuración"""
    print("🔬 CÁLCULO PASO A PASO DE DENSIDAD DE CONSUMO")
    print("=" * 60)
    
    calculator = AquacultureCalculator()
    calculator.fetch_data_tabla3()

    # Probar con formato español (coma decimal)
    print("📋 USANDO FORMATO ESPAÑOL (coma decimal):")
    calculator.set_controller_value('alimentoactualkg', '614')
    calculator.set_controller_value('hectareas', '7,8')  # Coma decimal
    calculator.set_controller_value('pesoactualgdia', '30,0')  # Coma decimal

    # Obtener valores parseados
    alimento_kg = calculator.parse_formatted_number('614')
    hectareas = calculator.parse_formatted_number('7,8')
    peso_g = calculator.parse_formatted_number('30,0')

    print(f"   alimentoActualKg: 614 → {alimento_kg}")
    print(f"   hectareas: 7,8 → {hectareas}")
    print(f"   pesoActualG: 30,0 → {peso_g}")

    # Buscar BWCosechas en los datos
    if calculator.pesos_alimento_data and 'rows' in calculator.pesos_alimento_data:
        data = calculator.pesos_alimento_data['rows']
        peso_encontrado = 0.0
        bw_cosechas = "0%"

        print(f"\n🔍 BÚSQUEDA EN TABLA DE PESOS:")
        print(f"   Buscando peso <= {peso_g}g...")

        for row in data:
            if "Pesos" in row and "BWCosechas" in row:
                peso = float(str(row["Pesos"]))
                if peso <= peso_g and peso > peso_encontrado:
                    peso_encontrado = peso
                    bw_cosechas = str(row["BWCosechas"])

        print(f"   Peso encontrado: {peso_encontrado}g")
        print(f"   BWCosechas: {bw_cosechas}")

        # Convertir porcentaje a decimal
        bw_decimal = float(bw_cosechas.replace('%', '').strip())
        print(f"   BWCosechas decimal: {bw_decimal}")

        # Calcular manualmente
        print(f"\n📐 CÁLCULO MANUAL:")
        print(f"   Fórmula: (alimentoKg / hectareas) * 10 / (pesoG * bwDecimal)")
        print(f"   Cálculo: ({alimento_kg} / {hectareas}) * 10 / ({peso_g} * {bw_decimal})")
        
        resultado_manual = (alimento_kg / hectareas) * 10 / (peso_g * bw_decimal)
        print(f"   Resultado manual: {resultado_manual}")
        print(f"   Resultado manual redondeado: {resultado_manual:.2f}")

    # Ejecutar el método oficial
    calculator.calcular_densidad_consumo()
    resultado_oficial = calculator.get_controller_value('densidad_consumo_im2')
    print(f"\n🎯 RESULTADO OFICIAL: {resultado_oficial}")

    return resultado_oficial


def test_con_diferentes_formatos():
    """Probar con diferentes formatos de entrada"""
    print("\n\n🧪 PRUEBA CON DIFERENTES FORMATOS")
    print("=" * 50)
    
    formatos = [
        {'name': 'Inglés (punto)', 'hectareas': '7.8', 'peso': '30.0'},
        {'name': 'Español (coma)', 'hectareas': '7,8', 'peso': '30,0'},
        {'name': 'Mixto 1', 'hectareas': '7.8', 'peso': '30,0'},
        {'name': 'Mixto 2', 'hectareas': '7,8', 'peso': '30.0'},
    ]

    for formato in formatos:
        print(f"\n🔸 Formato {formato['name']}:")
        
        calculator = AquacultureCalculator()
        calculator.fetch_data_tabla3()
        
        calculator.set_controller_value('alimentoactualkg', '614')
        calculator.set_controller_value('hectareas', formato['hectareas'])
        calculator.set_controller_value('pesoactualgdia', formato['peso'])
        
        calculator.calcular_densidad_consumo()
        resultado = calculator.get_controller_value('densidad_consumo_im2')
        
        hectareas_parsed = calculator.parse_formatted_number(formato['hectareas'])
        peso_parsed = calculator.parse_formatted_number(formato['peso'])
        
        print(f"   Hectáreas: {formato['hectareas']} → {hectareas_parsed}")
        print(f"   Peso: {formato['peso']} → {peso_parsed}")
        print(f"   Resultado: {resultado}")


def calcular_resultado_esperado_excel():
    """Calcular el resultado que esperaríamos en Excel con formato español"""
    print("\n\n📊 CÁLCULO ESPERADO EN EXCEL (formato español)")
    print("=" * 55)
    
    # Valores en formato español como aparecerían en Excel
    alimento_kg = 614.0
    hectareas = 7.8  # 7,8 en formato español
    peso_g = 30.0    # 30,0 en formato español
    
    print(f"   Alimento: {alimento_kg} kg")
    print(f"   Hectáreas: {hectareas} ha (7,8 en formato español)")
    print(f"   Peso: {peso_g} g (30,0 en formato español)")
    
    # Simular búsqueda VLOOKUP para BWCosechas
    # Asumiendo que para 30g el BWCosechas es aproximadamente 5.41934%
    bw_cosechas_percent = 5.41934447871134  # Como se encontró en las pruebas
    
    print(f"   BWCosechas: {bw_cosechas_percent}%")
    
    # Cálculo de Excel
    resultado_excel = (alimento_kg / hectareas) * 10 / (peso_g * bw_cosechas_percent)
    
    print(f"   Fórmula Excel: ({alimento_kg} / {hectareas}) * 10 / ({peso_g} * {bw_cosechas_percent})")
    print(f"   Resultado Excel: {resultado_excel}")
    print(f"   Resultado Excel redondeado: {resultado_excel:.2f}")
    
    return resultado_excel


if __name__ == "__main__":
    print("🚀 ANÁLISIS DETALLADO DE DENSIDAD DE CONSUMO")
    print("🎯 Comparando formatos decimales y resultados esperados")
    print("=" * 70)
    
    try:
        # Cálculo paso a paso
        resultado_python = test_calculo_paso_a_paso()
        
        # Prueba con diferentes formatos
        test_con_diferentes_formatos()
        
        # Cálculo esperado en Excel
        resultado_excel = calcular_resultado_esperado_excel()
        
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE RESULTADOS:")
        print(f"   Python (método oficial): {resultado_python}")
        print(f"   Excel (cálculo manual): {resultado_excel:.2f}")
        print(f"   Diferencia: {abs(float(resultado_python) - resultado_excel):.6f}")
        
        if abs(float(resultado_python) - resultado_excel) < 0.01:
            print("✅ Los resultados coinciden (diferencia < 0.01)")
        else:
            print("❌ Los resultados difieren significativamente")
            
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
