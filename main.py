from tkinter import *
import time
from tkinter import filedialog, simpledialog, messagebox, ttk
from os import path, listdir, makedirs, getcwd, startfile
import os
import shutil
import sqlite3
from downloadHTML import DownloadHTML

################## CONFIGURACIONES INICIALES ##################
root = Tk()
root.title("DIS Coquimbo - Gestor de documentacion")  # Titulo de la ventana
root.geometry("1230x720")  # Tamaño de la ventana
root.iconbitmap(default="./img/ucnLogo.ico")  # Icono de la ventana
root.config(bg="#323232")
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
if not path.exists(downloadDir):
    makedirs(downloadDir)

updateDownloadList()

#################################################################
# Treeview central para mostrar los archivos seleccionados

selectedFilesTreeview = ttk.Treeview(root, columns=("source", "fileName"), show="headings", height=2)
selectedFilesTreeview.heading("source", text="Fuente")
selectedFilesTreeview.heading("fileName", text="Nombre del archivo")
selectedFilesTreeview.column("source", width=100)
selectedFilesTreeview.column("fileName", width=200)
selectedFilesTreeview.grid(row=2, column=1, padx=10, pady=10, columnspan=2)

def addToSelectedFiles(file_name, source):
    if source == "left":
        if selectedFilesTreeview.exists("left"):
            selectedFilesTreeview.delete("left")
        selectedFilesTreeview.insert("", "end", iid="left", values=(source, file_name))
    elif source == "right":
        if selectedFilesTreeview.exists("right"):
            selectedFilesTreeview.delete("right")
        selectedFilesTreeview.insert("", "end", iid="right", values=(source, file_name))

def onFileTreeviewSelect(event):
    selected_item = fileTreeview.selection()[0]
    selectFile = fileTreeview.item(selected_item, "values")[0]
    addToSelectedFiles(selectFile, "left")

def onDownloadListboxSelect(event):
    selected_file = downloadListbox.get(downloadListbox.curselection())
    addToSelectedFiles(selected_file, "right")

fileTreeview.bind("<<TreeviewSelect>>", onFileTreeviewSelect)
downloadListbox.bind("<<ListboxSelect>>", onDownloadListboxSelect)


#################################################################
#Funcion para combinar archivos
# Función para combinar archivos
# Función para combinar archivos
def combineFiles():
    try:
        # Obtener los valores seleccionados en el Treeview
        left_item = selectedFilesTreeview.item("left", "values")
        right_item = selectedFilesTreeview.item("right", "values")

        # Validar que ambos archivos están seleccionados
        if not left_item or not right_item:
            raise ValueError("Ambos archivos deben estar seleccionados.")

        left_file = left_item[1]  # Nombre que reemplazará al archivo copiado
        right_file = right_item[1]  # Archivo que será copiado

        # Construir rutas completas
        original_file_path = path.join(downloadDir, right_file)  # Archivo de origen
        renamed_file_path = path.join(originalDir, left_file)  # Nuevo nombre del archivo

        # Verificar si el archivo de origen existe
        if not path.exists(original_file_path):
            raise FileNotFoundError(f"El archivo '{right_file}' no existe en la carpeta de descargas.")

        # Si el archivo destino ya existe, eliminarlo
        if path.exists(renamed_file_path):
            os.remove(renamed_file_path)

        # Copiar el archivo desde downloadDir a originalDir y renombrarlo
        shutil.copy(original_file_path, renamed_file_path)

        # Mostrar mensaje de éxito
        messagebox.showinfo("Éxito", f"Archivo '{right_file}' copiado y reemplazado como '{left_file}' en la carpeta original.")
    except ValueError as ve:
        messagebox.showerror("Error", str(ve))
    except KeyError:
        messagebox.showerror("Error", "Debe seleccionar un archivo de cada tabla.")
    except FileNotFoundError as fnf_error:
        messagebox.showerror("Error", str(fnf_error))
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {str(e)}")

#################################################################
#Botones para guardar las referencias en la carpeta @original y luego el segundo boton es para reemplazar los documentos del
#path de donde esta el proyecto original

combineButton = Button(root, text="Combinar archivos", font=("Arial"), width=18, height=1, bg="green", fg="white", justify="center", command=combineFiles)
combineButton.place(x=525, y=450)

def replaceFiles():
    try:
        # Copiar y reemplazar archivos de @original a @enterprise
        for file_name in listdir(originalDir):
            original_file_path = path.join(originalDir, file_name)
            enterprise_file_path = path.join(enterpriseDir, file_name)
            user_defined_path = path.join(directoryEnterprise, file_name)
            
            # Copiar a @enterprise
            shutil.copy(original_file_path, enterprise_file_path)
            
            # Copiar a la carpeta definida por el usuario
            shutil.copy(original_file_path, user_defined_path)
        
        # Borrar archivos en @original
        for file_name in listdir(originalDir):
            os.remove(path.join(originalDir, file_name))
        
        # Borrar archivos en @download
        for file_name in listdir(downloadDir):
            os.remove(path.join(downloadDir, file_name))
        
        updateDownloadList()

        messagebox.showinfo("Éxito", "Archivos reemplazados y copiados correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")


replaceButton = Button(root, text="Reemplazar archivos", font=("Arial"), width=18, height=1, bg="blue", fg="white", justify="center", command=replaceFiles)
replaceButton.place(x=525, y=500)
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

def openDownloadedFile():
    selected_file = downloadListbox.get(downloadListbox.curselection())
    filePath = path.join(downloadDir, selected_file)
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

# Menu contextual para la Listbox de archivos descargados
downloadContextMenu = Menu(root, tearoff=0)
downloadContextMenu.add_command(label="Abrir archivo", command=openDownloadedFile)

def showDownloadContextMenu(event):
    downloadContextMenu.post(event.x_root, event.y_root)

downloadListbox.bind("<Button-3>", showDownloadContextMenu)
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