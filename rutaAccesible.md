*Algoritmo de Rutas Accesibles*
Este documento describe la modificacion del algoritmo de cálculo de rutas para incluir filtros de accesibilidad, garantizando que las rutas generadas sean adecuadas para personas con movilidad reducida u otras necesidades específicas.

Una ruta es accesible si tienen:
-Estaciones que cuentan con ascensor o rampa.
-Ausencia de tramos con escaleras sin alternativa.
-Disponibilidad de señalización táctil o sonora.
-Transporte adaptado (colectivos o vagones accesibles).

una ruta se considera accesible si todas sus estaciones o tramos cumplen al menos los criterios mínimos de accesibilidad definidos.

Para cada ruta posible:
    verificar_accesibilidad(ruta)
    si es accesible:
        agregar a resultados_accesibles
    si no es accesible=false:
        incluir todas las rutas
        
| Método | Endpoint                 | Parámetros                                  | Descripción                                    |
| ------ | ------------------------ | ------------------------------------------- | ---------------------------------------------- |
| `GET`  | `/rutas`                 | `origen`, `destino`, `accesible=true/false` | Devuelve rutas según el nivel de accesibilidad |
| `GET`  | `/estaciones/accesibles` | —                                           | Lista de estaciones accesibles                 |
| `POST` | `/rutas/filtrar`         | JSON con preferencias de accesibilidad      | Devuelve rutas personalizadas                  |

{
  "origen": "Estación Central",
  "destino": "Plaza Norte",
  "ruta_accesible": true,
  "paradas": ["Central", "Belgrano", "Norte"]
}

| Tipo de ruta | Estacioness                 | tiempo total  |observaciones                      |
| -------------| ----------------------------| --------------|-----------------------------------|
| Accesible    | Central → Belgrano → Norte` |    22 min     | Todas las estaciones con ascensor |
| No accesible | Central → Rivadavia → Norte |    18 min     | Rivadavia sin rampa               |

*La implementación de filtros de accesibilidad mejora la inclusión en el sistema de transporte, permitiendo generar rutas adaptadas a diferentes usuarios.*
