#!/usr/bin/env python3
"""
Test para encontrar el factor correcto que hace que el resultado sea 10.15
"""

from app.alimentation import AquacultureCalculator


def test_factor_correction():
    """Probar diferentes factores para llegar a 10.15"""
    print("🔍 BÚSQUEDA DEL FACTOR CORRECTO PARA EXCEL")
    print("=" * 50)
    
    # Valores conocidos
    alimento_kg = 614.0
    hectareas = 7.8
    peso_g = 30.0
    objetivo_excel = 10.15
    
    calculator = AquacultureCalculator()
    calculator.fetch_data_tabla3()
    
    # Obtener BWCosechas original
    if calculator.pesos_alimento_data and 'rows' in calculator.pesos_alimento_data:
        data = calculator.pesos_alimento_data['rows']
        
        vlookup_result = None
        for row in data:
            if "Pesos" in row and "BWCosechas" in row:
                peso = float(str(row["Pesos"]))
                if peso <= peso_g:
                    if vlookup_result is None or peso > vlookup_result['peso']:
                        vlookup_result = {
                            'peso': peso,
                            'bw_raw': row["BWCosechas"]
                        }
        
        if vlookup_result:
            bw_raw = vlookup_result['bw_raw']
            bw_value = float(str(bw_raw).replace('%', '').strip())
            
            print(f"📋 DATOS BASE:")
            print(f"   Alimento: {alimento_kg} kg")
            print(f"   Hectáreas: {hectareas} ha")
            print(f"   Peso: {peso_g} g")
            print(f"   BWCosechas (VLOOKUP): {bw_value}")
            print(f"   Objetivo Excel: {objetivo_excel}")
            
            print(f"\n🧮 PROBANDO DIFERENTES FÓRMULAS:")
            
            # Fórmula base
            numerador = (alimento_kg / hectareas) * 10
            print(f"   Numerador: ({alimento_kg}/{hectareas}) * 10 = {numerador}")
            
            # Probar diferentes interpretaciones del denominador
            formulas = [
                {
                    'name': 'Original Python/Flutter',
                    'denominador': peso_g * bw_value,
                    'formula': f"{peso_g} * {bw_value}"
                },
                {
                    'name': 'Excel con *100',
                    'denominador': peso_g * (bw_value * 100),
                    'formula': f"{peso_g} * ({bw_value} * 100)"
                },
                {
                    'name': 'Excel con /100',
                    'denominador': peso_g * (bw_value / 100),
                    'formula': f"{peso_g} * ({bw_value} / 100)"
                },
                {
                    'name': 'BWCosechas como decimal',
                    'denominador': peso_g * (bw_value / 100),
                    'formula': f"{peso_g} * {bw_value/100}"
                },
                {
                    'name': 'Factor de conversión x50',
                    'denominador': peso_g * (bw_value / 50),
                    'formula': f"{peso_g} * ({bw_value} / 50)"
                },
                {
                    'name': 'Factor de conversión x47.7',
                    'denominador': peso_g * (bw_value / 47.7),
                    'formula': f"{peso_g} * ({bw_value} / 47.7)"
                }
            ]
            
            for formula in formulas:
                resultado = numerador / formula['denominador']
                diferencia = abs(resultado - objetivo_excel)
                
                print(f"\n   {formula['name']}:")
                print(f"     Fórmula: {numerador} / ({formula['formula']})")
                print(f"     Denominador: {formula['denominador']:.6f}")
                print(f"     Resultado: {resultado:.2f}")
                print(f"     Diferencia con 10.15: {diferencia:.6f}")
                
                if diferencia < 0.01:
                    print(f"     ✅ ¡COINCIDE!")
                    
            # Calcular el factor exacto necesario
            factor_exacto = (numerador / objetivo_excel) / peso_g
            print(f"\n🎯 FACTOR EXACTO NECESARIO:")
            print(f"   Para obtener {objetivo_excel}, BWCosechas debe ser: {factor_exacto:.10f}")
            print(f"   Relación con nuestro BWCosechas: {bw_value / factor_exacto:.6f}")


if __name__ == "__main__":
    test_factor_correction()
