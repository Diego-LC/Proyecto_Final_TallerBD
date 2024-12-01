import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from app.databases.mongodb import conectar_mongodb
from app.databases.neo4j import Neo4jConnector
from app.services.data_processing import (
    filtrar_accidentes_por_clima,
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
            # Seleccionar período de análisis
            print("\n--- Selección de Período de Análisis ---")
            fecha_inicio = obtener_fecha("Ingresa la fecha de inicio (YYYY-MM-DDTHH:MM:SSZ): ")
            fecha_fin = obtener_fecha("Ingresa la fecha de fin (YYYY-MM-DDTHH:MM:SSZ): ")
            print(f"Período seleccionado: {fecha_inicio} a {fecha_fin}")

        elif opcion == '2':
            # Filtrar por tipo de clima
            tipo_clima = input("Ingresa el tipo de clima a filtrar (e.g., Fog, Rain): ")
            print(f"Filtrando por tipo de clima: {tipo_clima}")

        elif opcion == '3':
            # Filtrar por severidad del clima
            severidad = input("Ingresa la severidad del clima a filtrar (e.g., Mild, Severe): ")
            print(f"Filtrando por severidad del clima: {severidad}")

        elif opcion == '4':
            # Visualizar gráficos combinados
            if not fecha_inicio or not fecha_fin:
                print("Por favor, selecciona primero un período de análisis (Opción 1).")
                continue

            # Extraer eventos climáticos de Neo4j
            eventos = neo4j.obtener_eventos_por_periodo(fecha_inicio, fecha_fin)

            # Asegurar que StartTime sea offset-aware
            for evento in eventos:
                start_time = evento["StartTime"]
                dt = datetime.fromisoformat(start_time)
                if dt.tzinfo is None:
                    evento["StartTime"] = dt.replace(tzinfo=timezone.utc)
                else:
                    evento["StartTime"] = dt

            # Extraer accidentes de MongoDB
            accidentes = list(coleccion_mongodb.find({
                "Start_Time": {"$gte": fecha_inicio, "$lte": fecha_fin}
            }))

            print(f"Se encontraron {len(accidentes)} accidentes y {len(eventos)} eventos climáticos")

            # Relacionar accidentes con eventos climáticos
            resultados = filtrar_accidentes_por_clima(accidentes, eventos)

            # Aplicar filtros adicionales si se han seleccionado
            if tipo_clima:
                resultados = filtrar_por_tipo_clima(resultados, tipo_clima)

            if severidad:
                resultados = filtrar_por_severidad_clima(resultados, severidad)

            # Obtener los conteos
            conteo_tipo = contar_accidentes_por_categoria(resultados, "EventType")
            conteo_severidad = contar_accidentes_por_categoria(resultados, "Severity")

            # Llamar a la función de graficación en plotting.py
            graficar_combinado(conteo_tipo, conteo_severidad)
            tipo_clima = None
            severidad = None

        elif opcion == '5':
            # Visualizar datos de MongoDB
            if not fecha_inicio or not fecha_fin:
                print("Por favor, selecciona primero un período de análisis (Opción 1).")
                continue

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
            graficar_todas_condiciones_mongodb(conteos, titulos, etiquetas_x, etiquetas_y, campos)

        elif opcion == '6':
            # Generar gráfico de accidentes por condición climática o severidad en un año
            print("\n--- Generación de Gráfico de Accidentes Mensuales ---")
            # Submenú para seleccionar el año
            anios = ['2016', '2017', '2018', '2019', '2020', '2021', '2022']
            print("Selecciona el año:")
            for idx, anio in enumerate(anios):
                print(f"{idx + 1}. {anio}")
            opcion_anio = input("Selecciona un año (1-7): ")
            if opcion_anio not in [str(i) for i in range(1, 8)]:
                print("Opción de año inválida.")
                continue
            anio_seleccionado = anios[int(opcion_anio) - 1]
            # Submenú para seleccionar el tipo de análisis
            print("\nSelecciona el tipo de análisis:")
            print("1. Condición climática")
            print("2. Severidad del accidente")
            tipo_analisis = input("Selecciona una opción (1-2): ")
            if tipo_analisis not in ['1', '2']:
                print("Opción inválida.")
                continue
            print(f"\nObteniendo datos para el año {anio_seleccionado}...")
            # Definir el rango de fechas7
            fecha_inicio = f"{anio_seleccionado}-01-01T00:00:00Z"
            fecha_fin = f"{anio_seleccionado}-12-31T23:59:59Z"
            # Obtener accidentes de MongoDB para el año seleccionado
            accidentes = list(coleccion_mongodb.find({
                "Start_Time": {"$gte": fecha_inicio, "$lte": fecha_fin}
            }))
            eventos = neo4j.obtener_eventos_por_periodo(fecha_inicio, fecha_fin)
            for evento in eventos:
                start_time = evento["StartTime"]
                dt = datetime.fromisoformat(start_time)
                dtf = datetime.fromisoformat(evento["EndTime"])
                if dt.tzinfo is None:
                    evento["StartTime"] = dt.replace(tzinfo=timezone.utc)
                    evento["EndTime"] = dtf.replace(tzinfo=timezone.utc)
                else:
                    evento["StartTime"] = dt
                    evento["EndTime"] = dtf
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
                    continue
                print(f"Generando gráfico de accidentes por condición climática en {anio_seleccionado}...")
                condicion_seleccionada = condiciones_climaticas[int(opcion_condicion) - 1]
                # Filtrar accidentes por condición climática seleccionada
                accidentes_filtrados = filtrar_accidentes_por_clima(accidentes, eventos)
                print(f"Se encontraron {len(accidentes_filtrados)} accidentes en {anio_seleccionado}")
                if condicion_seleccionada != 'Todos':
                    accidentes_filtrados = filtrar_por_tipo_clima(accidentes_filtrados, condicion_seleccionada)
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
                    continue
                print(f"Generando gráfico de accidentes por severidad en {anio_seleccionado}...")
                severidad_seleccionada = severidades[int(opcion_severidad) - 1]
                # Filtrar accidentes por severidad seleccionada
                accidentes_filtrados = filtrar_accidentes_por_clima(accidentes, eventos)
                resultados = filtrar_por_severidad_clima(accidentes_filtrados, severidad_seleccionada)
                # Contar accidentes por mes
                conteo_mensual = {}
                for acc in resultados:
                    mes = int(acc['Accidente']["Start_Time"][5:7])  # Extraer el mes de la fecha
                    conteo_mensual[mes] = conteo_mensual.get(mes, 0) + 1
                # Generar gráfico
                graficar_accidentes_mensuales(anio_seleccionado, conteo_mensual, severidad_seleccionada, 'Severidad')

        elif opcion == '7':
            # Salir
            print("Saliendo del programa...")
            neo4j.close()
            break

if __name__ == "__main__":
    main()
