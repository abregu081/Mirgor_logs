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

#--------------------------------------------------------------------------------------------
                                #logica del programa

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
    cfg_file = os.path.join(current_directory, "Setting_Autoinspeccion.cfg")
    return cfg_file

def Crear_directorio_salida(directorio_salida):
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
        print(f"Directorio de salida creado en: {directorio_salida}")
    else:
        print(f"Directorio de salida encontrado en: {directorio_salida}")

def extraer_fecha_y_hora(folder_name, file_name):
    if len(folder_name) == 6 and folder_name.isdigit():
        year, month, day = f"20{folder_name[:2]}", folder_name[2:4], folder_name[4:6]
        date_str = f"{year}{month}{day}"
    else:
        date_str = "Unknown"

    name_without_extension = os.path.basename(file_name).split('.', 1)[0]
    parts = name_without_extension.split('_')

    if len(parts) >= 1:
        date_time_part = parts[0]  # Primer segmento contiene YYYYMMDDHHMMSS
        if len(date_time_part) == 14 and date_time_part.isdigit():
            date_str = date_time_part[:8]  # Extraer YYYYMMDD
            time_str = date_time_part[8:]  # Extraer HHMMSS
        else:
            date_str = "Unknown"
            time_str = "Unknown"
    else:
        time_str = "Unknown"

    if len(parts) >= 2:
        barcode_part = parts[1]
    else:
        barcode_part = "Unknown"

    if file_name[-5] == "L":  # Penúltimo carácter antes de ".csv"
        jig = 1
    elif file_name[-5] == "R":  # Penúltimo carácter antes de ".csv"
        jig = 2
    else:
        jig = "Unknown"

    return date_str, time_str, barcode_part, jig

def guardar_log(directorio, fecha_str, jig):
    nombre_archivo = f"{model}_{nombre_estacion}_{code}_{fecha_str}_0{jig}.csv"
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
    # Iterar sobre los archivos CSV
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
        escritor.writerow(["Fecha", "Hora", "Barcode", "Detalle","Hostname","Box","Jig","TestTime","Resultado","Medio","Planta","Modelo"])
        for registro in registros_ordenados:
            escritor.writerow(registro)
    print(f"Archivos combinados, ordenados y guardados en {ruta_salida}")

def dividir_y_guardar_por_fecha(registros, directorio_salida, fecha_actual, procesar_todos=False):
    registros_por_fecha = defaultdict(list)
    resgistros_por_jig = defaultdict(list)
    
    # Agrupar los registros por fecha
    for registro in registros:
        hora = registro[1]
        fecha = registro[0]
        jig = registro[6]
        if procesar_todos or fecha == fecha_actual:
            registros_por_fecha[fecha].append(registro)
            resgistros_por_jig[(fecha,jig)].append(registro)

    
    for (fecha,jig),resgistros_por_jig in resgistros_por_jig.items():
        try:
            # Validar y convertir las fechas antes de ordenarlas
            registros_jig_ordenados = sorted(
                resgistros_por_jig, 
                key=lambda x: datetime.strptime(f"{x[0]} {x[1]}", "%Y%m%d %H%M%S")  # Corregido
            )
        except ValueError as e:
            print(f"Error al procesar registros para la fecha {fecha} y jig {jig}: {e}")
            continue  # Saltar esta iteración si hay un error de formato

        while True:
            output_file = guardar_log(directorio_salida, fecha, jig)  # Usar el jig dinámicamente
            
            if not os.path.exists(output_file):  
                # Si el archivo no existe, crearlo y escribir los registros
                with open(output_file, "w", newline='', encoding="utf-8") as outfile:
                    csv_writer = csv.writer(outfile)
                    csv_writer.writerow(["Fecha", "Hora", "Barcode", "Detalle","Hostname","Box","Jig","TestTime","Resultado","Medio","Planta","Modelo"])
                    csv_writer.writerows(registros_jig_ordenados)
                print(f"Registros guardados en {output_file}")
                break
            else:
                # Si el archivo ya existe, combinar los registros y reordenar
                with open(output_file, "r", newline='', encoding="utf-8") as infile:
                    csv_reader = csv.reader(infile)
                    registros_existentes = list(csv_reader)[1:]  # Leer registros existentes, omitir encabezado
                
                registros_combinados = registros_existentes + registros_jig_ordenados
                try:
                    registros_combinados_ordenados = sorted(
                        registros_combinados, 
                        key=lambda x: datetime.strptime(f"{x[0]} {x[1]}", "%Y%m%d %H%M%S")
                    )
                except ValueError as e:
                    print(f"Error al procesar registros combinados para jig {jig}: {e}")
                    break
                
                os.remove(output_file)  # Eliminar archivo existente
                with open(output_file, "w", newline='', encoding="utf-8") as outfile:
                    csv_writer = csv.writer(outfile)
                    csv_writer.writerow(["Fecha", "Hora", "Barcode", "Detalle","Hostname","Box","Jig","TestTime","Resultado","Medio","Planta","Modelo"])
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
    match = re.search(r'(\d{14})', archivo)
    return match.group(1) if match else ''

def obtener_estacion(hostaname):
    nombre = hostaname
    station = nombre[-1:]
    return station

def actualizar_registro_archivos(registro_archivos_path, archivos_procesados, archivo_nuevo):
    """Actualiza el archivo de registro con los nuevos archivos procesados."""
    archivos_procesados.add(archivo_nuevo)
    if len(archivos_procesados) > 500:
        archivos_procesados = set(list(archivos_procesados)[-500:])    
    archivos_procesados = sorted(archivos_procesados, key=extraer_fecha)
    with open(registro_archivos_path, "w") as file:
        for archivo in archivos_procesados:
            file.write(f"{archivo}\n")


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
station = obtener_estacion(hostname)
registro_archivos_path = r"C:\DGS\log\archivos_procesados.txt"
archivos_procesados = cargar_archivos_procesados(registro_archivos_path)
registros = []

planta = settings.get("planta", "")
nombre_estacion = settings.get("nombre_estacion", "") 
#Temporal hasta que se cambie el hostname del equipo
num_estacion = settings.get("num_estacion", "")

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
            date_str, formatted_time, barcode_part,jig = extraer_fecha_y_hora(folder_name, file)
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
                    registros.append([date_str, formatted_time, barcode_part, step, hostname,num_estacion, jig ,testime,result,medio,planta,model])
            except Exception as e:
                print(f"Error al procesar el archivo {file_path}: {e}")
            actualizar_registro_archivos(registro_archivos_path, archivos_procesados, file_path)
print(f"Total de registros procesados: {len(registros)}")
dividir_y_guardar_por_fecha(registros, directorio_salida, fecha_actual, procesar_todos=True)
guardar_resultados_completos(directorio_salida)
