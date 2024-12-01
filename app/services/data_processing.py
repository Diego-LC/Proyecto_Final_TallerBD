from datetime import datetime, timezone
from math import radians, cos, sin, asin, sqrt

def calcular_distancia(lat1, lon1, lat2, lon2):
    # Convertir de grados a radianes
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Fórmula de Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radio de la Tierra en kilómetros
    return c * r

DISTANCIA_MAXIMA = 500  # Definir la distancia máxima permitida

def filtrar_accidentes_por_clima(accidentes, eventos):
    resultados = []
    for accidente in accidentes:
        try:
            # Convertir la fecha del accidente a objeto datetime
            accidente_fecha = datetime.fromisoformat(accidente["Start_Time"].replace(" ", "T"))
            if accidente_fecha.tzinfo is None:
                accidente_fecha = accidente_fecha.replace(tzinfo=timezone.utc)
        except ValueError:
            print(f"Formato de fecha inválido en accidente ID {accidente.get('ID', 'Desconocido')}.")
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
        clave = accidente.get(condicion, "Desconocido")
        conteo[clave] = conteo.get(clave, 0) + 1
    return conteo
