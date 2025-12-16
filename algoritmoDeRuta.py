import requests, heapq, tkinter as tk
from tkinter import ttk, scrolledtext
from collections import defaultdict

API = {
    "serviceAlerts": "https://apitransporte.buenosaires.gob.ar/subtes/serviceAlerts",
    "forecastGTFS": "https://apitransporte.buenosaires.gob.ar/subtes/forecastGTFS",
    "vehiclePositions": "https://apitransporte.buenosaires.gob.ar/subtes/vehiclePositions"
}

PARAMS = {"client_id":"TU_ID","client_secret":"TU_SECRET","json":1}

LINEAS = {
    'A': ['Plaza de Mayo', 'Perú', 'Congreso', 'San Pedrito'],
    'B': ['Leandro N. Alem', 'Carlos Pellegrini', 'Federico Lacroze'],
    'C': ['Retiro', 'Diagonal Norte', 'Constitución']
}

BG, BTN = "#f1fbf4", "#6fbf73"

class RutaSubte:
    def __init__(self, root):
        self.root = root
        root.title("🚇 Ruta Subte BA")
        root.geometry("600x380")
        root.configure(bg=BG)

        self.grafo = self.crear_grafo()
        self.demoras = defaultdict(int)

        self.cargar_datos()
        self.crear_ui()

    def crear_grafo(self):
        grafo = defaultdict(dict)
        for linea, estaciones in LINEAS.items():
            for i in range(len(estaciones)-1):
                grafo[estaciones[i]][estaciones[i+1]] = {'tiempo': 2, 'linea': linea}
                grafo[estaciones[i+1]][estaciones[i]] = {'tiempo': 2, 'linea': linea}
        return grafo
        
    def cargar_datos(self):
        try:
            data = requests.get(API["serviceAlerts"], params=PARAMS, timeout=5).json()
            if "demora" in str(data).lower():
                self.demoras['A'] = 5  
        except:
            self.demoras['A'] = 5 


        self.forecast = API["forecastGTFS"]
        self.vehicles = API["vehiclePositions"]

    def dijkstra(self, origen, destino):
        dist = {e: float('inf') for e in self.grafo}
        dist[origen] = 0
        cola = [(0, origen)]
        previo = {}

        while cola:
            actual, u = heapq.heappop(cola)
            for v, datos in self.grafo[u].items():
                peso = datos['tiempo'] + self.demoras[datos['linea']]
                if actual + peso < dist[v]:
                    dist[v] = actual + peso
                    previo[v] = u
                    heapq.heappush(cola, (dist[v], v))

        ruta = []
        while destino in previo:
            ruta.insert(0, destino)
            destino = previo[destino]
        return ruta, dist[ruta[-1]] if ruta else 0

    def calcular_ruta(self):
        o, d = self.origen.get(), self.destino.get()
        ruta, tiempo = self.dijkstra(o, d)
        self.resultado.delete(1.0, tk.END)
        self.resultado.insert(tk.END,
            f"Ruta: {' → '.join([o] + ruta)}\nTiempo estimado: {tiempo} min")

    def crear_ui(self):
        estaciones = sorted({e for l in LINEAS.values() for e in l})

        ttk.Label(self.root, text="Origen").pack()
        self.origen = ttk.Combobox(self.root, values=estaciones)
        self.origen.pack()

        ttk.Label(self.root, text="Destino").pack()
        self.destino = ttk.Combobox(self.root, values=estaciones)
        self.destino.pack()

        tk.Button(self.root, text="Calcular Ruta",
                  bg=BTN, fg="white", command=self.calcular_ruta).pack(pady=8)

        self.resultado = scrolledtext.ScrolledText(self.root, height=8)
        self.resultado.pack(fill="both", expand=True, padx=10)

root = tk.Tk()
RutaSubte(root)
root.mainloop()
