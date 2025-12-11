# crear_db.py
import sqlite3

def crear_tablas():
    conn = sqlite3.connect("inventario.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        codigo TEXT PRIMARY KEY,
        nombre TEXT,
        descripcion TEXT,
        precio REAL DEFAULT 0,
        cantidad INTEGER DEFAULT 0,
        minimo INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS movimientos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        tipo TEXT,              -- "Entrada" / "Salida"
        cantidad INTEGER,
        costo_unitario REAL,    -- para entradas (y para salidas se guarda el costo promedio aplicado)
        costo_total REAL,
        fecha TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lotes_peps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        cantidad INTEGER,
        costo_unitario REAL,
        fecha TEXT
    )
    """)

    # existencias es opcional pero la dejamos para mostrar rápido info
    cur.execute("""
    CREATE TABLE IF NOT EXISTS existencias (
        codigo TEXT,
        descripcion TEXT,
        existencias INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_tablas()
    print("Tablas creadas/confirmadas en inventario.db")
