from tkinter import *
from tkinter import filedialog
from os import path
#directory = path.dirname(__file__)


root = Tk()
root.title("DIS Coquimbo")#Titulo de la ventana
root.geometry("1280x720")#Tamaño de la ventana
root.iconbitmap("ucnLogo.ico")#Icono de la ventana
root.resizable(0,0)#No se puede cambiar el tamaño de la ventana
directoryOrigin = ""
##################

def getPath():
    global directoryOrigin
    directory = filedialog.askdirectory()
    directoryOrigin = directory
    if directory:
        label1 = Label(root, text=directory, font=("Arial", 12), bg="white")
        label1.grid(row=0, column=1, padx=10, pady=10)


##################
scannButton = Button(root, text="Definir el directorio",font=("Arial"),width=30, height=2, bg="blue", fg="white", justify="center", command=getPath)
scannButton.grid(row=0, column=0, padx=10, pady=10)

###################

def saveReferences():
    if directoryOrigin == "":
        print("No se ha definido un directorio")
    else:
        print("Guardando referencias")
        print(directoryOrigin)

saveButton = Button(root, text="Guardar referencias",font=("Arial"),width=30, height=2, bg="yellow", fg="black", justify="center", command=saveReferences)
saveButton.grid(row=0, column=2, padx=10, pady=10)


#Este codigo debe estar al final del script
root.mainloop()