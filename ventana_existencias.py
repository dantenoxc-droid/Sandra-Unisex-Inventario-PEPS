# ventana_existencias.py
import tkinter as tk
from tkinter import ttk, messagebox
from base import obtener_existencias
from tkinter import scrolledtext

def ventana_existencias(parent):
    top = tk.Toplevel(parent)
    top.title("Existencias")
    top.geometry("900x520")
    top.config(bg="#fbfcfd")

    header = tk.Label(top, text="Existencias y alertas de stock mínimo", font=("Arial", 14, "bold"), bg="#fbfcfd")
    header.pack(pady=8)

    # Tabla existencias
    cols = ("codigo", "producto", "stock", "minimo", "valor")
    tree = ttk.Treeview(top, columns=cols, show="headings", height=14)
    for c in cols:
        tree.heading(c, text=c.capitalize())
        tree.column(c, width=150, anchor="center")
    tree.pack(fill="both", expand=True, padx=12, pady=10)

    # tags
    tree.tag_configure("bajo", background="#ffdada")   # rojo suave
    tree.tag_configure("ok", background="#eaffea")     # verde suave

    def cargar():
        tree.delete(*tree.get_children())
        datos = obtener_existencias()
        for codigo, nombre, cantidad, minimo, valor in datos:
            tag = "bajo" if cantidad <= (minimo or 0) else "ok"
            tree.insert("", "end", values=(codigo, nombre, cantidad, minimo, f"${valor:.2f}"), tags=(tag,))

    # panel lateral resumen
    frame_side = tk.Frame(top, bg="#fbfcfd")
    frame_side.pack(fill="x", padx=12, pady=(0,10))

    text = scrolledtext.ScrolledText(frame_side, height=4)
    text.pack(fill="x")

    def actualizar_resumen():
        datos = obtener_existencias()
        bajas = [f"{d[0]} - {d[1]} ({d[2]} <= {d[3]})" for d in datos if d[2] <= (d[3] or 0)]
        text.delete("1.0", tk.END)
        if bajas:
            text.insert(tk.END, "Productos con stock bajo (<= mínimo):\n")
            for b in bajas:
                text.insert(tk.END, "- " + b + "\n")
        else:
            text.insert(tk.END, "No hay productos por debajo del stock mínimo.")

    tk.Button(frame_side, text="Refrescar", command=lambda: [cargar(), actualizar_resumen()], bg="#3498db", fg="white").pack(side="left", padx=6)
    tk.Button(frame_side, text="Cerrar", command=top.destroy).pack(side="right", padx=6)

    cargar()
    actualizar_resumen()
    return top
