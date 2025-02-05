import os
import csv
from collections import defaultdict
from datetime import datetime, timedelta
from collections import Counter
import sys


def read_setting(file):
    setting = {}
    with open(file, 'r') as f:
        for line in f:
            # Ignorar las líneas que son comentarios (empiezan con "#")
            if line.startswith("#"):
                continue
            # Ignorar líneas vacías
            if not line.strip():
                continue
            # Separamos la línea en clave y valor por el signo "="
            if "=" in line:
                key, value = line.strip().split('=')
                # Limpiar espacios extra en las claves y valores
                value = value.strip()

                # Si el valor es una lista de rutas (se detecta por las comas)
                if "," in value:
                    # Convertir el valor en una lista de rutas
                    setting[key.strip()] = [v.strip() for v in value.split(",")]
                else:
                    setting[key.strip()] = value
                
    return setting

def obtener_ruta_cfg():
    # Obtener el directorio actual
    current_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    # Formar la ruta completa del archivo .cfg
    cfg_file = os.path.join(current_directory, "settings.cfg")
    
    return cfg_file


def reporte_diario(directorio_salida):
    fecha_actual = datetime.now().strftime("%Y%m%d")
    fails = 0
    passes = 0
    steps_fails = []   
    fail_UN_UNICO = 0  # Variable para contar los "fails" sin barcode duplicado
    barcodes_procesados = set()  # Conjunto para almacenar los barcodes procesados
    pass_UN_UNICOS = 0
    
    # Buscar los archivos CSV que corresponden al día actual
    for archivo in os.listdir(directorio_salida):
        if archivo.endswith(f"{fecha_actual}_1.csv"): 
            with open(os.path.join(directorio_salida, archivo), mode="r", encoding="ISO-8859-1") as f:
                csv_reader = csv.reader(f)
                next(csv_reader, None) 
                
                # Procesar cada fila para contar "FAIL" y "PASS"
                for fila in csv_reader:
                    result = fila[5]
                    step = fila[3]
                    barcode = fila[2]
                    
                    if "FAIL" in result.upper():
                        fails += 1
                        steps_fails.append(step)
                        if barcode not in barcodes_procesados:
                            barcodes_procesados.add(barcode)
                            fail_UN_UNICO+= 1         
                    elif "PASS" in result.upper():
                        passes += 1
                        if barcode not in barcodes_procesados:
                            barcodes_procesados.add(barcode)
                            pass_UN_UNICOS += 1
                        
    # Contar las 5 fallas más frecuentes
    conteo_fallas = Counter(steps_fails)
    cinco_mas_altas = conteo_fallas.most_common(5)

    # Calcular Yail rate con control de división por cero
    total = passes + fails
    if total > 0:
        yail_rate = (passes / total) * 100
    else:
        yail_rate = 0  # Si no hay fallas ni pasadas, Yail rate es 0
    
    # Calcular Yail rate (sin repetidos) con control de división por cero
    total_sin_repetidos = passes + fails - fail_UN_UNICO
    if total_sin_repetidos > 0:
        yail_rate_sin_repetidos = (passes / total_sin_repetidos) * 100
    else:
        yail_rate_sin_repetidos = 0  # Si no hay fallas ni pasadas sin repetidos, Yail rate es 0
    
    reporte_nombre = f"reporte_diario_{fecha_actual}.txt"
    output_file = os.path.join(directorio_salida, reporte_nombre)
    
    # Encabezado
    print(f"===== Reporte Diario del {fecha_actual} =====\n")
    print(f"Fecha y Hora: {fecha_actual}\n")
    
    # Sección de estadísticas generales
    print("------------ Estadísticas Generales ------------")
    print(f"Cantidad de fallas (FAIL): {fails}")
    print(f"Cantidad de pasadas (PASS): {passes}")
    print(f"Fallas Únicas (FAIL UNICOS): {fail_UN_UNICO}")
    print(f"Pasadas Únicas (PASS UNICOS): {pass_UN_UNICOS}\n")
    
    # Sección de Yield Rate
    print("--------- Cálculo de Yield Rate ---------")
    print(f"Yield rate: {round(yail_rate, 2)}%")
    print(f"Yield rate (sin repetidos): {round(yail_rate_sin_repetidos, 2)}%\n")
    
    # Mostrar las 5 fallas más frecuentes
    print("--------- Top 5 Pasos Más Repetidos en Fallas ---------")
    if cinco_mas_altas:
        for i, (nombre, cantidad) in enumerate(cinco_mas_altas, 1):
            print(f"{i}. {nombre}: {cantidad} repeticiones")
    else:
        print("No se encontraron pasos repetidos.\n")

        print("--------------------------------------\n")
    
    with open(output_file, mode='w', encoding="utf-8") as f:
        f.write(f"Reporte Diario del {fecha_actual} ---- Dia y Hora:{fecha_actual}\n")
        f.write(f"\nCantidad de fallas (FAIL): {fails}\n")
        f.write(f"Cantidad de pasadas (PASS): {passes}\n")
        f.write(f"FAIL UNICOS: {fail_UN_UNICO}\n")  # Agregar contador de fallas únicas
        f.write(f"PASS UNICOS: {pass_UN_UNICOS}\n")
        f.write(f"\n")
        f.write(f"---------Calculo de Yaild rate--------\n")
        f.write(f"Yield rate: {round(yail_rate,2)}%\n")
        f.write(f"First Yail rate: {round(yail_rate_sin_repetidos,2)}%\n")
        f.write(f"--------------------------------------\n")
        # Mostrar las 5 fallas más frecuentes
        f.write("\nTop 5 pasos más repetidos en las fallas:\n")
        for nombre, cantidad in cinco_mas_altas:
            f.write(f"{nombre}: {cantidad}\n")
    
    print(f"Reporte Diario guardado en: {output_file}")
    return output_file

def reporte_semanal(directorio_salida):
    fecha_actual = datetime.now()
    fecha_semanal_anterior = fecha_actual - timedelta(weeks=1)
    semana_anterior_inicio = fecha_semanal_anterior.strftime("%Y%m%d")  
    hora_actual = fecha_actual.strftime("%H:%M:%S")
    
    fails = 0
    passes = 0
    steps_fails = [] 
    fail_UN_UNICO = 0  # Variable para contar los "fails" sin barcode duplicado
    barcodes_procesados = set()  # Conjunto para almacenar los barcodes procesados
    pass_UN_UNICOS = 0 
    
    # Buscar los archivos CSV que corresponden a la semana anterior
    for archivo in os.listdir(directorio_salida):
        if archivo.endswith(".csv"):
            partes = archivo.split('_')
            if len(partes) > 1:
                fecha_archivo = partes[1][:8]  
                # Si el archivo corresponde a la semana pasada, procesarlo
                if fecha_archivo >= semana_anterior_inicio:
                    with open(os.path.join(directorio_salida, archivo), mode="r", encoding="ISO-8859-1") as f:
                        csv_reader = csv.reader(f)
                        next(csv_reader, None)  
                        # Procesar cada fila para contar "FAIL" y "PASS"
                        for fila in csv_reader:
                            result = fila[5]
                            step = fila[3]
                            barcode = fila[2]
                    
                            if "FAIL" in result.upper():
                                fails += 1
                                steps_fails.append(step)
                                if barcode not in barcodes_procesados:
                                    barcodes_procesados.add(barcode)
                                    fail_UN_UNICO+= 1         
                            elif "PASS" in result.upper():
                                passes += 1
                                if barcode not in barcodes_procesados:
                                    barcodes_procesados.add(barcode)
                                    pass_UN_UNICOS += 1
                    
                    
    
    # Contar las 5 fallas más frecuentes
    conteo_fallas = Counter(steps_fails)
    cinco_mas_altas = conteo_fallas.most_common(5)

    # Calcular Yail rate con control de división por cero
    total = passes + fails
    if total > 0:
        yail_rate = (passes / total) * 100
    else:
        yail_rate = 0  # Si no hay fallas ni pasadas, Yail rate es 0
    
    # Calcular Yail rate (sin repetidos) con control de división por cero
    total_sin_repetidos = passes + fails - fail_UN_UNICO
    if total_sin_repetidos > 0:
        yail_rate_sin_repetidos = (passes / total_sin_repetidos) * 100
    else:
        yail_rate_sin_repetidos = 0  # Si no hay fallas ni pasadas sin repetidos, Yail rate es 0
    
    reporte_nombre = f"reporte_semanal_{fecha_actual.strftime('%Y%m%d')}.txt"
    output_file = os.path.join(directorio_salida, reporte_nombre)

    print(f"===== Reporte Semanal hasta {fecha_actual.strftime('%Y%m%d')}=====\n")
    print(f"Fecha y Hora: {fecha_actual}\n")
    
    # Sección de estadísticas generales
    print("------------ Estadísticas Generales ------------")
    print(f"Cantidad de fallas (FAIL): {fails}")
    print(f"Cantidad de pasadas (PASS): {passes}")
    print(f"Fallas Únicas (FAIL UNICOS): {fail_UN_UNICO}")
    print(f"Pasadas Únicas (PASS UNICOS): {pass_UN_UNICOS}\n")
    
    # Sección de Yield Rate
    print("--------- Cálculo de Yield Rate ---------")
    print(f"Yield rate: {round(yail_rate, 2)}%")
    print(f"First Yiel rate: {round(yail_rate_sin_repetidos, 2)}%\n")
    
    # Mostrar las 5 fallas más frecuentes
    print("--------- Top 5 Pasos Más Repetidos en Fallas ---------")
    if cinco_mas_altas:
        for i, (nombre, cantidad) in enumerate(cinco_mas_altas, 1):
            print(f"{i}. {nombre}: {cantidad} repeticiones")
    else:
        print("No se encontraron pasos repetidos.\n")

        print("--------------------------------------\n")
        
    
    with open(output_file, mode='w', encoding="utf-8") as f:
        f.write(f"Reporte Semanal hasta {fecha_actual.strftime('%Y%m%d')}\n")
        f.write(f"\nCantidad de fallas (FAIL): {fails}\n")
        f.write(f"Cantidad de pasadas (PASS): {passes}\n")
        f.write(f"FAIL UNICOS: {fail_UN_UNICO}\n")  # Agregar contador de fallas únicas
        f.write(f"PASS UNICOS: {pass_UN_UNICOS}\n")
        f.write(f"\n")
        f.write(f"---------Calculo de Yaild rate--------\n")
        f.write(f"Yield rate: {round(yail_rate,2)}%\n")
        f.write(f"First Yield rate: {round(yail_rate_sin_repetidos,2)}%\n")
        f.write(f"--------------------------------------\n")
        # Mostrar las 5 fallas más frecuentes
        f.write("\nTop 5 fails:\n")
        for nombre, cantidad in cinco_mas_altas:
            f.write(f"{nombre}: {cantidad}\n")
    
    print(f"Reporte Semanal guardado en: {output_file}")
    return output_file

def reporte_mensual(directorio_salida):
    fecha_actual = datetime.now()
    mes_actual = fecha_actual.strftime("%Y%m")  
    hora_actual = datetime.now().strftime("%H:%M:%S")
    
    fails = 0
    passes = 0
    steps_fails = []  
    fail_UN_UNICO = 0  # Variable para contar los "fails" sin barcode duplicado
    barcodes_procesados = set()  # Conjunto para almacenar los barcodes procesados
    pass_UN_UNICOS = 0
    # Buscar los archivos CSV que corresponden al mes actual
    for archivo in os.listdir(directorio_salida):
        if archivo.endswith(".csv"):
            partes = archivo.split('_')
            if len(partes) > 1:
                
                fecha_archivo = partes[1][:6]  
                if fecha_archivo == mes_actual:
                    with open(os.path.join(directorio_salida, archivo), mode="r", encoding="ISO-8859-1") as f:
                        csv_reader = csv.reader(f)
                        next(csv_reader, None)  # Omitir el encabezado
                        # Procesar cada fila para contar "FAIL" y "PASS"
                        for fila in csv_reader:
                            result = fila[5]
                            step = fila[3]
                            barcode = fila[2]  # Suponiendo que el barcode estÃ¡ en la columna 2 (ajustar segÃºn sea necesario)
                            
                            if "FAIL" in result.upper():
                                fails += 1
                                steps_fails.append(step)
                                
                                # Si el barcode no ha sido procesado antes, lo contamos como fail sin duplicar
                                if barcode not in barcodes_procesados:
                                    barcodes_procesados.add(barcode)
                                    fail_UN_UNICO+= 1
                            elif "PASS" in result.upper():
                                passes += 1
                                if barcode not in barcodes_procesados:
                                    barcodes_procesados.add(barcode)
                                    pass_UN_UNICOS += 1
    
    # Contar las 5 fallas más frecuentes
    conteo_fallas = Counter(steps_fails)
    cinco_mas_altas = conteo_fallas.most_common(5)

    # Calcular Yail rate con control de división por cero
    total = passes + fails
    if total > 0:
        yail_rate = (passes / total) * 100
    else:
        yail_rate = 0  # Si no hay fallas ni pasadas, Yail rate es 0
    
    # Calcular Yail rate (sin repetidos) con control de división por cero
    total_sin_repetidos = passes + fails - fail_UN_UNICO
    if total_sin_repetidos > 0:
        yail_rate_sin_repetidos = (passes / total_sin_repetidos) * 100
    else:
        yail_rate_sin_repetidos = 0  # Si no hay fallas ni pasadas sin repetidos, Yail rate es 0
    
    reporte_nombre = f"reporte_mensual_{mes_actual}.txt"
    output_file = os.path.join(directorio_salida, reporte_nombre)


    print(f"===== Reporte Mensual del {mes_actual} ---- Dia y Hora:{fecha_actual} =====\n")
    print(f"Fecha y Hora: {fecha_actual}\n")
    
    # Sección de estadísticas generales
    print("------------ Estadísticas Generales ------------")
    print(f"Cantidad de fallas (FAIL): {fails}")
    print(f"Cantidad de pasadas (PASS): {passes}")
    print(f"Fallas Únicas (FAIL UNICOS): {fail_UN_UNICO}")
    print(f"Pasadas Únicas (PASS UNICOS): {pass_UN_UNICOS}\n")
    
    # Sección de Yield Rate
    print("--------- Cálculo de Yield Rate ---------")
    print(f"Yield rate: {round(yail_rate, 2)}%")
    print(f"First Yiel rate: {round(yail_rate_sin_repetidos, 2)}%\n")
    
    # Mostrar las 5 fallas más frecuentes
    print("--------- Top 5 Pasos Más Repetidos en Fallas ---------")
    if cinco_mas_altas:
        for i, (nombre, cantidad) in enumerate(cinco_mas_altas, 1):
            print(f"{i}. {nombre}: {cantidad} repeticiones")
    else:
        print("No se encontraron pasos repetidos.\n")

        print("--------------------------------------\n")
 
    
    
    with open(output_file, mode='w', encoding="utf-8") as f:
        f.write(f"Reporte Mensual del {mes_actual} ---- Dia y Hora:{fecha_actual}\n")
        f.write(f"\nCantidad de fallas (FAIL): {fails}\n")
        f.write(f"Cantidad de pasadas (PASS): {passes}\n")
        f.write(f"FAIL UNICOS: {fail_UN_UNICO}\n")  # Agregar contador de fallas únicas
        f.write(f"PASS UNICOS: {pass_UN_UNICOS}\n")
        f.write(f"\n")
        f.write(f"---------Calculo de Yaild rate--------\n")
        f.write(f"Yield rate: {round(yail_rate,2)}%\n")
        f.write(f"First Yield rate: {round(yail_rate_sin_repetidos,2)}%\n")
        f.write(f"--------------------------------------\n")
        # Mostrar las 5 fallas más frecuentes
        f.write("\nTop 5 fails:\n")
        for nombre, cantidad in cinco_mas_altas:
            f.write(f"{nombre}: {cantidad}\n")
    
    print(f"Reporte mensual guardado en: {output_file}")
    return output_file

def reporte_por_rango_fechas(directorios_salida, fecha_inicial_str, fecha_final_str):
    """
    Genera un reporte para un rango de fechas especificado.
    
    :param directorios_salida: Lista de directorios donde se encuentran los archivos CSV.
    :param fecha_inicial_str: Fecha inicial en formato "YYYYMMDD".
    :param fecha_final_str: Fecha final en formato "YYYYMMDD".
    :return: Ruta del archivo generado con el reporte.
    """
    
    # Convertir las fechas de las cadenas a objetos datetime
    try:
        fecha_inicial = datetime.strptime(fecha_inicial_str, "%Y%m%d")
        fecha_final = datetime.strptime(fecha_final_str, "%Y%m%d")
    except ValueError:
        print("Error en el formato de fechas. Debe ser YYYYMMDD.")
        return

    fails = 0
    passes = 0
    steps_fails = []  
    fail_UN_UNICO = 0  # Variable para contar los "fails" sin barcode duplicado
    barcodes_procesados = set()  # Conjunto para almacenar los barcodes procesados
    pass_UN_UNICOS = 0
    
    # Verificar si los directorios existen
    for directorio in directorios_salida:
        if not os.path.exists(directorio):
            print(f"El directorio {directorio} no existe.")
            continue  # Si el directorio no existe, saltar al siguiente
        
        # Buscar los archivos CSV en el directorio
        for archivo in os.listdir(directorio):
            if archivo.endswith(".csv"):
                partes = archivo.split('_')
                if len(partes) > 1:
                    fecha_archivo = partes[1][:8]  # Obtener la fecha del archivo
                    
                    # Convertir la fecha del archivo en objeto datetime
                    try:
                        fecha_archivo_dt = datetime.strptime(fecha_archivo, "%Y%m%d")
                    except ValueError:
                        continue  # Si no se puede convertir, ignorar ese archivo
                    
                    # Verificar si la fecha del archivo está dentro del rango
                    if fecha_inicial <= fecha_archivo_dt <= fecha_final:
                        with open(os.path.join(directorio, archivo), mode="r", encoding="ISO-8859-1") as f:
                            csv_reader = csv.reader(f)
                            next(csv_reader, None)  # Omitir el encabezado
                            
                            # Procesar cada fila para contar "FAIL" y "PASS"
                            for fila in csv_reader:
                                result = fila[5]
                                step = fila[3]
                                barcode = fila[2]
                                
                                if "FAIL" in result.upper():
                                    fails += 1
                                    steps_fails.append(step)
                                    if barcode not in barcodes_procesados:
                                        barcodes_procesados.add(barcode)
                                        fail_UN_UNICO += 1
                                elif "PASS" in result.upper():
                                    passes += 1
                                    if barcode not in barcodes_procesados:
                                        barcodes_procesados.add(barcode)
                                        pass_UN_UNICOS += 1

    # Contar las 5 fallas más frecuentes
    conteo_fallas = Counter(steps_fails)
    cinco_mas_altas = conteo_fallas.most_common(5)

    # Calcular Yail rate con control de división por cero
    total = passes + fails
    if total > 0:
        yail_rate = (passes / total) * 100
    else:
        yail_rate = 0  # Si no hay fallas ni pasadas, Yail rate es 0
    
    # Calcular Yail rate (sin repetidos) con control de división por cero
    total_sin_repetidos = passes + fails - fail_UN_UNICO
    if total_sin_repetidos > 0:
        yail_rate_sin_repetidos = (passes / total_sin_repetidos) * 100
    else:
        yail_rate_sin_repetidos = 0  # Si no hay fallas ni pasadas sin repetidos, Yail rate es 0
    
    # Generar nombre y guardar reporte
    reporte_nombre = f"reporte_{fecha_inicial_str}_{fecha_final_str}.txt"
    output_file = os.path.join(directorios_salida[0], reporte_nombre)  # Usamos el primer directorio para generar la ruta
    
    # Imprimir el reporte en consola
    print(f"Reporte de {fecha_inicial_str} a {fecha_final_str}\n")
    print(f"\nCantidad de fallas (FAIL): {fails}\n")
    print(f"Cantidad de pasadas (PASS): {passes}\n")
    print(f"FAIL UNICOS: {fail_UN_UNICO}\n")  # Agregar contador de fallas únicas
    print(f"PASS UNICOS: {pass_UN_UNICOS}\n")
    print(f"\n")
    print(f"---------Calculo de Yaild rate--------\n")
    print(f"Yield rate: {round(yail_rate,2)}%\n")
    print(f"First Yield rate: {round(yail_rate_sin_repetidos,2)}%\n")
    print(f"--------------------------------------\n")
    # Mostrar las 5 fallas más frecuentes
    print("\nTop 5 pasos más repetidos en las fallas:\n")
    for nombre, cantidad in cinco_mas_altas:
        print(f"{nombre}: {cantidad}\n")
    
    # Guardar el reporte en el archivo
    with open(output_file, mode='w', encoding="utf-8") as f:
        f.write(f"Reporte de {fecha_inicial_str} a {fecha_final_str}\n")
        f.write(f"\nCantidad de fallas (FAIL): {fails}\n")
        f.write(f"Cantidad de pasadas (PASS): {passes}\n")
        f.write(f"FAIL UNICOS: {fail_UN_UNICO}\n")  # Agregar contador de fallas únicas
        f.write(f"PASS UNICOS: {pass_UN_UNICOS}\n")
        f.write(f"\n")
        f.write(f"---------Calculo de Yaild rate--------\n")
        f.write(f"Yield rate: {round(yail_rate,2)}%\n")
        f.write(f"First Yiel rate: {round(yail_rate_sin_repetidos,2)}%\n")
        f.write(f"--------------------------------------\n")
        # Mostrar las 5 fallas más frecuentes
        f.write("\nTop 5 fails:\n")
        for nombre, cantidad in cinco_mas_altas:
            f.write(f"{nombre}: {cantidad}\n")
    
    print(f"Reporte generado en: {output_file}")
    return output_file

def Metrica_General(directorio_salida):
    fails = 0
    passes = 0
    steps_fails = []  
    fail_UN_UNICO = 0  
    barcodes_procesados = set()  
    pass_UN_UNICOS = 0
    registros = []  
    
    # Obtener el archivo generado por guardar_resultados_completos
    archivo_salida = 'results.csv'
    ruta_salida = os.path.join(directorio_salida, archivo_salida)
    
    # Leer el archivo CSV
    if os.path.exists(ruta_salida):
        with open(ruta_salida, mode="r", encoding="ISO-8859-1") as f:
            csv_reader = list(csv.reader(f))
            csv_reader.pop(0)  # Eliminar encabezado
            registros.extend(csv_reader)
    
    
    for fila in registros:
        result = fila[5]
        step = fila[3]
        barcode = fila[2]  
        
        if "FAIL" in result.upper():
            fails += 1
            steps_fails.append(step)
            
            if barcode not in barcodes_procesados:
                barcodes_procesados.add(barcode)
                fail_UN_UNICO += 1
        elif "PASS" in result.upper():
            passes += 1
            if barcode not in barcodes_procesados:
                barcodes_procesados.add(barcode)
                pass_UN_UNICOS += 1
    
    # Contar las 5 fallas más frecuentes
    conteo_fallas = Counter(steps_fails)
    cinco_mas_altas = conteo_fallas.most_common(5)
    
    # Calcular Yield Rate
    total = passes + fails
    yail_rate = (passes / total) * 100 if total > 0 else 0
    
    # Calcular Yield Rate sin repetidos
    total_sin_repetidos = passes + fails - fail_UN_UNICO
    yail_rate_sin_repetidos = (passes / total_sin_repetidos) * 100 if total_sin_repetidos > 0 else 0
    
    # Generar reporte
    print(f"===== Metrica general=====\n")
   
    # Sección de estadísticas generales
    print("------------ Estadísticas Generales ------------")
    print(f"Cantidad de fallas (FAIL): {fails}")
    print(f"Cantidad de pasadas (PASS): {passes}")
    print(f"Fallas Únicas (FAIL UNICOS): {fail_UN_UNICO}")
    print(f"Pasadas Únicas (PASS UNICOS): {pass_UN_UNICOS}\n")
    
    # Sección de Yield Rate
    print("--------- Cálculo de Yield Rate ---------")
    print(f"Yield rate: {round(yail_rate, 2)}%")
    print(f"First Yiel rate: {round(yail_rate_sin_repetidos, 2)}%\n")
    # Mostrar las 5 fallas más frecuentes
    print("--------- Top 5 Pasos Más Repetidos en Fallas ---------")
    if cinco_mas_altas:
        for i, (nombre, cantidad) in enumerate(cinco_mas_altas, 1):
            print(f"{i}. {nombre}: {cantidad} repeticiones")
    else:
        print("No se encontraron pasos repetidos.\n")

    print("--------------------------------------\n")

def reporte_general(directorios_salida):
    fails = 0
    passes = 0
    steps_fails = []
    fail_UN_UNICO = 0
    barcodes_procesados = set()
    pass_UN_UNICOS = 0
    
    archivos_procesados = set()  # Para evitar procesar el mismo archivo más de una vez
    
    for directorio in directorios_salida:
        for archivo in os.listdir(directorio):
            if archivo.endswith("results.csv"):
                archivo_path = os.path.join(directorio, archivo)
                if archivo_path not in archivos_procesados:
                    archivos_procesados.add(archivo_path)
                    with open(archivo_path, mode="r", encoding="ISO-8859-1") as f:
                        csv_reader = csv.reader(f)
                        next(csv_reader, None)
                        
                        for fila in csv_reader:
                            result = fila[4]
                            step = fila[3]
                            barcode = fila[2]
                            
                            if "FAIL" in result.upper():
                                fails += 1
                                steps_fails.append(step)
                                if barcode not in barcodes_procesados:
                                    barcodes_procesados.add(barcode)
                                    fail_UN_UNICO += 1
                            elif "PASS" in result.upper():
                                passes += 1
                                if barcode not in barcodes_procesados:
                                    barcodes_procesados.add(barcode)
                                    pass_UN_UNICOS += 1
    
    conteo_fallas = Counter(steps_fails)
    cinco_mas_altas = conteo_fallas.most_common(5)

    total = passes + fails
    if total > 0:
        yail_rate = (passes / total) * 100
    else:
        yail_rate = 0
    
    total_sin_repetidos = passes + fails - fail_UN_UNICO
    if total_sin_repetidos > 0:
        yail_rate_sin_repetidos = (passes / total_sin_repetidos) * 100
    else:
        yail_rate_sin_repetidos = 0
    
    fecha_actual = datetime.now().strftime("%Y%m%d")
    reporte_nombre = f"reporte_general_{fecha_actual}.txt"
    output_file = os.path.join(directorios_salida[0], reporte_nombre)
    
    print(f"===== Reporte General del {fecha_actual} =====\n")
    print(f"Fecha y Hora: {fecha_actual}\n")
    
    print("------------ Estadísticas Generales ------------")
    print(f"Cantidad de fallas (FAIL): {fails}")
    print(f"Cantidad de pasadas (PASS): {passes}")
    print(f"Fallas Únicas (FAIL UNICOS): {fail_UN_UNICO}")
    print(f"Pasadas Únicas (PASS UNICOS): {pass_UN_UNICOS}\n")
    
    print("--------- Cálculo de Yield Rate ---------")
    print(f"Yield rate: {round(yail_rate, 2)}%")
    print(f"Yield rate (sin repetidos): {round(yail_rate_sin_repetidos, 2)}%\n")
    
    print("--------- Top 5 Pasos Más Repetidos en Fallas ---------")
    if cinco_mas_altas:
        for i, (nombre, cantidad) in enumerate(cinco_mas_altas, 1):
            print(f"{i}. {nombre}: {cantidad} repeticiones")
    else:
        print("No se encontraron pasos repetidos.\n")
    
    with open(output_file, mode='w', encoding="utf-8") as f:
        f.write(f"Reporte General del {fecha_actual}\n")
        f.write(f"\nCantidad de fallas (FAIL): {fails}\n")
        f.write(f"Cantidad de pasadas (PASS): {passes}\n")
        f.write(f"FAIL UNICOS: {fail_UN_UNICO}\n")
        f.write(f"PASS UNICOS: {pass_UN_UNICOS}\n")
        f.write(f"\n")
        f.write(f"---------Calculo de Yaild rate--------\n")
        f.write(f"Yield rate: {round(yail_rate,2)}%\n")
        f.write(f"First Yield rate: {round(yail_rate_sin_repetidos,2)}%\n")
        f.write(f"--------------------------------------\n")
        f.write("\nTop 5 pasos más repetidos en las fallas:\n")
        for nombre, cantidad in cinco_mas_altas:
            f.write(f"{nombre}: {cantidad}\n")
    
    print(f"Reporte General guardado en: {output_file}")
    return output_file


cfg_file = obtener_ruta_cfg()
settings = read_setting(cfg_file)
model = int(settings.get("model", 0))  
input_dir = settings.get("input_dir", "")  
directorio_salida = settings.get("directorio_salida", "") 

reporte_mensual(directorio_salida)