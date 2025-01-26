from cx_Freeze import setup, Executable

includes = []
includefiles = []
excludes = ['Tkinter']
packages = ['os',"csv","sys","re","collections","datetime","socket"]

setup(
 name="Traductor_Segurity_SBOX",
 version="1.0",
 description="Traductor_Segurity_SBOX",
 options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}}, 
 executables = [Executable("Traductor_Segurity_SBOX.py")],
 )

build_exe_options = {
                 "includes":      includes,
}

