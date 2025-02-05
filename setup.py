from cx_Freeze import setup, Executable

# Datos de la versión
version = "1.0"
changelog = """
Cambios en la versión 1.0:
- Traductor_Sbox_Assy_1.
- Deshabilitacion de la funcion Obtener estacion debido a que no se modifico el hostname de la maquina.
"""
# Escribir la versión y cambios en un archivo
with open("Version.txt", "w", encoding="utf-8") as version_file:
    version_file.write(f"Versión: {version}\n")
    version_file.write(changelog)

# Configuración de cx_Freeze
includes = []
includefiles = ["Version.txt"]  # Aseguramos que se incluya en el .exe
excludes = ['Tkinter']
packages = ['os', 'csv', 'sys', 're', 'collections', 'datetime', 'socket']

setup(
    name="Traductor_Sbox_Assy_1",
    version=version,
    description="Traductor_Sbox_Assy_1",
    options={'build_exe': {'excludes': excludes, 'packages': packages, 'include_files': includefiles}},
    executables=[Executable("Traductor_Sbox_Assy_1.py")]
)
