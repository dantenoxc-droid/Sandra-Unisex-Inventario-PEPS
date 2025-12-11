# ventana_productos.py
import tkinter as tk
from tkinter import ttk, messagebox
from base import agregar_producto, obtener_productos, actualizar_producto, eliminar_producto

def crear_interfaz_productos(parent):
    # parent puede ser root o un frame
    top = tk.Toplevel(parent)
    top.title("Productos")
    top.geometry("950x600")
    top.config(bg="#f7f9fb")

    frame_form = tk.Frame(top, bg="#f7f9fb", pady=8)
    frame_form.pack(fill="x")

    labels = ["Código", "Nombre", "Descripción", "Precio", "Mínimo"]
    vars = {}
    for i, lab in enumerate(labels):
        tk.Label(frame_form, text=lab+":", bg="#f7f9fb").grid(row=0, column=i*2, sticky="w", padx=6)
        e = tk.Entry(frame_form, width=20)
        e.grid(row=0, column=i*2+1, padx=6)
        vars[lab.lower()] = e

    btn_frame = tk.Frame(top, bg="#f7f9fb", pady=6)
    btn_frame.pack(fill="x")

    def limpiar():
        for e in vars.values():
            e.delete(0, tk.END)

    def refrescar():
        tree.delete(*tree.get_children())
        for p in obtener_productos():
            tree.insert("", "end", values=p)

    def agregar():
        try:
            codigo = vars["código"].get().strip()
            nombre = vars["nombre"].get().strip()
            desc = vars["descripción"].get().strip()
            precio = float(vars["precio"].get() or 0)
            minimo = int(vars["mínimo"].get() or 0)
            if not codigo or not nombre:
                messagebox.showwarning("Atención", "Código y Nombre obligatorios.")
                return
            agregar_producto(codigo, nombre, desc, precio, minimo)
            refrescar()
            limpiar()
            messagebox.showinfo("Éxito", "Producto agregado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar():
        try:
            codigo = vars["código"].get().strip()
            nombre = vars["nombre"].get().strip()
            desc = vars["descripción"].get().strip()
            precio = float(vars["precio"].get() or 0)
            minimo = int(vars["mínimo"].get() or 0)
            if not codigo:
                messagebox.showwarning("Atención", "Introduce código para actualizar.")
                return
            actualizar_producto(codigo, nombre, desc, precio, minimo)
            refrescar()
            messagebox.showinfo("Éxito", "Producto actualizado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def eliminar():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona producto a eliminar.")
            return
        codigo = tree.item(sel[0])["values"][0]
        confirmar = messagebox.askyesno("Confirmar", f"Eliminar producto {codigo}?")
        if not confirmar:
            return
        eliminar_producto(codigo)
        refrescar()

    tk.Button(btn_frame, text="Agregar", bg="#2ecc71", fg="white", command=agregar, width=12).pack(side="left", padx=8)
    tk.Button(btn_frame, text="Actualizar", bg="#f1c40f", command=actualizar, width=12).pack(side="left", padx=8)
    tk.Button(btn_frame, text="Eliminar", bg="#e74c3c", fg="white", command=eliminar, width=12).pack(side="left", padx=8)
    tk.Button(btn_frame, text="Limpiar", command=limpiar, width=10).pack(side="left", padx=8)

    # Tabla
    columns = ("codigo", "nombre", "descripcion", "precio", "cantidad", "minimo")
    tree = ttk.Treeview(top, columns=columns, show="headings", height=18)
    for c in columns:
        tree.heading(c, text=c.capitalize())
        tree.column(c, width=140)
    tree.pack(fill="both", expand=True, padx=12, pady=10)

    def on_select(event):
        sel = tree.focus()
        if not sel:
            return
        vals = tree.item(sel)["values"]
        vars["código"].delete(0, tk.END); vars["código"].insert(0, vals[0])
        vars["nombre"].delete(0, tk.END); vars["nombre"].insert(0, vals[1])
        vars["descripción"].delete(0, tk.END); vars["descripción"].insert(0, vals[2] or "")
        vars["precio"].delete(0, tk.END); vars["precio"].insert(0, vals[3] or 0)
        vars["mínimo"].delete(0, tk.END); vars["mínimo"].insert(0, vals[5] or 0)

    tree.bind("<<TreeviewSelect>>", on_select)

    refrescar()
    return top
