from tkinter import *
from tkinter import filedialog, simpledialog, messagebox, ttk
from os import path, listdir, makedirs, getcwd, startfile
import shutil
import sqlite3
from downloadHTML import DownloadHTML

################## CONFIGURACIONES INICIALES ##################
root = Tk()
root.title("DIS Coquimbo - Gestor de documentacion")  # Titulo de la ventana
root.geometry("1280x720")  # Tamaño de la ventana
root.iconbitmap(default="./img/ucnLogo.ico")  # Icono de la ventana
directoryEnterprise = ""  # Directorio donde se van a sacar los nombres de los archivos generados por el Enterprise Architech
directoryWork = ""  # Directorio donde se van a sacar los nombres de los archivos generados por el trabajo
directoryOriginal = ""  # Directorio donde se van a sacar los nombres de los archivos originales
messageError = None
messageSuccess = None
textPathWork = None
textPathOriginal = None
tagColumns = ("Seleccionar Filtro", "Administrar plataformas TI", "Entregar soporte a usuarios", "Gestion de outsourcing")  # Tupla usada para luego usarlas de Tag en la base de datos
tagSubColumns = ("Seleccionar SubFiltro", "Implementar Servicios", "Monitoreo de servicios", "Respaldo de servicios", "Planes de contingencia", "Mantenciones", "a sus cuentas", "a sus equipos", "a plataformas", "a eventos")
originalDir = path.join(getcwd(), "original")
databaseDir = path.join(getcwd(), "database")
enterpriseDir = path.join(getcwd(), "enterprise")
downloadDir = path.join(getcwd(), "download")
#################################################################

def getPath():
    global directoryEnterprise, messageError, textPathOriginal
    directory = filedialog.askdirectory()
    directoryEnterprise = directory
    filePath = open("pathEnterprise.txt", "w")
    filePath.write("")
    filePath.write(directory)
    if directory:
        if textPathOriginal:
            textPathOriginal.destroy()
        textPathOriginal = Label(root, text=directory, font=("Arial", 12), bg="white")
        textPathOriginal.grid(row=1, column=0, padx=10, pady=10)
        if messageError:
            messageError.destroy()
            messageError = None

scannButton = Button(root, text="Definir el directorio", font=("Arial"), width=30, height=2, bg="blue", fg="white", justify="center", command=getPath)
scannButton.grid(row=0, column=0, padx=10, pady=10)
###################

def saveReferences():
    global messageError, messageSuccess
    if directoryEnterprise == "":
        if not messageError:
            messageError = Label(root, text="Debe seleccionar un directorio", font=("Arial", 12), bg="white", fg="red")
            messageError.grid(row=1, column=1, padx=10, pady=10)
    else:
        for fileName in listdir(directoryEnterprise):
            if fileName.endswith(".htm"):
                try:
                    shutil.copy(path.join(directoryEnterprise, fileName), enterpriseDir)
                    fileSize = path.getsize(path.join(directoryEnterprise, fileName))
                    print("Nombre:", fileName, "tamaño:", fileSize)
                    cursor.execute("INSERT INTO fileReferences(fileName, nickName, tag, subTag, size) VALUES(?,?,?,?,?)", (fileName, "", "", "", fileSize))
                    connectionDataBase.commit()
                except sqlite3.IntegrityError:
                    shutil.copy(path.join(directoryEnterprise, fileName), enterpriseDir)
                    fileSize = path.getsize(path.join(directoryEnterprise, fileName))
                    print("Nombre:", fileName, "tamaño:", fileSize)
        updateFileList("","")

saveButton = Button(root, text="Guardar referencias", font=("Arial"), width=30, height=2, bg="green", fg="white", justify="center", command=saveReferences)
saveButton.grid(row=0, column=1, padx=10, pady=10)
################################################################

def updateFileList(tag=None, subTag=None):
    print('tag: ', tag, 'subTag: ', subTag)
    fileTreeview.delete(*fileTreeview.get_children())
    if tag and tag != "Seleccionar Filtro" and subTag and subTag != "Seleccionar SubFiltro":
        cursor.execute("SELECT fileName, nickName FROM fileReferences WHERE tag = ? AND subTag = ? ORDER BY size DESC", (tag, subTag))
    elif tag and tag != "Seleccionar Filtro":
        cursor.execute("SELECT fileName, nickName FROM fileReferences WHERE tag = ? ORDER BY size DESC", (tag,))
    elif subTag and subTag != "Seleccionar SubFiltro":
        cursor.execute("SELECT fileName, nickName FROM fileReferences WHERE subTag = ? ORDER BY size DESC", (subTag,))
    else:
        cursor.execute("SELECT fileName, nickName FROM fileReferences ORDER BY size DESC")

    for row in cursor.fetchall():
        fileTreeview.insert("", "end", values=row)

fileTreeview = ttk.Treeview(root, columns=("fileName", "nickName"), show="headings", height=23)
fileTreeview.heading("fileName", text="Nombre del archivo")
fileTreeview.heading("nickName", text="Nickname")
fileTreeview.column("fileName", width=100)
fileTreeview.column("nickName", width=200)
fileTreeview.grid(row=2, column=0, padx=10, pady=10, columnspan=1)
#################################################################

def getPathWork():
    global directoryWork, textPathWork
    directory = filedialog.askdirectory()
    directoryWork = directory
    filePathWork = open("pathTrabajo.txt", "w")
    filePathWork.write("")
    filePathWork.write(directory)
    if directory:
        if textPathWork:
            textPathWork.destroy()
        textPathWork = Label(root, text=directory, font=("Arial", 12), bg="white")
        textPathWork.grid(row=1, column=2, padx=10, pady=10)

buttonPathWork = Button(root, text="Definir el directorio de trabajo", font=("Arial"), width=30, height=2, bg="blue", fg="white", justify="center", command=getPathWork)
buttonPathWork.grid(row=0, column=2, padx=10, pady=10)

#################################################################

def downloadFilesConverter():
    DownloadHTML.downloadHtml(directoryWork)
    updateDownloadList()

buttonDownload = Button(root, text="Descargar archivos", font=("Arial"), width=30, height=2, bg="green", fg="white", justify="center", command=downloadFilesConverter)
buttonDownload.grid(row=0, column=3, padx=10, pady=10)

#################################################################
# Listbox para mostrar los archivos en la carpeta download

downloadListbox = Listbox(root, width=30, height=24, font=("Arial", 12))
downloadListbox.grid(row=2, column=3, padx=10, pady=10,columnspan=1)

def updateDownloadList():
    downloadListbox.delete(0, END)
    for file_name in listdir(downloadDir):
        downloadListbox.insert(END, file_name)

# Actualizar la lista de archivos descargados al iniciar
updateDownloadList()
#################################################################

selectedTag = StringVar(root)
selectedTag.set("Seleccionar Filtro")
tagMenu = OptionMenu(root, selectedTag, *tagColumns, command=lambda _: updateFileList(selectedTag.get(), selectedSubTag.get()))
tagMenu.grid(row=3, column=0, padx=10, pady=10)

selectedSubTag = StringVar(root)
selectedSubTag.set("Seleccionar SubFiltro")
subTagMenu = OptionMenu(root, selectedSubTag, *tagSubColumns, command=lambda _: updateFileList(selectedTag.get(), selectedSubTag.get()))
subTagMenu.grid(row=4, column=0, padx=10, pady=10)
#################################################################
# Menu

def openFile():
    selected_item = fileTreeview.selection()[0]
    selectFile = fileTreeview.item(selected_item, "values")[0]
    filePath = path.join(enterpriseDir, selectFile)
    startfile(filePath)

def assignNickname():
    selected_item = fileTreeview.selection()[0]
    selected_file = fileTreeview.item(selected_item, "values")[0]
    new_nickname = simpledialog.askstring("Asignar Nickname", "Ingrese el nuevo nickname:")
    if new_nickname:
        cursor.execute("UPDATE fileReferences SET nickName = ? WHERE fileName = ?", (new_nickname, selected_file))
        connectionDataBase.commit()
        updateFileList()

def assignTag():
    selected_item = fileTreeview.selection()[0]
    selected_file = fileTreeview.item(selected_item, "values")[0]
    new_tag = simpledialog.askstring("Asignar Tag", "Ingrese el nuevo tag:")
    if new_tag:
        cursor.execute("UPDATE fileReferences SET tag = ? WHERE fileName = ?", (new_tag, selected_file))
        connectionDataBase.commit()
        updateFileList()

def assignSubTag():
    selected_item = fileTreeview.selection()[0]
    selected_file = fileTreeview.item(selected_item, "values")[0]
    new_subTag = simpledialog.askstring("Asignar SubTag", "Ingrese el nuevo subtag:")
    if new_subTag:
        cursor.execute("UPDATE fileReferences SET subTag = ? WHERE fileName = ?", (new_subTag, selected_file))
        connectionDataBase.commit()
        updateFileList()

def deleteTag():
    selected_item = fileTreeview.selection()[0]
    selected_file = fileTreeview.item(selected_item, "values")[0]
    cursor.execute("UPDATE fileReferences SET tag = ? WHERE fileName = ?", ("", selected_file))
    connectionDataBase.commit()
    updateFileList()

def deleteSubTag():
    selected_item = fileTreeview.selection()[0]
    selected_file = fileTreeview.item(selected_item, "values")[0]
    cursor.execute("UPDATE fileReferences SET subTag = ? WHERE fileName = ?", ("", selected_file))
    connectionDataBase.commit()
    updateFileList()

def deleteNickName():
    selected_item = fileTreeview.selection()[0]
    selected_file = fileTreeview.item(selected_item, "values")[0]
    cursor.execute("UPDATE fileReferences SET nickName = ? WHERE fileName = ?", ("", selected_file))
    connectionDataBase.commit()
    updateFileList()

contextMenu = Menu(root, tearoff=0)
contextMenu.add_command(label="Abrir archivo", command=openFile)
contextMenu.add_command(label="Asignar un nickname", command=assignNickname)
contextMenu.add_command(label="Asignar un tag", command=assignTag)
contextMenu.add_command(label="Asignar un subtag", command=assignSubTag)
contextMenu.add_command(label="Eliminar el nickname", command=deleteNickName)
contextMenu.add_command(label="Eliminar el tag", command=deleteTag)
contextMenu.add_command(label="Eliminar el subtag", command=deleteSubTag)

def showContextMenu(event):
    contextMenu.post(event.x_root, event.y_root)

fileTreeview.bind("<Button-3>", showContextMenu)
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
except(IndexError):
    directoryWork = ""
except(FileNotFoundError):
    filePathWork = open("pathTrabajo.txt", "w")
    filePathWork.write("")
finally:
    filePathWork.close()

if directoryEnterprise:
    textPathOriginal = Label(root, text=directoryEnterprise, font=("Arial", 12), bg="white")
    textPathOriginal.grid(row=1, column=0, padx=10, pady=10)

if directoryWork:
    textPathWork = Label(root, text=directoryWork, font=("Arial", 12), bg="white")
    textPathWork.grid(row=1, column=2, padx=10, pady=10)

if not path.exists(enterpriseDir):
    makedirs(enterpriseDir)

if not path.exists(databaseDir):
    makedirs(databaseDir)

if not path.exists(originalDir):
    makedirs(originalDir)

if not path.exists(downloadDir):
    makedirs(downloadDir)

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