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
    python3 -m .venv venv
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
