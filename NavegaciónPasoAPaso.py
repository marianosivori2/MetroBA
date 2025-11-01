import tkinter as tk
from tkinter import messagebox

class NavegacionPasoAPaso:
    def __init__(self, root):
        self.root = root
        self.root.title("Navegación Paso a Paso")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f8f0') 
        
        tk.Label(root, text="🧭 NAVEGACIÓN PASO A PASO", 
                font=('Arial', 14, 'bold'), 
                fg='#2e7d32',  
                bg='#f0f8f0').pack(pady=20)
        
        funciones = [
            ("🗺️ Simular Navegación", self.simular_navegacion),
            ("⏱️ Tiempos de Trasbordo", self.mostrar_tiempos),
            ("📋 Ver Instrucciones", self.mostrar_instrucciones)
        ]
        
        for texto, comando in funciones:
            tk.Button(root, text=texto, command=comando,
                     bg='#a5d6a7', 
                     fg='#1b5e20',  
                     font=('Arial', 10), 
                     pady=10, 
                     width=25).pack(pady=8)
    
    def simular_navegacion(self):
        messagebox.showinfo("Navegación", "Plaza de Mayo → Perú → Retiro\nTiempo total: 12 minutos\nCaminata: 3 minutos")
    
    def mostrar_tiempos(self):
        messagebox.showinfo("Tiempos de Trasbordo", "Rápido: 2-3 minutos\nMedio: 4-5 minutos\nLargo: 6-8 minutos")
    
    def mostrar_instrucciones(self):
        instrucciones = """
📋 INSTRUCCIONES:

• Siga las flechas direccionales
• Verifique los tiempos de trasbordo
• Preste atención a las salidas
• Consulte mapas en estaciones
"""
        messagebox.showinfo("Instrucciones", instrucciones)

if __name__ == "__main__":
    root = tk.Tk()
    app = NavegacionPasoAPaso(root)
    root.mainloop()
