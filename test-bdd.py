import sqlite3
import os

# Ruta a tu base de datos
DB_PATH = os.path.abspath("src/core/database/allCodes.db")  # Ajusta si es necesario

def dump_database(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("⚠️ No se encontraron tablas en la base de datos.")
            return

        print("📋 Contenido completo de la base de datos:\n")

        for table in tables:
            print(f"Tabla: {table}")
            # Obtener columnas
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            print(" | ".join(columns))

            # Obtener contenido
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                print(" | ".join(str(item) for item in row))
            print("-" * 50)

    except Exception as e:
        print(f"Error al acceder a la base de datos: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    dump_database(DB_PATH)
