import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox
from plyer import notification

# --- CONFIGURACIÓN DE API ---
URL = "https://apitransporte.buenosaires.gob.ar/subtes/serviceAlerts"
PARAMS = {
    "client_id": "f9a747a11dd94ea4984ebeba4091cbc7",
    "client_secret": "c73671B7b5234410AE0a4265C16B8e9F",
    "json": 1
}

# --- ARCHIVO DE PREFERENCIAS ---
CONFIG_FILE = "config.json"

def cargar_preferencias():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        prefs = {"mostrar_push": True, "alertas_sonido": True}
        guardar_preferencias(prefs)
        return prefs

def guardar_preferencias(prefs):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=4)

# --- FUNCIONES PRINCIPALES ---
def obtener_alertas_subte():
    """Consulta la API y devuelve las alertas activas."""
    try:
        response = requests.get(URL, params=PARAMS, timeout=10)
        response.raise_for_status()
        data = response.json()
        entities = data.get("entities", [])
        return entities
    except Exception as e:
        print("❌ Error al obtener las alertas:", e)
        return []

def clasificar_alerta(texto):
    """Clasifica la alerta en una categoría basándose en el texto."""
    texto_lower = texto.lower()
    
    # Palabras clave para cada categoría
    fuera_servicio_keywords = [
        "suspendido", "interrumpido", "sin servicio", "fuera de servicio",
        "corte", "paralizado", "detenido", "no funciona", "desvío"
    ]
    
    mantenimiento_keywords = [
        "mantenimiento", "tareas", "trabajos", "reparación", "obras",
        "mejora", "modernización", "renovación", "signalización"
    ]
    
    funcionando_keywords = [
        "normal", "regular", "funcionando", "operativo", "sin inconvenientes",
        "habitual", "correctamente"
    ]
    
    # Verificar categorías en orden de prioridad
    for keyword in fuera_servicio_keywords:
        if keyword in texto_lower:
            return "fuera_servicio"
    
    for keyword in mantenimiento_keywords:
        if keyword in texto_lower:
            return "mantenimiento"
    
    for keyword in funcionando_keywords:
        if keyword in texto_lower:
            return "funcionan"
    
    # Por defecto, considerar como fuera de servicio si no se puede clasificar
    return "fuera_servicio"

def mostrar_alertas(entities):
    """Muestra las alertas en la interfaz organizadas por categorías."""
    # Limpiar frames existentes
    for widget in frame_fuera_servicio.winfo_children():
        widget.destroy()
    for widget in frame_mantenimiento.winfo_children():
        widget.destroy()
    for widget in frame_funcionan.winfo_children():
        widget.destroy()

    # Mostrar mensaje "No hay alertas activas" en la sección "Funcionan"
    if not entities:
        mensaje_frame = tk.Frame(frame_funcionan, bg="#2d2d2d", relief="raised", bd=1)
        mensaje_frame.pack(fill="x", padx=5, pady=2)
        
        tk.Label(mensaje_frame, text="☑", bg="#2d2d2d", fg="#44ff44", font=("Segoe UI", 10)).pack(side="left", padx=(10, 5))
        
        content_frame = tk.Frame(mensaje_frame, bg="#2d2d2d")
        content_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        tk.Label(content_frame, text="No hay alertas activas en este momento", 
                bg="#2d2d2d", fg="#cccccc", font=("Segoe UI", 9), anchor="w").pack(fill="x")
        
        badge_label.config(text="0")
        return

    contador = 0
    alertas_por_categoria = {
        "fuera_servicio": [],
        "mantenimiento": [],
        "funcionan": []
    }
    
    # Clasificar todas las alertas
    for alerta in entities:
        info = alerta.get("alert", {})
        linea = info.get("informed_entity", [{}])[0].get("route_id", "Desconocida")
        texto = info.get("header_text", {}).get("translation", [{}])[0].get("text", "Sin información disponible")
        
        # Limpiar y formatear el nombre de la línea
        if linea and linea != "Desconocida":
            linea = linea.replace("Subte_", "Línea ").title()
        
        categoria = clasificar_alerta(texto)
        alertas_por_categoria[categoria].append((linea, texto))
        contador += 1

    # Mostrar alertas en sus respectivas categorías
    for categoria, alertas in alertas_por_categoria.items():
        if alertas:
            for linea, texto in alertas:
                if categoria == "fuera_servicio":
                    agregar_alerta_frame(frame_fuera_servicio, linea, texto)
                elif categoria == "mantenimiento":
                    agregar_alerta_frame(frame_mantenimiento, linea, texto)
                else:  # funcionan
                    agregar_alerta_frame(frame_funcionan, linea, texto)
        else:
            # Mostrar mensaje de "No hay" para categorías vacías
            if categoria == "fuera_servicio":
                agregar_mensaje_vacio(frame_fuera_servicio)
            elif categoria == "mantenimiento":
                agregar_mensaje_vacio(frame_mantenimiento)
            else:  # funcionan
                agregar_mensaje_vacio(frame_funcionan)

    badge_label.config(text=str(contador))

    # 🔔 Notificación push
    if prefs.get("mostrar_push") and contador > 0:
        notification.notify(
            title="🚇 Nuevas Alertas del Subte",
            message=f"Se detectaron {contador} alertas activas.",
            timeout=10
        )

def agregar_mensaje_vacio(frame):
    """Agrega un mensaje indicando que no hay alertas en una categoría."""
    mensaje_frame = tk.Frame(frame, bg="#2d2d2d", relief="raised", bd=1)
    mensaje_frame.pack(fill="x", padx=5, pady=2)
    
    # Icono según la categoría del frame padre
    if frame == frame_fuera_servicio:
        icono = "🔴"
        color = "#ff4444"
        texto = "No hay líneas fuera de servicio"
    elif frame == frame_mantenimiento:
        icono = "🟡"
        color = "#ffaa00"
        texto = "No hay líneas en mantenimiento"
    else:  # frame_funcionan
        icono = "🟢"
        color = "#44ff44"
        texto = "Todas las líneas funcionan correctamente"
    
    tk.Label(mensaje_frame, text=icono, bg="#2d2d2d", fg=color, font=("Segoe UI", 10)).pack(side="left", padx=(10, 5))
    
    content_frame = tk.Frame(mensaje_frame, bg="#2d2d2d")
    content_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
    
    tk.Label(content_frame, text=texto, bg="#2d2d2d", fg="#cccccc", font=("Segoe UI", 9), anchor="w").pack(fill="x")

def agregar_alerta_frame(frame, linea, mensaje):
    """Agrega una alerta a un frame específico con el formato adecuado."""
    alert_frame = tk.Frame(frame, bg="#2d2d2d", relief="raised", bd=1)
    alert_frame.pack(fill="x", padx=5, pady=2)
    
    # Icono según la categoría del frame padre
    if frame == frame_fuera_servicio:
        icono = "🔴"
        color = "#ff4444"
    elif frame == frame_mantenimiento:
        icono = "🟡"
        color = "#ffaa00"
    else:  # frame_funcionan
        icono = "🟢"
        color = "#44ff44"
    
    tk.Label(alert_frame, text=icono, bg="#2d2d2d", fg=color, font=("Segoe UI", 10)).pack(side="left", padx=(10, 5))
    
    # Contenido de la alerta
    content_frame = tk.Frame(alert_frame, bg="#2d2d2d")
    content_frame.pack(side="left", fill="x", expand=True, padx=5, pady=5)
    
    tk.Label(content_frame, text=linea, bg="#2d2d2d", fg="white", font=("Segoe UI", 10, "bold"), anchor="w").pack(fill="x")
    tk.Label(content_frame, text=mensaje, bg="#2d2d2d", fg="#cccccc", font=("Segoe UI", 9), anchor="w", wraplength=500).pack(fill="x")

def actualizar_alertas():
    """Actualiza las alertas y programa la próxima verificación."""
    alertas = obtener_alertas_subte()
    mostrar_alertas(alertas)
    root.after(60000, actualizar_alertas)  # Actualiza cada 60 segundos

def abrir_config():
    """Ventana para gestionar preferencias."""
    def guardar():
        prefs["mostrar_push"] = var_push.get()
        prefs["alertas_sonido"] = var_sonido.get()
        guardar_preferencias(prefs)
        messagebox.showinfo("Guardado", "Preferencias actualizadas correctamente.")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Preferencias de Notificaciones")
    win.geometry("300x200")
    win.config(bg="#1e1e1e")

    var_push = tk.BooleanVar(value=prefs.get("mostrar_push", True))
    var_sonido = tk.BooleanVar(value=prefs.get("alertas_sonido", True))

    ttk.Checkbutton(win, text="Mostrar notificaciones push", variable=var_push).pack(pady=10)
    ttk.Checkbutton(win, text="Activar sonido/vibración", variable=var_sonido).pack(pady=10)
    ttk.Button(win, text="Guardar", command=guardar).pack(pady=20)

# --- INTERFAZ PRINCIPAL ---
root = tk.Tk()
root.title("🚇 Alertas y Notificaciones del Subte")
root.geometry("600x500")
root.configure(bg="#1e1e1e")

prefs = cargar_preferencias()

# Header
header_frame = tk.Frame(root, bg="#1e1e1e")
header_frame.pack(fill="x", padx=20, pady=10)

tk.Label(header_frame, text="Alertas", fg="white", bg="#1e1e1e", font=("Segoe UI", 16, "bold")).pack(side="left")

badge_frame = tk.Frame(header_frame, bg="#1e1e1e")
badge_frame.pack(side="right")

tk.Label(badge_frame, text="Alertas activas", fg="#cccccc", bg="#1e1e1e", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
badge_label = tk.Label(badge_frame, text="0", bg="#ff4444", fg="white", font=("Segoe UI", 12, "bold"), width=3, height=1)
badge_label.pack(side="right")

# Contenedor principal
main_container = tk.Frame(root, bg="#1e1e1e")
main_container.pack(fill="both", expand=True, padx=20, pady=10)

# Crear secciones de alertas
def crear_seccion_alerta(parent, titulo, color):
    """Crea una sección de alertas con título y color específico."""
    section_frame = tk.Frame(parent, bg="#1e1e1e")
    section_frame.pack(fill="x", pady=(0, 15))
    
    # Título de la sección
    title_frame = tk.Frame(section_frame, bg="#1e1e1e")
    title_frame.pack(fill="x", pady=(0, 5))
    
    tk.Label(title_frame, text=titulo, fg=color, bg="#1e1e1e", font=("Segoe UI", 12, "bold")).pack(side="left")
    
    # Frame para las alertas
    alertas_frame = tk.Frame(section_frame, bg="#1e1e1e")
    alertas_frame.pack(fill="x")
    
    return alertas_frame

# Crear las tres secciones
frame_fuera_servicio = crear_seccion_alerta(main_container, "Fuera de servicio", "#ff4444")
frame_mantenimiento = crear_seccion_alerta(main_container, "En mantenimiento", "#ffaa00")
frame_funcionan = crear_seccion_alerta(main_container, "Funcionan", "#44ff44")

# Botón de configuración en la parte inferior
button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack(fill="x", padx=20, pady=10)

ttk.Button(button_frame, text="Preferencias ⚙", command=abrir_config).pack(side="right")

# Primera carga con datos reales de la API
actualizar_alertas()

root.mainloop()
