import matplotlib.pyplot as plt
import numpy as np

def graficar_comparacion(conteo, titulo, etiqueta_x, etiqueta_y):
    plt.figure(figsize=(10, 6))
    plt.bar(conteo.keys(), conteo.values(), color='skyblue')
    plt.xlabel(etiqueta_x)
    plt.ylabel(etiqueta_y)
    plt.title(titulo)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def graficar_todas_condiciones_mongodb(conteos, titulos, etiquetas_x, etiquetas_y, campos):
    # Crear subgráficos (2 filas x 2 columnas)
    fig, axs = plt.subplots(2, 2, figsize=(20, 12))
    axs = axs.flatten()  # Facilitar el acceso a los ejes
    
    for idx, campo in enumerate(campos):
        conteo = conteos[idx]
        titulo = titulos[idx]
        etiqueta_x = etiquetas_x[idx]
        etiqueta_y = etiquetas_y[idx]
        
        if campo in ['Precipitation(in)', 'Temperature(F)', 'Humidity(%)']:
            # Datos continuos
            try:
                # Filtrar 'Desconocido' y convertir las claves a float
                valores = [float(k) for k in conteo.keys() if k != 'Desconocido']
                cantidades = [v for k, v in conteo.items() if k != 'Desconocido']
                
                # Manejar 'Desconocido'
                desconocidos = conteo.get('Desconocido', 0)
                if desconocidos > 0:
                    axs[idx].text(0.95, 0.95, f'Desconocidos: {desconocidos}', 
                                horizontalalignment='right',
                                verticalalignment='top',
                                transform=axs[idx].transAxes,
                                fontsize=12,
                                bbox=dict(facecolor='white', alpha=0.5))
                
                # Definir 10 bins
                bins = np.linspace(min(valores), max(valores), 11)
                counts, bin_edges = np.histogram(valores, bins=bins, weights=cantidades)
                
                # Crear etiquetas para los bins
                etiquetas_bins = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)]
                
                axs[idx].bar(etiquetas_bins, counts, color='coral')
                axs[idx].set_xlabel(etiqueta_x)
                axs[idx].set_ylabel(etiqueta_y)
                axs[idx].set_title(titulo)
                axs[idx].tick_params(axis='x', rotation=45)
            
            except ValueError as e:
                axs[idx].text(0.5, 0.5, f"Error al procesar los datos: {e}", 
                            horizontalalignment='center',
                            verticalalignment='center',
                            transform=axs[idx].transAxes,
                            fontsize=12,
                            color='red')
        else:
            # Datos categóricos
            etiquetas = [str(k) for k in conteo.keys()]
            valores = list(conteo.values())
            
            # Filtrar y contar 'Clear' si es 'Weather_Condition'
            if campo == "Weather_Condition":
                clear_count = conteo.get("Clear", 0)
                if clear_count > 0:
                    # Excluir 'Clear' del conteo principal
                    etiquetas = [k for k in etiquetas if k != "Clear"]
                    valores = [v for k, v in conteo.items() if k != "Clear"]
                    
                    # Añadir texto con la cantidad filtrada
                    axs[idx].text(0.95, 0.95, f'Clear: {clear_count}', 
                                horizontalalignment='right',
                                verticalalignment='top',
                                transform=axs[idx].transAxes,
                                fontsize=12,
                                bbox=dict(facecolor='white', alpha=0.5))
            
            axs[idx].bar(etiquetas, valores, color='skyblue')
            axs[idx].set_xlabel(etiqueta_x)
            axs[idx].set_ylabel(etiqueta_y)
            axs[idx].set_title(titulo)
            axs[idx].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()

def graficar_combinado(conteo_tipo, conteo_severidad):
    import matplotlib.pyplot as plt
    
    # Crear figura con subplots
    fig, axs = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico de Accidentes por Tipo de Clima
    axs[0].bar(conteo_tipo.keys(), conteo_tipo.values(), color='skyblue')
    axs[0].set_xlabel("Tipo de Clima")
    axs[0].set_ylabel("Cantidad de Accidentes")
    axs[0].set_title("Número de Accidentes por Tipo de Clima")
    axs[0].tick_params(axis='x', rotation=45)
    
    # Gráfico de Accidentes por Severidad del Clima
    axs[1].bar(conteo_severidad.keys(), conteo_severidad.values(), color='salmon')
    axs[1].set_xlabel("Severidad del Clima")
    axs[1].set_ylabel("Cantidad de Accidentes")
    axs[1].set_title("Número de Accidentes por Severidad del Clima")
    axs[1].tick_params(axis='x', rotation=45)
    
    # Ajustar el diseño y mostrar los gráficos
    plt.tight_layout()
    plt.show()


def graficar_accidentes_mensuales(anio, conteo_mensual, categoria_seleccionada, tipo_categoria):
    import matplotlib.pyplot as plt
    # Crear una lista de meses
    meses = [mes for mes in range(1, 13)]
    # Obtener los valores correspondientes a cada mes
    cantidades = [conteo_mensual.get(mes, 0) for mes in meses]
    # Nombres de los meses
    nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    plt.figure(figsize=(10, 6))
    plt.bar(nombres_meses, cantidades, color='purple')
    plt.xlabel("Mes")
    plt.ylabel("Cantidad de Accidentes")
    plt.title(f"Accidentes en {anio} por Mes\n{tipo_categoria}: '{categoria_seleccionada}'")
    plt.tight_layout()
    plt.show()
