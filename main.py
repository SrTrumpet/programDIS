from tkinter import *
from tkinter import filedialog
from os import path, listdir, makedirs, getcwd
import shutil
import sqlite3

################## CONFIGURACIONES INICIALES ##################
root = Tk()
root.title("DIS Coquimbo - Gestor de documentacion")#Titulo de la ventana
root.geometry("1280x720")# Tamaño de la ventana
root.iconbitmap("./img/ucnLogo.ico")#Icono de la ventana
directoryEnterprise = "" # Directorio donde se van a sacar los nombres de los archivos generados por el Enterprise Architech
directoryWork = "" # Directorio donde se van a sacar los nombres de los archivos generados por el trabajo
directoryOriginal = "" # Directorio donde se van a sacar los nombres de los archivos originales
messageError = None
messageSuccess = None
tagColumns = ("Seleccionar Filtro","Administrar plataformas TI", "Entregar soporte a usuarios", "Gestion de outsourcing")# Tupla usada para luego usarlas de Tag en la base de datos
tagSubColumns = ("Seleccionar SubFiltro","Implementar Servicios", "Monitoreo de servicios", "Respaldo de servicios", "Planes de contingencia", "Mantenciones", "a sus cuentas", "a sus equipos", "a plataformas", "a eventos")
originalDir = path.join(getcwd(), "original")
databaseDir = path.join(getcwd(), "database")
enterpriseDir = path.join(getcwd(), "enterprise")
#################################################################

def getPath():
    global directoryEnterprise, messageError
    directory = filedialog.askdirectory()
    directoryEnterprise = directory
    filePath = open("pathEnterprise.txt", "w")
    filePath.write("")
    filePath.write(directory)
    if directory:
        label1 = Label(root, text=directory, font=("Arial", 12), bg="white")
        label1.grid(row=0, column=1, padx=10, pady=10)
        if messageError:
            messageError.destroy()
            messageError = None

scannButton = Button(root, text="Definir el directorio",font=("Arial"),width=30, height=2, bg="blue", fg="white", justify="center", command=getPath)
scannButton.grid(row=0, column=0, padx=10, pady=10)
###################

def saveReferences():
    global messageError, messageSuccess
    if directoryEnterprise == "":
        if not messageError:
            messageError = Label(root, text="Debe seleccionar un directorio", font=("Arial", 12), bg="white", fg="red")
            messageError.grid(row=0, column=3, padx=10, pady=10)
    else:
        for fileName in listdir(directoryEnterprise):
            if fileName.endswith(".htm"):
                try:
                    shutil.copy(path.join(directoryEnterprise, fileName), enterpriseDir)
                    fileSize = path.getsize(path.join(directoryEnterprise, fileName))
                    print("Nombre:",fileName,"tamaño:", fileSize)
                    cursor.execute("INSERT INTO fileReferences(fileName, nickName, tag, subTag, size) VALUES(?,?,?,?,?)", (fileName, "", "", "",fileSize))
                    connectionDataBase.commit()
                except(sqlite3.IntegrityError):
                    shutil.copy(path.join(directoryEnterprise, fileName), enterpriseDir)
                    fileSize = path.getsize(path.join(directoryEnterprise, fileName))
                    print("Nombre:",fileName,"tamaño:", fileSize)
        updateFileList("","")

saveButton = Button(root, text="Guardar referencias",font=("Arial"),width=30, height=2, bg="green", fg="white", justify="center", command=saveReferences)
saveButton.grid(row=0, column=1, padx=10, pady=10)
################################################################

def updateFileList(tag=NONE, subTag=NONE):
    print('tag: ',tag, 'subTag: ',subTag)
    fileListbox.delete(0, END)
    if "Seleccionar Filtro" and subTag != "Seleccionar SubFiltro":
        cursor.execute("SELECT fileName FROM fileReferences WHERE subTag = ? ORDER BY size DESC", (subTag,))
    elif tag != "Seleccionar Filtro" and subTag == "Seleccionar SubFiltro":
        cursor.execute("SELECT fileName FROM fileReferences WHERE tag = ? ORDER BY size DESC", (tag,))
    elif subTag != "Seleccionar SubFiltro" and tag != "Seleccionar Filtro":
        cursor.execute("SELECT fileName FROM fileReferences WHERE tag = ? AND subTag = ? ORDER BY size DESC", (tag, subTag))
    else:
        cursor.execute("SELECT fileName FROM fileReferences ORDER BY size DESC")

    for row in cursor.fetchall():
        fileListbox.insert(END, row[0])

fileListbox = Listbox(root, width=30, height=25, font=("Arial", 12))
fileListbox.grid(row=2, column=0, padx=10, pady=10)
#################################################################

def getPathWork():
    global directoryWork
    directory = filedialog.askdirectory()
    directoryWork = directory
    filePathWork = open("pathTrabajo.txt", "w")
    filePathWork.write("")
    filePathWork.write(directory)
    if directory:
        textPathWork = Label(root, text=directory, font=("Arial", 12), bg="white")
        textPathWork.grid(row=1, column=2, padx=10, pady=10)

buttonPathWork = Button(root, text="Definir el directorio de trabajo",font=("Arial"),width=30, height=2, bg="blue", fg="white", justify="center", command=getPathWork)
buttonPathWork.grid(row=0, column=2, padx=10, pady=10)

#################################################################

selectedTag = StringVar(root)
selectedTag.set("Seleccionar Filtro")
tagMenu = OptionMenu(root,selectedTag, *tagColumns, command=lambda _: updateFileList(selectedTag.get(), selectedSubTag.get()))
tagMenu.grid(row=3, column=0, padx=10, pady=10)

selectedSubTag = StringVar(root)
selectedSubTag.set("Seleccionar SubFiltro")
subTagMenu = OptionMenu(root, selectedSubTag, *tagSubColumns, command=lambda _: updateFileList(selectedTag.get(), selectedSubTag.get()))
subTagMenu.grid(row=4, column=0, padx=10, pady=10)
#################################################################

# Este codigo debe estar al final del script
#RUTAS
#Directorio guardado para el la ruta del enterprise
try:
    filePath = open("pathEnterprise.txt", "r")
    directoryEnterprise = filePath.readlines()[0]
except(IndexError):
    directoryEnterprise = ""
except(FileNotFoundError):
    filePath = open("pathEnterprise.txt", "w")
    filePath.write("")
finally:
    filePath.close()

#Directorio guardado para el la ruta de donde se guardaran los archivos originales
try:
    filePathOriginal = open("pathOriginal.txt", "r")
    directoryOriginal = filePathOriginal.readlines()[0]
except(IndexError):
    directoryOriginal = ""
except(FileNotFoundError):
    filePathOriginal = open("pathOriginal.txt", "w")
    filePathOriginal.write("")
finally:
    filePathOriginal.close()

#Direcotrio guardado para el la ruta de trabajo donde se agreguen la documentacion para luego convertirlo a html
try:
    filePathWork = open("pathTrabajo.txt", "r")
    directoryWork = filePathWork.readlines()[0]
    textPathWork.destroy()
except(IndexError):
    directoryWork = ""
except(FileNotFoundError):
    filePathWork = open("pathTrabajo.txt", "w")
    filePathWork.write("")
finally:
    filePathWork.close()

if directoryEnterprise:
    label1 = Label(root, text=directoryEnterprise, font=("Arial", 12), bg="white")
    label1.grid(row=1, column=0, padx=10, pady=10)

if not path.exists(enterpriseDir):
    makedirs(enterpriseDir)

if not path.exists(databaseDir):
    makedirs(databaseDir)

if not path.exists(originalDir):
    makedirs(originalDir)

#BASE DE DATOS
connectionDataBase = sqlite3.connect("./database/database.db")
cursor = connectionDataBase.cursor()
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS fileReferences(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fileName TEXT NOT NULL UNIQUE,
        nickName TEXT,
        tag TEXT,
        subTag TEXT,
        size INTEGER
    )
''')
connectionDataBase.commit()

#ACTUALIZACION DE LA LISTA DE ARCHIVOS
updateFileList("Seleccionar Filtro","Seleccionar SubFiltro")

root.mainloop()