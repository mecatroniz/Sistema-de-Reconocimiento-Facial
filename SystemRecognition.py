
# libraries
import cv2
import face_recognition as fr
import numpy as np
import mediapipe as mp
import os
from tkinter import *
from PIL import Image, ImageTk
import imutil
import math




# Objeto de detección de rostros
FaceObject = mp.solutions.face_detection
detector = FaceObject.FaceDetection(min_detection_confidence=0.5, model_selection=1)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Definir el umbral de confianza =Threshold
confThreshold = 0.5

# Offsety
offsety = 40
offsetx = 20

#Profile
def Profile():
    global step, conteo, UserName, OutFolderPathUser

    #Reset variables
    step = 0
    conteo = 0

    # Load Background Image
    imagenbc = PhotoImage(file="C:/Unal/SepUp/Back2.png")

    # Window
    pantalla4 = Toplevel(pantalla)
    pantalla4.title("PROFILE")
    pantalla4.geometry("1280x720")

    # Set Background
    bg_label = Label(pantalla4, image=imagenbc)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # File
    UserFile = open(F"{OutFolderPathUser}/{UserName}.txt","r")
    InfoUser = UserFile.read().split(',')
    Name =  InfoUser[0]
    User = InfoUser[1]
    #Pass = InfoUser[3]

    #Check User
    if User in clases:
        # Interfaz
        texto1 = Label(pantalla4, text= f"Bienvenido {Name}", bg="white", fg="black")
        texto1.place(x= 580, y=50)

        #Label IMG
        lblimage = Label(pantalla4, bg="white")
        lblimage.place(x=490, y=80)

        #Imagen
        ImgUser = cv2.imread(f"{OutFolderPathFace}/{User}.png")
        ImgUser = cv2.cvtColor(ImgUser, cv2.COLOR_BGR2RGB)
        ImgUser = Image.fromarray(ImgUser)
        ImgUser = ImageTk.PhotoImage(ImgUser)

        lblimage.configure(image=ImgUser)
        lblimage.image = ImgUser

    pantalla4.mainloop()


# Close Windows Funtion
def Close_window():
    global step, conteo

    # Reset
    conteo = 0
    step = 0
    pantalla2.destroy()

def Close_window2():
    global step, conteo

    # Reset
    conteo = 0
    step = 0
    pantalla3.destroy()

#Code Faces Funtion
def Code_Face(images):
    listcod = []
    for img in images:
        # Color
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Img Code
        face_encodings = fr.face_encodings(img)
        if face_encodings:
            cod = face_encodings[0]
            listcod.append(cod)
        else:
            print(f"No se encontró ningún rostro en la imagen.")
    return listcod

# Sig Up Biometric Function
def Sign_Biometric():
    global LogUser,LogPass, OutFolderPathFace, cap, lblVideo, pantalla3, FaceCode, clases, images, step, parpadeo, conteo, UserName

    # Chequea si la cámara está abierta
    if cap is not None:
        ret, frame = cap.read()

        frameSave = frame.copy()

        # Invertir horizontalmente la imagen
        frame = cv2.flip(frame, 1)
        # Redimensiona el frame
        frame = cv2.resize(frame, (440, 370))

        # Convertir el frame a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


        # Detectar los rostros y obtener la malla facial
        results = face_mesh.process(frame_rgb)

        px = []
        py = []
        lista = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Dibujar la malla facial en el frame
                mp_drawing = mp.solutions.drawing_utils
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(220, 220, 220), thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(220, 220, 220), thickness=1)

                )

                # Extract KeyPoint
                for id, puntos in enumerate(face_landmarks.landmark):
                    # Info img
                    al, an, c = frame.shape
                    x, y = int(puntos.x * an), int(puntos.y * al)
                    px.append(x)
                    py.append(y)
                    lista.append([id, x, y])

                # 468 KeyPoints
                if len(lista) == 478:
                    # Ojo derecho
                    x1, y1 = lista[145][1:]
                    x2, y2 = lista[159][1:]
                    longitud1 = math.hypot(x2 - x1, y2 - y1)

                    # Ojo Izquierdo
                    x3, y3 = lista[374][1:]
                    x4, y4 = lista[386][1:]
                    longitud2 = math.hypot(x4 - x3, y4 - y3)

                    # Parietal Derecho
                    x5, y5 = lista[139][1:]
                    # Parietal Izquierdo
                    x6, y6 = lista[368][1:]

                    # Ceja Derecha
                    x7, y7 = lista[70][1:]
                    x8, y8 = lista[300][1:]


                    # Círculo x1, y1 x2, y2
                    cv2.circle(frame, (x1, y1), 2, (255, 255, 0), cv2.FILLED)
                    cv2.circle(frame, (x2, y2), 2, (255, 255, 0), cv2.FILLED)


                    # Círculo x3, y3 x4, y4
                    cv2.circle(frame, (x3, y3), 2, (255, 255, 0), cv2.FILLED)
                    cv2.circle(frame, (x4, y4), 2, (255, 255, 0), cv2.FILLED)


                    cv2.circle(frame, (x5, y5), 2, (255, 255, 0), cv2.FILLED)
                    cv2.circle(frame, (x6, y6), 2, (255, 255, 0), cv2.FILLED)

                    cv2.circle(frame, (x7, y7), 2, (255, 255, 0), cv2.FILLED)
                    cv2.circle(frame, (x8, y8), 2, (255, 255, 0), cv2.FILLED)
                    # Detección de rostros
                    faces = detector.process(frame_rgb)

                    if faces.detections is not None:
                        for face in faces.detections:
                            # Bbox: "ID, BBOX, SCORE"
                            score = face.score
                            score = score[0]
                            bbox = face.location_data.relative_bounding_box

                            # Umbral
                            if score > confThreshold:

                                # Píxeles
                                xi, yi, anc, alt = bbox.xmin, bbox.ymin, bbox.width, bbox.height
                                xi, yi, anc, alt = int(xi * an), int(yi * al), int(anc * an), int(alt * al)

                                #Offset x
                                offsetan = (offsetx / 100) * anc
                                xi = int(xi - int(offsetan/2))
                                anc = int(anc + offsetan)
                                xf = xi + anc

                                # Offset x
                                offsetal = (offsety / 100) * alt
                                yi = int(yi - offsetal)
                                alt = int(alt + offsetal)
                                yf = yi + alt

                                # Error
                                if xi < 0: xi = 0
                                if yi < 0: yi = 0
                                if anc < 0: anc = 0
                                if alt < 0: alt = 0

                                # Step
                                if step == 0:
                                    # Dibujar
                                    cv2.rectangle(frame, (xi, yi, anc, alt), (255, 255, 60), 2)

                                    # IMG Step0
                                    als0, ans0, c = img_step0.shape
                                    frame[230:230 + als0, 0:0 + ans0] = img_step0
                                    # IMG Step1
                                    als1, ans1, c = img_step1.shape
                                    frame[30:30 + als1, 310:310 + ans1] = img_step1
                                    # IMG Step2
                                    als2, ans2, c = img_step2.shape
                                    frame[230:230 + als2, 310:310 + ans2] = img_step2

                                    # Face Center
                                    if x7 > x5 and x8 < x6:
                                        #IMG Check
                                        alch, anch, c = img_check.shape
                                        frame[100:100 + alch, 320:320 + anch] = img_check

                                        #Cont parpadeo
                                        if longitud1 <= 10 and longitud2 <= 10 and parpadeo == False:
                                            conteo = conteo + 1
                                            parpadeo = True

                                        elif longitud1 > 10 and longitud2 > 10 and parpadeo == True:
                                            parpadeo = False

                                        cv2.putText(frame, f'parpadeos: {int(conteo)}', (333,270), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                                        #Cond
                                        if conteo >= 3:
                                            alch, anch, c = img_check.shape
                                            frame[320:320 + alch, 290:290 + anch] = img_check

                                            #Open Eyes
                                            if longitud1 > 15 and longitud2 >15:


                                                #Step 1
                                                step = 1

                                    else:
                                            conteo = 0

                                if step == 1:
                                    # Dibujar
                                    cv2.rectangle(frame, (xi, yi, anc, alt), (0, 255, 0), 2)
                                    # IMG Check Liveness
                                    alli, anli, c = img_liche.shape
                                    frame[50:50 + alli, 50:50 + anli] = img_liche

                                    #Find Faces
                                    facess = fr.face_locations(frame_rgb)
                                    facescod = fr.face_encodings(frame_rgb, facess)

                                    #iteramos
                                    for facecod,facesloc in zip(facescod,facess):

                                        #Matching
                                        Match = fr.compare_faces(FaceCode, facecod)

                                        # Sim
                                        simi = fr.face_distance(FaceCode, facecod)

                                        # Min
                                        min = np.argmin(simi)

                                        if Match[min]:
                                            #UserName
                                            UserName = clases[min].upper()

                                            Profile()


                            # close = pantalla2.protocool("WM_DELETE_WINDOW", Close_window()) def Close_window():
                            close = pantalla3.protocol("WM_DELETE_WINDOW", Close_window2)





        # Convierte el frame a una imagen de Tkinter
        im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = ImageTk.PhotoImage(image=im)
        frameSave = im.copy()


        # Muestra el vide
        lblVideo.configure(image=img)
        lblVideo.image = img
        lblVideo.after(10, Sign_Biometric)
    else:
        # Si la cámara no está abierta, ciérrala
        cap.release()



def Log_Biometric():
    global pantalla2, conteo, parpadeo, img_info, step, cap, lblVideo, px, py, lista, RegUser

    # Chequea si la cámara está abierta
    if cap is not None:
        ret, frame = cap.read()

        frameSave = frame.copy()

        # Invertir horizontalmente la imagen
        frame = cv2.flip(frame, 1)
        # Redimensiona el frame
        frame = cv2.resize(frame, (1280, 720))

        # Convertir el frame a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


        # Detectar los rostros y obtener la malla facial
        results = face_mesh.process(frame_rgb)

        px = []
        py = []
        lista = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Dibujar la malla facial en el frame
                mp_drawing = mp.solutions.drawing_utils
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=1),
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)
                )

                # Extract KeyPoint
                for id, puntos in enumerate(face_landmarks.landmark):
                    # Info img
                    al, an, c = frame.shape
                    x, y = int(puntos.x * an), int(puntos.y * al)
                    px.append(x)
                    py.append(y)
                    lista.append([id, x, y])

                # 468 KeyPoints
                if len(lista) == 478:
                    # Ojo derecho
                    x1, y1 = lista[145][1:]
                    x2, y2 = lista[159][1:]
                    longitud1 = math.hypot(x2 - x1, y2 - y1)

                    # Ojo Izquierdo
                    x3, y3 = lista[374][1:]
                    x4, y4 = lista[386][1:]
                    longitud2 = math.hypot(x4 - x3, y4 - y3)

                    # Parietal Derecho
                    x5, y5 = lista[139][1:]
                    # Parietal Izquierdo
                    x6, y6 = lista[368][1:]

                    # Ceja Derecha
                    x7, y7 = lista[70][1:]
                    x8, y8 = lista[300][1:]


                    # Círculo x1, y1 x2, y2
                    cv2.circle(frame, (x1, y1), 2, (255, 255, 0), cv2.FILLED)
                    cv2.circle(frame, (x2, y2), 2, (255, 255, 0), cv2.FILLED)


                    # Círculo x3, y3 x4, y4
                    cv2.circle(frame, (x3, y3), 2, (255, 255, 0), cv2.FILLED)
                    cv2.circle(frame, (x4, y4), 2, (255, 255, 0), cv2.FILLED)


                    cv2.circle(frame, (x5, y5), 2, (255, 255, 0), cv2.FILLED)
                    cv2.circle(frame, (x6, y6), 2, (255, 255, 0), cv2.FILLED)

                    cv2.circle(frame, (x7, y7), 2, (255, 255, 0), cv2.FILLED)
                    cv2.circle(frame, (x8, y8), 2, (255, 255, 0), cv2.FILLED)
                    # Detección de rostros
                    faces = detector.process(frame_rgb)

                    if faces.detections is not None:
                        for face in faces.detections:
                            # Bbox: "ID, BBOX, SCORE"
                            score = face.score
                            score = score[0]
                            bbox = face.location_data.relative_bounding_box

                            # Umbral
                            if score > confThreshold:

                                # Píxeles
                                xi, yi, anc, alt = bbox.xmin, bbox.ymin, bbox.width, bbox.height
                                xi, yi, anc, alt = int(xi * an), int(yi * al), int(anc * an), int(alt * al)

                                #Offset x
                                offsetan = (offsetx / 100) * anc
                                xi = int(xi - int(offsetan/2))
                                anc = int(anc + offsetan)
                                xf = xi + anc

                                # Offset x
                                offsetal = (offsety / 100) * alt
                                yi = int(yi - offsetal)
                                alt = int(alt + offsetal)
                                yf = yi + alt

                                # Error
                                if xi < 0: xi = 0
                                if yi < 0: yi = 0
                                if anc < 0: anc = 0
                                if alt < 0: alt = 0

                                # Step
                                if step == 0:
                                    # Dibujar
                                    cv2.rectangle(frame, (xi, yi, anc, alt), (255, 255, 60), 2)

                                    # IMG Step0
                                    als0, ans0, c = img_step0.shape
                                    frame[50:50 + als0, 50:50 + ans0] = img_step0
                                    # IMG Step1
                                    als1, ans1, c = img_step1.shape
                                    frame[50:50 + als1, 1030:1030 + ans1] = img_step1
                                    # IMG Step2
                                    als2, ans2, c = img_step2.shape
                                    frame[250:250 + als2, 1030:1030 + ans2] = img_step2

                                    # Face Center
                                    if x7 > x5 and x8 < x6:
                                        #IMG Check
                                        alch, anch, c = img_check.shape
                                        frame[165:165 + alch, 1105:1105 + anch] = img_check

                                        #Cont parpadeo
                                        if longitud1 <= 10 and longitud2 <= 10 and parpadeo == False:
                                            conteo = conteo + 1
                                            parpadeo = True

                                        elif longitud1 > 10 and longitud2 > 10 and parpadeo == True:
                                            parpadeo = False

                                        cv2.putText(frame, f'parpadeos: {int(conteo)}', (1070,375), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                                        #Cond
                                        if conteo >= 3:
                                            alch, anch, c = img_check.shape
                                            frame[385:385 + alch, 1105:1105 + anch] = img_check

                                            #Open Eyes
                                            if longitud1 > 15 and longitud2 >15:
                                                #Cut
                                                cut = frameSave[yi:yf, xi:xf]

                                                # Save Face
                                                cv2.imwrite(f"{OutFolderPathFace}/{RegUser}.png", cut)

                                                #Step 1
                                                step = 1

                                    else:
                                            conteo = 0

                                if step ==1:
                                    # Dibujar
                                    cv2.rectangle(frame, (xi, yi, anc, alt), (0, 255, 0), 2)
                                    # IMG Check Liveness
                                    alli, anli, c = img_liche.shape
                                    frame[50:50 + alli, 50:50 + anli] = img_liche
                            # close = pantalla2.protocool("WM_DELETE_WINDOW", Close_window()) def Close_window():
                            close = pantalla2.protocol("WM_DELETE_WINDOW", Close_window)





        # Convierte el frame a una imagen de Tkinter
        im = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = ImageTk.PhotoImage(image=im)
        frameSave = im.copy()


        # Muestra el vide
        lblVideo.configure(image=img)
        lblVideo.image = img
        lblVideo.after(10, Log_Biometric)
    else:
        # Si la cámara no está abierta, ciérrala
        cap.release()

def Log():
    global RegName, RegUser, RegPass, InputNameReg, InputUserReg, InputPassReg, cap, lblVideo, pantalla2

    # Extract: Name - user -PassWord
    RegName = InputNameReg.get()
    RegUser = InputUserReg.get()
    RegPass = InputPassReg.get()

    # Incompleted Form
    if len(RegName) == 0 or len(RegUser) == 0 or len(RegPass) == 0:
        # Print Error
        print("FORMULARIO INCOMPLETO")
    # Completed Form
    else:
        # Check Users
        UserList = os.listdir(PathUserCheck)
        print(UserList)

        # Name Users
        UserName = []

        # Check user list
        for lis in UserList:
            # Extract user
            User = lis.split('.')[0]
            # Save User
            UserName.append(User)

        # Check User
        if RegUser in UserName:
            # Registered
            print("USUARIO REGISTRADO ANTERIORMENTE")
        else:
            # No Registered
            # Save Info
            info.append(RegName)
            info.append(RegUser)
            info.append(RegPass)

            # Export Info
            with open(f"{OutFolderPathUser}/{RegUser}.txt", "w") as f:
                f.write(f"{RegName},{RegUser},{RegPass}")

            # Clean
            InputNameReg.delete(0, END)
            InputUserReg.delete(0, END)
            InputUserReg.delete(0, END)

            # New Screen
            pantalla2 = Toplevel(pantalla)
            pantalla2.title("Login Biometric")
            pantalla2.geometry("1280x720")

            # Label video
            lblVideo = Label(pantalla2)
            lblVideo.place(x=0, y=0)

            # VideoCapture
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            cap.set(3, 2280)
            cap.set(4, 720)
            Log_Biometric()


# Funtion Sign
def Sign():
    global LogUser,LogPass, OutFolderPathFace, cap, lblVideo, pantalla3, FaceCode, clases, images,bg_image 
    
    #Extrac: Name, User, PassWord
    LogUser, LogPass = InputUserLog.get(), InputPassLog.get()

    #DB Faces
    images = []
    clases = []
    lista = os.listdir(OutFolderPathFace)

    #read Face Images
    for lis in lista:
        #Read Img
        imgdb = cv2.imread(f"{OutFolderPathFace}/{lis}")
        #Save Img Db
        images.append(imgdb)
        # Name Img
        clases.append(os.path.splitext(lis)[0])

    # FaceCode
    FaceCode = Code_Face(images)

    # Window
    pantalla3 = Toplevel(pantalla)
    pantalla3.title("BIOMETRIC SIGN UP")
    pantalla3.geometry("1280x700")

    # Establecer una imagen de fondo
    bg_image = PhotoImage(file="C:/Unal/SepUp/fondo.png")
    bg_label = Label(pantalla3, image=bg_image)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)


    # Label video

    lblVideo = Label(pantalla3)
    lblVideo.place(x=215, y=72)

    # VideoCapture
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, 2280)
    cap.set(4, 720)
    Sign_Biometric()





    

# Funtion long

#Path
OutFolderPathUser = 'C:/Unal/DateBase/Users'
PathUserCheck = 'C:/Unal/DateBase/Users'
OutFolderPathFace = 'C:/Unal/DateBase/Faces'

# Variables
parpadeo = False
conteo = 0
muestra = 0
step = 0

# Read img
img_info = cv2.imread("C:/Unal/SepUp/Back2.png")
img_check = cv2.imread("C:/Unal/SepUp/check.png")
img_step0 = cv2.imread("C:/Unal/SepUp/Step0.png")
img_step1 = cv2.imread("C:/Unal/SepUp/Step1.png")
img_step2 = cv2.imread("C:/Unal/SepUp/Step2.png")
img_liche = cv2.imread("C:/Unal/SepUp/LivenessCheck.png")


# info List
info = []

# ventana principal
pantalla = Tk()
pantalla.title("FACE RECOGNITION SYSTEM")
pantalla.geometry("1259x720")


# Fondo
imageF = PhotoImage(file="C:/Unal/SepUp/Inicio.png")
background = Label(image=imageF, text= "Inicio")
background.place(x=0, y=0, relheight=1, relwidth=1)

imagenbc = PhotoImage(file="C:/Unal/SepUp/Back2.png")

# Input Text Long
# Name
InputNameReg = Entry(pantalla)
InputNameReg.place(x=110, y=225)

#User
InputUserReg = Entry(pantalla)
InputUserReg.place(x=110, y=347)

#Pass
InputPassReg = Entry(pantalla)
InputPassReg.place(x=110, y=477)

# Input Text Sign uP
# User
InputUserLog = Entry(pantalla)
InputUserLog.place()

#Pass
InputPassLog = Entry(pantalla)
InputPassLog.place()

# Button
# Log
imageBR = PhotoImage(file="C:/Unal/SepUp/BtLogin.png")
BtReg = Button(pantalla, text="Registro", image=imageBR, height="60",width="270", command=Log)
BtReg.place(x=80, y= 560)
# Sig
imageBL = PhotoImage(file="C:/Unal/SepUp/BtSign.png")
BtSign = Button(pantalla, text="Registro", image=imageBL, height="60",width="270", command=Sign)
BtSign.place(x=598, y= 560)

pantalla.mainloop()
