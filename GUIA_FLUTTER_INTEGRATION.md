# Guía de Integración Flutter - Sistema de Alimentación Extendido

## 📋 Resumen

El sistema de alimentación ahora acepta **datos adicionales opcionales** desde Flutter que permiten:

- ✅ Enviar datos que no son para el modelo pero enriquecen la información
- ✅ Validar consistencia entre datos calculados en Flutter vs servidor
- ✅ Obtener análisis más detallado y completo
- ✅ Rastrear metadatos de la aplicación y dispositivo

## 🔧 Modelo de Datos Actualizado

### Datos Principales (Requeridos)

Estos son los datos que **SIEMPRE** debe enviar Flutter para el modelo:

```dart
// Datos principales - REQUERIDOS
final Map<String, dynamic> datosRequeridos = {
  "finca": "CAMANOVILLO",              // String
  "Hectareas": 7.8,                    // double
  "Piscinas": 5,                       // int
  "Fechadesiembra": "10/10/2024",      // String (dd/mm/yyyy)
  "Fechademuestreo": "10/12/2024",     // String (dd/mm/yyyy)
  "Edaddelcultivo": 62,                // int
  "Pesoanterior": 23.33,               // double
  "Pesoactualgdia": 30.0,              // double
  "Densidadbiologoindm2": 11.0,        // double
  "AcumuladoactualLBS": 55042.0,       // double
  "numeroAA": 4,                       // int
  "Aireadores": 8,                     // int
  "Alimentoactualkg": 614.0,           // double
};
```

### Datos Adicionales (Opcionales)

Estos datos pueden enviarse para enriquecer la información:

```dart
// Datos adicionales - OPCIONALES
final Map<String, dynamic> datosOpcionales = {
  // Datos biológicos adicionales
  "Pesosiembra": 0.5,                  // double - Peso inicial de siembra
  "Densidadatarraya": 10.5,            // double - Densidad medida por atarraya

  // Datos técnicos
  "TipoBalanceado": "Premium",         // String - Tipo de alimento
  "MarcaAA": "AquaTech",               // String - Marca de aireadores automáticos

  // Datos pre-calculados en Flutter (para validación)
  "Incrementogr": 6.67,                // double - Incremento en gramos
  "Crecimientoactualgdia": 0.48,       // double - Crecimiento actual g/día
  "Pesoproyectadogdia": 33.0,          // double - Peso proyectado
  "Crecimientoesperadosem": 3.0,       // double - Crecimiento esperado semanal

  // Metadatos de la aplicación
  "VersionApp": "1.2.3",               // String - Versión de la app Flutter
  "DispositivoId": "DEVICE_001",       // String - ID único del dispositivo
};
```

## 📱 Implementación en Flutter

### Clase de Modelo de Datos

```dart
class PredictionRequestAlimentation {
  // Datos principales (requeridos)
  final String finca;
  final double hectareas;
  final int piscinas;
  final String fechadesiembra;
  final String fechademuestreo;
  final int edaddelcultivo;
  final double pesoanterior;
  final double pesoactualgdia;
  final double densidadbiologoindm2;
  final double acumuladoactualLBS;
  final int numeroAA;
  final int aireadores;
  final double alimentoactualkg;

  // Datos adicionales (opcionales)
  final double? pesosiembra;
  final double? densidadatarraya;
  final String? tipoBalanceado;
  final String? marcaAA;
  final double? incrementogr;
  final double? crecimientoactualgdia;
  final double? pesoproyectadogdia;
  final double? crecimientoesperadosem;
  final String? versionApp;
  final String? dispositivoId;

  PredictionRequestAlimentation({
    // Requeridos
    required this.finca,
    required this.hectareas,
    required this.piscinas,
    required this.fechadesiembra,
    required this.fechademuestreo,
    required this.edaddelcultivo,
    required this.pesoanterior,
    required this.pesoactualgdia,
    required this.densidadbiologoindm2,
    required this.acumuladoactualLBS,
    required this.numeroAA,
    required this.aireadores,
    required this.alimentoactualkg,

    // Opcionales
    this.pesosiembra,
    this.densidadatarraya,
    this.tipoBalanceado,
    this.marcaAA,
    this.incrementogr,
    this.crecimientoactualgdia,
    this.pesoproyectadogdia,
    this.crecimientoesperadosem,
    this.versionApp,
    this.dispositivoId,
  });

  Map<String, dynamic> toJson() {
    final Map<String, dynamic> data = {
      // Datos principales
      'finca': finca,
      'Hectareas': hectareas,
      'Piscinas': piscinas,
      'Fechadesiembra': fechadesiembra,
      'Fechademuestreo': fechademuestreo,
      'Edaddelcultivo': edaddelcultivo,
      'Pesoanterior': pesoanterior,
      'Pesoactualgdia': pesoactualgdia,
      'Densidadbiologoindm2': densidadbiologoindm2,
      'AcumuladoactualLBS': acumuladoactualLBS,
      'numeroAA': numeroAA,
      'Aireadores': aireadores,
      'Alimentoactualkg': alimentoactualkg,
    };

    // Agregar datos opcionales solo si no son null
    if (pesosiembra != null) data['Pesosiembra'] = pesosiembra;
    if (densidadatarraya != null) data['Densidadatarraya'] = densidadatarraya;
    if (tipoBalanceado != null) data['TipoBalanceado'] = tipoBalanceado;
    if (marcaAA != null) data['MarcaAA'] = marcaAA;
    if (incrementogr != null) data['Incrementogr'] = incrementogr;
    if (crecimientoactualgdia != null) data['Crecimientoactualgdia'] = crecimientoactualgdia;
    if (pesoproyectadogdia != null) data['Pesoproyectadogdia'] = pesoproyectadogdia;
    if (crecimientoesperadosem != null) data['Crecimientoesperadosem'] = crecimientoesperadosem;
    if (versionApp != null) data['VersionApp'] = versionApp;
    if (dispositivoId != null) data['DispositivoId'] = dispositivoId;

    return data;
  }
}
```

### Servicio de API

```dart
class AlimentationService {
  static const String baseUrl = 'https://tu-servidor.com';

  /// Envía datos de alimentación al servidor
  /// Puede incluir datos opcionales para enriquecer la respuesta
  static Future<Map<String, dynamic>> enviarDatosAlimentation({
    required PredictionRequestAlimentation request,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/predict-alimentation'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: json.encode(request.toJson()),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> resultado = json.decode(response.body);
        return _procesarRespuestaExitosa(resultado);
      } else {
        throw Exception('Error del servidor: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  /// Procesa una respuesta exitosa del servidor
  static Map<String, dynamic> _procesarRespuestaExitosa(Map<String, dynamic> data) {
    // El servidor devuelve una estructura enriquecida
    return {
      'status': data['status'],
      'mensaje': data['mensaje'],
      'finca': data['finca'],
      'resultados': data['resultados'],
      'analisis': data['analisis'],
      'metadatos': data['metadatos'],
      'datos_enviados': data['datos_enviados'],
    };
  }
}
```

### Uso en el Widget

```dart
class AlimentationScreen extends StatefulWidget {
  @override
  _AlimentationScreenState createState() => _AlimentationScreenState();
}

class _AlimentationScreenState extends State<AlimentationScreen> {
  final _formKey = GlobalKey<FormState>();

  // Controladores para datos principales
  final TextEditingController hectareasController = TextEditingController();
  final TextEditingController piscinasController = TextEditingController();
  // ... otros controladores

  // Controladores para datos opcionales
  final TextEditingController pesosiembraController = TextEditingController();
  final TextEditingController densidadatarrayaController = TextEditingController();
  String? tipoBalanceadoSeleccionado;
  String? marcaAASeleccionada;

  Future<void> _enviarDatos() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      // Crear request con datos principales
      final request = PredictionRequestAlimentation(
        // Datos principales (siempre requeridos)
        finca: 'CAMANOVILLO',
        hectareas: double.parse(hectareasController.text),
        piscinas: int.parse(piscinasController.text),
        fechadesiembra: fechasiembraController.text,
        fechademuestreo: fechamuestreoController.text,
        edaddelcultivo: int.parse(edadcultivoController.text),
        pesoanterior: double.parse(pesoanteriorController.text),
        pesoactualgdia: double.parse(pesoactualgdiaController.text),
        densidadbiologoindm2: double.parse(densidadbiologoController.text),
        acumuladoactualLBS: double.parse(acumuladoLBSController.text),
        numeroAA: int.parse(numeroAAController.text),
        aireadores: int.parse(aireadoresController.text),
        alimentoactualkg: double.parse(alimentokgController.text),

        // Datos opcionales (pueden ser null)
        pesosiembra: pesosiembraController.text.isNotEmpty
            ? double.parse(pesosiembraController.text)
            : null,
        densidadatarraya: densidadatarrayaController.text.isNotEmpty
            ? double.parse(densidadatarrayaController.text)
            : null,
        tipoBalanceado: tipoBalanceadoSeleccionado,
        marcaAA: marcaAASeleccionada,

        // Metadatos de la app
        versionApp: await _getAppVersion(),
        dispositivoId: await _getDeviceId(),

        // Datos pre-calculados (si ya los tienes en Flutter)
        incrementogr: _calcularIncrementoGramos(),
        crecimientoactualgdia: _calcularCrecimientoActual(),
      );

      // Enviar al servidor
      final resultado = await AlimentationService.enviarDatosAlimentation(
        request: request,
      );

      // Procesar respuesta
      _procesarResultado(resultado);

    } catch (e) {
      _mostrarError('Error al procesar datos: $e');
    }
  }

  void _procesarResultado(Map<String, dynamic> resultado) {
    if (resultado['status'] == 'success') {
      // ✅ Éxito - mostrar resultados
      _mostrarResultados(resultado);

      // Verificar si hay análisis inteligente
      if (resultado['analisis'] != null) {
        _mostrarAnalisis(resultado['analisis']);
      }

      // Verificar validaciones
      if (resultado['metadatos']?['validaciones'] != null) {
        _procesarValidaciones(resultado['metadatos']['validaciones']);
      }

    } else {
      // ❌ Error - mostrar mensaje
      _mostrarError(resultado['mensaje']);
    }
  }

  void _mostrarResultados(Map<String, dynamic> resultado) {
    final resultados = resultado['resultados'] as Map<String, dynamic>;

    // Mostrar datos principales
    setState(() {
      // Actualizar UI con resultados del servidor
      _edadCultivo = resultados['edad_cultivo']?.toString() ?? '';
      _pesoActual = resultados['peso_actual_gdia']?.toString() ?? '';
      _crecimientoActual = resultados['crecim_actual_gdia']?.toString() ?? '';

      // Recomendaciones semanales
      _lunesRecomendacion = resultados['lunes_dia1']?.toString() ?? '';
      _martesRecomendacion = resultados['martes_dia2']?.toString() ?? '';
      // ... otros días

      // Datos adicionales del análisis
      _fcaCampo = resultados['fca_campo']?.toString() ?? '';
      _librasTotales = resultados['libras_totales_campo']?.toString() ?? '';
    });

    // Mostrar diferencias si hay datos pre-calculados
    _mostrarDiferenciasCalculos(resultados);
  }

  void _mostrarDiferenciasCalculos(Map<String, dynamic> resultados) {
    final diferencias = resultados['diferencias_flutter_vs_calculado'];
    if (diferencias != null && diferencias.isNotEmpty) {
      // Mostrar dialog con comparación Flutter vs Servidor
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('Comparación de Cálculos'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: diferencias.entries.map<Widget>((entry) {
              final campo = entry.key;
              final datos = entry.value as Map<String, dynamic>;

              return ListTile(
                title: Text(campo.replaceAll('_', ' ').toUpperCase()),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Flutter: ${datos['flutter']}'),
                    Text('Servidor: ${datos['calculado']}'),
                    Text('Diferencia: ${datos['diferencia_porcentaje']?.toStringAsFixed(1)}%'),
                  ],
                ),
              );
            }).toList(),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  void _mostrarAnalisis(Map<String, dynamic> analisis) {
    // Mostrar problemas identificados
    if (analisis['problems']?.isNotEmpty == true) {
      _mostrarAlerta('Problemas Identificados', analisis['problems']);
    }

    // Mostrar recomendaciones
    if (analisis['recommendations']?.isNotEmpty == true) {
      _mostrarInfo('Recomendaciones', analisis['recommendations']);
    }
  }

  // ... resto de la implementación del widget
}
```

## 📤 Estructura de Respuesta del Servidor

El servidor devuelve una respuesta enriquecida con la siguiente estructura:

```json
{
  "finca": "CAMANOVILLO",
  "mensaje": "Predicción de alimentación calculada exitosamente",
  "status": "success",

  "datos_enviados": {
    "principales": {
      // Datos principales que se usaron para el modelo
    },
    "adicionales": {
      // Datos adicionales enviados desde Flutter
    }
  },

  "resultados": {
    // Todos los cálculos y recomendaciones
    "edad_cultivo": 62,
    "peso_actual_gdia": 30.0,
    "crecim_actual_gdia": 0.48,
    "lunes_dia1": 450,
    "martes_dia2": 465,
    // ... más resultados

    // Datos adicionales procesados
    "tipo_balanceado": "Premium",
    "marca_aa": "AquaTech",

    // Comparaciones Flutter vs Calculado
    "diferencias_flutter_vs_calculado": {
      "incremento_gr": {
        "flutter": 6.67,
        "calculado": 6.67,
        "diferencia_abs": 0.0,
        "diferencia_porcentaje": 0.0
      }
    },

    // Validaciones cruzadas
    "validaciones_cruzadas": {
      "fechas": {
        "edad_enviada": 62,
        "edad_calculada": 62,
        "es_consistente": true
      }
    }
  },

  "analisis": {
    "problems": [
      // Lista de problemas identificados automáticamente
    ],
    "recommendations": [
      // Lista de recomendaciones operativas
    ],
    "observations": [
      // Observaciones generales
    ]
  },

  "metadatos": {
    "version_app": "1.2.3",
    "dispositivo_id": "DEVICE_001",
    "timestamp": "2024-12-10T15:30:00",
    "campos_calculados": {
      // Todos los campos que fueron calculados por el servidor
    },
    "validaciones": {
      // Validaciones de consistencia de datos
    }
  }
}
```

## 🚀 Ventajas del Sistema Extendido

1. **Flexibilidad**: Puedes enviar solo datos requeridos o incluir opcionales
2. **Validación**: El servidor compara tus cálculos con los suyos
3. **Análisis Inteligente**: Detecta problemas automáticamente
4. **Trazabilidad**: Rastrear versión de app y dispositivo
5. **Compatibilidad**: Funciona con implementaciones existentes
6. **Diagnóstico**: Información detallada para debugging

## ⚠️ Consideraciones Importantes

- Los campos opcionales pueden enviarse como `null` o omitirse completamente
- Las fechas deben estar en formato `dd/mm/yyyy`
- Los datos principales son siempre requeridos para el modelo
- El servidor siempre calculará todos los valores, independientemente de lo que envíes
- Las comparaciones Flutter vs Servidor te ayudan a validar tus cálculos locales
