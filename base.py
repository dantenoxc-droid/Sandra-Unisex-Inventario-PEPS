# base.py
import sqlite3
from datetime import datetime
import crear_db

# asegurar que las tablas existen
crear_db.crear_tablas()

DB = "inventario.db"

def conectar():
    return sqlite3.connect(DB)

# -------------------
# Productos
# -------------------
def agregar_producto(codigo, nombre, descripcion, precio, minimo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO productos (codigo, nombre, descripcion, precio, cantidad, minimo)
        VALUES (?, ?, ?, ?, 0, ?)
    """, (codigo, nombre, descripcion, precio, minimo))
    # mantener existencias tabla simple
    cur.execute("INSERT OR IGNORE INTO existencias (codigo, descripcion, existencias) VALUES (?, ?, 0)",
                (codigo, descripcion))
    conn.commit()
    conn.close()

def obtener_productos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT codigo, nombre, descripcion, precio, cantidad, minimo FROM productos ORDER BY nombre")
    r = cur.fetchall()
    conn.close()
    return r

def actualizar_producto(codigo, nombre, descripcion, precio, minimo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE productos SET nombre=?, descripcion=?, precio=?, minimo=? WHERE codigo=?",
                (nombre, descripcion, precio, minimo, codigo))
    conn.commit()
    conn.close()

def eliminar_producto(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE codigo=?", (codigo,))
    cur.execute("DELETE FROM existencias WHERE codigo=?", (codigo,))
    cur.execute("DELETE FROM lotes_peps WHERE codigo=?", (codigo,))
    cur.execute("DELETE FROM movimientos WHERE codigo=?", (codigo,))
    conn.commit()
    conn.close()

def obtener_existencias():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT p.codigo, p.nombre, p.cantidad, p.minimo, (p.cantidad * p.precio) as valor_total FROM productos p")
    r = cur.fetchall()
    conn.close()
    return r

# -------------------
# Lotes PEPS (FIFO)
# -------------------
def agregar_lote_peps(codigo, cantidad, costo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("INSERT INTO lotes_peps (codigo, cantidad, costo_unitario, fecha) VALUES (?, ?, ?, ?)",
                (codigo, cantidad, costo, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def obtener_lotes_peps(codigo):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT id, cantidad, costo_unitario, fecha FROM lotes_peps WHERE codigo=? ORDER BY fecha ASC", (codigo,))
    r = cur.fetchall()
    conn.close()
    return r

def descontar_peps(codigo, cantidad_salida):
    """
    Consume lotes FIFO y devuelve el costo_total de la salida (suma cantidad*costo)
    Modifica lotes_peps eliminando o restando cantidades.
    """
    lotes = obtener_lotes_peps(codigo)
    cantidad_restante = cantidad_salida
    costo_total = 0.0
    conn = conectar()
    cur = conn.cursor()

    for lote_id, cant, costo, _ in lotes:
        if cantidad_restante <= 0:
            break
        if cant <= cantidad_restante:
            costo_total += cant * costo
            cantidad_restante -= cant
            cur.execute("DELETE FROM lotes_peps WHERE id=?", (lote_id,))
        else:
            # tomar parte del lote
            costo_total += cantidad_restante * costo
            nuevo = cant - cantidad_restante
            cur.execute("UPDATE lotes_peps SET cantidad=? WHERE id=?", (nuevo, lote_id))
            cantidad_restante = 0

    conn.commit()
    conn.close()
    return costo_total

def stock_total(codigo):
    lotes = obtener_lotes_peps(codigo)
    return sum(l[1] for l in lotes)

# -------------------
# Movimientos
# -------------------
def agregar_movimiento(codigo, tipo, cantidad, costo_unitario=None):
    """
    tipo: "Entrada" o "Salida"
    Para Entrada: se crea lote PEPS con costo_unitario y se suma cantidad al producto.
    Para Salida: se consume lotes PEPS con descontar_peps y se guarda costo_total y costo promedio.
    """
    conn = conectar()
    cur = conn.cursor()
    fecha = datetime.now().isoformat()

    if tipo == "Entrada":
        if costo_unitario is None:
            # tomar precio del producto como fallback
            cur.execute("SELECT precio FROM productos WHERE codigo=?", (codigo,))
            row = cur.fetchone()
            costo_unitario = float(row[0]) if row else 0.0

        costo_total = cantidad * float(costo_unitario)
        # insertar movimiento
        cur.execute("INSERT INTO movimientos (codigo, tipo, cantidad, costo_unitario, costo_total, fecha) VALUES (?, ?, ?, ?, ?, ?)",
                    (codigo, tipo, cantidad, costo_unitario, costo_total, fecha))
        # aumentar stock en productos
        cur.execute("UPDATE productos SET cantidad = cantidad + ? WHERE codigo=?", (cantidad, codigo))
        # crear lote peps
        agregar_lote_peps(codigo, cantidad, costo_unitario)

    elif tipo == "Salida":
        # descontar lotes
        costo_total = descontar_peps(codigo, cantidad)
        costo_unit_prom = (costo_total / cantidad) if cantidad > 0 else 0.0
        cur.execute("INSERT INTO movimientos (codigo, tipo, cantidad, costo_unitario, costo_total, fecha) VALUES (?, ?, ?, ?, ?, ?)",
                    (codigo, tipo, cantidad, costo_unit_prom, costo_total, fecha))
        # disminuir stock
        cur.execute("UPDATE productos SET cantidad = cantidad - ? WHERE codigo=?", (cantidad, codigo))

    conn.commit()
    conn.close()
    return True

def obtener_movimientos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT codigo, tipo, cantidad, costo_unitario, fecha FROM movimientos ORDER BY fecha ASC")
    r = cur.fetchall()
    conn.close()
    return r

# -------------------
# Calculos PEPS globales
# -------------------
def calcular_peps_global():
    """
    Retorna (costo_total_ventas, inventario_final_valorado, stock_total)
    """
    conn = conectar()
    cur = conn.cursor()
    # costo total ventas (sumar costo_total en salidas)
    cur.execute("SELECT IFNULL(SUM(costo_total),0) FROM movimientos WHERE tipo='Salida'")
    costo_ventas = float(cur.fetchone()[0] or 0.0)

    # inventario final valorado = sum(lotes * costo)
    cur.execute("SELECT IFNULL(SUM(cantidad * costo_unitario),0) FROM lotes_peps")
    inv_final = float(cur.fetchone()[0] or 0.0)

    # stock_total
    cur.execute("SELECT IFNULL(SUM(cantidad),0) FROM lotes_peps")
    stock_total_val = int(cur.fetchone()[0] or 0)

    conn.close()
    return costo_ventas, inv_final, stock_total_val
