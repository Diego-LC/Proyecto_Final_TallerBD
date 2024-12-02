import sys
import os
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.databases.mongodb import conectar_mongodb
from app.databases.neo4j import Neo4jConnector
from app.services.data_processing import (
    filtrar_accidentes_por_clima_optimizado,
    filtrar_por_tipo_clima,
    filtrar_por_severidad_clima,
    contar_accidentes_por_categoria,
    contar_condiciones_ambientales_mongodb
)
from app.services.plotting import (
    graficar_combinado,
    graficar_comparacion,
    graficar_todas_condiciones_mongodb,
    graficar_accidentes_mensuales
)
from app.utils.helpers import obtener_fecha

def procesar_eventos(eventos):
    df = pd.DataFrame(eventos)
    df["StartTime"] = pd.to_datetime(df["StartTime"], utc=True)
    df["EndTime"] = pd.to_datetime(df["EndTime"], utc=True)
    return df.to_dict('records')

def mostrar_menu():
    print("\n===== Menú de Análisis de Accidentes =====")
    print("1. Seleccionar período de análisis")
    print("2. Filtrar por tipo de clima")
    print("3. Filtrar por severidad del clima")
    print("4. Visualizar gráficos combinados")
    print("5. Visualizar datos de MongoDB")
    print("6. Generar gráfico de accidentes por condición climática o severidad en un año")
    print("7. Salir")
    print("==========================================")

def seleccionar_opcion():
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción: ")
        if opcion in ['1', '2', '3', '4', '5', '6', '7']:
            return opcion
        else:
            print("Opción inválida. Por favor, elige una entre 1 y 7.")

def opcion_seleccionar_periodo():
    print("\n--- Selección de Período de Análisis ---")
    
    # Seleccionar año
    anios = [str(año) for año in range(2016, 2023)]
    print("Selecciona un año:")
    for idx, anio in enumerate(anios, 1):
        print(f"{idx}. {anio}")
    opcion_anio = input(f"Selecciona una opción (1-{len(anios)}): ")
    if opcion_anio not in [str(i) for i in range(1, len(anios) + 1)]:
        print("Opción de año inválida.")
        return None, None
    anio_seleccionado = anios[int(opcion_anio) - 1]
    
    # Seleccionar método de ingreso de fecha
    print("\nSelecciona el método de selección de período:")
    print("1. Seleccionar un mes completo")
    print("2. Ingresar fecha manualmente")
    metodo = input("Selecciona una opción (1-2): ")
    
    if metodo == '1':
        # Seleccionar mes
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        print("\nSelecciona un mes:")
        for idx, mes in enumerate(meses, 1):
            print(f"{idx}. {mes}")
        opcion_mes = input("Selecciona una opción (1-12): ")
        if opcion_mes not in [str(i) for i in range(1, 13)]:
            print("Opción de mes inválida.")
            return None, None
        mes_seleccionado = int(opcion_mes)
        fecha_inicio = f"{anio_seleccionado}-{mes_seleccionado:02d}-01T00:00:00Z"
        # Calcular último día del mes
        import calendar
        ultimo_dia = calendar.monthrange(int(anio_seleccionado), mes_seleccionado)[1]
        fecha_fin = f"{anio_seleccionado}-{mes_seleccionado:02d}-{ultimo_dia:02d}T23:59:59Z"
        if fecha_fin < fecha_inicio:
            print("La fecha de fin debe ser posterior a la fecha de inicio.")
            return
        print(f"Período seleccionado: {fecha_inicio} a {fecha_fin}")
        return fecha_inicio, fecha_fin
    
    elif metodo == '2':
        # Ingresar fecha manualmente
        print("\nIngresar fecha de inicio:")
        fecha_inicio = obtener_fecha_manual(anio_seleccionado, fecha_inicio=True)
        print("\nIngresar fecha de fin:")
        fecha_fin = obtener_fecha_manual(anio_seleccionado)
        if fecha_fin < fecha_inicio:
            print("La fecha de fin debe ser posterior a la fecha de inicio.")
            return
        print(f"Período seleccionado: {fecha_inicio} a {fecha_fin}")
        return fecha_inicio, fecha_fin
    else:
        print("Opción de método inválida.")
        return None, None

def obtener_fecha_manual(anio, fecha_inicio=False):
    while True:
        try:
            dia = input("Ingresa el día (DD): ")
            mes = input("Ingresa el mes (MM): ")
            hora = input("Ingresa la hora (HH:MM:SS) en formato 24h (o vacío por defecto): ")
            fecha = f"{anio}-{int(mes):02d}-{int(dia):02d}T{hora}Z"
            # Validar fecha
            if hora == "" and fecha_inicio:
                fecha = f"{anio}-{int(mes):02d}-{int(dia):02d}T00:00:00Z"
            elif hora == "":
                fecha = f"{anio}-{int(mes):02d}-{int(dia):02d}T23:59:59Z"
            pd.to_datetime(fecha)
            return fecha
        except:
            print("Formato de fecha inválido. Intenta nuevamente.")

def opcion_filtrar_tipo_clima():
    tipo_clima = input("Ingresa el tipo de clima a filtrar (e.g., Fog, Rain): ")
    print(f"Filtrando por tipo de clima: {tipo_clima}")
    return tipo_clima

def opcion_filtrar_severidad_clima():
    severidad = input("Ingresa la severidad del clima a filtrar (e.g., Mild, Severe): ")
    print(f"Filtrando por severidad del clima: {severidad}")
    return severidad

def opcion_visualizar_graficos(fecha_inicio, fecha_fin, tipo_clima, severidad, coleccion_mongodb, neo4j):
    if not fecha_inicio or not fecha_fin:
        print("Por favor, selecciona primero un período de análisis (Opción 1).")
        return
    print("\nBuscando datos para el período seleccionado...")

    # Extraer eventos climáticos de Neo4j
    eventos = neo4j.obtener_eventos_por_periodo(fecha_inicio, fecha_fin)

    # Procesar eventos
    #eventos = procesar_eventos(eventos)

    # Extraer accidentes de MongoDB
    accidentes = list(coleccion_mongodb.find({
        "Start_Time": {"$gte": fecha_inicio, "$lte": fecha_fin}
    }))

    print(f"Se encontraron {len(accidentes)} accidentes y {len(eventos)} eventos climáticos")

    # Relacionar accidentes con eventos climáticos
    resultados = filtrar_accidentes_por_clima_optimizado(accidentes, eventos)

    # Aplicar filtros adicionales si se han seleccionado
    if tipo_clima:
        resultados = filtrar_por_tipo_clima(resultados, tipo_clima)

    if severidad:
        resultados = filtrar_por_severidad_clima(resultados, severidad)

    # Obtener los conteos
    conteo_tipo = contar_accidentes_por_categoria(resultados, "EventType")
    conteo_severidad = contar_accidentes_por_categoria(resultados, "Severity")

    # Formatear período sin hora
    periodo = f"{fecha_inicio.split('T')[0]} a {fecha_fin.split('T')[0]}"

    # Llamar a la función de graficación en plotting.py
    graficar_combinado(conteo_tipo, conteo_severidad, periodo=periodo)

def opcion_visualizar_mongodb(fecha_inicio, fecha_fin, coleccion_mongodb):
    if not fecha_inicio or not fecha_fin:
        print("Por favor, selecciona primero un período de análisis (Opción 1).")
        return
    print("\nBuscando datos para el período seleccionado...")

    # Extraer accidentes de MongoDB
    accidentes = list(coleccion_mongodb.find({
        "Start_Time": {"$gte": fecha_inicio, "$lte": fecha_fin}
    }))

    print(f"Se encontraron {len(accidentes)} accidentes en MongoDB")

    # Definir todas las condiciones a analizar
    condiciones = {
        "Weather_Condition": {
            "titulo": "Número de Accidentes por Condición Climática",
            "etiqueta_x": "Condición Climática",
            "etiqueta_y": "Cantidad de Accidentes"
        },
        "Precipitation(in)": {
            "titulo": "Número de Accidentes por Precipitación",
            "etiqueta_x": "Precipitación (in)",
            "etiqueta_y": "Cantidad de Accidentes"
        },
        "Temperature(F)": {
            "titulo": "Número de Accidentes por Temperatura",
            "etiqueta_x": "Temperatura (F)",
            "etiqueta_y": "Cantidad de Accidentes"
        },
        "Humidity(%)": {
            "titulo": "Número de Accidentes por Humedad",
            "etiqueta_x": "Humedad (%)",
            "etiqueta_y": "Cantidad de Accidentes"
        }
    }

    # Contar accidentes por cada condición
    conteos = []
    titulos = []
    etiquetas_x = []
    etiquetas_y = []
    campos = []

    for campo, info in condiciones.items():
        conteo = contar_condiciones_ambientales_mongodb(accidentes, campo)
        conteos.append(conteo)
        titulos.append(info["titulo"])
        etiquetas_x.append(info["etiqueta_x"])
        etiquetas_y.append(info["etiqueta_y"])
        campos.append(campo)

    # Graficar todas las condiciones en un solo plot
    graficar_todas_condiciones_mongodb(conteos, titulos, etiquetas_x, etiquetas_y, campos, periodo=f"{fecha_inicio} a {fecha_fin}")

def opcion_graficar_accidentes_anuales(coleccion_mongodb, neo4j):
    print("\n--- Generación de Gráfico de Accidentes Mensuales ---")
    # Submenú para seleccionar el año
    anios = ['2016', '2017', '2018', '2019', '2020', '2021', '2022']
    print("Selecciona el año:")
    for idx, anio in enumerate(anios):
        print(f"{idx + 1}. {anio}")
    opcion_anio = input("Selecciona un año (1-7): ")
    if opcion_anio not in [str(i) for i in range(1, 8)]:
        print("Opción de año inválida.")
        return
    anio_seleccionado = anios[int(opcion_anio) - 1]
    # Submenú para seleccionar el tipo de análisis
    print("\nSelecciona el tipo de análisis:")
    print("1. Condición climática")
    print("2. Severidad del accidente")
    tipo_analisis = input("Selecciona una opción (1-2): ")
    if tipo_analisis not in ['1', '2']:
        print("Opción inválida.")
        return
    print(f"\nObteniendo datos para el año {anio_seleccionado}...")
    # Definir el rango de fechas
    fecha_inicio = f"{anio_seleccionado}-01-01T00:00:00Z"
    fecha_fin = f"{anio_seleccionado}-12-31T23:59:59Z"
    # Obtener accidentes de MongoDB para el año seleccionado
    accidentes = list(coleccion_mongodb.find({
        "Start_Time": {"$gte": fecha_inicio, "$lte": fecha_fin}
    }))
    eventos = neo4j.obtener_eventos_por_periodo(fecha_inicio, fecha_fin)
    #eventos = procesar_eventos(eventos)
    print(f"Se encontraron {len(accidentes)} accidentes y {len(eventos)} eventos climáticos en {anio_seleccionado}")
    if tipo_analisis == '1':
        # Opciones de condiciones climáticas
        condiciones_climaticas = ['Snow', 'Rain', 'Cold', 'Fog', 'Storm', 'Precipitation', 'Todos']
        print("\nSelecciona la condición climática:")
        for idx, condicion in enumerate(condiciones_climaticas):
            print(f"{idx + 1}. {condicion}")
        opcion_condicion = input(f"Selecciona una opción (1-{len(condiciones_climaticas)}): ")
        if opcion_condicion not in [str(i) for i in range(1, len(condiciones_climaticas) + 1)]:
            print("Opción inválida.")
            return
        condicion_seleccionada = condiciones_climaticas[int(opcion_condicion) - 1]
        print(f"\nGenerando gráfico de accidentes por condición climática en {anio_seleccionado}...")
        # Filtrar accidentes por condición climática seleccionada
        accidentes_filtrados = filtrar_accidentes_por_clima_optimizado(accidentes, eventos)
        if condicion_seleccionada != 'Todos':
            accidentes_filtrados = filtrar_por_tipo_clima(accidentes_filtrados, condicion_seleccionada)
        print(f"Se encontraron {len(accidentes_filtrados)} accidentes en {anio_seleccionado}")
        # Contar accidentes por mes
        conteo_mensual = {}
        for acc in accidentes_filtrados:
            mes = int(acc['Accidente']["Start_Time"][5:7])  # Extraer el mes de la fecha
            conteo_mensual[mes] = conteo_mensual.get(mes, 0) + 1
        # Generar gráfico
        graficar_accidentes_mensuales(anio_seleccionado, conteo_mensual, condicion_seleccionada, 'Condición Climática')
    else:
        # Opciones de severidad
        severidades = ['1', '2', '3', '4']
        print("\nSelecciona la severidad del accidente:")
        for idx, sev in enumerate(severidades):
            print(f"{idx + 1}. {sev}")
        opcion_severidad = input(f"Selecciona una opción (1-{len(severidades)}): ")
        if opcion_severidad not in [str(i) for i in range(1, len(severidades) + 1)]:
            print("Opción inválida.")
            return
        severidad_seleccionada = severidades[int(opcion_severidad) - 1]
        print(f"Generando gráfico de accidentes por severidad en {anio_seleccionado}...")
        # Filtrar accidentes por severidad seleccionada
        accidentes_filtrados = filtrar_accidentes_por_clima_optimizado(accidentes, eventos)
        resultados = filtrar_por_severidad_clima(accidentes_filtrados, severidad_seleccionada)
        # Contar accidentes por mes
        conteo_mensual = {}
        for acc in resultados:
            mes = int(acc['Accidente']["Start_Time"][5:7])  # Extraer el mes de la fecha
            conteo_mensual[mes] = conteo_mensual.get(mes, 0) + 1
        # Generar gráfico
        graficar_accidentes_mensuales(anio_seleccionado, conteo_mensual, severidad_seleccionada, 'Severidad')

def main():
    # Conexión a MongoDB
    coleccion_mongodb = conectar_mongodb()

    # Conexión a Neo4j
    neo4j = Neo4jConnector()

    # Variables para filtros
    fecha_inicio = None
    fecha_fin = None
    tipo_clima = None
    severidad = None

    while True:
        opcion = seleccionar_opcion()

        if opcion == '1':
            fecha_inicio, fecha_fin = opcion_seleccionar_periodo()
        elif opcion == '2':
            tipo_clima = opcion_filtrar_tipo_clima()
        elif opcion == '3':
            severidad = opcion_filtrar_severidad_clima()
        elif opcion == '4':
            opcion_visualizar_graficos(fecha_inicio, fecha_fin, tipo_clima, severidad, coleccion_mongodb, neo4j)
            # Restablecer filtros
            tipo_clima = None
            severidad = None
        elif opcion == '5':
            opcion_visualizar_mongodb(fecha_inicio, fecha_fin, coleccion_mongodb)
        elif opcion == '6':
            opcion_graficar_accidentes_anuales(coleccion_mongodb, neo4j)
        elif opcion == '7':
            print("Saliendo del programa...")
            neo4j.close()
            break

if __name__ == "__main__":
    main()