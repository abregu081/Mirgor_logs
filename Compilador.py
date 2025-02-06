import os
import csv

def guardar_resultados_completos(directorio_salida):
    archivo_salida = 'Tabla Combinada.csv'
    archivos = [archivo for archivo in os.listdir(directorio_salida) if archivo.endswith('.csv')]
    ruta_salida = os.path.join(directorio_salida, archivo_salida)
    registros_unicos = set()
    encabezado_global = None
    
    for archivo in archivos:
        ruta_completa = os.path.join(directorio_salida, archivo)
        with open(ruta_completa, mode='r', encoding='utf-8') as archivo_actual:
            lector = csv.reader(archivo_actual)
            encabezado = next(lector, None)
            
            if encabezado_global is None:
                encabezado_global = encabezado  # Guardar encabezado del primer archivo
            
            for fila in lector:
                registros_unicos.add(tuple(fila))
    
    registros_ordenados = sorted(
        registros_unicos, 
        key=lambda x: (x[0], x[1])  # Ordenar por "Date" (índice 0) y "Time" (índice 1)
    )
    
    with open(ruta_salida, mode='w', newline='', encoding='utf-8') as archivo_final:
        escritor = csv.writer(archivo_final)
        if encabezado_global:
            escritor.writerow(encabezado_global)  # Escribir encabezado
        escritor.writerows(registros_ordenados)
    
    print(f"Archivo combinado guardado en: {ruta_salida}")

#Usar para ajustar los datos
guardar_resultados_completos(r"E:\abregu076")
