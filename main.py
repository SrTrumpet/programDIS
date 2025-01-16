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
directoryOrigin = "" # Directorio donde se van a sacar los nombres de los archivos generados por el Enterprise Architech
messageError = None
messageSuccess = None
tagColumns = ("","Administrar plataformas TI", "Entregar soporte a usuarios", "Gestion de outsourcing")# Tupla usada para luego usarlas de Tag en la base de datos
tagSubColumns = ("","Implementar Servicios", "Monitoreo de servicios", "Respaldo de servicios", "Planes de contingencia", "Mantenciones", "a sus cuentas", "a sus equipos", "a plataformas", "a eventos")
backupDir = path.join(getcwd(), "backup")
databaseDir = path.join(getcwd(), "database")
#################################################################

def getPath():
    global directoryOrigin, messageError
    directory = filedialog.askdirectory()
    directoryOrigin = directory
    filePath = open("path.txt", "w")
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
    global messageError, messageSuccess, fileBackup
    if directoryOrigin == "":
        if not messageError:
            messageError = Label(root, text="Debe seleccionar un directorio", font=("Arial", 12), bg="white", fg="red")
            messageError.grid(row=0, column=3, padx=10, pady=10)
    else:
        for fileName in listdir(directoryOrigin):
            if fileName.endswith(".htm"):
                shutil.copy(path.join(directoryOrigin, fileName), backupDir)
                fileSize = path.getsize(path.join(directoryOrigin, fileName))
                print("Nombre:",fileName,"tamaño:", fileSize)
                cursor.execute("INSERT INTO fileReferences(fileName, nickName, tag, subTag, size) VALUES(?,?,?,?,?)", (fileName, "", "", "",fileSize))
                connectionDataBase.commit()
        updateFileList("","")

saveButton = Button(root, text="Guardar referencias",font=("Arial"),width=30, height=2, bg="yellow", fg="black", justify="center", command=saveReferences)
saveButton.grid(row=0, column=2, padx=10, pady=10)

#################################################################

fileListbox = Listbox(root, width=30, height=25, font=("Arial", 12))
fileListbox.grid(row=1, column=0, padx=10, pady=10)

def updateFileList(tag="", subTag=""):
    fileListbox.delete(0, END)
    if (tag == "Seleccionar Filtro" or tag == "") and subTag != "Seleccionar SubFiltro":
        cursor.execute("SELECT fileName FROM fileReferences WHERE subTag = ? ORDER BY size DESC", (subTag,))
    elif tag != "Seleccionar Filtro" and (subTag == "Seleccionar SubFiltro" or subTag == ""):
        cursor.execute("SELECT fileName FROM fileReferences WHERE tag = ? ORDER BY size DESC", (tag,))
    elif subTag != "Seleccionar SubFiltro" and tag != "Seleccionar Filtro":
        cursor.execute("SELECT fileName FROM fileReferences WHERE tag = ? AND subTag = ? ORDER BY size DESC", (tag, subTag))
    else:
        cursor.execute("SELECT fileName FROM fileReferences ORDER BY size DESC")

    for row in cursor.fetchall():
        fileListbox.insert(END, row[0])


#################################################################

selectedTag = StringVar(root)
selectedTag.set("Seleccionar Filtro")
tagMenu = OptionMenu(root,selectedTag, *tagColumns, command=lambda _: updateFileList(selectedTag.get(), selectedSubTag.get()))
tagMenu.grid(row=2, column=0, padx=10, pady=10)

selectedSubTag = StringVar(root)
selectedSubTag.set("Seleccionar SubFiltro")
subTagMenu = OptionMenu(root, selectedSubTag, *tagSubColumns, command=lambda _: updateFileList(selectedTag.get(), selectedSubTag.get()))
subTagMenu.grid(row=3, column=0, padx=10, pady=10)


#################################################################

# Este codigo debe estar al final del script
try:
    filePath = open("path.txt", "r")
    directoryOrigin = filePath.readlines()[0]
except(IndexError):
    directoryOrigin = ""
except(FileNotFoundError):
    filePath = open("path.txt", "w")
    filePath.write("")
finally:
    filePath.close()

if directoryOrigin:
    label1 = Label(root, text=directoryOrigin, font=("Arial", 12), bg="white")
    label1.grid(row=0, column=1, padx=10, pady=10)

if not path.exists(backupDir):
    makedirs(backupDir)

if not path.exists(databaseDir):
    makedirs(databaseDir)

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

updateFileList("","")

root.mainloop()