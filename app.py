import os
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "medicamentos.db"))

app = Dash(__name__)
server = app.server
app.title = "Tablero de medicamentos EPS"


def get_connection():
    return sqlite3.connect(DB_PATH)


def sql_df(query, params=None):
    with get_connection() as con:
        return pd.read_sql_query(query, con, params=params or [])


def filter_clause(year, month, regional, group):
    clauses = []
    params = []

    if year and year != "Todos":
        clauses.append("strftime('%Y', fecha_entrega) = ?")
        params.append(str(year))

    if month and month != "Todos":
        clauses.append("strftime('%m', fecha_entrega) = ?")
        params.append(f"{int(month):02d}")

    if regional and regional != "Todos":
        clauses.append("regional_caf = ?")
        params.append(regional)

    if group and group != "Todos":
        clauses.append("grupo_fco_economico = ?")
        params.append(group)

    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    return where, params


def options(query):
    df = sql_df(query)
    return [{"label": str(v), "value": v} for v in df.iloc[:, 0].dropna().tolist()]


years = options("SELECT DISTINCT strftime('%Y', fecha_entrega) AS year FROM dispensacion ORDER BY year")
months = [{"label": "Enero", "value": 1}, {"label": "Febrero", "value": 2},
          {"label": "Marzo", "value": 3}, {"label": "Abril", "value": 4},
          {"label": "Mayo", "value": 5}, {"label": "Junio", "value": 6},
          {"label": "Julio", "value": 7}, {"label": "Agosto", "value": 8},
          {"label": "Septiembre", "value": 9}, {"label": "Octubre", "value": 10},
          {"label": "Noviembre", "value": 11}, {"label": "Diciembre", "value": 12}]
regionals = options("SELECT DISTINCT regional_caf FROM dispensacion WHERE TRIM(regional_caf) <> '' ORDER BY regional_caf")
groups = options("SELECT DISTINCT grupo_fco_economico FROM dispensacion WHERE TRIM(grupo_fco_economico) <> '' ORDER BY grupo_fco_economico")


def money(v):
    return f"${v:,.0f}".replace(",", ".")


def card(title, value, subtitle=""):
    return html.Div([
        html.Div(title, className="card-title"),
        html.Div(value, className="card-value"),
        html.Div(subtitle, className="card-subtitle")
    ], className="kpi-card")


app.layout = html.Div([
    html.Div([
        html.H1("Tablero de medicamentos dispensados"),
        html.P("EPS | Dispensaciones 2020–2021 | Fuente: SQLite"),
    ], className="header"),

    html.Div([
        html.Div([html.Label("Año"), dcc.Dropdown(
            [{"label": "Todos", "value": "Todos"}] + years,
            "Todos", id="year-filter", clearable=False
        )], className="filter"),
        html.Div([html.Label("Mes"), dcc.Dropdown(
            [{"label": "Todos", "value": "Todos"}] + months,
            "Todos", id="month-filter", clearable=False
        )], className="filter"),
        html.Div([html.Label("Regional CAF"), dcc.Dropdown(
            [{"label": "Todos", "value": "Todos"}] + regionals,
            "Todos", id="regional-filter", clearable=False
        )], className="filter"),
        html.Div([html.Label("Grupo farmacológico"), dcc.Dropdown(
            [{"label": "Todos", "value": "Todos"}] + groups,
            "Todos", id="group-filter", clearable=False
        )], className="filter"),
    ], className="filters"),

    html.Div(id="kpis", className="kpis"),

    html.Div([
        html.Div([dcc.Graph(id="time-chart")], className="panel wide"),
        html.Div([dcc.Graph(id="pbs-chart")], className="panel"),
    ], className="grid"),

    html.Div([
        html.Div([dcc.Graph(id="top-med-chart")], className="panel"),
        html.Div([dcc.Graph(id="delivery-chart")], className="panel"),
    ], className="grid"),

    html.Div([
        html.Div([dcc.Graph(id="municipality-chart")], className="panel wide"),
    ], className="grid"),

    html.Div([
        html.H2("Análisis específico: ANTIDIABÉTICOS"),
        html.Div(id="anti-summary", className="anti-summary"),
        html.Div([dcc.Graph(id="anti-time-chart")], className="panel"),
        html.Div([dcc.Graph(id="anti-top-chart")], className="panel"),
    ], className="anti-section"),

    html.Div([
        html.Hr(),
        html.P("Nota metodológica: el costo promedio de una fórmula se calcula como costo total / número de fórmulas distintas."),
        html.P("El campo municipio_caf se utiliza para el desglose geográfico solicitado; regional_caf se usa como filtro."),
    ], className="footer")
])


@app.callback(
    Output("kpis", "children"),
    Output("time-chart", "figure"),
    Output("pbs-chart", "figure"),
    Output("top-med-chart", "figure"),
    Output("delivery-chart", "figure"),
    Output("municipality-chart", "figure"),
    Output("anti-summary", "children"),
    Output("anti-time-chart", "figure"),
    Output("anti-top-chart", "figure"),
    Input("year-filter", "value"),
    Input("month-filter", "value"),
    Input("regional-filter", "value"),
    Input("group-filter", "value"),
)
def update_dashboard(year, month, regional, group):
    where, params = filter_clause(year, month, regional, group)

    kpi = sql_df(f"""
        SELECT
            COUNT(DISTINCT id) AS personas,
            COUNT(DISTINCT formula) AS formulas,
            COALESCE(SUM(costo_total),0) AS costo_total
        FROM dispensacion {where}
    """, params).iloc[0]

    avg_formula = (kpi["costo_total"] / kpi["formulas"]) if kpi["formulas"] else 0
    kpis = [
        card("Personas con dispensaciones", f'{int(kpi["personas"]):,}'.replace(",", ".")),
        card("Fórmulas distintas", f'{int(kpi["formulas"]):,}'.replace(",", ".")),
        card("Costo total", money(kpi["costo_total"])),
        card("Costo promedio por fórmula", money(avg_formula)),
    ]

    time_df = sql_df(f"""
        SELECT strftime('%Y-%m', fecha_entrega) AS periodo,
               SUM(costo_total) AS costo,
               COUNT(*) AS dispensaciones
        FROM dispensacion {where}
        GROUP BY periodo ORDER BY periodo
    """, params)
    fig_time = px.line(time_df, x="periodo", y="costo", markers=True,
                       title="Costo de medicamentos en el tiempo",
                       labels={"periodo":"Mes", "costo":"Costo total"})
    fig_time.update_layout(yaxis_tickprefix="$", hovermode="x unified")

    pbs_df = sql_df(f"""
        SELECT COALESCE(NULLIF(TRIM(pbs),''),'Sin dato') AS pbs,
               SUM(costo_total) AS costo
        FROM dispensacion {where}
        GROUP BY 1 ORDER BY costo DESC
    """, params)
    fig_pbs = px.bar(pbs_df, x="pbs", y="costo", title="Costo según PBS / No PBS",
                     labels={"pbs":"PBS", "costo":"Costo total"}, text_auto=".3s")
    fig_pbs.update_layout(yaxis_tickprefix="$")

    top_df = sql_df(f"""
        SELECT descripcion AS medicamento, SUM(costo_total) AS costo
        FROM dispensacion {where}
        GROUP BY descripcion
        ORDER BY costo DESC LIMIT 10
    """, params).sort_values("costo")
    fig_top = px.bar(top_df, x="costo", y="medicamento", orientation="h",
                     title="Top 10 medicamentos por costo total",
                     labels={"costo":"Costo total", "medicamento":"Medicamento"})
    fig_top.update_layout(xaxis_tickprefix="$")

    delivery_df = sql_df(f"""
        SELECT COALESCE(NULLIF(TRIM(tipo_entrega),''),'Sin dato') AS tipo_entrega,
               SUM(costo_total) AS costo
        FROM dispensacion {where}
        GROUP BY 1 ORDER BY costo DESC
    """, params)
    fig_delivery = px.bar(delivery_df, x="tipo_entrega", y="costo",
                          title="Costo según tipo de entrega",
                          labels={"tipo_entrega":"Tipo de entrega","costo":"Costo total"})
    fig_delivery.update_layout(yaxis_tickprefix="$")

    mun_df = sql_df(f"""
        SELECT COALESCE(NULLIF(TRIM(municipio_caf),''),'Sin dato') AS municipio_caf,
               SUM(costo_total) AS costo
        FROM dispensacion {where}
        GROUP BY 1 ORDER BY costo DESC LIMIT 15
    """, params)
    fig_mun = px.bar(mun_df.sort_values("costo"), x="costo", y="municipio_caf",
                     orientation="h", title="Costo por municipio CAF (Top 15)",
                     labels={"municipio_caf":"Municipio CAF","costo":"Costo total"})
    fig_mun.update_layout(xaxis_tickprefix="$")

    # ANTIDIABÉTICOS: se analiza aparte de los filtros generales para que el bloque
    # responda siempre a la pregunta específica del taller.
    anti = sql_df("""
        SELECT
            COUNT(*) AS dispensaciones,
            COUNT(DISTINCT id) AS personas,
            COUNT(DISTINCT formula) AS formulas,
            SUM(costo_total) AS costo
        FROM dispensacion
        WHERE grupo_fco_economico = 'ANTIDIABETICOS'
    """).iloc[0]
    anti_avg = anti["costo"] / anti["formulas"] if anti["formulas"] else 0

    anti_top = sql_df("""
        SELECT descripcion AS medicamento, SUM(costo_total) AS costo
        FROM dispensacion
        WHERE grupo_fco_economico = 'ANTIDIABETICOS'
        GROUP BY descripcion ORDER BY costo DESC LIMIT 10
    """).sort_values("costo")
    anti_time = sql_df("""
        SELECT strftime('%Y-%m', fecha_entrega) AS periodo,
               SUM(costo_total) AS costo,
               COUNT(DISTINCT formula) AS formulas
        FROM dispensacion
        WHERE grupo_fco_economico = 'ANTIDIABETICOS'
        GROUP BY periodo ORDER BY periodo
    """)
    anti_first = anti_time.iloc[0]["costo"] if len(anti_time) else 0
    anti_last = anti_time.iloc[-1]["costo"] if len(anti_time) else 0
    trend_text = "aumentó" if anti_last > anti_first else "disminuyó o no aumentó"
    anti_summary = [
        card("Costo total ANTIDIABÉTICOS", money(anti["costo"])),
        card("Fórmulas distintas", f'{int(anti["formulas"]):,}'.replace(",", ".")),
        card("Costo promedio por fórmula", money(anti_avg)),
        html.Div([
            html.B("Lectura temporal: "),
            html.Span(
                f"el costo mensual {trend_text} entre {anti_time.iloc[0]['periodo']} "
                f"y {anti_time.iloc[-1]['periodo']}; el grupo no tiene registros en 2020."
                if len(anti_time) else "No hay registros."
            )
        ], className="anti-note")
    ]

    fig_anti_time = px.line(anti_time, x="periodo", y="costo", markers=True,
                            title="ANTIDIABÉTICOS: costo mensual",
                            labels={"periodo":"Mes","costo":"Costo total"})
    fig_anti_time.update_layout(yaxis_tickprefix="$")

    fig_anti_top = px.bar(anti_top, x="costo", y="medicamento", orientation="h",
                          title="ANTIDIABÉTICOS: medicamentos con mayor costo total",
                          labels={"costo":"Costo total","medicamento":"Medicamento"})
    fig_anti_top.update_layout(xaxis_tickprefix="$")

    return kpis, fig_time, fig_pbs, fig_top, fig_delivery, fig_mun, anti_summary, fig_anti_time, fig_anti_top


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8050)), debug=False)


