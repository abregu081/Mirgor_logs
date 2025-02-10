import csv
import pandas as pd


def ensure_min_columns(row, min_columns=12):
    """
    Asegura que la fila tenga al menos 'min_columns' columnas.
    Si no es así, se agregan columnas vacías al final.
    """
    if len(row) < min_columns:
        row.extend([''] * (min_columns - len(row)))
    return row

def update_row(row):
    """
    Actualiza las columnas específicas de la fila con los valores requeridos.
    Se espera que la fila tenga al menos 12 columnas.
    """
    row = ensure_min_columns(row, 12)
    row[5] = '2'
    row[9] = 'PCB INSPECTION'
    row[10] = '1'
    row[11] = '52245228'
    return row

def update_csv(input_file, output_file):
    """
    Lee el archivo CSV de entrada, actualiza cada registro (excepto el encabezado) y 
    escribe el resultado en un nuevo archivo CSV.
    """
    try:
        with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            rows = list(reader)
    except Exception as e:
        print(f"Error al leer el archivo {input_file}: {e}")
        return

    if not rows:
        print("El archivo de entrada está vacío.")
        return

    # Suponiendo que el primer registro es un encabezado
    header = rows[0]
    data_rows = rows[1:]

    # Actualizamos cada fila de datos
    updated_data = [update_row(row) for row in data_rows]

    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            # Escribimos el encabezado y los datos actualizados
            writer.writerow(header)
            writer.writerows(updated_data)
        print(f"Archivo modificado guardado en: {output_file}")
    except Exception as e:
        print(f"Error al escribir en el archivo {output_file}: {e}")

if __name__ == "__main__":
    input_file = r"C:\Users\tabregu\Downloads\PCB_INSPECTION_DCSD_2.csv"
    output_file = r"C:\Users\tabregu\Downloads\PCB_INSPECTION_DCSD_2l.csv"
    update_csv(input_file, output_file)
