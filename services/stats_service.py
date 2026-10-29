from datetime import datetime, date
from collections import defaultdict
from models import Reserva, Alojamiento, Usuario

MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

def calculate_dashboard_statistics():
    """
    Genera metricas financieras y operativas calculadas dinamicamente
    a partir del estado real de la base de datos.
    """
    hoy = date.today()
    reservas = Reserva.query.all()
    usuarios = Usuario.query.all()
    alojamientos = Alojamiento.query.all()

    # 1. Totales generales
    total_reservas = len(reservas)
    reservas_activas = [r for r in reservas if r.estado != "cancelled"]
    confirmadas = len([r for r in reservas if r.estado == "confirmed"])
    pendientes = len([r for r in reservas if r.estado == "pending"])
    canceladas = len([r for r in reservas if r.estado == "cancelled"])
    
    ingresos_totales = sum(r.precio_total for r in reservas_activas)

    # 2. Tasa de conversion dinamica
    # Relacion entre reservas activas y usuarios totales registrados (o estimacion proporcional)
    total_usuarios = len(usuarios)
    if total_usuarios > 0:
        tasa_conversion = round((confirmadas / total_usuarios) * 100, 2)
    else:
        tasa_conversion = 0.0

    # 3. Ingresos mes a mes (Ano en curso dinamico)
    ano_actual = hoy.year
    ingresos_por_mes = {m: 0 for m in range(1, 13)}
    
    for r in reservas_activas:
        if r.check_in and r.check_in.year == ano_actual:
            ingresos_por_mes[r.check_in.month] += r.precio_total

    ingresos_mensuales_lista = [
        {"mes": MESES_ES[m - 1], "monto": ingresos_por_mes[m]}
        for m in range(1, 13)
    ]

    # 4. Comparativa mes actual vs mes anterior
    mes_actual = hoy.month
    mes_anterior = 12 if mes_actual == 1 else mes_actual - 1
    
    ingresos_mes_actual = ingresos_por_mes[mes_actual]
    ingresos_mes_anterior = ingresos_por_mes[mes_anterior]

    diferencia_porcentaje = 0.0
    if ingresos_mes_anterior > 0:
        diferencia_porcentaje = round(((ingresos_mes_actual - ingresos_mes_anterior) / ingresos_mes_anterior) * 100, 1)
    elif ingresos_mes_actual > 0:
        diferencia_porcentaje = 100.0

    # 5. Distribucion de reservas por provincia
    reservas_por_provincia = defaultdict(int)
    for r in reservas_activas:
        if r.alojamiento and r.alojamiento.provincia:
            reservas_por_provincia[r.alojamiento.provincia] += 1

    reservas_por_provincia_lista = [
        {"provincia": prov, "cantidad": cant}
        for prov, cant in sorted(reservas_por_provincia.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "ingresos_totales": ingresos_totales,
        "total_reservas": total_reservas,
        "reservas_confirmadas": confirmadas,
        "reservas_pendientes": pendientes,
        "reservas_canceladas": canceladas,
        "total_usuarios": total_usuarios,
        "tasa_conversion": tasa_conversion,
        "ano_fiscal": ano_actual,
        "ingresos_mes_actual": ingresos_mes_actual,
        "ingresos_mes_anterior": ingresos_mes_anterior,
        "diferencia_porcentaje": diferencia_porcentaje,
        "ingresos_mensuales": ingresos_mensuales_lista,
        "reservas_por_provincia": reservas_por_provincia_lista
    }
