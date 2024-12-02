# Análisis de Accidentes por Condiciones Climáticas

Este proyecto analiza accidentes de tráfico relacionados con condiciones climáticas utilizando datos de MongoDB y Neo4j, y genera gráficos para visualizar los resultados.

## Estructura del Proyecto

- `app/`: Contiene todo el código fuente dividido en módulos.
  - `databases/`: Módulos para conectar y operar con las bases de datos MongoDB y Neo4j.
  - `services/`: Servicios para procesar datos y generar gráficos.
  - `utils/`: Funciones auxiliares.
  - `config.py`: Configuraciones y credenciales.
  - `main.py`: Punto de entrada del programa.

## Instalación

1. Clona el repositorio.
2. Navega al directorio del proyecto.
3. Crea un entorno virtual (opcional pero recomendado).

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

4. Instala las dependencias.

    ```bash
    pip install -r requirements.txt
    ```

## Uso

Ejecuta el programa principal:

```bash
python app/main.py
```

Una vez ejecutado, se presentará un menú interactivo con las siguientes opciones:

1. Seleccionar período de análisis: Define el rango de fechas para el análisis de accidentes.
2. Filtrar por tipo de clima: Filtra los accidentes según el tipo de condición climática (e.g., Neblina, Lluvia).
3. Filtrar por severidad del clima: Filtra los accidentes según la severidad del clima (e.g., Leve, Severo).
4. Visualizar gráficos combinados: Genera gráficos que combinan tipos y severidades de clima.
5. Generar gráfico de accidentes por condición climática o severidad en un año: Crea gráficos mensuales para un año específico.
6. Visualizar datos de MongoDB: Muestra los datos de accidentes almacenados en MongoDB.
7. Visualizar datos de Neo4j: Muestra los eventos climáticos almacenados en Neo4j.
8. Salir: Cierra la aplicación.

## Configuración de Bases de Datos

### MongoDB

Configura las credenciales y la URL de conexión en `config.py`:

```py
MONGODB_URI = "mongodb://usuario:contraseña@host:puerto/base_de_datos"
```

### Neo4j

Configura las credenciales y la URL de conexión en `config.py`:

```py
NEO4J_URI = "bolt://host:puerto"
NEO4J_USER = "usuario"
NEO4J_PASSWORD = "contraseña"
```

## Exportación de datos

Los gráficos generados pueden exportarse en formato CSV en el directorio `data/exports/`.

## Requisitos

- python 3.8+
- MongoDB
- Neo4j
