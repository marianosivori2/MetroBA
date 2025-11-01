import tkinter as tk
from tkinter import messagebox

class ModoTurista:
    def __init__(self, root):
        self.root = root
        self.root.title("Modo Turista")
        self.root.geometry("400x400")
        self.root.configure(bg='#f0f8f0') 
        
        self.color_fondo = '#f0f8f0'
        self.color_boton = '#a8e6a3'
        self.color_texto = '#2e7d32'
        self.color_hover = '#c8e6c9'
        
        titulo = tk.Label(root, text="🌍 MODO TURISTA", 
                         font=('Arial', 14, 'bold'), 
                         fg=self.color_texto, 
                         bg=self.color_fondo)
        titulo.pack(pady=20)
    
        botones = [
            ("🗺️ Rutas Turísticas", self.mostrar_rutas),
            ("🏛️ Puntos de Interés", self.mostrar_puntos),
            ("🌐 Idiomas", self.mostrar_idiomas),
            ("📄 Generar Documento", self.generar_doc)
        ]
        
        for texto, comando in botones:
            btn = tk.Button(root, text=texto, command=comando, 
                           width=20, pady=8,
                           bg=self.color_boton,
                           fg=self.color_texto,
                           font=('Arial', 10, 'bold'),
                           relief='flat',
                           bd=0)
            btn.pack(pady=8)
            
            
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.color_hover))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.color_boton))
    
    def mostrar_rutas(self):
        rutas = """
RUTAS TURÍSTICAS:

1. Histórica: Plaza de Mayo, Catedral
2. Cultural: Teatro Colón, MALBA  
3. Moderna: Puerto Madero, Palermo
4. Nocturna: San Telmo, Recoleta
"""
        messagebox.showinfo("🗺️ Rutas Turísticas", rutas)
    
    def mostrar_puntos(self):
        puntos = """
PUNTOS DE INTERÉS:

• Plaza de Mayo: Casa Rosada
• Catedral: Teatro Colón
• Retiro: Puerto Madero
• Palermo: Jardín Japonés
"""
        messagebox.showinfo("🏛️ Puntos de Interés", puntos)
    
    def mostrar_idiomas(self):
        messagebox.showinfo("🌐 Idiomas", "Soportados: Español, Inglés, Portugués")
    
    def generar_doc(self):
        messagebox.showinfo("📄 Documento", "Modo_Turista.txt generado")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModoTurista(root)
    root.mainloop()
