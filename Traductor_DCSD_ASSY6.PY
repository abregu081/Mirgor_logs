#Enero 2025 Abregu Tomas proyecto para Mirgor/Motrex

import socket
import os
import csv
import sys
import re
from collections import defaultdict
from datetime import datetime, timedelta
from collections import Counter
from collections import deque

def obtener_hostname():
    try:
        hostname = socket.gethostname()
        return hostname
    except Exception as e:
        print("no se puedo obtener el hostname del equipo")

def read_setting(file):
    setting = {}
    with open(file, 'r') as f:
        for line in f:
            if line.startswith("#"):
                continue
            if not line.strip():
                continue
            if "=" in line:
                key, value = line.strip().split('=')
                value = value.strip()
                if "," in value:
                    setting[key.strip()] = [v.strip() for v in value.split(",")]
                else:
                    setting[key.strip()] = value
    return setting

def obtener_ruta_cfg():
    current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    cfg_file = os.path.join(current_directory, "Setting_DCSD_ASSY6.cfg")
    return cfg_file

def Crear_directorio_salida(directorio_salida):
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
        print(f"Directorio de salida creado en: {directorio_salida}")
    else:
        print(f"Directorio de salida encontrado en: {directorio_salida}")

def guardar_log(directorio, fecha_str, jig):
    nombre_archivo = f"{model}_{medio}_{code}_{fecha_str}_0{jig}.csv"
    output_file = os.path.join(directorio, nombre_archivo)
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_file

def guardar_resultados_completos(directorio_salida):
    archivo_salida = 'results.csv'
    archivos = [archivo for archivo in os.listdir(directorio_salida) if archivo.endswith('.csv')]
    ruta_salida = os.path.join(directorio_salida, archivo_salida)
    registros_unicos = set()
    
    for archivo in archivos:
        ruta_completa = os.path.join(directorio_salida, archivo)
        with open(ruta_completa, mode='r', encoding='utf-8') as archivo_actual:
            lector = csv.reader(archivo_actual)
            encabezado = next(lector, None)
            for fila in lector:
                registros_unicos.add(tuple(fila))
    
    registros_ordenados = sorted(
        registros_unicos, 
        key=lambda x: (x[0], x[1])  # Ordenar por "Date" (índice 0) y "Time" (índice 1)
    )
    
    with open(ruta_salida, mode='w', newline='', encoding='utf-8') as archivo_final:
        escritor = csv.writer(archivo_final)
        escritor.writerow(["Fecha", "Hora", "Barcode", "Detalle","Hostname","Box","Jig","TestTime","Resultado","Planta"])
        for registro in registros_ordenados:
            escritor.writerow(registro)
    print(f"Archivos combinados, ordenados y guardados en {ruta_salida}")

def dividir_y_guardar_por_fecha(registros, directorio_salida, procesar_todos=True):
    registros_por_fecha = defaultdict(list)

    for registro in registros:
        fecha = registro[0]  # Accede al campo "Date" usando el índice 0
        registros_por_fecha[fecha].append(registro)

    for fecha, registros_fecha in registros_por_fecha.items():
        registros_fecha_ordenados = sorted(
            registros_fecha, 
            key=lambda x: datetime.strptime(f"{x[0]} {x[1]}", "%Y%m%d %H:%M:%S")  # Ordenar usando índices
        )
        jig = 1
        while True:
            output_file = guardar_log(directorio_salida, fecha, jig)  # Usar Jig=1 por defecto
            if not os.path.exists(output_file):
                # Si el archivo no existe, crearlo y escribir los registros
                with open(output_file, "w", newline='', encoding="utf-8") as outfile:
                    csv_writer = csv.writer(outfile)
                    csv_writer.writerow(["Fecha", "Hora", "Barcode", "Detalle","Hostname","Box","Jig","TestTime","Resultado","Planta"])
                    csv_writer.writerows(registros_fecha_ordenados)
                print(f"Registros guardados en {output_file}")
                break
            else:
                with open(output_file, "r", newline='', encoding="utf-8") as infile:
                    csv_reader = csv.reader(infile)
                    registros_existentes = list(csv_reader)[1:]  # Omitir encabezado
                registros_combinados = registros_existentes + registros_fecha_ordenados
                registros_combinados_ordenados = sorted(
                    registros_combinados, 
                    key=lambda x: datetime.strptime(f"{x[0]} {x[1]}", "%Y%m%d %H:%M:%S")
                )
                os.remove(output_file)
                with open(output_file, "w", newline='', encoding="utf-8") as outfile:
                    csv_writer = csv.writer(outfile)
                    csv_writer.writerow(["Fecha", "Hora", "Barcode", "Detalle","Hostname","Box","Jig","TestTime","Resultado","Planta"])
                    csv_writer.writerows(registros_combinados_ordenados)
                print(f"Registros combinados y guardados en {output_file}")
                break


def cargar_archivos_procesados(registro_archivos_path):
    """Carga el registro de los últimos archivos procesados desde un archivo de texto."""
    if os.path.exists(registro_archivos_path):
        with open(registro_archivos_path, "r") as file:
            archivos_procesados = set(line.strip() for line in file.readlines())
    else:
        archivos_procesados = set()
    return archivos_procesados

def extraer_fecha(archivo):
    """Extrae la fecha del nombre del archivo en formato YYYYMMDDHHMMSS."""
    match = re.search(r'(\d{12})', archivo)
    return match.group(1) if match else ''

def actualizar_registro_archivos(registro_archivos_path, archivos_procesados, archivo_nuevo):
    """Actualiza el archivo de registro con los nuevos archivos procesados."""
    archivos_procesados.add(archivo_nuevo)
    if len(archivos_procesados) > 500:
        archivos_procesados = set(list(archivos_procesados)[-500:])    
    archivos_procesados = sorted(archivos_procesados, key=extraer_fecha)
    with open(registro_archivos_path, "w") as file:
        for archivo in archivos_procesados:
            file.write(f"{archivo}\n")

def obtener_Estacion(hostname):
    data = hostname
    estacion = data[-1:]
    return estacion

def procesar_tiempo(tiempo):
    if tiempo:
        try:
            return datetime.strptime(tiempo, "%H:%M:%S")
        except ValueError:
            return None
    return None  

#-----------------------inicio-----------------------------
cfg_file = obtener_ruta_cfg()
settings = read_setting(cfg_file)
model = int(settings.get("model", 0))  
input_dir = settings.get("input_dir", "")  
directorio_salida = settings.get("directorio_salida", "") 
mode = settings.get("mode", "")
medio = settings.get("medio", "")
code = settings.get("code","")
fecha_actual = datetime.now().strftime("%Y%m%d")
Crear_directorio_salida(directorio_salida)
hostname = obtener_hostname()
station = obtener_Estacion(hostname)
registro_archivos_path = r"C:\DGS\log\archivos_procesados.txt"
archivos_procesados = cargar_archivos_procesados(registro_archivos_path)
registros = []
registros_totales = []
jig = 1 

for root, dirs, files in os.walk(input_dir):
    folder_name = os.path.basename(root)  
    ruta_carpeta_fecha = os.path.join(input_dir, root)

    for file in files:
        if file.endswith(".csv"):
            file_path = os.path.join(root, file)
            try:
                fecha_archivo = datetime.strptime(file.split('.')[0], "%Y%m%d")
                if file_path in archivos_procesados:
                    continue

                if mode == "dev":
                    print(f"Procesando archivo: {file_path}")

                with open(file_path, mode="r", encoding="ISO-8859-1") as f:
                    csv_reader = csv.reader(f, delimiter=',')
                    next(csv_reader, None)
                    last_line_is_empty = False
                    for row in csv_reader:
                        # Verificar si es una línea con comas y "NG" al final
                        if all(cell == "" for cell in row[:-1]) and row[-1] == "NG":
                            step = "NG"
                            start_time = row[0]
                            test_time = row[1]  # Tiempo de prueba
                            barcode = row[3]    # Barcode
                            result = "FAIL" 
                            registros.append([folder_name, start_time, barcode, step, hostname, station, jig, test_time, result, "1"])
                            continue

                        # Verificar si es una línea con solo "OK" al final
                        if all(cell == "" for cell in row[:-1]) and row[-1] == "OK":
                            step = "N/A"  # No asignamos un paso específico para "OK"
                            result = "FAIL"  # Lo marcamos como "FAIL"
                            start_time = row[0]
                            barcode = row[3]
                            registros.append([folder_name, start_time, barcode, step, hostname, station, jig, test_time, result, "1"])
                            continue

                        # Verificar si es una línea de "User interrupt"
                        if all(cell == "" for cell in row):
                            last_line_is_empty = True
                            continue

                        # Procesar las líneas relevantes
                        if len(row) > 4 and row[3] and row[12]: 
                            start_time = row[0]
                            test_time = row[1]  
                            barcode = row[3]    
                            result = row[12]    

                            # Verificar si el archivo está en la carpeta "OK" o "NG"
                            if "NG" in root:
                                result = "FAIL"  # Si está en la carpeta "NG", el resultado es FAIL
                                step = "N/A"  # Aquí no tenemos paso definido
                                registros.append([folder_name, start_time, barcode, step, hostname, station, jig, test_time, result, "1"])

                            elif "OK" in root:
                                # En la carpeta "OK" los registros deberían ser "PASS"
                                result = "PASS"
                                step = "PASS"  # Paso de éxito
                                registros.append([folder_name, start_time, barcode, step, hostname, station, jig, test_time, result, "1"])

                            # Si la última línea está vacía, esto implica un "User interrupt"
                            if last_line_is_empty:
                                step = "User interrupt"
                                result = "FAIL"
                                # Aseguramos que no agreguemos este registro si ya se ha agregado uno
                                if [folder_name, start_time, barcode, step, hostname, station, jig, test_time, result, "1"] not in registros:
                                    registros.append([folder_name, start_time, barcode, step, hostname, station, jig, test_time, result, "1"])

            except Exception as e:
                print(f"Error al procesar el archivo {file_path}: {e}")

            actualizar_registro_archivos(registro_archivos_path, archivos_procesados, file_path)

print(f"Total de registros procesados: {len(registros)}")
dividir_y_guardar_por_fecha(registros, directorio_salida, procesar_todos=True)
guardar_resultados_completos(directorio_salida)