from cx_Freeze import setup, Executable

includes = []
includefiles = []
excludes = ['Tkinter']
packages = ['os',"csv","sys","re","collections","datetime","socket"]

setup(
 name="Traductor_PCB_DCSD",
 version="1.0",
 description="Traductor_PCB_DCSD",
 options = {'build_exe': {'excludes':excludes,'packages':packages,'include_files':includefiles}}, 
 executables = [Executable("Traductor_PCB_DCSD.py")],
 )

build_exe_options = {
                 "includes":      includes,
}

