import cv2
import os
import threading
import tkinter as tk
import json
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'port': '3306',
    'database': 'bdusuarios1'
}

dataPath = 'C:\\Unal\\Data'
pathxml = "C:\\Unal\\haarcascade_frontalface_default.xml"

imagePaths = os.listdir(dataPath)
face_recognizer = cv2.face.FisherFaceRecognizer_create()
face_recognizer.read('3.xml')

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
faceClassif = cv2.CascadeClassifier(pathxml)

attendance_counter = {name: 0 for name in imagePaths}
recognized_people = set()
running = False

def load_attendance():
    if os.path.exists('attendance.json'):
        with open('attendance.json', 'r') as f:
            return json.load(f)
    return {name: 0 for name in imagePaths}

def save_attendance():
    with open('attendance.json', 'w') as f:
        json.dump(attendance_counter, f)

def get_user_id_by_name(name):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = "SELECT id FROM usuarios WHERE nombres = %s"
        cursor.execute(sql, (name,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def register_attendance_in_db(user_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        now = datetime.now()
        sql = "INSERT INTO asistencia (user_id, fecha) VALUES (%s, %s)"
        values = (user_id, now.strftime('%Y-%m-%d %H:%M:%S'))
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        message = f"Asistencia registrada para user_id {user_id} a las {now.strftime('%Y-%m-%d %H:%M:%S')}"
        print(message)
        attendance_message_label.config(text=message)
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def update_frame():
    global recognized_people, running
    if running:
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceClassif.detectMultiScale(gray, 1.1, 5)

            for (x, y, w, h) in faces:
                rostro = cv2.resize(gray[y:y + h, x:x + w], (150, 150), interpolation=cv2.INTER_CUBIC)
                result = face_recognizer.predict(rostro)

                if result[1] < 550:
                    person_name = imagePaths[result[0]]
                    user_id = get_user_id_by_name(person_name)

                    if user_id and person_name not in recognized_people:
                        attendance_counter[person_name] += 1
                        recognized_people.add(person_name)
                        register_attendance_in_db(user_id)

                    cv2.putText(frame, person_name, (x, y - 25), 2, 1.1, (0, 255, 0), 1, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                else:
                    cv2.putText(frame, 'Desconocido', (x, y - 20), 2, 0.8, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # Convertir el marco a imagen y mostrarlo en Tkinter
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.configure(image=imgtk)

        video_label.after(10, update_frame)

def start_video_capture():
    global running
    running = True
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    attendance_button.config(state=tk.DISABLED)
    video_label.pack()  # Mostrar el video
    update_frame()

def stop_video_capture():
    global running
    running = False
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    attendance_button.config(state=tk.NORMAL)
    video_label.pack_forget()  # Ocultar el video

def show_attendance():
    attendance_text = "Contador de Asistencia:\n"
    for name, count in attendance_counter.items():
        attendance_text += f"{name}: {count}\n"
    attendance_label.config(text=attendance_text)

def close_app():
    stop_video_capture()
    root.quit()

attendance_counter = load_attendance()

root = tk.Tk()
root.title("Rostros")
root.geometry("1280x720")

# Cargar imagen de fondo
bg_image = Image.open("C:/Unal/Temas/Difrostros.png")
bg_image = bg_image.resize((1280, 720), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

# Etiqueta para la imagen de fondo
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Etiqueta para mostrar el video
video_label = tk.Label(root)
video_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Centrar el video
video_label.config(width=640, height=480)  # Ajustar el tamaño del video

# Crear botones
attendance_message_label = tk.Label(root, text="", bg='white', font=('Arial', 12), justify=tk.LEFT)
attendance_message_label.pack(pady=10)

start_button = tk.Button(root, text="Iniciar Captura", command=start_video_capture)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Detener Captura", command=stop_video_capture, state=tk.DISABLED)
stop_button.pack(pady=10)

attendance_button = tk.Button(root, text="Mostrar Asistencia", command=show_attendance)
attendance_button.pack(pady=10)

close_button = tk.Button(root, text="Cerrar", command=close_app)
close_button.pack(pady=10)

attendance_label = tk.Label(root, text="", justify=tk.LEFT)
attendance_label.pack(pady=10)

root.mainloop()
