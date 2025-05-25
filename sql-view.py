import sqlite3
from tabulate import tabulate

# Ruta a tu base de datos
DB_PATH = "src/core/database/allCodes.db"

def mostrar_codigos():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT code, type, datetime, url_generated, isUsed FROM codes")
        rows = cursor.fetchall()

        if not rows:
            print("🔍 No hay códigos en la base de datos.")
            return

        headers = ["Código", "Tipo", "Fecha/Hora", "URL", "Usado"]
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

    except Exception as e:
        print(f"❌ Error al acceder a la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    mostrar_codigos()
