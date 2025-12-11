# ventana_movimientos.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from base import agregar_movimiento, obtener_movimientos, calcular_peps_global
from datetime import datetime

def ventana_movimientos(parent):
    vm = tk.Toplevel(parent)
    vm.title("Movimientos (PEPS)")
    vm.geometry("1200x820")
    vm.config(bg="#f3f6f8")

    # estilo
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=28, font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

    # FORM
    frm = tk.Frame(vm, bg="#f3f6f8")
    frm.pack(fill="x", pady=8, padx=10)

    tk.Label(frm, text="Código:", bg="#f3f6f8").grid(row=0, column=0, padx=4)
    entry_codigo = tk.Entry(frm, width=12); entry_codigo.grid(row=0, column=1, padx=4)

    tk.Label(frm, text="Tipo:", bg="#f3f6f8").grid(row=0, column=2, padx=4)
    combo_tipo = ttk.Combobox(frm, values=["Entrada", "Salida"], state="readonly", width=10)
    combo_tipo.grid(row=0, column=3, padx=4); combo_tipo.set("Entrada")

    tk.Label(frm, text="Cantidad:", bg="#f3f6f8").grid(row=0, column=4, padx=4)
    entry_cantidad = tk.Entry(frm, width=10); entry_cantidad.grid(row=0, column=5, padx=4)

    tk.Label(frm, text="Costo unit. (solo ENTRADA):", bg="#f3f6f8").grid(row=0, column=6, padx=4)
    entry_costo = tk.Entry(frm, width=12); entry_costo.grid(row=0, column=7, padx=4)

    btn_reg = tk.Button(frm, text="Registrar", bg="#27ae60", fg="white",
                        command=lambda: cmd_registrar(), width=12)
    btn_reg.grid(row=0, column=8, padx=8)

    # botones export
    def exportar_excel():
        try:
            from openpyxl import Workbook
        except Exception:
            messagebox.showerror("Error", "openpyxl no instalado. Ejecuta: py -m pip install openpyxl")
            return
        wb = Workbook(); ws = wb.active; ws.title = "Movimientos"
        ws.append(["Código","Tipo","Entrada","Salida","Costo Unit.","Fecha"])
        for iid in tabla.get_children():
            row = tabla.item(iid)["values"]
            ws.append(row)
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel","*.xlsx")], initialfile="movimientos.xlsx")
        if not path: return
        wb.save(path)
        messagebox.showinfo("Éxito", f"Guardado: {path}")

    def exportar_pdf():
        try:
            from reportlab.pdfgen import canvas
        except Exception:
            messagebox.showerror("Error", "reportlab no instalado. Ejecuta: py -m pip install reportlab")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")], initialfile="movimientos.pdf")
        if not path: return
        c = canvas.Canvas(path, pagesize=(800,1100))
        y = 1050
        c.setFont("Helvetica-Bold", 14); c.drawString(40, y, "Movimientos registrados"); y -= 30
        c.setFont("Helvetica", 10)
        headers = ["Código","Tipo","Entrada","Salida","Costo","Fecha"]
        c.drawString(40, y, " | ".join(headers)); y -= 20
        for iid in tabla.get_children():
            row = [str(x) for x in tabla.item(iid)["values"]]
            c.drawString(40, y, " | ".join(row)); y -= 16
            if y < 60:
                c.showPage(); y = 1050; c.setFont("Helvetica", 10)
        c.save()
        messagebox.showinfo("Éxito", f"PDF guardado en {path}")

    # zona botones export
    frame_btns = tk.Frame(vm, bg="#f3f6f8")
    frame_btns.pack(fill="x", padx=12)
    tk.Button(frame_btns, text="📤 Exportar Excel", bg="#3498db", fg="white", command=exportar_excel, width=16).pack(side="left", padx=6)
    tk.Button(frame_btns, text="📄 Exportar PDF", bg="#e74c3c", fg="white", command=exportar_pdf, width=16).pack(side="left")

    # split area: movimientos (izq) y tarjeta peps (der)
    split = tk.Frame(vm, bg="#f3f6f8")
    split.pack(fill="both", expand=True, padx=10, pady=8)

    left = tk.Frame(split, bg="#ffffff", bd=1, relief="solid")
    left.pack(side="left", fill="both", expand=True, padx=(0,6))

    right = tk.Frame(split, bg="#ffffff", bd=1, relief="solid", width=420)
    right.pack(side="right", fill="y")

    # Tabla movimientos (izq)
    cols = ("codigo","tipo","entrada","salida","costo","fecha")
    tabla = ttk.Treeview(left, columns=cols, show="headings", height=18)
    for c in cols:
        tabla.heading(c, text=c.capitalize())
        tabla.column(c, width=110, anchor="center")
    tabla.pack(fill="both", expand=True, padx=10, pady=10)

    tabla.tag_configure("entrada", background="#e9fff0")
    tabla.tag_configure("salida", background="#fff0f0")

    # TARJETA PEPS (der)
    tk.Label(right, text="Tarjeta PEPS (FIFO)", bg="#ffffff", font=("Arial", 12, "bold")).pack(pady=8)
    cols_peps = ("lote","fecha","entrada","salida","existencia","costo_unit","costo_total")
    tabla_peps = ttk.Treeview(right, columns=cols_peps, show="headings", height=18)
    for c in cols_peps:
        tabla_peps.heading(c, text=c.capitalize())
        tabla_peps.column(c, width=120, anchor="center")
    tabla_peps.pack(fill="both", expand=True, padx=8, pady=8)

    lbl_peps_info = tk.Label(right, text="", bg="#ffffff", justify="left")
    lbl_peps_info.pack(padx=8, pady=4, anchor="w")

    # funciones cargar
    def cargar_movimientos():
        tabla.delete(*tabla.get_children())
        for codigo, tipo, cantidad, costo_unit, fecha in obtener_movimientos():
            if tipo == "Entrada":
                row = (codigo, "Entrada", cantidad, "", f"{costo_unit:.2f}" if costo_unit is not None else "", fecha)
                tabla.insert("", "end", values=row, tags=("entrada",))
            else:
                row = (codigo, "Salida", "", cantidad, f"{costo_unit:.2f}" if costo_unit is not None else "", fecha)
                tabla.insert("", "end", values=row, tags=("salida",))

    def generar_tarjeta_peps_ui():
        tabla_peps.delete(*tabla_peps.get_children())
        datos = obtener_movimientos()

        # 🔒 Nueva versión segura — evita None
        lotes = []
        lote_num = 1

        for codigo, tipo, cantidad, costo_unit, fecha in datos:

            cantidad = cantidad or 0
            costo_unit = costo_unit or 0

            if tipo == "Entrada":
                lotes.append([cantidad, costo_unit])

                total = sum((q or 0) * (c or 0) for q, c in lotes)
                existencia = sum((q or 0) for q, _ in lotes)

                tabla_peps.insert(
                    "", "end",
                    values=(lote_num, fecha, f"{cantidad}u / ${costo_unit:.2f}", "",
                            f"{existencia} u", f"${costo_unit:.2f}", f"${total:.2f}")
                )
                lote_num += 1

            else:  # salida
                salida = cantidad
                costo_salida = 0.0

                while salida > 0 and lotes:
                    q, c = lotes[0]
                    q = q or 0
                    c = c or 0

                    if q <= salida:
                        costo_salida += q * c
                        salida -= q
                        lotes.pop(0)
                    else:
                        costo_salida += salida * c
                        lotes[0][0] = q - salida
                        salida = 0

                total = sum((q or 0) * (c or 0) for q, c in lotes)
                existencia = sum((q or 0) for q, _ in lotes)

                promedio = (costo_salida / cantidad) if cantidad else 0

                tabla_peps.insert(
                    "", "end",
                    values=("", fecha, "",
                            f"{cantidad}u / ${promedio:.2f}",
                            f"{existencia} u", "",
                            f"${total:.2f}")
                )

        # resumen
        costo_ventas, inv_final, stock_total_val = calcular_peps_global()
        lbl_peps_info.config(
            text=f"Costo ventas: ${costo_ventas:.2f}\nInventario final valorado: ${inv_final:.2f}\nStock total (lotes): {stock_total_val} u"
        )

    def cargar_tablas():
        cargar_movimientos()
        generar_tarjeta_peps_ui()

    def cmd_registrar():
        codigo = entry_codigo.get().strip()
        tipo = combo_tipo.get()
        cant = entry_cantidad.get().strip()
        costo = entry_costo.get().strip() if tipo == "Entrada" else None

        if not codigo or not tipo or not cant:
            messagebox.showerror("Error", "Completa los campos.")
            return

        try:
            cant = int(cant)
            if cant <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Cantidad inválida.")
            return

        if tipo == "Entrada":
            try:
                costo_f = float(costo)
            except:
                messagebox.showerror("Error", "Costo inválido.")
                return
            agregar_movimiento(codigo, "Entrada", cant, costo_f)
        else:
            agregar_movimiento(codigo, "Salida", cant)

        entry_costo.delete(0, tk.END)
        entry_cantidad.delete(0, tk.END)
        entry_codigo.delete(0, tk.END)

        cargar_tablas()
        messagebox.showinfo("OK", f"{tipo} registrada.")

    cargar_tablas()
    return vm



