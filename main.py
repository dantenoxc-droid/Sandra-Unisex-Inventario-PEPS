# main.py
import tkinter as tk
from ventana_productos import crear_interfaz_productos
from ventana_existencias import ventana_existencias
from ventana_movimientos import ventana_movimientos
import crear_db

def main():
    # asegurar DB
    crear_db.crear_tablas()

    root = tk.Tk()
    root.title("Sistema de Inventario - PEPS (SQLite)")
    root.geometry("420x360")
    root.config(bg="#eef5fb")

    tk.Label(root, text="Sistema de Inventario", font=("Arial", 18, "bold"), bg="#eef5fb").pack(pady=12)
    tk.Label(root, text="Menú principal", bg="#eef5fb").pack()

    frame = tk.Frame(root, bg="#eef5fb")
    frame.pack(pady=20)

    tk.Button(frame, text="Productos", width=22, height=2, bg="#3498db", fg="white",
              command=lambda: crear_interfaz_productos(root)).grid(row=0, column=0, padx=10, pady=10)
    tk.Button(frame, text="Existencias", width=22, height=2, bg="#2ecc71", fg="white",
              command=lambda: ventana_existencias(root)).grid(row=1, column=0, padx=10, pady=10)
    tk.Button(frame, text="Movimientos (PEPS)", width=22, height=2, bg="#9b59b6", fg="white",
              command=lambda: ventana_movimientos(root)).grid(row=2, column=0, padx=10, pady=10)

    tk.Button(root, text="Salir", command=root.quit, bg="#e74c3c", fg="white", width=10).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()
