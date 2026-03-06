# LATAM Data Pipeline – Infracommerce Technical Challenge

Este proyecto implementa un **pipeline ETL automatizado** utilizando **Apache Airflow, Python (Pandas) y SQLite**, simulando un escenario real de centralización de métricas operativas de distintos países de Latinoamérica.

El objetivo es automatizar la extracción, transformación y carga de datos provenientes de distintos equipos regionales (Argentina, Brasil y Colombia) hacia un **Data Warehouse centralizado**.

---

# Arquitectura del Proyecto

El pipeline se ejecuta mediante **Apache Airflow** corriendo dentro de un contenedor Docker.

Cada país tiene su propio flujo de procesamiento dentro del DAG principal.

```

CSV Files → Airflow DAG → Transformaciones con Pandas → SQLite Data Warehouse

```

---

# Estructura del Proyecto

```

Infracommerce-Pipeline/
├── dags/
│   └── pipeline_latam.py
│
├── data/
│   ├── dwh.db
│   ├── stock_brasil.csv
│   ├── trafico_colombia.csv
│   └── ventas_argentina.csv
│
├── scripts_db/
│   └── init.sql
│
├── docker-compose.yml
└── README.md

```

---

# Stack Tecnológico

- **Orquestación:** Apache Airflow
- **Procesamiento:** Python + Pandas
- **Base de datos:** SQLite
- **Contenerización:** Docker + Docker Compose

---

# Pipelines Implementados

## 🇦🇷 Argentina – Ventas Diarias

Patrón utilizado: **Truncate & Load**

Proceso:

1. Leer el archivo `ventas_argentina.csv`
2. Eliminar registros donde `ID_Venta` sea nulo
3. Convertir `fecha_transaccion` al formato `YYYY-MM-DD`
4. Borrar los registros existentes en la tabla
5. Insertar los datos transformados

Tabla destino:

```

argentina_ventas

```

---

## 🇧🇷 Brasil – Inventario

Patrón utilizado: **Carga Incremental (UPSERT)**

Proceso:

1. Leer el archivo `stock_brasil.csv`
2. Calcular una nueva columna `Costo_USD`
3. Aplicar tipo de cambio fijo:

```

1 USD = 5.5 BRL

```

4. Insertar o actualizar registros según el `SKU`

Si el `SKU` ya existe → se actualiza el stock y costo  
Si el `SKU` no existe → se inserta el registro

Tabla destino:

```

brasil_inventario

```

---

## 🇨🇴 Colombia – KPIs de Tráfico Web

Patrón utilizado: **Agregación / Data Mart**

Proceso:

1. Leer `trafico_colombia.csv`
2. Extraer el **mes** desde la columna `fecha`
3. Agrupar por:

- `mes`
- `Fuente_Trafico`

4. Calcular:

- total de `visitas`
- total de `compras`

5. Insertar el resultado agregado en la tabla de KPIs.

Tabla destino:

```

colombia_kpi_mensual

```

---

# Inicialización de Base de Datos

Las tablas se crean automáticamente usando el script:

```

scripts_db/init.sql

```

Tablas generadas:

- `argentina_ventas`
- `brasil_inventario`
- `colombia_kpi_mensual`

---

# Ejecución del Proyecto

## 1️⃣ Clonar el repositorio

```

git clone <repo_url>

cd Infracommerce-Pipeline

```

---

## 2️⃣ Iniciar el entorno

```

docker-compose up

```

Este comando:

- inicia Apache Airflow
- crea el usuario administrador
- inicializa la base de datos
- levanta el scheduler y webserver

---

## 3️⃣ Acceder a Airflow

Abrir en el navegador:

```

[http://localhost:8080](http://localhost:8080)

```

Credenciales:

```

usuario: admin
password: admin

```

---

## 4️⃣ Ejecutar el DAG

En la interfaz de Airflow:

1. Activar el DAG `latam_data_pipeline`
2. Ejecutar manualmente el workflow

El pipeline ejecutará los siguientes pasos:

```

init_db
├── argentina_pipeline
├── brasil_pipeline
└── colombia_pipeline

```

---

# Idempotencia del Pipeline

El pipeline está diseñado para ser **re-ejecutable sin generar inconsistencias**.

Argentina  
→ se utiliza **DELETE + INSERT**

Brasil  
→ se utiliza **UPSERT mediante ON CONFLICT**

Colombia  
→ se reemplazan los datos agregados en cada ejecución

---

# Decisiones Técnicas

- Se utilizó **SQLite** para simplificar la instalación y mantener un entorno completamente local.
- Los datos de prueba se almacenan en la carpeta `data/` para facilitar la reproducibilidad.
- Se utilizó **Pandas** para las transformaciones por su simplicidad y capacidad de manipulación de datos tabulares.
- El pipeline está implementado mediante **PythonOperator** dentro de un único DAG.

---

# Posibles Mejoras

En un entorno productivo podrían implementarse mejoras como:

- separación de lógica ETL en módulos independientes
- uso de un Data Warehouse más robusto (BigQuery, Snowflake, Redshift)
- validaciones de calidad de datos
- almacenamiento de logs centralizado
- parametrización de pipelines

---

# Autor

Raúl Díaz - 
Data Engineer

