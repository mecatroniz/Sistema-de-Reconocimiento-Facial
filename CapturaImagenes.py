import cv2
import os
import imutils
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk  # Importar PIL para manejar imágenes
import time

# Ruta al clasificador en cascada de Haar
pathxml = "C:\\Unal\\haarcascade_frontalface_default.xml"

class FaceCaptureApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Captura de Rostros")

        # Cargar la imagen de fondo
        self.bg_image = Image.open("C:/Unal/Temas/fondo.png")
        self.bg_image = self.bg_image.resize((1280, 720), Image.LANCZOS)  # Ajustar el tamaño
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Crear un Label para la imagen de fondo
        self.bg_label = tk.Label(master, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Colocar el Label en toda la ventana

        self.label = tk.Label(master, text="Ingrese su Nombre-Documento:", bg='white')  # Fondo blanco para el texto
        self.label.pack(pady=10)

        self.entry = tk.Entry(master)
        self.entry.pack(pady=10)

        self.video_button = tk.Button(master, text="Seleccionar Video", command=self.select_video)
        self.video_button.pack(pady=10)

        self.start_button = tk.Button(master, text="Iniciar Grabación", command=self.start_capture)
        self.start_button.pack(pady=10)

        self.quit_button = tk.Button(master, text="Salir", command=master.quit)
        self.quit_button.pack(pady=10)

        self.cap = None
        self.faceClassif = None
        self.count = 0
        self.personPath = ""
        self.is_paused = False
        self.start_time = None
        self.recording = False
        self.out = None
        self.video_path = None  # Variable para almacenar la ruta del video

    def select_video(self):
        self.video_path = filedialog.askopenfilename(title="Seleccionar Video", 
                                                      filetypes=[("Archivos de video", "*.mp4;*.avi;*.mov")])
        if self.video_path:
            messagebox.showinfo("Información", "Video seleccionado: " + self.video_path)

    def start_capture(self):
        personName = self.entry.get()
        if not personName:
            messagebox.showwarning("Advertencia", "Por favor ingrese un documento.")
            return
        
        dataPath = 'C:\\Unal\\Data'  # Cambia a la ruta donde hayas almacenado Data
        self.personPath = os.path.join(dataPath, personName)

        # Crear la carpeta para almacenar imágenes si no existe
        if not os.path.exists(self.personPath):
            os.makedirs(self.personPath)

        # Captura de video desde la cámara o archivo
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
        else:
            self.cap = cv2.VideoCapture(0)  # Cambia a 0 para usar la cámara en vivo

        self.faceClassif = cv2.CascadeClassifier(pathxml)
        self.start_time = time.time()
        self.recording = True
        self.count = 0
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(os.path.join(self.personPath, 'grabacion.avi'), fourcc, 20.0, (640, 480))

        self.create_capture_window()

    def create_capture_window(self):
        # Crear una ventana de captura
        self.capture_window = tk.Toplevel(self.master)
        self.capture_window.title("Captura de Rostros")
        
        self.pause_button = tk.Button(self.capture_window, text="Pausar Grabación", command=self.pause_capture, state=tk.NORMAL)
        self.pause_button.pack(pady=10)

        self.resume_button = tk.Button(self.capture_window, text="Reanudar Grabación", command=self.resume_capture, state=tk.DISABLED)
        self.resume_button.pack(pady=10)

        self.stop_button = tk.Button(self.capture_window, text="Detener Grabación", command=self.stop_capture, state=tk.NORMAL)
        self.stop_button.pack(pady=10)

        self.capture_faces()

    def capture_faces(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Redimensionar el marco
            frame = imutils.resize(frame, width=640)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            auxFrame = frame.copy()

            # Detección de rostros
            faces = self.faceClassif.detectMultiScale(gray, 1.1, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                rostro = auxFrame[y:y + h, x:x + w]
                rostro = cv2.resize(rostro, (150, 150), interpolation=cv2.INTER_CUBIC)
                cv2.imwrite(os.path.join(self.personPath, f'rostro_{self.count}.jpg'), rostro)  # Guardar imagen
                self.count += 1

            # Mostrar el tiempo transcurrido
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            timer_text = f'Tiempo: {minutes:02}:{seconds:02}'
            cv2.putText(frame, timer_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            # Mostrar el marco con detección de rostros
            cv2.imshow('frame', frame)

            # Guardar el frame en el video de salida
            if self.recording:
                self.out.write(frame)

            # Detener después de 60 segundos
            if elapsed_time > 60:
                break

            k = cv2.waitKey(1)
            if k == 27:  # Presionar 'ESC' para detener la grabación
                break
            if self.is_paused:
                cv2.waitKey(-1)  # Esperar hasta que se reanude

        # Liberar recursos
        self.out.release()
        self.cap.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Información", f"Captura finalizada. Se guardaron {self.count} imágenes.")
        self.capture_window.destroy()

    def pause_capture(self):
        self.is_paused = True
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)

    def resume_capture(self):
        self.is_paused = False
        self.resume_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)

    def stop_capture(self):
        self.recording = False
        self.is_paused = False
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.DISABLED)

        if self.cap is not None:
            self.cap.release()
        if self.out is not None:
            self.out.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Información", "Grabación detenida y guardada.")
        self.capture_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceCaptureApp(root)
    root.mainloop()
