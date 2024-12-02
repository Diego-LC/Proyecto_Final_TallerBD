from datetime import datetime, timezone
from math import radians, cos, sin, asin, sqrt
from sklearn.neighbors import BallTree
import numpy as np
from dateutil import parser

def calcular_distancia(lat1, lon1, lat2, lon2):
    # Convertir de grados a radianes
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Fórmula de Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radio de la Tierra en kilómetros
    return c * r

DISTANCIA_MAXIMA = 1000  # Definir la distancia máxima permitida

def filtrar_accidentes_por_clima(accidentes, eventos):
    resultados = []
    for accidente in accidentes:
        try:
            # Convertir la fecha del accidente a objeto datetime
            accidente_fecha = datetime.fromisoformat(accidente["Start_Time"].replace(" ", "T"))
            if accidente_fecha.tzinfo is None:
                accidente_fecha = accidente_fecha.replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Formato de fecha inválido en accidente ID {accidente.get('ID', 'Unknown')}.")
            continue

        accidente_lat = accidente["Start_Lat"]
        accidente_lng = accidente["Start_Lng"]

        evento_asociado = None
        distancia_minima = float('inf')
        for evento in eventos:
            # Convertir las fechas del evento a objetos datetime
            evento_inicio = evento["StartTime"]
            evento_fin = evento["EndTime"]
            if isinstance(evento_inicio, str):
                evento_inicio = datetime.fromisoformat(evento_inicio.replace("Z", "+00:00"))
            if isinstance(evento_fin, str):
                evento_fin = datetime.fromisoformat(evento_fin.replace("Z", "+00:00"))

            # Calcular la distancia entre el accidente y el evento
            distancia = calcular_distancia(accidente_lat, accidente_lng, evento["Lat"], evento["Lng"])
            # Verificar si el accidente ocurrió dentro del rango de tiempo del evento
            accidente_en_rango_tiempo = evento_inicio <= accidente_fecha <= evento_fin

            if distancia <= DISTANCIA_MAXIMA and accidente_en_rango_tiempo:
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    evento_asociado = evento

        if evento_asociado:
            resultados.append({
                "Accidente": accidente,
                "Evento": evento_asociado
            })

    return resultados

def filtrar_accidentes_por_clima_optimizado(accidentes, eventos, distancia_maxima_km=1000):
    # Preparar datos de accidentes
    accidentes_coords = np.radians([[accidente["Start_Lat"], accidente["Start_Lng"]] for accidente in accidentes])
    
    # Al preparar las fechas de los accidentes
    accidentes_fechas = []
    for accidente in accidentes:
        acc_fecha = datetime.fromisoformat(accidente["Start_Time"].replace(" ", "T"))
        if acc_fecha.tzinfo is None:
            acc_fecha = acc_fecha.replace(tzinfo=timezone.utc)
        accidentes_fechas.append(acc_fecha)

    # Preparar datos de eventos
    eventos_coords = np.radians([[evento["Lat"], evento["Lng"]] for evento in eventos])
    
    # Al preparar las fechas de los eventos
    eventos_fechas_inicio = []
    eventos_fechas_fin = []
    for evento in eventos:
        try:
            evento_inicio = parser.isoparse(evento["StartTime"])
            if evento_inicio.tzinfo is None:
                evento_inicio = evento_inicio.replace(tzinfo=timezone.utc)
            eventos_fechas_inicio.append(evento_inicio)
        except ValueError:
            print(f"Formato de fecha inválido en evento: {evento['StartTime']}")
        
        evento_fin = parser.isoparse(evento["EndTime"])
        if evento_fin.tzinfo is None:
            evento_fin = evento_fin.replace(tzinfo=timezone.utc)
        eventos_fechas_fin.append(evento_fin)

    # Construir BallTree para eventos
    tree = BallTree(eventos_coords, metric='haversine')

    resultados = []

    for idx, (acc_coord, acc_fecha) in enumerate(zip(accidentes_coords, accidentes_fechas)):
        # Encontrar índices de eventos cercanos
        radio = distancia_maxima_km / 6371.0  # Convertir distancia a radianes
        indices_cercanos = tree.query_radius([acc_coord], r=radio)[0]

        # Filtrar eventos por rango de tiempo
        for i in indices_cercanos:
            evento_inicio = eventos_fechas_inicio[i]
            evento_fin = eventos_fechas_fin[i]

            if evento_inicio <= acc_fecha <= evento_fin:
                resultados.append({
                    "Accidente": accidentes[idx],
                    "Evento": eventos[i]
                })
                break  # Si se encuentra un evento correspondiente, salir del bucle

    return resultados

def filtrar_por_tipo_clima(resultados, tipo_clima):
    return [resultado for resultado in resultados if resultado["Evento"]["EventType"] == tipo_clima]

def filtrar_por_severidad_clima(resultados, severidad):
    return [resultado for resultado in resultados if resultado["Evento"]["Severity"] == severidad]

def contar_accidentes_por_categoria(resultados, categoria):
    conteo = {}
    for resultado in resultados:
        clave = resultado["Evento"][categoria]
        conteo[clave] = conteo.get(clave, 0) + 1
    return conteo

def contar_condiciones_ambientales_mongodb(accidentes, condicion):
    conteo = {}
    for accidente in accidentes:
        clave = accidente.get(condicion, "Unknown")
        conteo[clave] = conteo.get(clave, 0) + 1
    return conteo
