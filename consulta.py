import sqlite3

conexion = sqlite3.connect("medicamentos.db")
cursor = conexion.cursor()

consulta = """
SELECT
    tipo_entrega,
    COUNT(*) AS registros,
    SUM(costo_total) AS costo_total
FROM dispensacion
GROUP BY tipo_entrega
ORDER BY costo_total DESC;
"""

cursor.execute(consulta)
resultados = cursor.fetchall()

print("COSTO POR TIPO DE ENTREGA")
print("=========================")

for fila in resultados:

    tipo = fila[0]
    registros = fila[1]
    costo = fila[2]

    if tipo is None or tipo == "":
        tipo = "Sin dato"

    print(
        "Tipo:", tipo,
        "| Registros:", registros,
        "| Costo total:", costo
    )

conexion.close()
