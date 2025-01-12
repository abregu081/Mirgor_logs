#Diciembre 2024. Abregu Tomas para proyecto Motrex/Fiat. Mirgor

#version 1.0: primera implementacion filtrado de logs y creacion de estructura de datos

import socket
import os
import csv
import sys
import re
from collections import defaultdict
from datetime import datetime, timedelta
from collections import Counter
from collections import deque

#--------------------------------------------------------------------------------------------
                                #Funciones del programa

def obtener_hostname():
    try:
        hostname = socket.gethostname()
        return hostname
    except Exception as e:
        print("no se puedo obtener el hostame del equipo")

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
    cfg_file = os.path.join(current_directory, "settings.cfg")
    return cfg_file

def Crear_directorio_salida(directorio_salida):
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
        print(f"Directorio de salida creado en: {directorio_salida}")
    else:
        print(f"Directorio de salida encontrado en: {directorio_salida}")

def extraer_fecha_y_hora(folder_name, file_name):
    # Extraer la fecha del nombre de la carpeta
    if len(folder_name) == 6 and folder_name.isdigit():
        year, month, day = f"20{folder_name[:2]}", folder_name[2:4], folder_name[4:6]
        date_str = f"{year}{month}{day}"
    else:
        date_str = "Unknown"
    # Extraer partes del nombre del archivo
    name_without_extension = os.path.basename(file_name).split('.', 1)[0]
    parts = name_without_extension.split('_')
    if len(parts) == 3:
        date_part, barcode_part, _ = parts
        time_part = date_part[len(date_part) // 2:]
        formatted_time = f"{time_part[:2]}{time_part[2:4]}{time_part[4:]}"
    else:
        barcode_part = "Unknown"
        formatted_time = "Unknown"
    return date_str, formatted_time, barcode_part

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
        key=lambda x: (x[0], x[1])  # Ordenar primero por "Date" (índice 0) y luego por "Time" (índice 1)
    )
    with open(ruta_salida, mode='w', newline='', encoding='utf-8') as archivo_final:
        escritor = csv.writer(archivo_final)
        escritor.writerow(["Date", "Time", "Barcode", "Step","Hostname","Station","Jig","TestTime","Result"])
        for registro in registros_ordenados:
            escritor.writerow(registro)
    print(f"Archivos combinados, ordenados y guardados en {ruta_salida}")

def dividir_y_guardar_por_fecha(registros, directorio_salida, fecha_actual, procesar_todos=False):
    registros_por_fecha = defaultdict(list)

    # Agrupar los registros por fecha
    for registro in registros:
        fecha = registro[0]
        if procesar_todos or fecha == fecha_actual:
            registros_por_fecha[fecha].append(registro)

    # Guardar los registros por fecha
    for fecha, registros_fecha in registros_por_fecha.items():
        # Ordenar por fecha y hora como datetime
        registros_fecha_ordenados = sorted(
            registros_fecha, 
            key=lambda x: datetime.strptime(f"{x[0]} {x[1]}", "%Y%m%d %H%M%S")  # Usar datetime para comparar
        )

        jig = 1
        while True:
            output_file = guardar_log(directorio_salida, fecha, jig) #Como unicamente se utiliza un solo jig siempre es uno para Manual Inspeccion
            
            if not os.path.exists(output_file):  
                # Si el archivo no existe, crearlo y escribir los registros
                with open(output_file, "w", newline='', encoding="utf-8") as outfile:
                    csv_writer = csv.writer(outfile)
                    csv_writer.writerow(["Date", "Time", "Barcode", "Step","Hostname","Station","Jig","TestTime","Result"])
                    csv_writer.writerows(registros_fecha_ordenados)
                print(f"Registros guardados en {output_file}")
                break
            else:
                # Si el archivo ya existe, leer los registros existentes, combinar con los nuevos y reordenar
                with open(output_file, "r", newline='', encoding="utf-8") as infile:
                    csv_reader = csv.reader(infile)
                    # Leer los registros existentes, omitir el encabezado
                    registros_existentes = list(csv_reader)[1:]
                registros_combinados = registros_existentes + registros_fecha_ordenados
                registros_combinados_ordenados = sorted(
                    registros_combinados, 
                    key=lambda x: datetime.strptime(f"{x[0]} {x[1]}", "%Y%m%d %H%M%S")
                )
                os.remove(output_file)
                with open(output_file, "w", newline='', encoding="utf-8") as outfile:
                    csv_writer = csv.writer(outfile)
                    csv_writer.writerow(["Date", "Time", "Barcode", "Step","Hostname","Station","Jig","TestTime","Result"])
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

#-----------------------inicio-----------------------------
cfg_file = obtener_ruta_cfg()
settings = read_setting(cfg_file)
model = int(settings.get("model", 0))  
input_dir = settings.get("input_dir", "")  
directorio_salida = settings.get("directorio_salida", "") 
mode = settings.get("mode", "")
code = settings.get("code","")
medio = settings.get("Medio", "")
fecha_actual = datetime.now().strftime("%Y%m%d")
Crear_directorio_salida(directorio_salida)
hostname = obtener_hostname()
station = obtener_Estacion(hostname)
registro_archivos_path = r"C:\DGS\log\archivos_procesados.txt"
archivos_procesados = cargar_archivos_procesados(registro_archivos_path)
registros = []
jig = 1

for root, dirs, files in os.walk(input_dir):
    if "PASS" in root.upper():
        default_result = "PASS"
    elif "FAIL" in root.upper():
        default_result = "FAIL"
    else:
        continue  
    for file in files:
        if file.endswith(".csv"):
            file_path = os.path.join(root, file)
            if file_path in archivos_procesados:
                continue
            if mode == "dev":
                print(f"Procesando archivo: {file_path}")
            folder_name = os.path.basename(root)
            date_str, formatted_time, barcode_part = extraer_fecha_y_hora(folder_name, file)
            testime = "N/A"
            try:
                with open(file_path, mode="r", encoding="ISO-8859-1") as f:
                    csv_reader = csv.reader(f)
                    next(csv_reader, None) 
                    filas = list(csv_reader)
                    for fila in reversed(filas):
                        for col in fila:
                            if "TEST-TIME" in col.upper():
                                try:
                                    testime = col.split(':')[1].strip()
                                    break
                                except IndexError:
                                    testime = "N/A"
                        if testime is not None:
                            break
                    
                    resultados_fail = [fila[0] for fila in filas if any("FAIL" in col.upper() for col in fila)]
                    if resultados_fail:
                        result = "FAIL"
                        step = " ".join(resultados_fail)
                    else:
                        result = default_result
                        step = "PASS" if default_result == "PASS" else "N/A"
                    registros.append([date_str, formatted_time, barcode_part, step, hostname,station, jig ,testime,result])
            except Exception as e:
                print(f"Error al procesar el archivo {file_path}: {e}")
            actualizar_registro_archivos(registro_archivos_path, archivos_procesados, file_path)
print(f"Total de registros procesados: {len(registros)}")
dividir_y_guardar_por_fecha(registros, directorio_salida, fecha_actual, procesar_todos=True)
guardar_resultados_completos(directorio_salida)


