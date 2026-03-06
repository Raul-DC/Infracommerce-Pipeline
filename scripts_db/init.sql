CREATE TABLE IF NOT EXISTS argentina_ventas (
    ID_Venta TEXT,
    fecha_transaccion DATE,
    monto_venta REAL,
    producto_id TEXT
);

CREATE TABLE IF NOT EXISTS brasil_inventario (
    SKU TEXT PRIMARY KEY,
    nombre_producto TEXT,
    cantidad_stock INTEGER,
    Costo_BRL REAL,
    Costo_USD REAL
);

CREATE TABLE IF NOT EXISTS colombia_kpi_mensual (
    mes TEXT,
    fuente_trafico TEXT,
    visitas INTEGER,
    compras INTEGER
);