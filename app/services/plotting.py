import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'exports')
os.makedirs(EXPORT_DIR, exist_ok=True)

def plot_comparison(count, title, xlabel, ylabel, period=None):
    plt.figure(figsize=(12, 8))
    bars = plt.bar(count.keys(), count.values(), color=plt.cm.Paired.colors)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, fontsize=14)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    if period:
        plt.figtext(0.99, 0.95, f'Period: {period}', horizontalalignment='right', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

    # Add annotations
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + max(count.values()) * 0.01,
                 f'{height}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()

def graficar_todas_condiciones_mongodb(counts, titles, x_labels, y_labels, fields, period=None, total_accidents=None, export=True):
    import matplotlib.pyplot as plt

    # Guardar datos en CSV
    if export:
        for count, field in zip(counts, fields):
            df = pd.DataFrame(list(count.items()), columns=[field, 'Count'])
            filename = f'mongodb/{field}_{period}.csv'
            df.to_csv(os.path.join(EXPORT_DIR, filename), index=False)

    # Generar gráficos
    num_fields = len(fields)
    cols = 2
    rows = (num_fields + 1) // 2
    fig, axs = plt.subplots(rows, cols, figsize=(20, 6 * rows))
    axs = axs.flatten()

    for idx, field in enumerate(fields):
        count = counts[idx]
        title = titles[idx]
        xlabel = x_labels[idx]
        ylabel = y_labels[idx]
        ax = axs[idx]

        if field in ['Precipitation(in)', 'Temperature(F)', 'Humidity(%)']:
            # Continuous data
            try:
                values = [float(k) for k in count.keys() if k != 'Unknown']
                quantities = [v for k, v in count.items() if k != 'Unknown']

                unknowns = count.get('Unknown', 0)
                if unknowns > 0:
                    ax.text(0.95, 0.95, f'Unknown: {unknowns}', 
                            horizontalalignment='right',
                            verticalalignment='top',
                            transform=ax.transAxes,
                            fontsize=12,
                            bbox=dict(facecolor='white', alpha=0.5))

                bins = np.linspace(min(values), max(values), 11)
                counts_hist, bin_edges = np.histogram(values, bins=bins, weights=quantities)
                bin_labels = [f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(len(bin_edges)-1)]

                bars = ax.bar(bin_labels, counts_hist, color='coral')
                ax.set_xlabel(xlabel, fontsize=10)
                ax.set_ylabel(ylabel, fontsize=10)
                ax.set_title(title, fontsize=12)
                ax.tick_params(axis='x', rotation=22, labelsize=6)
                ax.grid(axis='y', linestyle='--', alpha=0.7)

                # Annotations
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2, height + max(counts_hist)*0.01,
                            f'{int(height)}', ha='center', va='bottom', fontsize=8, fontweight='light')

            except ValueError as e:
                ax.text(0.5, 0.5, f"Error processing data: {e}", 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=ax.transAxes,
                        fontsize=12,
                        color='red')
        else:
            # Categorical data
            labels = [str(k) for k in count.keys()]
            values = list(count.values())

            # Filter conditions with less than 50 data points
            threshold = 2000
            filtered_labels = []
            filtered_values = []
            others_total = 0
            for lbl, val in zip(labels, values):
                if val < threshold:
                    others_total += val
                else:
                    filtered_labels.append(lbl)
                    filtered_values.append(val)
            if others_total > 0:
                filtered_labels.append("Others")
                filtered_values.append(others_total)

            if field == "Weather_Condition":
                clear_count = count.get("Clear", 0)
                if clear_count > 0:
                    filtered_labels = [k for k in filtered_labels if k != "Clear"]
                    filtered_values = [v for k, v in zip(filtered_labels, filtered_values) if k != "Clear"]
                    ax.text(0.95, 0.95, f'Clear: {clear_count}', 
                            horizontalalignment='right',
                            verticalalignment='top',
                            transform=ax.transAxes,
                            fontsize=12,
                            bbox=dict(facecolor='white', alpha=0.5))

            bars = ax.bar(filtered_labels, filtered_values, color=plt.cm.Paired.colors)
            ax.set_xlabel(xlabel, fontsize=10)
            ax.set_ylabel(ylabel, fontsize=10)
            ax.set_title(title, fontsize=12)
            ax.tick_params(axis='x', rotation=22, labelsize=6)
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            # Annotations
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, height + max(filtered_values)*0.01,
                        f'{height}', ha='center', va='bottom', fontsize=8, fontweight='light')

    # Remove empty subplots if any
    for j in range(idx + 1, len(axs)):
        fig.delaxes(axs[j])

    if period or total_accidents:
        total_title = ''
        if period:
            total_title += f'Period: {period}'
        if total_accidents:
            total_title += f'\nTotal Accidents: {total_accidents}' if period else f'Total Accidents: {total_accidents}'
        fig.suptitle(total_title, fontsize=14, y=0.98)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

def graficar_combinado(count_type, count_severity, period=None, total_accidents=None, export=True):
    import matplotlib.pyplot as plt

    # Guardar datos en CSV
    if export:
        df_type = pd.DataFrame(list(count_type.items()), columns=['EventType', 'Count'])
        df_severity = pd.DataFrame(list(count_severity.items()), columns=['Severity', 'Count'])
        df_type.to_csv(os.path.join(EXPORT_DIR, f'Combinated/type{period}.csv'), index=False)
        df_severity.to_csv(os.path.join(EXPORT_DIR, f'Combinated/severity_{period}.csv'), index=False)

    # Generar gráficos
    fig, axs = plt.subplots(1, 2, figsize=(18, 8))

    # Events by Type
    bars_type = axs[0].bar(count_type.keys(), count_type.values(), color=plt.cm.Paired.colors)
    axs[0].set_xlabel("Weather Type", fontsize=12)
    axs[0].set_ylabel("Number of Accidents", fontsize=12)
    axs[0].set_title("Number of Accidents by Weather Type", fontsize=14)
    axs[0].tick_params(axis='x', rotation=45, labelsize=10)
    axs[0].grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars_type:
        height = bar.get_height()
        axs[0].text(bar.get_x() + bar.get_width() / 2, height + max(count_type.values()) * 0.01,
                    f'{height}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Events by Severity
    bars_severity = axs[1].bar(count_severity.keys(), count_severity.values(), color=plt.cm.Set3.colors)
    axs[1].set_xlabel("Climate Severity", fontsize=12)
    axs[1].set_ylabel("Number of Accidents", fontsize=12)
    axs[1].set_title("Number of Accidents by Climate Severity", fontsize=14)
    axs[1].tick_params(axis='x', rotation=45, labelsize=10)
    axs[1].grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars_severity:
        height = bar.get_height()
        axs[1].text(bar.get_x() + bar.get_width() / 2, height + max(count_severity.values()) * 0.01,
                    f'{height}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add total accident information in the top right corner
    if period or total_accidents:
        total_info = ''
        if period:
            total_info += f'Period: {period}'
        if total_accidents:
            total_info += f'\nTotal Accidents: {total_accidents}' if period else f'Total Accidents: {total_accidents}'
        plt.figtext(0.95, 0.95, total_info, horizontalalignment='right', fontsize=12, bbox=dict(facecolor='white', alpha=0.5))

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.show()

def graficar_neo4j(count_type, count_severity, period=None, total_events=None, export=True):
    
    if export:
        df_type = pd.DataFrame(list(count_type.items()), columns=['EventType', 'Count'])
        df_severity = pd.DataFrame(list(count_severity.items()), columns=['Severity', 'Count'])
        filename_type = f'neo4j/count_type_neo4j_{period.replace(" ", "_")}.csv' if period else 'count_type_neo4j.csv'
        filename_severity = f'neo4j/count_severity_neo4j_{period.replace(" ", "_")}.csv' if period else 'count_severity_neo4j.csv'
        df_type.to_csv(os.path.join(EXPORT_DIR, filename_type), index=False)
        df_severity.to_csv(os.path.join(EXPORT_DIR, filename_severity), index=False)

    # Generar gráficos
    fig, axs = plt.subplots(1, 2, figsize=(18, 8))

    # Events by Type
    bars_type = axs[0].bar(count_type.keys(), count_type.values(), color=plt.cm.Paired.colors)
    axs[0].set_xlabel("Event Type", fontsize=12)
    axs[0].set_ylabel("Number of Events", fontsize=12)
    axs[0].set_title("Number of Events by Type", fontsize=14)
    axs[0].tick_params(axis='x', rotation=45, labelsize=10)
    axs[0].grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars_type:
        height = bar.get_height()
        axs[0].text(bar.get_x() + bar.get_width() / 2, height + max(count_type.values()) * 0.01,
                    f'{height}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Events by Severity
    bars_severity = axs[1].bar(count_severity.keys(), count_severity.values(), color=plt.cm.Set3.colors)
    axs[1].set_xlabel("Event Severity", fontsize=12)
    axs[1].set_ylabel("Number of Events", fontsize=12)
    axs[1].set_title("Number of Events by Severity", fontsize=14)
    axs[1].tick_params(axis='x', rotation=45, labelsize=10)
    axs[1].grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars_severity:
        height = bar.get_height()
        axs[1].text(bar.get_x() + bar.get_width() / 2, height + max(count_severity.values()) * 0.01,
                    f'{height}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Add total event information in the top right corner
    if period or total_events:
        total_info = ''
        if period:
            total_info += f'Period: {period}\n'
        if total_events:
            total_info += f'Total Events: {total_events}'
        plt.figtext(0.95, 0.95, total_info, horizontalalignment='right', fontsize=12,
                    bbox=dict(facecolor='white', alpha=0.5))

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.show()

def graficar_accidentes_mensuales(year, monthly_count, selected_category, category_type, total_accidents=None, export=True):
    months = [month for month in range(1, 13)]
    quantities = [monthly_count.get(month, 0) for month in months]
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    plt.figure(figsize=(12, 8))
    bars = plt.bar(month_names, quantities, color=plt.cm.viridis.colors)
    plt.xlabel("Month", fontsize=12)
    plt.ylabel("Number of Accidents", fontsize=12)
    plt.title(f"Accidents in {year} by Month\n{category_type}: '{selected_category}'", fontsize=14)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Guardar datos en CSV
    if export:
        df = pd.DataFrame({
            'Month': month_names,
            'Accidents': quantities
        })
        filename = f'mensual/accidentes_mensuales_{year}_{selected_category.replace(" ", "_")}.csv'
        df.to_csv(os.path.join(EXPORT_DIR, filename), index=False)

    if total_accidents:
        plt.figtext(0.95, 0.95, f'Total Accidents: {total_accidents}', horizontalalignment='right', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

    # Annotations
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + max(quantities)*0.01,
                 f'{height}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()