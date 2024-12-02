import matplotlib.pyplot as plt
import numpy as np

def graficar_comparacion(conteo, titulo, etiqueta_x, etiqueta_y, periodo=None):
    plt.figure(figsize=(12, 8))
    barras = plt.bar(conteo.keys(), conteo.values(), color=plt.cm.Paired.colors)
    plt.xlabel(etiqueta_x, fontsize=12)
    plt.ylabel(etiqueta_y, fontsize=12)
    plt.title(titulo, fontsize=14)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    if periodo:
        plt.figtext(0.99, 0.01, f'Período: {periodo}', horizontalalignment='right', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

    # Añadir anotaciones
    for barra in barras:
        altura = barra.get_height()
        plt.text(barra.get_x() + barra.get_width() / 2, altura + max(conteo.values()) * 0.01,
                 f'{altura}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()

def graficar_todas_condiciones_mongodb(conteos, titulos, etiquetas_x, etiquetas_y, campos, periodo=None):
    # Crear subgráficos dinámicamente según el número de campos
    num_campos = len(campos)
    cols = 2
    rows = (num_campos + 1) // 2
    fig, axs = plt.subplots(rows, cols, figsize=(20, 6 * rows))
    axs = axs.flatten()

    for idx, campo in enumerate(campos):
        conteo = conteos[idx]
        titulo = titulos[idx]
        etiqueta_x = etiquetas_x[idx]
        etiqueta_y = etiquetas_y[idx]
        ax = axs[idx]

        if campo in ['Precipitation(in)', 'Temperature(F)', 'Humidity(%)']:
            # Datos continuos
            try:
                valores = [float(k) for k in conteo.keys() if k != 'Desconocido']
                cantidades = [v for k, v in conteo.items() if k != 'Desconocido']

                desconocidos = conteo.get('Desconocido', 0)
                if desconocidos > 0:
                    ax.text(0.95, 0.95, f'Desconocidos: {desconocidos}', 
                            horizontalalignment='right',
                            verticalalignment='top',
                            transform=ax.transAxes,
                            fontsize=12,
                            bbox=dict(facecolor='white', alpha=0.5))

                bins = np.linspace(min(valores), max(valores), 11)
                counts, bin_edges = np.histogram(valores, bins=bins, weights=cantidades)
                etiquetas_bins = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)]

                barras = ax.bar(etiquetas_bins, counts, color='coral')
                ax.set_xlabel(etiqueta_x, fontsize=12)
                ax.set_ylabel(etiqueta_y, fontsize=12)
                ax.set_title(titulo, fontsize=14)
                ax.tick_params(axis='x', rotation=45, labelsize=10)
                ax.grid(axis='y', linestyle='--', alpha=0.7)

                # Anotaciones
                for barra in barras:
                    altura = barra.get_height()
                    ax.text(barra.get_x() + barra.get_width() / 2, altura + max(counts)*0.01,
                            f'{int(altura)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

            except ValueError as e:
                ax.text(0.5, 0.5, f"Error al procesar los datos: {e}", 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax.transAxes,
                        fontsize=12,
                        color='red')
        else:
            # Datos categóricos
            etiquetas = [str(k) for k in conteo.keys()]
            valores = list(conteo.values())

            if campo == "Weather_Condition":
                clear_count = conteo.get("Clear", 0)
                if clear_count > 0:
                    etiquetas = [k for k in etiquetas if k != "Clear"]
                    valores = [v for k, v in conteo.items() if k != "Clear"]
                    ax.text(0.95, 0.95, f'Clear: {clear_count}', 
                            horizontalalignment='right',
                            verticalalignment='top',
                            transform=ax.transAxes,
                            fontsize=12,
                            bbox=dict(facecolor='white', alpha=0.5))

            barras = ax.bar(etiquetas, valores, color=plt.cm.Paired.colors)
            ax.set_xlabel(etiqueta_x, fontsize=12)
            ax.set_ylabel(etiqueta_y, fontsize=12)
            ax.set_title(titulo, fontsize=14)
            ax.tick_params(axis='x', rotation=45, labelsize=10)
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Anotaciones
            for barra in barras:
                altura = barra.get_height()
                ax.text(barra.get_x() + barra.get_width() / 2, altura + max(valores)*0.01,
                        f'{altura}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Eliminar subgráficos vacíos si los hay
    for j in range(idx + 1, len(axs)):
        fig.delaxes(axs[j])

    if periodo:
        fig.suptitle(f'Período: {periodo}', fontsize=16, y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

def graficar_combinado(conteo_tipo, conteo_severidad, periodo=None):
    fig, axs = plt.subplots(1, 2, figsize=(18, 8))

    # Gráfico de Accidentes por Tipo de Clima
    barras_tipo = axs[0].bar(conteo_tipo.keys(), conteo_tipo.values(), color=plt.cm.Paired.colors)
    axs[0].set_xlabel("Tipo de Clima", fontsize=12)
    axs[0].set_ylabel("Cantidad de Accidentes", fontsize=12)
    axs[0].set_title("Número de Accidentes por Tipo de Clima", fontsize=14)
    axs[0].tick_params(axis='x', rotation=45, labelsize=10)
    axs[0].grid(axis='y', linestyle='--', alpha=0.7)

    for barra in barras_tipo:
        altura = barra.get_height()
        axs[0].text(barra.get_x() + barra.get_width() / 2, altura + max(conteo_tipo.values()) * 0.01,
                    f'{altura}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Gráfico de Accidentes por Severidad del Clima
    barras_severidad = axs[1].bar(conteo_severidad.keys(), conteo_severidad.values(), color=plt.cm.Set3.colors)
    axs[1].set_xlabel("Severidad del Clima", fontsize=12)
    axs[1].set_ylabel("Cantidad de Accidentes", fontsize=12)
    axs[1].set_title("Número de Accidentes por Severidad del Clima", fontsize=14)
    axs[1].tick_params(axis='x', rotation=45, labelsize=10)
    axs[1].grid(axis='y', linestyle='--', alpha=0.7)

    for barra in barras_severidad:
        altura = barra.get_height()
        axs[1].text(barra.get_x() + barra.get_width() / 2, altura + max(conteo_severidad.values()) * 0.01,
                    f'{altura}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    if periodo:
        fig.suptitle(f'Período: {periodo}', fontsize=16, y=0.95)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.show()

def graficar_accidentes_mensuales(anio, conteo_mensual, categoria_seleccionada, tipo_categoria, periodo=None):
    meses = [mes for mes in range(1, 13)]
    cantidades = [conteo_mensual.get(mes, 0) for mes in meses]
    nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                    'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    plt.figure(figsize=(12, 8))
    barras = plt.bar(nombres_meses, cantidades, color=plt.cm.viridis.colors)
    plt.xlabel("Mes", fontsize=12)
    plt.ylabel("Cantidad de Accidentes", fontsize=12)
    plt.title(f"Accidentes en {anio} por Mes\n{tipo_categoria}: '{categoria_seleccionada}'", fontsize=14)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    if periodo:
        plt.figtext(0.99, 0.01, f'Período: {periodo}', horizontalalignment='right', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

    # Anotaciones
    for barra in barras:
        altura = barra.get_height()
        plt.text(barra.get_x() + barra.get_width() / 2, altura + max(cantidades)*0.01,
                 f'{altura}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()
