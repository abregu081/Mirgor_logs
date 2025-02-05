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
    cfg_file = os.path.join(current_directory, "Setting_Update_Sbox.cfg")
    return cfg_file

def Crear_directorio_salida(directorio_salida):
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
        print(f"Directorio de salida creado en: {directorio_salida}")
    else:
        print(f"Directorio de salida encontrado en: {directorio_salida}")

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
        escritor.writerow(["Fecha", "Hora", "Barcode", "Detalle","Hostname","Box","Jig","TestTime","Resultado","Medio","Planta","Modelo"])
        for registro in registros_ordenados:
            escritor.writerow(registro)
    print(f"Archivos combinados, ordenados y guardados en {ruta_salida}")

def dividir_y_guardar_por_fecha(registros, directorio_salida, procesar_todos=False):
    registros_por_fecha = defaultdict(list)
    resgistros_por_jig = defaultdict(list)
    for registro in registros:
        hora = registro[1]
        fecha = registro[0]
        jig = registro[6]
        if procesar_todos or fecha == fecha_actual:
            registros_por_fecha[fecha].append(registro)
            resgistros_por_jig[(fecha,jig)].append(registro)
    for (fecha,jig),resgistros_por_jig in resgistros_por_jig.items():
        try:
            registros_jig_ordenados = sorted(
                resgistros_por_jig, 
                key=lambda x: datetime.strptime(f"{x[0]} {x[1]}", "%Y%m%d %H:%M:%S")  # Corregido
            )
        except ValueError as e:
            print(f"Error al procesar registros para la fecha {fecha} y jig {jig}: {e}")
            continue

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

planta = settings.get("planta", "")
nombre_estacion = settings.get("nombre_estacion", "") 
#Temporal hasta que se cambie el hostname del equipo
num_estacion = settings.get("num_estacion", "")



for carpeta_fecha in os.listdir(input_dir):
    ruta_carpeta_fecha = os.path.join(input_dir, carpeta_fecha)
    try:
        if os.path.isdir(ruta_carpeta_fecha) and carpeta_fecha.isdigit() and len(carpeta_fecha) == 6:
            fecha = "20" + carpeta_fecha
        else:
            print(f"Carpeta de fecha no válida {carpeta_fecha}")
            continue
        
        for carpeta_test in os.listdir(ruta_carpeta_fecha):  # Iterar sobre las subcarpetas dentro de la carpeta de fecha
            ruta_carpeta_test = os.path.join(ruta_carpeta_fecha, carpeta_test)
            if os.path.exists(ruta_carpeta_test):
                for estado in ["FAIL", "NG DEBUG", "PASS"]:  # Revisar las carpetas de estado
                    carpeta_estado = os.path.join(ruta_carpeta_test, estado)
                    if os.path.exists(carpeta_estado):
                        for subdirectorio in os.listdir(carpeta_estado):
                            ruta_subdirectorio = os.path.join(carpeta_estado, subdirectorio)
                            if os.path.exists(ruta_subdirectorio):
                                for archivo in os.listdir(ruta_subdirectorio):
                                    if archivo.endswith(".csv"):
                                        jig = int(carpeta_test.split("_")[0])  # Extraer el valor de jig del nombre de la carpeta
                                        ruta_archivo = os.path.join(ruta_subdirectorio, archivo)
                                        if ruta_archivo in archivos_procesados:
                                            continue
                                        try:
                                            registros_nuevos = []
                                            total_time = "N/A"
                                            with open(ruta_archivo, mode="r", encoding="ISO-8859-1") as f:
                                                csv_reader = csv.reader(f)
                                                next(csv_reader, None)  # Saltar encabezado
                                                fila = next(csv_reader, None)  # Leer la primera fila
                                                if not fila or len(fila) < 2:  # Validar la fila
                                                    print(f"Archivo {ruta_archivo} tiene un encabezado inválido o faltan columnas.")
                                                    continue
                                                start_time, barcode = fila[0], fila[1]
                                                start_time = start_time.split("_")[1]  # Obtener el tiempo de inicio
                                                if "PASS" in carpeta_estado:
                                                    step = "PASS"
                                                    result = "PASS"
                                                elif "FAIL" in carpeta_estado:
                                                    encabezados = ["WORK DATE", "BARCODE", "SW ¹öÀü Data", "SW ¹öÀü Spec", "FW GPS ¹öÀü Data", "FW GPS ¹öÀü Spec", "MICOM ¹öÀü Data", "MICOM ¹öÀü Spec", "RESULT"]
                                                    for idx, columna in enumerate(fila[2:8], start=2):
                                                        if "NG" in columna:
                                                            step = encabezados[idx]
                                                            result = "FAIL"
                                                            break
                                                else:
                                                    step = "UNKNOWN"
                                                    result = "UNKNOWN"
                                                
                                                # Actualización de archivo procesado
                                                actualizar_registro_archivos(registro_archivos_path, archivos_procesados, ruta_archivo)
                                                
                                                # Guardar el registro
                                                registros.append(
                                                    [fecha, start_time, barcode, step, hostname, num_estacion, jig, total_time, result,medio, planta, model]
                                                )
                                        except Exception as e:
                                            print(f"Error al procesar el archivo {ruta_archivo}: {e}")
    except Exception as e:
        ...
print(f"Total de registros procesados: {len(registros)}")
dividir_y_guardar_por_fecha(registros, directorio_salida, procesar_todos=True)
guardar_resultados_completos(directorio_salida)