import sqlite3
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# -----------------------------
# CONEXIÓN A LA BASE DE DATOS
# -----------------------------
conexion = sqlite3.connect("medicamentos.db")


# -----------------------------
# PERSONAS CON DISPENSACIONES
# -----------------------------
consulta_personas = """
SELECT COUNT(DISTINCT id)
FROM dispensacion;
"""

personas = conexion.execute(consulta_personas).fetchone()[0]


# -----------------------------
# FÓRMULAS DISTINTAS
# -----------------------------
consulta_formulas = """
SELECT COUNT(DISTINCT formula)
FROM dispensacion;
"""

formulas = conexion.execute(consulta_formulas).fetchone()[0]


# -----------------------------
# COSTO PROMEDIO POR FÓRMULA
# -----------------------------
consulta_costo = """
SELECT AVG(costo_total)
FROM (
    SELECT
        formula,
        SUM(costo_total) AS costo_total
    FROM dispensacion
    GROUP BY formula
);
"""

costo_promedio = conexion.execute(consulta_costo).fetchone()[0]
# -----------------------------
# DISPENSACIONES POR MES
# -----------------------------
consulta_tiempo = """
SELECT
    substr(fecha_entrega, 1, 7) AS mes,
    COUNT(*) AS dispensaciones
FROM dispensacion
GROUP BY mes
ORDER BY mes;
"""

datos_tiempo = conexion.execute(consulta_tiempo).fetchall()
# Crear listas para la gráfica
meses = [fila[0] for fila in datos_tiempo]
dispensaciones = [fila[1] for fila in datos_tiempo]

# Crear gráfica
fig_tiempo = px.line(
    x=meses,
    y=dispensaciones,
    markers=True,
    labels={
        "x": "Mes",
        "y": "Número de dispensaciones"
    },
    title="Dispensaciones de medicamentos por mes"
)
# -----------------------------
# TOP 10 MEDICAMENTOS POR COSTO
# -----------------------------
consulta_top = """
SELECT
    descripcion,
    SUM(costo_total) AS costo_total
FROM dispensacion
GROUP BY descripcion
ORDER BY costo_total DESC
LIMIT 10;
"""

datos_top = conexion.execute(consulta_top).fetchall()

medicamentos = [fila[0] for fila in datos_top]
costos = [fila[1] for fila in datos_top]
medicamentos_cortos = [
    medicamento if len(medicamento) <= 50
    else medicamento[:47] + "..."
    for medicamento in medicamentos
]

fig_top = px.bar(
    x=costos,
    y=medicamentos_cortos,
    orientation="h",
    labels={
        "x": "Costo total",
        "y": "Medicamento"
    },
    title="Top 10 medicamentos por costo total"
)

fig_top.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    )
)

# -----------------------------
# COSTO POR PBS / NO PBS
# -----------------------------
consulta_pbs = """
SELECT
    pbs,
    SUM(costo_total) AS costo_total
FROM dispensacion
GROUP BY pbs
ORDER BY costo_total DESC;
"""

datos_pbs = conexion.execute(consulta_pbs).fetchall()
pbs = [fila[0] for fila in datos_pbs]
costos_pbs = [fila[1] for fila in datos_pbs]

fig_pbs = px.bar(
    x=pbs,
    y=costos_pbs,
    labels={
        "x": "PBS",
        "y": "Costo total"
    },
    title="Costo de medicamentos por PBS / No PBS"
)

import sqlite3

conexion = sqlite3.connect("medicamentos.db")
cursor = conexion.cursor()

consulta = """
SELECT
    pbs,
    COUNT(*) AS registros,
    SUM(costo_total) AS costo_total
FROM dispensacion
GROUP BY pbs
ORDER BY costo_total DESC;
"""

cursor.execute(consulta)
resultados = cursor.fetchall()

print("COSTO POR PBS / NO PBS")
print("======================")

for fila in resultados:
    pbs = fila[0]
    registros = fila[1]
    costo = fila[2]

    if pbs == "" or pbs is None:
        pbs = "Sin dato"

    print(
        "PBS:", pbs,
        "| Registros:", registros,
        "| Costo total:", costo
    )





# -----------------------------
# COSTO POR PBS / NO PBS
# -----------------------------
consulta_pbs = """
SELECT
    pbs,
    SUM(costo_total) AS costo_total
FROM dispensacion
GROUP BY pbs
ORDER BY costo_total DESC;
"""

datos_pbs = conexion.execute(consulta_pbs).fetchall()
# -----------------------------
# COSTO POR MUNICIPIO
# -----------------------------
consulta_municipio = """
SELECT
    municipio_caf,
    SUM(costo_total) AS costo_total
FROM dispensacion
GROUP BY municipio_caf
ORDER BY costo_total DESC
LIMIT 15;
"""

datos_municipio = conexion.execute(consulta_municipio).fetchall()
# -----------------------------
# COSTO POR TIPO DE ENTREGA
# -----------------------------
consulta_entrega = """
SELECT
    tipo_entrega,
    SUM(costo_total) AS costo_total
FROM dispensacion
GROUP BY tipo_entrega
ORDER BY costo_total DESC;
"""

datos_entrega = conexion.execute(consulta_entrega).fetchall()
tipos_entrega = [
    "Sin dato" if fila[0] is None or fila[0] == "" else fila[0]
    for fila in datos_entrega
]

costos_entrega = [fila[1] for fila in datos_entrega]

fig_entrega = px.bar(
    x=tipos_entrega,
    y=costos_entrega,
    labels={
        "x": "Tipo de entrega",
        "y": "Costo total"
    },
    title="Costo de medicamentos por tipo de entrega"
)
municipios = [
    "Sin dato" if fila[0] == "0" or fila[0] is None or fila[0] == "" else fila[0]
    for fila in datos_municipio
]

costos_municipio = [fila[1] for fila in datos_municipio]

fig_municipio = px.bar(
    x=costos_municipio,
    y=municipios,
    orientation="h",
    labels={
        "x": "Costo total",
        "y": "Municipio"
    },
    title="Top 15 municipios por costo de medicamentos"
)

fig_municipio.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    )
)
medicamentos = [fila[0] for fila in datos_top]
costos = [fila[1] for fila in datos_top]

medicamentos_cortos = [
    medicamento if len(medicamento) <= 55
    else medicamento[:52] + "..."
    for medicamento in medicamentos
]
fig_top = px.bar(
    x=costos,
    y=medicamentos_cortos,
    orientation="h",
    labels={
        "x": "Costo total",
        "y": "Medicamento"
    },
    title="Top 10 medicamentos por costo total"
)

fig_top.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    )
)
# Cerrar conexión
conexion.close()


# -----------------------------
# CREAR APLICACIÓN DASH
# -----------------------------
app = Dash(__name__)

@app.callback(
    Output("grafico-entrega", "figure"),
    Input("filtro-grupo", "value"),
    Input("filtro-anio", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-regional", "value")
)
def actualizar_entrega(grupo, anio, mes, regional):

    conexion = sqlite3.connect("medicamentos.db")

    condiciones = []
    parametros = []

    if grupo != "TODOS":
        condiciones.append("grupo_fco_economico = ?")
        parametros.append(grupo)

    if anio != "TODOS":
        condiciones.append("strftime('%Y', fecha_entrega) = ?")
        parametros.append(anio)

    if mes != "TODOS":
        condiciones.append("strftime('%m', fecha_entrega) = ?")
        parametros.append(mes)

    if regional != "TODOS":
        condiciones.append("regional_caf = ?")
        parametros.append(regional)

    consulta_entrega = """
    SELECT
        tipo_entrega,
        SUM(costo_total) AS costo_total
    FROM dispensacion
    """

    if condiciones:
        consulta_entrega += " WHERE " + " AND ".join(condiciones)

    consulta_entrega += """
    GROUP BY tipo_entrega
    ORDER BY costo_total DESC;
    """

    datos_entrega = conexion.execute(
        consulta_entrega,
        parametros
    ).fetchall()

    conexion.close()

    tipos = [
        "Sin dato" if fila[0] is None or fila[0] == "" else fila[0]
        for fila in datos_entrega
    ]

    costos = [fila[1] for fila in datos_entrega]

    figura = px.bar(
        x=costos,
        y=medicamentos,
        orientation="h",
        labels={
            "x": "Costo total",
            "y": "Medicamento"
        },
        title="Top 10 medicamentos por costo total"
    )

    figura.update_layout(
        height=600,
        margin=dict(l=20, r=40, t=80, b=60),
        yaxis=dict(
            categoryorder="total ascending",
            automargin=True
        ),
        xaxis=dict(
            tickprefix="$ ",
            ticksuffix=" M"
        )
    )

    return figura

@app.callback(
    Output("grafico-municipio", "figure"),
    Input("filtro-grupo", "value"),
    Input("filtro-anio", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-regional", "value")
)
def actualizar_municipio(grupo, anio, mes, regional):

    conexion = sqlite3.connect("medicamentos.db")

    condiciones = []
    parametros = []

    if grupo != "TODOS":
        condiciones.append("grupo_fco_economico = ?")
        parametros.append(grupo)

    if anio != "TODOS":
        condiciones.append("strftime('%Y', fecha_entrega) = ?")
        parametros.append(anio)

    if mes != "TODOS":
        condiciones.append("strftime('%m', fecha_entrega) = ?")
        parametros.append(mes)

    if regional != "TODOS":
        condiciones.append("regional_caf = ?")
        parametros.append(regional)

    consulta_municipio = """
    SELECT
        municipio_caf,
        SUM(costo_total) AS costo_total
    FROM dispensacion
    """

    if condiciones:
        consulta_municipio += " WHERE " + " AND ".join(condiciones)

    consulta_municipio += """
    GROUP BY municipio_caf
    ORDER BY costo_total DESC
    LIMIT 15;
    """

    datos_municipio = conexion.execute(
        consulta_municipio,
        parametros
    ).fetchall()

    conexion.close()

    municipios = [
        "Sin dato" if fila[0] is None or fila[0] == "" or fila[0] == "0"
        else fila[0]
        for fila in datos_municipio
    ]


    figura = px.bar(
        x=costos,
        y=municipios,
        orientation="h",
        labels={
            "x": "Costo total",
            "y": "Municipio"
        },
        title="Top 15 municipios por costo de medicamentos"
    )

    figura.update_layout(
        yaxis=dict(
            categoryorder="total ascending"
        )
    )

    return figura

@app.callback(
    Output("grafico-pbs", "figure"),
    Input("filtro-grupo", "value"),
    Input("filtro-anio", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-regional", "value")
)
def actualizar_pbs(grupo, anio, mes, regional):

    conexion = sqlite3.connect("medicamentos.db")

    condiciones = []
    parametros = []

    if grupo != "TODOS":
        condiciones.append("grupo_fco_economico = ?")
        parametros.append(grupo)

    if anio != "TODOS":
        condiciones.append("strftime('%Y', fecha_entrega) = ?")
        parametros.append(anio)

    if mes != "TODOS":
        condiciones.append("strftime('%m', fecha_entrega) = ?")
        parametros.append(mes)

    if regional != "TODOS":
        condiciones.append("regional_caf = ?")
        parametros.append(regional)

    consulta_pbs = """
    SELECT
        pbs,
        SUM(costo_total) AS costo_total
    FROM dispensacion
    """

    if condiciones:
        consulta_pbs += " WHERE " + " AND ".join(condiciones)

    consulta_pbs += """
    GROUP BY pbs
    ORDER BY costo_total DESC;
    """

    datos_pbs = conexion.execute(
        consulta_pbs,
        parametros
    ).fetchall()

    conexion.close()

    categorias = [
        "Sin dato" if fila[0] is None or fila[0] == "" else fila[0]
        for fila in datos_pbs
    ]

    costos = [fila[1] for fila in datos_pbs]

    figura = px.bar(
        x=categorias,
        y=costos,
        labels={
            "x": "PBS",
            "y": "Costo total"
        },
        title="Costo de medicamentos por PBS / No PBS"
    )

    return figura
# -----------------------------
# DISEÑO DEL DASHBOARD
# -----------------------------
app.layout = html.Div([

    # BARRA LATERAL
    html.Div([

        html.H2(
            "Filtros",
            style={
                "textAlign": "center",
                "marginBottom": "25px"
            }
        ),

        html.Label("Año de dispensación"),
        dcc.Dropdown(
            id="filtro-anio",
            options=[
                {"label": "Todos", "value": "TODOS"},
                {"label": "2020", "value": "2020"},
                {"label": "2021", "value": "2021"}
            ],
            value="TODOS",
            clearable=False
        ),

        html.Br(),

        html.Label("Mes de dispensación"),
        dcc.Dropdown(
            id="filtro-mes",
            options=[
                {"label": "Todos", "value": "TODOS"},
                {"label": "Enero", "value": "01"},
                {"label": "Febrero", "value": "02"},
                {"label": "Marzo", "value": "03"},
                {"label": "Abril", "value": "04"},
                {"label": "Mayo", "value": "05"},
                {"label": "Junio", "value": "06"},
                {"label": "Julio", "value": "07"},
                {"label": "Agosto", "value": "08"},
                {"label": "Septiembre", "value": "09"},
                {"label": "Octubre", "value": "10"},
                {"label": "Noviembre", "value": "11"},
                {"label": "Diciembre", "value": "12"}
            ],
            value="TODOS",
            clearable=False
        ),

        html.Br(),

        html.Label("CAF regional"),
        dcc.Dropdown(
            id="filtro-regional",
            options=[
                {"label": "Todos", "value": "TODOS"},
                {"label": "CARTAGENA", "value": "CARTAGENA"},
                {"label": "BOLIVAR NORTE", "value": "BOLIVAR NORTE"},
                {"label": "BOLIVAR CENTRO", "value": "BOLIVAR CENTRO"},
                {"label": "BOLIVAR SUR", "value": "BOLIVAR SUR"},
                {"label": "ATLANTICO", "value": "ATLANTICO"},
                {"label": "CORDOBA", "value": "CORDOBA"},
                {"label": "SUCRE", "value": "SUCRE"},
                {"label": "MAGDALENA", "value": "MAGDALENA"},
                {"label": "BOGOTA", "value": "BOGOTA"},
                {"label": "Sin dato", "value": "0"}
            ],
            value="TODOS",
            clearable=False
        ),

        html.Br(),

        html.Label("Grupo farmacológico"),
        dcc.Dropdown(
            id="filtro-grupo",
            options=[
                {"label": "Todos", "value": "TODOS"},
                {"label": "ANTIDIABETICOS", "value": "ANTIDIABETICOS"},
                {"label": "ANTIHIPERTENSIVOS", "value": "ANTIHIPERTENSIVOS"},
                {"label": "ANALGESICOS Y ANTIINFLAMATORIOS", "value": "ANALGESICOS Y ANTIINFLAMATORIOS"},
                {"label": "VITAMINAS", "value": "VITAMINAS"},
                {"label": "HIPOLIPEMIANTES", "value": "HIPOLIPEMIANTES"}
            ],
            value="TODOS",
            clearable=False
        )

    ], style={
        "width": "260px",
        "padding": "25px",
        "backgroundColor": "#f4f6f8",
        "minHeight": "100vh",
        "boxSizing": "border-box"
    }),

    # PANEL PRINCIPAL
    html.Div([

        html.H1(
            "Dashboard de Medicamentos",
            style={
                "textAlign": "center",
                "marginBottom": "5px"
            }
        ),

        html.P(
            "Análisis de dispensación 2020 - 2021",
            style={
                "textAlign": "center",
                "color": "#666",
                "marginBottom": "25px"
            }
        ),

        # INDICADORES
        html.Div([

            html.Div([
                html.H4("Personas con dispensaciones"),
                html.H2(
                    f"{personas:,}",
                    id="indicador-personas"
                )
            ], style={
                "flex": "1",
                "padding": "20px",
                "margin": "5px",
                "textAlign": "center",
                "backgroundColor": "#f4f6f8",
                "borderRadius": "10px"
            }),

            html.Div([
                html.H4("Fórmulas distintas"),
                html.H2(
                    f"{formulas:,}",
                    id="indicador-formulas"
                )
            ], style={
                "flex": "1",
                "padding": "20px",
                "margin": "5px",
                "textAlign": "center",
                "backgroundColor": "#f4f6f8",
                "borderRadius": "10px"
            }),

            html.Div([
                html.H4("Costo promedio por fórmula"),
                html.H2(
                    f"${costo_promedio:,.2f}",
                    id="indicador-costo"
                )
            ], style={
                "flex": "1",
                "padding": "20px",
                "margin": "5px",
                "textAlign": "center",
                "backgroundColor": "#f4f6f8",
                "borderRadius": "10px"
            })

        ], style={
            "display": "flex",
            "marginBottom": "20px"
        }),

        # GRÁFICO DE TIEMPO
        dcc.Graph(
            id="grafico-tiempo",
            figure=fig_tiempo
        ),

        # FILA DE GRÁFICOS
        html.Div([

            html.Div([
                dcc.Graph(
                    id="grafico-top",
                    figure=fig_top
                )
            ], style={
                "width": "50%"
            }),

            html.Div([
                dcc.Graph(
                    id="grafico-pbs",
                    figure=fig_pbs
                )
            ], style={
                "width": "50%"
            })

        ], style={
            "display": "flex"
        }),

        # SEGUNDA FILA
        html.Div([

            html.Div([
                dcc.Graph(
                    id="grafico-municipio",
                    figure=fig_municipio
                )
            ], style={
                "width": "50%"
            }),

            html.Div([
                dcc.Graph(
                    id="grafico-entrega",
                    figure=fig_entrega
                )
            ], style={
                "width": "50%"
            })

        ], style={
            "display": "flex"
        })

    ], style={
        "flex": "1",
        "padding": "25px",
        "boxSizing": "border-box"
    })

], style={
    "display": "flex",
    "fontFamily": "Arial, sans-serif"
})

conexion.close()
# -----------------------------
# EJECUTAR APLICACIÓN
# -----------------------------
@app.callback(
    Output("indicador-formulas", "children"),
    Input("filtro-grupo", "value"),
    Input("filtro-anio", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-regional", "value")
)
def actualizar_formulas(grupo, anio, mes, regional):

    conexion = sqlite3.connect("medicamentos.db")

    condiciones = []
    parametros = []

    if grupo != "TODOS":
        condiciones.append("grupo_fco_economico = ?")
        parametros.append(grupo)

    if anio != "TODOS":
        condiciones.append("strftime('%Y', fecha_entrega) = ?")
        parametros.append(anio)

    if mes != "TODOS":
        condiciones.append("strftime('%m', fecha_entrega) = ?")
        parametros.append(mes)

    if regional != "TODOS":
        condiciones.append("regional_caf = ?")
        parametros.append(regional)

    consulta = """
    SELECT COUNT(DISTINCT formula)
    FROM dispensacion
    """

    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)

    formulas_filtradas = conexion.execute(
        consulta,
        parametros
    ).fetchone()[0]

    conexion.close()

    return f"{formulas_filtradas:,}"


@app.callback(
    Output("indicador-costo", "children"),
    Input("filtro-grupo", "value"),
    Input("filtro-anio", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-regional", "value")
)
def actualizar_costo(grupo, anio, mes, regional):

    conexion = sqlite3.connect("medicamentos.db")

    condiciones = []
    parametros = []

    if grupo != "TODOS":
        condiciones.append("grupo_fco_economico = ?")
        parametros.append(grupo)

    if anio != "TODOS":
        condiciones.append("strftime('%Y', fecha_entrega) = ?")
        parametros.append(anio)

    if mes != "TODOS":
        condiciones.append("strftime('%m', fecha_entrega) = ?")
        parametros.append(mes)

    if regional != "TODOS":
        condiciones.append("regional_caf = ?")
        parametros.append(regional)

    consulta = """
    SELECT
        SUM(costo_total) / COUNT(DISTINCT formula)
    FROM dispensacion
    """

    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)

    costo_filtrado = conexion.execute(
        consulta,
        parametros
    ).fetchone()[0]

    conexion.close()

    return f"${costo_filtrado:,.2f}"
@app.callback(
    Output("indicador-personas", "children"),
    Input("filtro-grupo", "value"),
    Input("filtro-anio", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-regional", "value")
)
def actualizar_personas(grupo, anio, mes, regional):

    conexion = sqlite3.connect("medicamentos.db")

    condiciones = []
    parametros = []

    if grupo != "TODOS":
        condiciones.append("grupo_fco_economico = ?")
        parametros.append(grupo)

    if anio != "TODOS":
        condiciones.append("strftime('%Y', fecha_entrega) = ?")
        parametros.append(anio)

    if mes != "TODOS":
        condiciones.append("strftime('%m', fecha_entrega) = ?")
        parametros.append(mes)

    if regional != "TODOS":
        condiciones.append("regional_caf = ?")
        parametros.append(regional)

    consulta = """
    SELECT COUNT(DISTINCT id)
    FROM dispensacion
    """

    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)

    personas_filtradas = conexion.execute(
        consulta,
        parametros
    ).fetchone()[0]

    conexion.close()

    return f"{personas_filtradas:,}"

@app.callback(
    Output("grafico-tiempo", "figure"),
    Input("filtro-grupo", "value"),
    Input("filtro-anio", "value"),
    Input("filtro-mes", "value"),
    Input("filtro-regional", "value")
)
def actualizar_tiempo(grupo, anio, mes, regional):

    conexion = sqlite3.connect("medicamentos.db")

    condiciones = []
    parametros = []

    if grupo != "TODOS":
        condiciones.append("grupo_fco_economico = ?")
        parametros.append(grupo)

    if anio != "TODOS":
        condiciones.append("strftime('%Y', fecha_entrega) = ?")
        parametros.append(anio)

    if mes != "TODOS":
        condiciones.append("strftime('%m', fecha_entrega) = ?")
        parametros.append(mes)

    if regional != "TODOS":
        condiciones.append("regional_caf = ?")
        parametros.append(regional)

    consulta = """
    SELECT
        substr(fecha_entrega, 1, 7) AS mes,
        COUNT(*) AS dispensaciones
    FROM dispensacion
    """

    if condiciones:
        consulta += " WHERE " + " AND ".join(condiciones)

    consulta += """
    GROUP BY substr(fecha_entrega, 1, 7)
    ORDER BY mes;
    """

    datos = conexion.execute(
        consulta,
        parametros
    ).fetchall()

    conexion.close()

    meses = [fila[0] for fila in datos]
    dispensaciones = [fila[1] for fila in datos]

    figura = px.line(
        x=meses,
        y=dispensaciones,
        markers=True,
        labels={
            "x": "Mes",
            "y": "Número de dispensaciones"
        },
        title="Dispensación de medicamentos en el tiempo"
    )

    figura.update_xaxes(
        type="category",
        tickangle=45
    )

    return figura


if __name__ == "__main__":
    app.run(debug=True)

