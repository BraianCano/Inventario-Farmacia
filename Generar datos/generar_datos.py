import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

OUTPUT_DIR = r"C:\Users\Braian\Documents\Proyectos\Inventario_Farmacia\Datos crudo"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HOY = datetime(2024, 6, 30)
INICIO_HISTORICO = datetime(2023, 1, 1)

# PRODUCTOS

categorias = {
    "Analgésicos":        ["Ibuprofeno 400mg", "Paracetamol 500mg", "Aspirina 100mg", "Diclofenac 50mg", "Ketorolac 10mg"],
    "Antibióticos":       ["Amoxicilina 500mg", "Azitromicina 500mg", "Ciprofloxacina 500mg", "Claritromicina 500mg", "Cefalexina 500mg"],
    "Antihipertensivos":  ["Enalapril 10mg", "Losartan 50mg", "Amlodipina 5mg", "Metoprolol 50mg", "Hidroclorotiazida 25mg"],
    "Diabetes":           ["Metformina 850mg", "Glibenclamida 5mg", "Insulina Glargina", "Insulina Regular", "Sitagliptina 100mg"],
    "Vitaminas":          ["Vitamina C 500mg", "Complejo B", "Vitamina D3 1000UI", "Omega 3 1000mg", "Zinc 20mg"],
    "Dermatológicos":     ["Clotrimazol Crema", "Hidrocortisona 1%", "Permetrina Loción", "Aciclovir Crema", "Mupirocina Ungüento"],
    "Gastrointestinal":   ["Omeprazol 20mg", "Ranitidina 150mg", "Metoclopramida 10mg", "Loperamida 2mg", "Simeticona 80mg"],
    "Respiratorio":       ["Salbutamol Inhalador", "Loratadina 10mg", "Cetirizina 10mg", "Bromhexina 8mg", "Ambroxol 30mg"],
}

laboratorios = ["Bayer", "Pfizer", "Roemmers", "Bagó", "Elea", "Investi", "Gador", "MK Pharma"]

productos_rows = []
sku_counter = 1000
for cat, prods in categorias.items():
    for prod in prods:
        requiere_frio = prod in ["Insulina Glargina", "Insulina Regular"]
        precio_costo = round(random.uniform(80, 2500), 2)
        margen = random.uniform(0.25, 0.55)
        precio_venta = round(precio_costo * (1 + margen), 2)
        vida_util_dias = random.choice([180, 365, 540, 730]) if not requiere_frio else 365
        productos_rows.append({
            "sku": f"SKU-{sku_counter}",
            "nombre": prod,
            "categoria": cat,
            "laboratorio": random.choice(laboratorios),
            "precio_costo": precio_costo,
            "precio_venta": precio_venta,
            "requiere_frio": requiere_frio,
            "vida_util_dias": vida_util_dias,
            "unidad_medida": "unidad",
            "stock_minimo": random.randint(10, 30),
            "stock_maximo": random.randint(100, 300),
        })
        sku_counter += 1

df_productos = pd.DataFrame(productos_rows)
df_productos.to_csv(f"{OUTPUT_DIR}/productos.csv", index=False)
print(f" productos.csv — {len(df_productos)} registros")

# SUCURSALES

sucursales_data = [
    {"sucursal_id": "SUC-01", "nombre": "Casa Central",    "ciudad": "Buenos Aires", "tipo": "urbana",   "zona": "Norte"},
    {"sucursal_id": "SUC-02", "nombre": "Palermo",          "ciudad": "Buenos Aires", "tipo": "urbana",   "zona": "Centro"},
    {"sucursal_id": "SUC-03", "nombre": "Belgrano",         "ciudad": "Buenos Aires", "tipo": "urbana",   "zona": "Norte"},
    {"sucursal_id": "SUC-04", "nombre": "La Plata Centro",  "ciudad": "La Plata",     "tipo": "urbana",   "zona": "Sur"},
    {"sucursal_id": "SUC-05", "nombre": "Rosario Norte",    "ciudad": "Rosario",      "tipo": "urbana",   "zona": "Centro"},
    {"sucursal_id": "SUC-06", "nombre": "Córdoba Capital",  "ciudad": "Córdoba",      "tipo": "urbana",   "zona": "Centro"},
    {"sucursal_id": "SUC-07", "nombre": "Mar del Plata",    "ciudad": "Mar del Plata","tipo": "costera",  "zona": "Sur"},
    {"sucursal_id": "SUC-08", "nombre": "Mendoza Centro",   "ciudad": "Mendoza",      "tipo": "urbana",   "zona": "Oeste"},
    {"sucursal_id": "SUC-09", "nombre": "Tucumán",          "ciudad": "Tucumán",      "tipo": "urbana",   "zona": "Norte"},
    {"sucursal_id": "SUC-10", "nombre": "Salta Capital",    "ciudad": "Salta",        "tipo": "rural",    "zona": "Norte"},
]
df_sucursales = pd.DataFrame(sucursales_data)
df_sucursales.to_csv(f"{OUTPUT_DIR}/sucursales.csv", index=False)
print(f" sucursales.csv — {len(df_sucursales)} registros")


# INVENTARIO ACTUAL

# Estacionalidad: respiratorio sube en invierno (mayo-agosto), vitaminas en invierno también
def factor_estacional(categoria, mes):
    if categoria == "Respiratorio" and mes in [5, 6, 7, 8]:
        return 1.5
    if categoria == "Vitaminas" and mes in [5, 6, 7, 8]:
        return 1.3
    if categoria == "Dermatológicos" and mes in [11, 12, 1, 2]:
        return 1.4
    return 1.0

inventario_rows = []
for _, prod in df_productos.iterrows():
    for _, suc in df_sucursales.iterrows():
        factor = factor_estacional(prod["categoria"], HOY.month)
        stock_base = random.randint(0, int(prod["stock_maximo"] * factor))

        # Inyectar problemas realistas
        problema = random.random()
        if problema < 0.08:   # 8% sobrestock severo
            stock_base = int(prod["stock_maximo"] * random.uniform(1.5, 3.0))
        elif problema < 0.15: # 7% quiebre de stock
            stock_base = 0
        elif problema < 0.20: # 5% stock crítico
            stock_base = random.randint(1, prod["stock_minimo"] - 1)

        # Fecha de vencimiento
        dias_hasta_venc = random.randint(30, prod["vida_util_dias"])
        # Inyectar algunos próximos a vencer
        if random.random() < 0.12:
            dias_hasta_venc = random.randint(1, 89)  # vence en menos de 90 días
        fecha_venc = (HOY + timedelta(days=dias_hasta_venc)).strftime("%Y-%m-%d")

        inventario_rows.append({
            "sku": prod["sku"],
            "sucursal_id": suc["sucursal_id"],
            "stock_actual": stock_base,
            "fecha_vencimiento": fecha_venc,
            "lote": f"L{random.randint(10000,99999)}",
            "ubicacion": f"Estante-{random.randint(1,20)}-{random.choice('ABCDE')}",
            "fecha_actualizacion": HOY.strftime("%Y-%m-%d"),
        })

df_inventario = pd.DataFrame(inventario_rows)
df_inventario.to_csv(f"{OUTPUT_DIR}/inventario_actual.csv", index=False)
print(f" inventario_actual.csv — {len(df_inventario)} registros")

# VENTAS (Va a ser de 18 meses)

ventas_rows = []
skus = df_productos["sku"].tolist()
sucursal_ids = df_sucursales["sucursal_id"].tolist()
prod_dict = df_productos.set_index("sku").to_dict("index")

fecha_actual = INICIO_HISTORICO
while fecha_actual <= HOY:
    dia_semana = fecha_actual.weekday()
    es_finde = dia_semana >= 5
    factor_dia = 0.5 if es_finde else 1.0

    for suc_id in sucursal_ids:
        tipo_suc = df_sucursales[df_sucursales["sucursal_id"] == suc_id]["tipo"].values[0]
        factor_suc = 1.3 if tipo_suc == "urbana" else 0.7

        n_transacciones = int(random.gauss(15, 4) * factor_dia * factor_suc)
        n_transacciones = max(0, n_transacciones)

        skus_vendidos = random.sample(skus, min(n_transacciones, len(skus)))
        for sku in skus_vendidos:
            cat = prod_dict[sku]["categoria"]
            f_estacional = factor_estacional(cat, fecha_actual.month)
            cantidad = max(1, int(random.gauss(5, 2) * f_estacional))
            precio = prod_dict[sku]["precio_venta"]

            ventas_rows.append({
                "fecha": fecha_actual.strftime("%Y-%m-%d"),
                "sku": sku,
                "sucursal_id": suc_id,
                "cantidad_vendida": cantidad,
                "precio_unitario": precio,
                "ingreso_total": round(cantidad * precio, 2),
            })
    fecha_actual += timedelta(days=1)

df_ventas = pd.DataFrame(ventas_rows)
df_ventas.to_csv(f"{OUTPUT_DIR}/ventas.csv", index=False)
print(f" ventas.csv — {len(df_ventas):,} registros")

# MOVIMIENTOS DE INVENTARIO

movimientos_rows = []
mov_id = 1
fecha_actual = INICIO_HISTORICO
tipos_mov = ["entrada", "salida_venta", "devolucion", "ajuste_negativo", "vencimiento_baja"]
pesos_mov = [0.45, 0.40, 0.07, 0.05, 0.03]

while fecha_actual <= HOY:
    n_movs = random.randint(30, 80)
    for _ in range(n_movs):
        sku = random.choice(skus)
        suc_id = random.choice(sucursal_ids)
        tipo = random.choices(tipos_mov, weights=pesos_mov)[0]
        cantidad = random.randint(1, 50) if tipo == "entrada" else random.randint(1, 20)
        costo = prod_dict[sku]["precio_costo"]

        movimientos_rows.append({
            "movimiento_id": f"MOV-{mov_id:06d}",
            "fecha": fecha_actual.strftime("%Y-%m-%d"),
            "sku": sku,
            "sucursal_id": suc_id,
            "tipo_movimiento": tipo,
            "cantidad": cantidad,
            "costo_unitario": costo,
            "costo_total": round(cantidad * costo, 2),
            "usuario": f"USR-{random.randint(1,20):02d}",
        })
        mov_id += 1
    fecha_actual += timedelta(days=1)

df_movimientos = pd.DataFrame(movimientos_rows)
df_movimientos.to_csv(f"{OUTPUT_DIR}/movimientos.csv", index=False)
print(f" movimientos.csv — {len(df_movimientos):,} registros")


# ÓRDENES DE COMPRA

proveedores = {
    "Bayer":     {"lead_time_base": 7,  "variabilidad": 2, "cumplimiento": 0.92},
    "Pfizer":    {"lead_time_base": 10, "variabilidad": 3, "cumplimiento": 0.88},
    "Roemmers":  {"lead_time_base": 5,  "variabilidad": 1, "cumplimiento": 0.95},
    "Bagó":      {"lead_time_base": 6,  "variabilidad": 2, "cumplimiento": 0.93},
    "Elea":      {"lead_time_base": 8,  "variabilidad": 3, "cumplimiento": 0.90},
    "Investi":   {"lead_time_base": 14, "variabilidad": 4, "cumplimiento": 0.82},
    "Gador":     {"lead_time_base": 7,  "variabilidad": 2, "cumplimiento": 0.91},
    "MK Pharma": {"lead_time_base": 12, "variabilidad": 5, "cumplimiento": 0.79},
}

ordenes_rows = []
orden_id = 1
fecha_actual = INICIO_HISTORICO

while fecha_actual <= HOY:
    if random.random() < 0.35:  # el 35% de los días hay órdenes
        n_ordenes = random.randint(1, 5)
        for _ in range(n_ordenes):
            sku = random.choice(skus)
            lab = prod_dict[sku]["laboratorio"]
            prov_info = proveedores.get(lab, proveedores["Bagó"])

            lead_time = max(1, int(random.gauss(prov_info["lead_time_base"], prov_info["variabilidad"])))
            fecha_entrega_esperada = fecha_actual + timedelta(days=lead_time)
            cumple = random.random() < prov_info["cumplimiento"]
            demora = 0 if cumple else random.randint(1, 7)
            fecha_entrega_real = (fecha_entrega_esperada + timedelta(days=demora)).strftime("%Y-%m-%d") \
                if fecha_entrega_esperada <= HOY else None

            cantidad = random.randint(50, 500)
            precio_compra = prod_dict[sku]["precio_costo"]

            ordenes_rows.append({
                "orden_id": f"OC-{orden_id:05d}",
                "fecha_emision": fecha_actual.strftime("%Y-%m-%d"),
                "sku": sku,
                "proveedor": lab,
                "cantidad_solicitada": cantidad,
                "cantidad_recibida": cantidad if cumple else int(cantidad * random.uniform(0.7, 0.99)),
                "precio_unitario": precio_compra,
                "monto_total": round(cantidad * precio_compra, 2),
                "lead_time_esperado": lead_time,
                "lead_time_real": lead_time + demora if fecha_entrega_real else None,
                "fecha_entrega_esperada": fecha_entrega_esperada.strftime("%Y-%m-%d"),
                "fecha_entrega_real": fecha_entrega_real,
                "estado": "completada" if fecha_entrega_real else "pendiente",
                "cumplimiento_cantidad": cumple,
            })
            orden_id += 1
    fecha_actual += timedelta(days=1)

df_ordenes = pd.DataFrame(ordenes_rows)
df_ordenes.to_csv(f"{OUTPUT_DIR}/ordenes_compra.csv", index=False)
print(f" ordenes_compra.csv — {len(df_ordenes):,} registros")


# RESUMEN FINAL

print("\n" + "="*50)
print(" GENERACIÓN DE DATOS COMPLETADA")
print("="*50)
print(f"  Período: {INICIO_HISTORICO.date()} → {HOY.date()} (18 meses)")
print(f"  Productos:    {len(df_productos):>8,}")
print(f"  Sucursales:   {len(df_sucursales):>8,}")
print(f"  Inv. actual:  {len(df_inventario):>8,}")
print(f"  Ventas:       {len(df_ventas):>8,}")
print(f"  Movimientos:  {len(df_movimientos):>8,}")
print(f"  Órd. compra:  {len(df_ordenes):>8,}")
print(f"\n   Archivos en: {OUTPUT_DIR}")
