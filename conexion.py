import mysql.connector
import tkinter as tk
from tkinter import messagebox, Scrollbar, Listbox
import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image, ImageTk

# Función para insertar un nuevo usuario
def insertar_usuario():
    try:
        conn = mysql.connector.Connect(
            host="localhost",
            user="root",
            password="",
            port="3306",
            database="bdusuarios1"
        )
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO usuarios (id, nombres, apellidos, fkingreso, edad, Fingreso, foto, Documento, Users)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        ruta_archivo = (r"C:\Unal\DateBase\Users\prado.txt")
        valores = [
            "",  # id (puede ser autoincremental)
            entry_nombres.get(),
            entry_apellidos.get(),
            entry_fkingreso.get(),
            entry_edad.get(),
            entry_fingreso.get(),
            "",  # foto
            entry_documento.get(),
            ruta_archivo
        ]
        
        cursor.execute(sql, valores)
        conn.commit()
        messagebox.showinfo("Éxito", "Usuario insertado correctamente.")
        mostrar_usuarios()  # Actualizar la lista después de insertar
        
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al insertar usuario: {err}")
    finally:
        cursor.close()
        conn.close()

# Función para mostrar todos los usuarios en la base de datos
def mostrar_usuarios():
    try:
        conn = mysql.connector.Connect(
            host="localhost",
            user="root",
            password="",
            port="3306",
            database="bdusuarios1"
        )
        cursor = conn.cursor()
        
        sql = """
        SELECT id, nombres, apellidos, Documento, Fingreso
        FROM usuarios
        """
        cursor.execute(sql)
        resultados = cursor.fetchall()
        
        # Limpiar la lista antes de agregar nuevos elementos
        listbox_usuarios.delete(0, tk.END)
        for row in resultados:
            listbox_usuarios.insert(tk.END, (row[0], f"Nombres: {row[1]}, Apellidos: {row[2]}, Documento: {row[3]}, Fecha de Ingreso: {row[4]}"))
    
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al mostrar usuarios: {err}")
    finally:
        cursor.close()
        conn.close()

# Función para buscar usuarios
def buscar_usuarios():
    try:
        conn = mysql.connector.Connect(
            host="localhost",
            user="root",
            password="",
            port="3306",
            database="bdusuarios1"
        )
        cursor = conn.cursor()
        
        # Obtener los criterios de búsqueda
        nombre = entry_buscar_nombre.get()
        apellido = entry_buscar_apellido.get()
        documento = entry_buscar_documento.get()
        fecha_ingreso = entry_buscar_fingreso.get()
        
        sql = """
        SELECT id, nombres, apellidos, Documento, Fingreso
        FROM usuarios
        WHERE (nombres LIKE %s AND %s != '') OR
              (apellidos LIKE %s AND %s != '') OR
              (Documento LIKE %s AND %s != '') OR
              (Fingreso LIKE %s AND %s != '')
        """
        
        cursor.execute(sql, (f'%{nombre}%', nombre, f'%{apellido}%', apellido, f'%{documento}%', documento, f'%{fecha_ingreso}%', fecha_ingreso))
        resultados = cursor.fetchall()
        
        # Limpiar la lista antes de agregar nuevos elementos
        listbox_usuarios.delete(0, tk.END)
        
        for row in resultados:
            listbox_usuarios.insert(tk.END, (row[0], f"Nombres: {row[1]}, Apellidos: {row[2]}, Documento: {row[3]}, Fecha de Ingreso: {row[4]}"))
    
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al buscar usuarios: {err}")
    finally:
        cursor.close()
        conn.close()

# Función para registrar asistencia
def registrar_asistencia():
    try:
        selected_user = listbox_usuarios.curselection()
        if not selected_user:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un usuario.")
            return
        
        user_id = listbox_usuarios.get(selected_user)[0]  # Obtener el ID del usuario seleccionado
        fecha_asistencia = entry_fecha_asistencia.get()
        
        conn = mysql.connector.Connect(
            host="localhost",
            user="root",
            password="",
            port="3306",
            database="bdusuarios1"
        )
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO asistencia (user_id, fecha)
        VALUES (%s, %s)
        """
        cursor.execute(sql, (user_id, fecha_asistencia))
        conn.commit()
        messagebox.showinfo("Éxito", "Asistencia registrada correctamente.")
        
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al registrar asistencia: {err}")
    finally:
        cursor.close()
        conn.close()

# Función para mostrar la gráfica de asistencia por usuario
def mostrar_grafica_asistencia():
    try:
        conn = mysql.connector.Connect(
            host="localhost",
            user="root",
            password="",
            port="3306",
            database="bdusuarios1"
        )
        cursor = conn.cursor()
        
        sql = """
        SELECT u.nombres, u.apellidos, a.fecha, COUNT(*) as total
        FROM asistencia a
        JOIN usuarios u ON a.user_id = u.id
        GROUP BY u.id, a.fecha
        ORDER BY a.fecha
        """
        cursor.execute(sql)
        resultados = cursor.fetchall()
        
        # Preparar los datos para la gráfica
        datos = {}
        for row in resultados:
            nombre = f"{row[0]} {row[1]}"
            fecha = row[2].strftime("%Y-%m-%d")  # Formatear la fecha completa
            total = int(row[3])  # Asegurarse de que sea un número entero
            if nombre not in datos:
                datos[nombre] = {}
            datos[nombre][fecha] = total
        
        # Crear la gráfica
        plt.figure(figsize=(10, 5))
        for nombre, fechas in datos.items():
            plt.plot(list(fechas.keys()), list(fechas.values()), marker='o', label=nombre)
        
        plt.xlabel('Fecha')
        plt.ylabel('Total de Asistencias')
        plt.title('Asistencia por Usuario')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        # Configurar el eje y para mostrar solo números enteros
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))

        plt.show()
    
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al mostrar la gráfica: {err}")
    finally:
        cursor.close()
        conn.close()

# Configuración de la ventana principal
root = tk.Tk()
root.title("Registro de Usuarios")

# Cargar la imagen de fondo
imagen_fondo = Image.open(r"C:/Unal/Temas/Informacion.png")
imagen_fondo = imagen_fondo.resize((1280, 720), Image.LANCZOS)  # Ajustar tamaño si es necesario
fondo = ImageTk.PhotoImage(imagen_fondo)


# Crear un Label para el fondo y añadirlo a la ventana
label_fondo = tk.Label(root, image=fondo)
label_fondo.place(x=0, y=0, relwidth=1, relheight=1)  # Cubrir toda la ventana

# Creación del frame para insertar usuarios
frame_insertar = tk.Frame(root)
frame_insertar.pack(padx=10, pady=10)

# Campos de entrada para insertar usuarios
tk.Label(frame_insertar, text="Nombre-Documento:").grid(row=0, column=0)
entry_nombres = tk.Entry(frame_insertar)
entry_nombres.grid(row=0, column=1)

tk.Label(frame_insertar, text="Apellidos:").grid(row=1, column=0)
entry_apellidos = tk.Entry(frame_insertar)
entry_apellidos.grid(row=1, column=1)

tk.Label(frame_insertar, text="Fecha de Ingreso:").grid(row=2, column=0)
entry_fingreso = tk.Entry(frame_insertar)
entry_fingreso.grid(row=2, column=1)

tk.Label(frame_insertar, text="Edad:").grid(row=3, column=0)
entry_edad = tk.Entry(frame_insertar)
entry_edad.grid(row=3, column=1)

tk.Label(frame_insertar, text="Documento:").grid(row=4, column=0)
entry_documento = tk.Entry(frame_insertar)
entry_documento.grid(row=4, column=1)

tk.Label(frame_insertar, text="FK Ingreso:").grid(row=5, column=0)
entry_fkingreso = tk.Entry(frame_insertar)
entry_fkingreso.grid(row=5, column=1)

# Botón para insertar el usuario
btn_insertar = tk.Button(frame_insertar, text="Insertar Usuario", command=insertar_usuario)
btn_insertar.grid(row=6, columnspan=2)

# Creación del frame para buscar usuarios
frame_buscar = tk.Frame(root)
frame_buscar.pack(padx=10, pady=10)

# Campos de entrada para buscar usuarios
tk.Label(frame_buscar, text="Buscar por Nombre:").grid(row=0, column=0)
entry_buscar_nombre = tk.Entry(frame_buscar)
entry_buscar_nombre.grid(row=0, column=1)

tk.Label(frame_buscar, text="Buscar por Apellido:").grid(row=1, column=0)
entry_buscar_apellido = tk.Entry(frame_buscar)
entry_buscar_apellido.grid(row=1, column=1)

tk.Label(frame_buscar, text="Buscar por Documento:").grid(row=2, column=0)
entry_buscar_documento = tk.Entry(frame_buscar)
entry_buscar_documento.grid(row=2, column=1)

tk.Label(frame_buscar, text="Buscar por Fecha de Ingreso:").grid(row=3, column=0)
entry_buscar_fingreso = tk.Entry(frame_buscar)
entry_buscar_fingreso.grid(row=3, column=1)

# Botón para buscar usuarios
btn_buscar = tk.Button(frame_buscar, text="Buscar Usuario", command=buscar_usuarios)
btn_buscar.grid(row=4, columnspan=2)

# Listbox para mostrar usuarios
listbox_usuarios = Listbox(root, width=50)
listbox_usuarios.pack(padx=10, pady=10)

# Scrollbar para el Listbox
scrollbar = Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox_usuarios.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox_usuarios.yview)

# Frame para registrar asistencia
frame_asistencia = tk.Frame(root)
frame_asistencia.pack(padx=10, pady=10)

tk.Label(frame_asistencia, text="Fecha de Asistencia (YYYY-MM-DD):").grid(row=0, column=0)
entry_fecha_asistencia = tk.Entry(frame_asistencia)
entry_fecha_asistencia.grid(row=0, column=1)

btn_registrar_asistencia = tk.Button(frame_asistencia, text="Registrar Asistencia", command=registrar_asistencia)
btn_registrar_asistencia.grid(row=1, columnspan=2)

btn_graficar_asistencia = tk.Button(frame_asistencia, text="Mostrar Gráfica de Asistencia", command=mostrar_grafica_asistencia)
btn_graficar_asistencia.grid(row=2, columnspan=2)

# Mostrar usuarios al iniciar la aplicación
mostrar_usuarios()

# Ejecutar la aplicación
root.mainloop()





# Agregar una nueva columna "informacion_adicional" de tipo TEXT a la tabla "usuarios"
# cursor.execute("ALTER TABLE usuarios ADD COLUMN Users TEXT")


# para cambiar el nombre de un usuario
# sql = """UPDATE usuarios SET nombres = "juancrack" WHERE nombres = "camilo" """
# cursor.execute(sql)
# conn.commit()

# Consulta INSERT para agregar un nuevo usuario
#sql = """
    #INSERT INTO usuarios (id, nombres, apellidos, fkingreso, edad, Fingreso, foto, Documento )
    #VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#"""
#valores = ["", "Alejo", "prado","1", "87","2024-04-04","","100634627"]
#cursor.execute(sql, valores)

# Confirmar los cambios en la base de datos
#conn.commit()
