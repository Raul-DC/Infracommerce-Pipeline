import pandas as pd
import sqlite3
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def init_db():

    with sqlite3.connect("/opt/airflow/data/dwh.db") as conn:

        with open("/opt/airflow/scripts_db/init.sql") as f:
            conn.executescript(f.read())

def argentina_pipeline():

    url = "/opt/airflow/data/ventas_argentina.csv"

    df = pd.read_csv(url)

    df = df.dropna(subset=["ID_Venta"])

    print(f"Argentina pipeline - filas cargadas: {len(df)}")

    df["fecha_transaccion"] = pd.to_datetime(
        df["fecha_transaccion"],
        format="%d/%m/%Y %H:%M:%S"
    ).dt.strftime("%Y-%m-%d")

    with sqlite3.connect("/opt/airflow/data/dwh.db") as conn:

        conn.execute("DELETE FROM argentina_ventas")

        df.to_sql(
            "argentina_ventas",
            conn,
            if_exists="append",
            index=False
        )


def brasil_pipeline():

    url = "/opt/airflow/data/stock_brasil.csv"

    df = pd.read_csv(url)

    print(f"Brasil inventario generado: {len(df)}")

    exchange_rate = 5.5

    df["Costo_USD"] = df["Costo_BRL"] / exchange_rate

    with sqlite3.connect("/opt/airflow/data/dwh.db") as conn:

        cursor = conn.cursor()

        data = df[[
            "SKU",
            "nombre_producto",
            "cantidad_stock",
            "Costo_BRL",
            "Costo_USD"
        ]].values.tolist()

        cursor.executemany("""
            INSERT INTO brasil_inventario
            (SKU,nombre_producto,cantidad_stock,Costo_BRL,Costo_USD)
            VALUES (?,?,?,?,?)
            ON CONFLICT(SKU)
            DO UPDATE SET
                cantidad_stock=excluded.cantidad_stock,
                Costo_BRL=excluded.Costo_BRL,
                Costo_USD=excluded.Costo_USD
        """, data)

        conn.commit()


def colombia_pipeline():

    url = "/opt/airflow/data/trafico_colombia.csv"

    df = pd.read_csv(url)

    df["mes"] = pd.to_datetime(df["fecha"]).dt.to_period("M").astype(str)

    df_grouped = df.groupby(
        ["mes","Fuente_Trafico"]
    ).agg({
        "visitas":"sum",
        "compras":"sum"
    }).reset_index()

    print(f"Colombia KPI generados: {len(df_grouped)}")

    df_grouped.columns = [
        "mes",
        "fuente_trafico",
        "visitas",
        "compras"
    ]

    with sqlite3.connect("/opt/airflow/data/dwh.db") as conn:

        conn.execute("DELETE FROM colombia_kpi_mensual")

        df_grouped.to_sql(
            "colombia_kpi_mensual",
            conn,
            if_exists="append",
            index=False
        )


with DAG(
    dag_id="latam_data_pipeline",
    start_date=datetime(2024,1,1),
    schedule="@daily",
    catchup=False,
    tags=["latam","etl"]
) as dag:

    init_task = PythonOperator(
    task_id="init_db",
    python_callable=init_db
)

    argentina_task = PythonOperator(
        task_id="argentina_pipeline",
        python_callable=argentina_pipeline
    )

    brasil_task = PythonOperator(
        task_id="brasil_pipeline",
        python_callable=brasil_pipeline
    )

    colombia_task = PythonOperator(
        task_id="colombia_pipeline",
        python_callable=colombia_pipeline
    )

init_task >> [argentina_task, brasil_task, colombia_task]