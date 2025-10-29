import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
import heapq
from collections import defaultdict

class AlgoritmoRutaTiempoReal:
    def _init_(self, root):
        self.root = root
        self.root.title("🚇 Algoritmo de Ruta con Tiempo Real - Subte BA")
        self.root.geometry("1100x750")
        
        # Paleta de colores verde pastel
        self.COLOR_FONDO = "#f8fff8"
        self.COLOR_TARJETA = "#ffffff"
        self.COLOR_HEADER = "#90be6d"
        self.COLOR_BOTON = "#a3c585"
        self.COLOR_TEXTO = "#2c5530"
        self.COLOR_SECUNDARIO = "#666666"
        self.COLOR_ACENTO = "#7cb518"
        self.COLOR_BORDE = "#e8f5e8"
        
        self.root.configure(bg=self.COLOR_FONDO)
        
        # Configuración API
        self.API_URLS = {
            "serviceAlerts": "https://apitransporte.buenosaires.gob.ar/subtes/serviceAlerts",
            "forecastGTFS": "https://apitransporte.buenosaires.gob.ar/subtes/forecastGTFS",
            "vehiclePositions": "https://apitransporte.buenosaires.gob.ar/subtes/vehiclePositions"
        }
        self.PARAMS = {
            "client_id": "f9a747a11dd94ea4984ebeba4091cbc7",
            "client_secret": "c73671B7b5234410AE0a4265C16B8e9F",
            "json": 1
        }
        
        # Estructura de datos de estado en tiempo real
        self.estado_tiempo_real = {
            "alertas_activas": [],
            "demoras_por_linea": defaultdict(int),
            "trenes_en_servicio": defaultdict(list),
            "estaciones_afectadas": set(),
            "timestamp_actualizacion": None
        }
        
        # Datos de la red de subte
        self.grafo_subte = self.inicializar_grafo_completo()
        self.estaciones = self.cargar_estaciones()
        self.conexiones = self.definir_conexiones()
        
        self.setup_ui()
        self.actualizar_datos_tiempo_real()

    def definir_conexiones(self):
        """Define las conexiones entre líneas para transbordos"""
        return {
            'Plaza de Mayo': {'lineas': ['A', 'D', 'C'], 'tiempo_transbordo': 5},
            'Perú': {'lineas': ['A', 'C'], 'tiempo_transbordo': 5},
            'Avenida de Mayo': {'lineas': ['C', 'E'], 'tiempo_transbordo': 5},
            'Catedral': {'lineas': ['D', 'B'], 'tiempo_transbordo': 5},
            '9 de Julio': {'lineas': ['B', 'D'], 'tiempo_transbordo': 5},
            'Carlos Pellegrini': {'lineas': ['B'], 'tiempo_transbordo': 0},
            'Retiro': {'lineas': ['C', 'E'], 'tiempo_transbordo': 5},
            'Once': {'lineas': ['H', 'A'], 'tiempo_transbordo': 5},
            'Plaza Miserere': {'lineas': ['A', 'H'], 'tiempo_transbordo': 5}
        }
        
    def inicializar_grafo_completo(self):
        """Inicializa el grafo completo de la red de subte"""
        grafo = defaultdict(dict)
        
        # Definir todas las líneas con tiempos base
        lineas = {
            'A': ['Plaza de Mayo', 'Perú', 'Piedras', 'Lima', 'Sáenz Peña', 'Congreso', 'Pasco', 
                  'Alberti', 'Plaza Miserere', 'Loria', 'Castro Barros', 'Río de Janeiro', 'Acoyte', 
                  'Primera Junta', 'Puán', 'Carabobo', 'San Pedrito'],
            'B': ['Leandro N. Alem', 'Florida', 'Carlos Pellegrini', 'Uruguay', 'Callao', 'Pasteur', 
                  'Pueyrredón', 'Carlos Gardel', 'Medrano', 'Ángel Gallardo', 'Malabia', 'Dorrego', 
                  'Federico Lacroze'],
            'C': ['Retiro', 'General San Martín', 'Lavalle', 'Diagonal Norte', 'Avenida de Mayo', 
                  'Moreno', 'Independencia', 'San Juan', 'Constitución'],
            'D': ['Catedral', '9 de Julio', 'Tribunales', 'Facultad de Medicina', 'Pueyrredón', 
                  'Agüero', 'Bulnes', 'Scalabrini Ortiz', 'Plaza Italia', 'Palermo', 'Ministro Carranza', 
                  'Olleros', 'José Hernández', 'Juramento', 'Congreso de Tucumán'],
            'E': ['Retiro', 'Catalinas', 'Correo Central', 'Bolívar', 'Belgrano', 'Independencia', 
                  'San José', 'Entre Ríos', 'Pichincha', 'Jujuy', 'General Urquiza', 'Boedo', 
                  'Avenida La Plata', 'José María Moreno', 'Emilio Mitre', 'Medalla Milagrosa', 
                  'Varela', 'Plaza de los Virreyes'],
            'H': ['Facultad de Derecho', 'Las Heras', 'Santa Fe', 'Córdoba', 'Corrientes', 'Once', 
                  'Venezuela', 'Humberto I', 'Inclán', 'Caseros', 'Parque Patricios']
        }
        
        # Construir grafo con tiempos base
        for linea, estaciones in lineas.items():
            for i in range(len(estaciones)-1):
                grafo[estaciones[i]][estaciones[i+1]] = {'tiempo_base': 2, 'linea': linea}
                grafo[estaciones[i+1]][estaciones[i]] = {'tiempo_base': 2, 'linea': linea}
        
        # Agregar conexiones entre líneas
        for estacion, info in self.definir_conexiones().items():
            for otra_estacion, otra_info in self.definir_conexiones().items():
                if estacion != otra_estacion and set(info['lineas']).intersection(set(otra_info['lineas'])):
                    grafo[estacion][otra_estacion] = {
                        'tiempo_base': info['tiempo_transbordo'], 
                        'linea': 'TRANSBORDO'
                    }
        
        return grafo
    
    def cargar_estaciones(self):
        """Carga el mapeo de estaciones por línea"""
        return {
            'A': ['Plaza de Mayo', 'Perú', 'Piedras', 'Lima', 'Sáenz Peña', 'Congreso', 'Pasco', 
                  'Alberti', 'Plaza Miserere', 'Loria', 'Castro Barros', 'Río de Janeiro', 'Acoyte', 
                  'Primera Junta', 'Puán', 'Carabobo', 'San Pedrito'],
            'B': ['Leandro N. Alem', 'Florida', 'Carlos Pellegrini', 'Uruguay', 'Callao', 'Pasteur', 
                  'Pueyrredón', 'Carlos Gardel', 'Medrano', 'Ángel Gallardo', 'Malabia', 'Dorrego', 
                  'Federico Lacroze'],
            'C': ['Retiro', 'General San Martín', 'Lavalle', 'Diagonal Norte', 'Avenida de Mayo', 
                  'Moreno', 'Independencia', 'San Juan', 'Constitución'],
            'D': ['Catedral', '9 de Julio', 'Tribunales', 'Facultad de Medicina', 'Pueyrredón', 
                  'Agüero', 'Bulnes', 'Scalabrini Ortiz', 'Plaza Italia', 'Palermo', 'Ministro Carranza', 
                  'Olleros', 'José Hernández', 'Juramento', 'Congreso de Tucumán'],
            'E': ['Retiro', 'Catalinas', 'Correo Central', 'Bolívar', 'Belgrano', 'Independencia', 
                  'San José', 'Entre Ríos', 'Pichincha', 'Jujuy', 'General Urquiza', 'Boedo', 
                  'Avenida La Plata', 'José María Moreno', 'Emilio Mitre', 'Medalla Milagrosa', 
                  'Varela', 'Plaza de los Virreyes'],
            'H': ['Facultad de Derecho', 'Las Heras', 'Santa Fe', 'Córdoba', 'Corrientes', 'Once', 
                  'Venezuela', 'Humberto I', 'Inclán', 'Caseros', 'Parque Patricios']
        }
    
    def setup_ui(self):
        """Configura la interfaz gráfica"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.COLOR_HEADER, pady=15)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(header_frame, text="🚇 Algoritmo de Ruta con Tiempo Real - Sprint 2", 
                font=('Arial', 16, 'bold'), fg='white', bg=self.COLOR_HEADER).pack()
        
        # Panel de control
        control_frame = tk.Frame(self.root, bg=self.COLOR_FONDO, pady=10)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Entradas de origen y destino
        input_frame = tk.Frame(control_frame, bg=self.COLOR_FONDO)
        input_frame.pack(fill='x', pady=5)
        
        tk.Label(input_frame, text="Origen:", bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO,
                font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, sticky='w')
        self.origen_var = tk.StringVar()
        self.origen_combo = ttk.Combobox(input_frame, textvariable=self.origen_var, width=25)
        self.origen_combo['values'] = self.obtener_todas_estaciones()
        self.origen_combo.grid(row=0, column=1, padx=5)
        
        tk.Label(input_frame, text="Destino:", bg=self.COLOR_FONDO, fg=self.COLOR_TEXTO,
                font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5, sticky='w')
        self.destino_var = tk.StringVar()
        self.destino_combo = ttk.Combobox(input_frame, textvariable=self.destino_var, width=25)
        self.destino_combo['values'] = self.obtener_todas_estaciones()
        self.destino_combo.grid(row=0, column=3, padx=5)
        
        # Botones principales
        btn_frame = tk.Frame(control_frame, bg=self.COLOR_FONDO)
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="📍 Calcular Ruta Normal", 
                 command=self.calcular_ruta_normal,
                 bg=self.COLOR_BOTON, fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="🚀 Calcular con Tiempo Real", 
                 command=self.calcular_ruta_tiempo_real,
                 bg=self.COLOR_ACENTO, fg='white', font=('Arial', 10, 'bold'),
                 padx=15, pady=8).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="📊 Comparar Rutas", 
                 command=self.comparar_rutas,
                 bg='#e67e22', fg='white', font=('Arial', 10),
                 padx=15, pady=8).pack(side='left', padx=5)
        
        # Botones de análisis
        analysis_frame = tk.Frame(control_frame, bg=self.COLOR_FONDO)
        analysis_frame.pack(fill='x', pady=5)
        
        tk.Button(analysis_frame, text="🔄 Actualizar Datos Tiempo Real", 
                 command=self.actualizar_datos_tiempo_real,
                 bg='#3498db', fg='white', font=('Arial', 9),
                 padx=10, pady=6).pack(side='left', padx=5)
        
        tk.Button(analysis_frame, text="📈 Ver Estado Red", 
                 command=self.mostrar_estado_red,
                 bg='#9b59b6', fg='white', font=('Arial', 9),
                 padx=10, pady=6).pack(side='left', padx=5)
        
        tk.Button(analysis_frame, text="📄 Generar Documento", 
                 command=self.generar_documento,
                 bg='#e74c3c', fg='white', font=('Arial', 9),
                 padx=10, pady=6).pack(side='left', padx=5)
        
        # Área de resultados
        results_frame = tk.Frame(self.root, bg=self.COLOR_FONDO)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Notebook para diferentes vistas
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Pestaña de resultados
        self.results_tab = tk.Frame(self.notebook, bg=self.COLOR_FONDO)
        self.notebook.add(self.results_tab, text="📋 Resultados de Rutas")
        
        self.results_text = scrolledtext.ScrolledText(self.results_tab, height=15, 
                                                     font=('Consolas', 10), bg=self.COLOR_TARJETA)
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Pestaña de datos API
        self.api_tab = tk.Frame(self.notebook, bg=self.COLOR_FONDO)
        self.notebook.add(self.api_tab, text="📡 Datos Tiempo Real")
        
        self.api_text = scrolledtext.ScrolledText(self.api_tab, height=15, 
                                                font=('Consolas', 8), bg=self.COLOR_TARJETA)
        self.api_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Pestaña de estado de red
        self.status_tab = tk.Frame(self.notebook, bg=self.COLOR_FONDO)
        self.notebook.add(self.status_tab, text="🚦 Estado de la Red")
        
        self.status_text = scrolledtext.ScrolledText(self.status_tab, height=15, 
                                                   font=('Consolas', 9), bg=self.COLOR_TARJETA)
        self.status_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Footer
        footer_frame = tk.Frame(self.root, bg=self.COLOR_BORDE, pady=8)
        footer_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = tk.Label(footer_frame, 
                                   text=f"Estado: Inicializando - {datetime.datetime.now().strftime('%H:%M:%S')}", 
                                   font=('Arial', 9), fg=self.COLOR_SECUNDARIO, bg=self.COLOR_BORDE)
        self.status_label.pack()
        
    def obtener_todas_estaciones(self):
        """Obtiene todas las estaciones disponibles"""
        todas_estaciones = []
        for linea, estaciones in self.estaciones.items():
            todas_estaciones.extend(estaciones)
        return sorted(set(todas_estaciones))
    
    def actualizar_datos_tiempo_real(self):
        """Actualiza los datos en tiempo real desde la API"""
        try:
            self.status_label.config(text="Estado: Actualizando datos tiempo real...")
            
            # Limpiar estado anterior
            self.estado_tiempo_real = {
                "alertas_activas": [],
                "demoras_por_linea": defaultdict(int),
                "trenes_en_servicio": defaultdict(list),
                "estaciones_afectadas": set(),
                "timestamp_actualizacion": datetime.datetime.now()
            }
            
            # Obtener datos de serviceAlerts
            response = requests.get(self.API_URLS["serviceAlerts"], params=self.PARAMS, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.procesar_alertas_tiempo_real(data)
                self.api_text.delete(1.0, tk.END)
                self.api_text.insert(tk.END, "✅ Datos en tiempo real actualizados\n\n")
                self.api_text.insert(tk.END, json.dumps(data, indent=2, ensure_ascii=False))
            else:
                self.api_text.delete(1.0, tk.END)
                self.api_text.insert(tk.END, f"❌ Error API: {response.status_code}\n")
                # Usar datos de demostración
                self.usar_datos_demostracion()
                
            self.actualizar_panel_estado()
            self.status_label.config(text=f"Estado: Datos actualizados - {datetime.datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.api_text.delete(1.0, tk.END)
            self.api_text.insert(tk.END, f"❌ Error conexión: {str(e)}\n")
            self.usar_datos_demostracion()
            self.status_label.config(text=f"Estado: Usando datos demo - {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    def procesar_alertas_tiempo_real(self, data):
        """Procesa las alertas en tiempo real y actualiza el estado"""
        if 'entities' in data:
            for entity in data['entities']:
                if 'alert' in entity:
                    alerta = entity['alert']
                    header_text = alerta.get('header_text', {}).get('translation', [{}])[0].get('text', '')
                    
                    # REGLA 1: Detectar demoras por mantenimiento
                    if any(keyword in header_text.lower() for keyword in ['demora', 'mantenimiento', 'lento']):
                        for entidad in alerta.get('informed_entity', []):
                            if 'route_id' in entidad:
                                linea = entidad['route_id'].replace('Subte_', '')
                                self.estado_tiempo_real["demoras_por_linea"][linea] += 5  # +5 minutos
                    
                    # REGLA 2: Detectar suspensiones totales
                    elif any(keyword in header_text.lower() for keyword in ['suspendido', 'interrumpido', 'corte']):
                        for entidad in alerta.get('informed_entity', []):
                            if 'route_id' in entidad:
                                linea = entidad['route_id'].replace('Subte_', '')
                                self.estado_tiempo_real["demoras_por_linea"][linea] += 15  # +15 minutos
                    
                    self.estado_tiempo_real["alertas_activas"].append(header_text)
    
    def usar_datos_demostracion(self):
        """Usa datos de demostración cuando la API no está disponible"""
        # Simular demora en línea A por mantenimiento
        self.estado_tiempo_real["demoras_por_linea"]['A'] = 8
        self.estado_tiempo_real["alertas_activas"].append("Línea A - Demoras por mantenimiento de vías")
        
        # Simular problema menor en línea D
        self.estado_tiempo_real["demoras_por_linea"]['D'] = 3
        self.estado_tiempo_real["alertas_activas"].append("Línea D - Circulación lenta por alta demanda")
    
    def calcular_tiempo_arista(self, origen, destino, datos_arista):
        """Calcula el tiempo real de una arista considerando demoras"""
        tiempo_base = datos_arista['tiempo_base']
        linea = datos_arista['linea']
        
        # REGLA 3: Aplicar demoras por línea
        if linea in self.estado_tiempo_real["demoras_por_linea"]:
            tiempo_base += self.estado_tiempo_real["demoras_por_linea"][linea]
        
        # REGLA 4: Penalizar transbordos en estaciones problemáticas
        if linea == 'TRANSBORDO' and origen in self.estado_tiempo_real["estaciones_afectadas"]:
            tiempo_base += 2
        
        return tiempo_base
    
    def dijkstra_tiempo_real(self, origen, destino, usar_tiempo_real=True):
        """Algoritmo de Dijkstra mejorado para considerar datos en tiempo real"""
        distancias = {estacion: float('inf') for estacion in self.grafo_subte}
        distancias[origen] = 0
        previo = {}
        cola = [(0, origen)]
        
        while cola:
            distancia_actual, estacion_actual = heapq.heappop(cola)
            
            if estacion_actual == destino:
                break
                
            if distancia_actual > distancias[estacion_actual]:
                continue
                
            for vecina, datos_arista in self.grafo_subte[estacion_actual].items():
                if usar_tiempo_real:
                    peso = self.calcular_tiempo_arista(estacion_actual, vecina, datos_arista)
                else:
                    peso = datos_arista['tiempo_base']  # Tiempo base sin ajustes
                
                nueva_distancia = distancia_actual + peso
                if nueva_distancia < distancias[vecina]:
                    distancias[vecina] = nueva_distancia
                    previo[vecina] = estacion_actual
                    heapq.heappush(cola, (nueva_distancia, vecina))
        
        # Reconstruir ruta
        ruta = []
        actual = destino
        while actual in previo:
            ruta.insert(0, actual)
            actual = previo[actual]
        if ruta or origen == destino:
            ruta.insert(0, origen)
        
        return ruta, distancias.get(destino, float('inf'))
    
    def calcular_ruta_normal(self):
        """Calcula ruta SIN considerar datos en tiempo real"""
        origen = self.origen_var.get()
        destino = self.destino_var.get()
        
        if not self.validar_entradas(origen, destino):
            return
        
        ruta, tiempo = self.dijkstra_tiempo_real(origen, destino, usar_tiempo_real=False)
        self.mostrar_resultado("RUTA NORMAL (Sin datos tiempo real)", ruta, tiempo)
    
    def calcular_ruta_tiempo_real(self):
        """Calcula ruta CONSIDERANDO datos en tiempo real"""
        origen = self.origen_var.get()
        destino = self.destino_var.get()
        
        if not self.validar_entradas(origen, destino):
            return
        
        ruta, tiempo = self.dijkstra_tiempo_real(origen, destino, usar_tiempo_real=True)
        self.mostrar_resultado("RUTA OPTIMIZADA (Con datos tiempo real)", ruta, tiempo, True)
    
    def comparar_rutas(self):
        """Compara rutas con y sin datos en tiempo real"""
        origen = self.origen_var.get()
        destino = self.destino_var.get()
        
        if not self.validar_entradas(origen, destino):
            return
        
        # EJEMPLO 1: Ruta normal
        ruta_normal, tiempo_normal = self.dijkstra_tiempo_real(origen, destino, usar_tiempo_real=False)
        
        # EJEMPLO 2: Ruta con tiempo real
        ruta_real, tiempo_real = self.dijkstra_tiempo_real(origen, destino, usar_tiempo_real=True)
        
        resultado = "📊 COMPARACIÓN DE RUTAS - EJEMPLO PRÁCTICO\n"
        resultado += "=" * 60 + "\n\n"
        
        resultado += "📍 RUTA NORMAL (Sin datos tiempo real):\n"
        resultado += f"Ruta: {' → '.join(ruta_normal) if ruta_normal else 'No encontrada'}\n"
        resultado += f"Tiempo estimado: {tiempo_normal} minutos\n\n"
        
        resultado += "🚀 RUTA OPTIMIZADA (Con datos tiempo real):\n"
        resultado += f"Ruta: {' → '.join(ruta_real) if ruta_real else 'No encontrada'}\n"
        resultado += f"Tiempo estimado: {tiempo_real} minutos\n\n"
        
        # Análisis de diferencias
        if ruta_normal and ruta_real:
            diferencia = tiempo_real - tiempo_normal
            
            resultado += "🔍 ANÁLISIS DE DIFERENCIAS:\n"
            if diferencia > 0:
                resultado += f"• La ruta optimizada es {diferencia} minutos más lenta\n"
                resultado += "• Razón: Demoras detectadas en tiempo real\n"
            elif diferencia < 0:
                resultado += f"• La ruta optimizada es {abs(diferencia)} minutos más rápida\n"
                resultado += "• Razón: Evitación de zonas problemáticas\n"
            else:
                resultado += "• Ambas rutas tienen el mismo tiempo estimado\n"
                resultado += "• Razón: No hay alertas activas que afecten esta ruta\n"
            
            # Mostrar reglas aplicadas
            resultado += "\n🎯 REGLAS APLICADAS EN TIEMPO REAL:\n"
            for linea, demora in self.estado_tiempo_real["demoras_por_linea"].items():
                if demora > 0:
                    resultado += f"• Línea {linea}: +{demora} minutos por demoras\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, resultado)
    
    def validar_entradas(self, origen, destino):
        """Valida las entradas del usuario"""
        if not origen or not destino:
            self.mostrar_error("Seleccione origen y destino")
            return False
        if origen not in self.grafo_subte or destino not in self.grafo_subte:
            self.mostrar_error("Estaciones no válidas")
            return False
        return True
    
    def mostrar_resultado(self, titulo, ruta, tiempo, con_tiempo_real=False):
        """Muestra el resultado del cálculo de ruta"""
        resultado = f"{titulo}\n"
        resultado += "=" * 60 + "\n\n"
        
        if ruta and tiempo < float('inf'):
            resultado += f"📍 Ruta calculada ({len(ruta)} estaciones):\n"
            for i, estacion in enumerate(ruta, 1):
                linea = self.obtener_linea_estacion(estacion)
                resultado += f"{i}. {estacion} (Línea {linea})\n"
            
            resultado += f"\n⏱  Tiempo total estimado: {tiempo} minutos\n"
            
            if con_tiempo_real:
                resultado += f"\n📡 FACTORES DE TIEMPO REAL CONSIDERADOS:\n"
                for alerta in self.estado_tiempo_real["alertas_activas"]:
                    resultado += f"• {alerta}\n"
        else:
            resultado += "❌ No se pudo calcular una ruta entre las estaciones seleccionadas\n"
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, resultado)
    
    def obtener_linea_estacion(self, estacion):
        """Obtiene la línea de una estación"""
        for linea, estaciones in self.estaciones.items():
            if estacion in estaciones:
                return linea
        return "?"
    
    def mostrar_estado_red(self):
        """Muestra el estado actual de la red de subte"""
        self.actualizar_panel_estado()
        self.notebook.select(2)  # Cambiar a pestaña de estado
    
    def actualizar_panel_estado(self):
        """Actualiza el panel de estado de la red"""
        estado = "🚦 ESTADO DE LA RED - TIEMPO REAL\n"
        estado += "=" * 50 + "\n\n"
        
        estado += f"🕐 Última actualización: {self.estado_tiempo_real['timestamp_actualizacion'].strftime('%H:%M:%S')}\n\n"
        
        estado += "📊 RESUMEN POR LÍNEA:\n"
        for linea in ['A', 'B', 'C', 'D', 'E', 'H']:
            demora = self.estado_tiempo_real["demoras_por_linea"][linea]
            if demora == 0:
                estado += f"• Línea {linea}: ✅ Normal ({len(self.estaciones[linea])} estaciones)\n"
            elif demora <= 5:
                estado += f"• Línea {linea}: 🟡 Demoras leves (+{demora} min)\n"
            else:
                estado += f"• Línea {linea}: 🔴 Demoras significativas (+{demora} min)\n"
        
        estado += f"\n🚨 ALERTAS ACTIVAS: {len(self.estado_tiempo_real['alertas_activas'])}\n"
        for alerta in self.estado_tiempo_real['alertas_activas']:
            estado += f"• {alerta}\n"
        
        estado += f"\n🏗  ESTRUCTURA DE DATOS DE ESTADO:\n"
        estado += f"• Alertas activas: {len(self.estado_tiempo_real['alertas_activas'])}\n"
        estado += f"• Líneas con demoras: {len([x for x in self.estado_tiempo_real['demoras_por_linea'].values() if x > 0])}\n"
        estado += f"• Estaciones en grafo: {len(self.grafo_subte)}\n"
        estado += f"• Conexiones de transbordo: {len(self.conexiones)}\n"
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, estado)
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        messagebox.showerror("Error", mensaje)
    
    def generar_documento(self):
        """Genera documentación del algoritmo mejorado"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Algoritmo_Tiempo_Real_Mejorado_{timestamp}.txt"
            
            contenido = self.generar_contenido_documento()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            messagebox.showinfo("Éxito", f"Documento generado: {filename}")
            
        except Exception as e:
            self.mostrar_error(f"Error al generar documento: {str(e)}")
    
    def generar_contenido_documento(self):
        """Genera el contenido del documento técnico"""
        contenido = "ALGORITMO DE RUTA CON TIEMPO REAL - SPRINT 2\n"
        contenido += "=" * 70 + "\n\n"
        
        contenido += "FECHA DE GENERACIÓN: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n"
        
        contenido += "1. MEJORAS IMPLEMENTADAS SOBRE SPRINT 1\n"
        contenido += "-" * 50 + "\n"
        contenido += "• Integración completa con API de tiempo real\n"
        contenido += "• Estructura de datos de estado en tiempo real\n"
        contenido += "• Reglas inteligentes para rutas alternativas\n"
        contenido += "• Sistema de demoras dinámicas por línea\n"
        contenido += "• Mecanismo de fallback con datos de demostración\n\n"
        
        contenido += "2. INTEGRACIÓN DE DATOS EN TIEMPO REAL\n"
        contenido += "-" * 50 + "\n"
        contenido += "• Fuente: API Buenos Aires Data (serviceAlerts)\n"
        contenido += "• Frecuencia: Actualización bajo demanda\n"
        contenido += "• Procesamiento: Análisis de alertas y demoras\n"
        contenido += "• Estructura: Estado global de la red\n\n"
        
        contenido += "3. REGLAS PARA RUTAS ALTERNATIVAS\n"
        contenido += "-" * 50 + "\n"
        contenido += "REGLA 1: Demoras por mantenimiento → +5 min por línea\n"
        contenido += "REGLA 2: Suspensiones totales → +15 min por línea\n"
        contenido += "REGLA 3: Ajuste dinámico de tiempos por arista\n"
        contenido += "REGLA 4: Penalización de transbordos problemáticos\n\n"
        
        contenido += "4. ESTRUCTURA DE DATOS DE ESTADO\n"
        contenido += "-" * 50 + "\n"
        contenido += "estado_tiempo_real = {\n"
        contenido += "  'alertas_activas': [lista de alertas],\n"
        contenido += "  'demoras_por_linea': {linea: minutos},\n"
        contenido += "  'trenes_en_servicio': {linea: [trenes]},\n"
        contenido += "  'estaciones_afectadas': set(),\n"
        contenido += "  'timestamp_actualizacion': datetime\n"
        contenido += "}\n\n"
        
        contenido += "5. EJEMPLOS IMPLEMENTADOS\n"
        contenido += "-" * 50 + "\n"
        contenido += "• Ruta normal: Cálculo con tiempos base estáticos\n"
        contenido += "• Ruta optimizada: Considera estado actual de la red\n"
        contenido += "• Comparación side-by-side: Análisis de diferencias\n"
        contenido += "• Datos demostración: Funcionamiento sin conexión\n\n"
        
        contenido += "6. ENDPOINTS UTILIZADOS\n"
        contenido += "-" * 50 + "\n"
        contenido += "• Service Alerts: /subtes/serviceAlerts\n"
        contenido += "• Forecast GTFS: /subtes/forecastGTFS\n"
        contenido += "• Vehicle Positions: /subtes/vehiclePositions\n"
        
        return contenido

def main():
    root = tk.Tk()
    app = AlgoritmoRutaTiempoReal(root)
    root.mainloop()

if _name_ == "_main_":
    main()
