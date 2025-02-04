#Diciembre 2024. Abregu Tomas para proyecto Motrex/Fiat. Mirgor
#version 1.0: primera implementacion filtrado de logs y creacion de estructura de datos
import os
import csv
import sys
import re
from collections import defaultdict
from datetime import datetime, timedelta
from collections import Counter
from collections import deque
import platform
import psutil
import platform
import shutil
#--------------------------------------------------------------------------------------------
                                #Funciones del programa

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
        date_str = f"{year}/{month}/{day}"
    else:
        date_str = "Unknown"
    # Extraer partes del nombre del archivo
    name_without_extension = os.path.basename(file_name).split('.', 1)[0]
    parts = name_without_extension.split('_')
    if len(parts) == 3:
        date_part, barcode_part, _ = parts
        time_part = date_part[len(date_part) // 2:]
        formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
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
        key=lambda x: (x[0], x[1]) 
    )
    with open(ruta_salida, mode='w', newline='', encoding='utf-8') as archivo_final:
        escritor = csv.writer(archivo_final)
        escritor.writerow(["Date", "Time", "Barcode", "Step","Hostname","Station","Jig","TestTime","Result"])
        for registro in registros_ordenados:
            escritor.writerow(registro)
    print(f"Archivos combinados, ordenados y guardados en {ruta_salida}")

def dividir_y_guardar_por_fecha(registros, directorio_salida, fecha_actual, procesar_todos=False):
    registros_por_fecha = defaultdict(list)
    for registro in registros:
        combined_string = registro[0]  # Asegurándonos de obtener el string combinado correctamente
        try:
            fecha_line = combined_string.split('\n')[12]  # Suponiendo que la fecha está en la séptima línea del registro
            fecha = fecha_line.split(': ')[1].replace('/', '')  # Convertir fecha a formato 'YYYYMMDD'
        except IndexError as e:
            print(f"Error al extraer la fecha del registro: {e}")
            continue 

        if procesar_todos or fecha == fecha_actual:
            registros_por_fecha[fecha].append(combined_string)

    # Guardar los registros por fecha
    for fecha, registros_fecha in registros_por_fecha.items():
        jig = 1
        while True:
            output_file = guardar_log(directorio_salida, fecha, jig)  # Asumiendo que `guardar_log` devuelve el nombre del archivo
            
            if not os.path.exists(output_file):
                # Si el archivo no existe, crearlo y escribir los registros
                with open(output_file, "w", newline='', encoding="utf-8") as outfile:
                    for registro in registros_fecha:
                        outfile.write(registro + "\n\n")
                print(f"Registros guardados en {output_file}")
                break
            else:
                # Si el archivo ya existe, leer los registros existentes, combinar con los nuevos y reordenar
                with open(output_file, "r", encoding="utf-8") as infile:
                    registros_existentes = infile.read().strip().split('\n\n')
                
                registros_combinados = registros_existentes + registros_fecha
                
                # Ordenar los registros combinados por fecha y hora (asumiendo que la hora está en la misma línea de la fecha)
                try:
                    registros_combinados_ordenados = sorted(
                        registros_combinados,
                        key=lambda x: datetime.strptime(
                            x.split('\n')[12].split(': ')[1] + ' ' + x.split('\n')[13].split(': ')[1], "%Y/%m/%d %H:%M:%S"
                        )
                    )
                except IndexError as e:
                    print(f"Error al ordenar los registros combinados: {e}")
                    continue  # Saltar este ordenamiento si hay un error
                
                with open(output_file, "w", encoding="utf-8") as outfile:
                    for registro in registros_combinados_ordenados:
                        outfile.write(registro + "\n\n")
                
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

def determinar_grupo_prueba(test_condition):
    for grupo, pruebas in grupos_pruebas.items():
        if any(test_condition.startswith(prueba) for prueba in pruebas):
            return grupo
    return None


def obtener_pc_cpu():
    """Obtiene la frecuencia y el número de núcleos de la CPU."""
    try:
        freq = psutil.cpu_freq().current / 1000  # Convertir a GHz
        cores = psutil.cpu_count(logical=False)  # Núcleos físicos
        return f"{freq:.2f} GHz/{cores}-Core"
    except Exception:
        return "N/A"

def obtener_pc_ram_available():
    """Obtiene la memoria RAM disponible en MB."""
    try:
        memoria_virtual = psutil.virtual_memory()
        return f"{memoria_virtual.available // (1024 ** 2)} MB"
    except Exception:
        return "N/A"

def obtener_pc_ram_init_free():
    """Obtiene la memoria RAM libre en KB."""
    try:
        memoria_virtual = psutil.virtual_memory()
        return f"{memoria_virtual.free // 1024} KB"
    except Exception:
        return "N/A"

def obtener_pc_disk_free_total():
    """Obtiene el espacio libre y total del disco C: en MB."""
    try:
        disco = psutil.disk_usage("C:")
        libre = disco.free // (1024 ** 2)
        total = disco.total // (1024 ** 2)
        return f"{libre}/{total} MB"
    except Exception:
        return "N/A"

def obtener_pc_os():
    """Obtiene el sistema operativo, versión y arquitectura."""
    try:
        sistema = platform.system()
        version = platform.version()
        build = platform.win32_ver()[1] if sistema == "Windows" else ""
        arquitectura = platform.architecture()[0]
        return f"{sistema} {version} (build {build}) {arquitectura}"
    except Exception:
        return "N/A"


#-----------------------inicio-----------------------------
cfg_file = obtener_ruta_cfg()
settings = read_setting(cfg_file)
model = int(settings.get("model", 0))  
input_dir = settings.get("input_dir", "")  
directorio_salida = settings.get("directorio_salida", "") 
mode = settings.get("mode", "")
code = settings.get("code","")
medio = settings.get("medio", "")
fecha_actual = datetime.now().strftime("%Y%m%d")
Crear_directorio_salida(directorio_salida)
registro_archivos_path = r"C:\DGS\log\archivos_procesados.txt"
archivos_procesados = cargar_archivos_procesados(registro_archivos_path)
registros = []
jig = 1
version = "1.0"
caracter_retorno = chr(13)



grupos_pruebas = {
    "BT": ["BT PAIRING", "BT ACCEPT", "BT MIC STD Level", "BT MEDIA SETTING", "BT MEDIA TEST", "BT DISCONNECT"],
    "GPS": ["Read GPS Version", "GPS",],
    "Android Auto": ["Android Auto", "Android Auto(wire less)"],
    "Car Play": ["Car Play", "Car Play(wire less)"],
    "FM/AM": ["FM SEEK STOP", "AM SEEK STOP"],
    "KEY": ["KEY VOL UP TEST", "KEY VOL DN TEST", "POWER ON TEST", "KEY TUNE UP TEST", "KEY TUNE DN TEST", "KEY TUNE OK TEST", "KEY MUTE TEST", "KEY DISPLAY TEST"],
}

pruebas_prioritarias = [
    "Rear Cam Inspection", "FACTORY RESET", "SEAT SEQ", "VISUAL Check"]
init_info_template= [
    "/*================================================================================",
    "Test Conditions, Measured Value, Lower Limit, Upper Limit, P/F, Sec, Code, Code Lsl, Code Usl, Meas Fine, Code Fine", 
    "================================================================================*/",
    "Modem Port Search,   1.00 ,   1.00 ,   1.00 , P , 0 ,,,",
    "CONTROLN, 84715LGB02346, 84715LGB02346, 84715LGB02346, P, 1",
    "",
    "#INIT",
    "MODEL_LAST : ",
    f"MODEL_PROGRAM : ",
    f"MODEL : {model}",
    "P/N : {barcode}",
    "S/W : ",
    "DATE : {date_str}",
    "TIME : {formatted_time}",
    f"TESTCODE : {code}",
    f"LOGVERSION : {version}",
    "INSTRUMENT : ",
    "INSTRUMENT_CALDATE : N/A",
    "INSTRUMENT_INTERFACE : ",
    "FIRMWARE : ",
    "FIRMWARE_GPRF Gen/Meas/Sig : ",
    "FIRMWARE_GSM Gen/Meas/Sig : ",
    "FIRMWARE_WCDMA Gen/Meas/Sig : ",
    "FIRMWARE_LTE Gen/Meas/Sig : ",
    "FIRMWARE_1xEV-DO Gen/Meas/Sig : ",
    "FIRMWARE_CDMA2000 Gen/Meas/Sig : ",
    "FIRMWARE_TDSCDMA Gen/Meas/Sig : ",
    "FIRMWARE_WiMAX Gen/Meas/Sig : ",
    "FIRMWARE_WLAN Gen/Meas/Sig : ",
    "FIRMWARE_NRSub6G Gen/Meas/Sig : ",
    "WAVEFORM : ",
    "UWB_INST : (null)/(null)/(null)",
    "UWB_INST(Firmware) : (null)",
    f"PC_CPU : {obtener_pc_cpu()}",
    f"PC_RAM(Available) : {obtener_pc_ram_available()}",
    f"PC_RAM_INIT(free) : {obtener_pc_ram_init_free()}",
    f"PC_DISK(C-Drive free/Total) : {obtener_pc_disk_free_total()}",
    f"PC_OS : {obtener_pc_os()}",
    "USB_DRIVER_VERSION : ",
    "PC_DISK_Type : ",
    f"JIG : {jig}",
    "PROGRAM : ",
    "ENTERPRISE : ",
    "INIFILE : ",
    "STANDARD_LOSS_FILE : ",
    "IMEINO : ",
    "SKU : ",
    "HW : ",
    "CN : ",
    "BT_ADDR : ",
    "USE_GFDS : FALSE",
    "RDM_SSG : ",
    "RDM_LOT : ",
    "FailLogRestful : ",
    "LINENAME : ",
    "TOTALDUT : ",
    "CURRENTDUT : ",
    "ROBOTVER : ",
    "ROBOTIP : ",
    "PRODCODE : "
]

end_info_template = [
    "",
    "#END",
    "RESULT : {result}",
    "ERROR-CODE : ",
    "FAILITEM : {fail_item}",
    "PROCESS SKIP : ",
    "RETEST_CHANGE_CH : 0",
    "TEST-TIME : {test_time}",
    "//Total : 1 Pass : {pass_count} Fail : {fail_count}",
    "//FAIL_RATE : {fail_rate}%",
    "//PC_RAM_END(free) :",
    f"{caracter_retorno}"
]

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
                    next(csv_reader, None)  # Saltar encabezado
                    filas = list(csv_reader)
                    
                    # Procesar cada fila del CSV
                    test_info_content = []
                    grupos_utilizados = set()  # Para evitar duplicar encabezados de grupo
                    pruebas_prioritarias_content = []  
                    for fila in filas:
                        if len(fila) < 5:  # Validar filas incompletas
                            continue
                            
                        test_condition = fila[0]
                        measured_value = fila[1]
                        lower_limit = fila[2] if fila[2] else "N/A" 
                        upper_limit = fila[3] if fila[3] else "N/A"  
                        p_f = fila[3] if fila[3] in ['P', 'F'] else default_result  # Resultado (P/F)
                        sec = fila[4]  # Tiempo en segundos
                        
                        # Crear línea formateada
                        test_line = (
                            f"{test_condition}: {measured_value}, {lower_limit}, "
                            f"{upper_limit}, {p_f}, {sec}, , , , ,"
                        )
                        if test_condition in pruebas_prioritarias:
                            pruebas_prioritarias_content.append(test_line)
                        else:
                            grupo = determinar_grupo_prueba(test_condition)
                            if grupo and grupo not in grupos_utilizados:
                                test_info_content.append("")
                                test_info_content.append(f"// << {grupo} Test >>")
                                grupos_utilizados.add(grupo)
                            test_info_content.append(test_line)
                    if pruebas_prioritarias_content:
                        test_info_content = pruebas_prioritarias_content + [""] + test_info_content
                    resultados_fail = [fila[0] for fila in filas if any("FAIL" in col.upper() for col in fila)]
                    result = "FAIL" if resultados_fail else default_result
                    step = " ".join(resultados_fail) if resultados_fail else "PASS"
                    init_info = [line.format(barcode=barcode_part, 
                                          date_str=date_str, 
                                          formatted_time=formatted_time) 
                               for line in init_info_template]
                    test_info = ["", "#TEST"] + test_info_content
                    end_info = [line.format(result=result,
                                         fail_item=step,
                                         test_time=testime,
                                         pass_count=1 if result == "PASS" else 0,
                                         fail_count=1 if result == "FAIL" else 0,
                                         fail_rate=100 if result == "FAIL" else 0) 
                              for line in end_info_template]
                    combined_info = init_info + test_info + end_info
                    combined_record = "\n".join(combined_info)
                    registros.append([combined_record])
            except Exception as e:
                print(f"Error al procesar el archivo {file_path}: {e}")
            actualizar_registro_archivos(registro_archivos_path, archivos_procesados, file_path)
print(f"Total de registros procesados: {len(registros)}")
dividir_y_guardar_por_fecha(registros, directorio_salida, fecha_actual, procesar_todos=True)
