from cx_Freeze import setup, Executable

includes = []
includefiles = []
excludes = ['Tkinter']
packages = ['os',"csv","sys","re","collections","datetime","socket"]

setup(
 name="Traductor_Display_Inspection_LCD",
 version="1.0",
 description="Traductor_Display_Inspection_LCD",
 options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}}, 
 executables = [Executable("Traductor_Display_Inspection_LCD.py")],
 )

build_exe_options = {
                 "includes":      includes,
}

