from flask import Flask, render_template, Response
import sys
import argparse
import datetime
import imutils
import time
import cv2
import numpy
import pygame
import pygame.camera
from pygame.locals import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    i=1
    while i<10:
        yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+str(i)+b'\r\n')
        i+=1

def get_frame():

    #camera_port=0

    #ramp_frames=100

    ap = argparse.ArgumentParser() # построить анализатор аргументов и разобрать аргументы
    #ap.add_argument("-v", "--video", help="C:\\Users\\vad10\\Desktop\\dev\\python\\basic-motion-detection\\videos\example_01.mp4")
    ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
    args = vars(ap.parse_args())

    text = "Unoccupied"
    cap=cv2.VideoCapture(0) #this makes a web cam object

    retval, frame = cap.read() # захват текущего кадра

    #pygame.init()
    #pygame.camera.init()

    #cam = pygame.camera.Camera("/dev/video0",(640,480))
    #cam.start()

    #frame = cam.get_image()

    frame = imutils.resize(frame, width=500) # изменяем размер кадра
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # делаем кадр серым 
    gray = cv2.GaussianBlur(gray, (21, 21), 0) # размазываем его

    firstFrame = None

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480))

    #camera=cv2.VideoCapture(1) #this makes a web cam object
    

    i=1
    while True:
        #retval, im = camera.read()
        ##################

        firstFrame = gray

        retval, frame = cap.read() # захват текущего кадра

        #frame = cam.get_image()

        #if frame is None: # если что-то пошло не так заканчиваем цикл
        #    break

        frameForWrite = cv2.flip(frame,180)

        frame = imutils.resize(frame, width=500) # изменяем размер кадра
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # делаем кадр серым 
        gray = cv2.GaussianBlur(gray, (21, 21), 0) # размазываем его

        #if firstFrame is None: # повторная инициализация первого кадра
        #    firstFrame = gray
        #    continue

        frameDelta = cv2.absdiff(firstFrame, gray) # вычисляем абсолютную разницу между текущим кадром и первым
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # расширяем изображение и ищем контуры на нем
        #thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

    

        if len(cnts) > 0:
            out.write(frameForWrite)
    
    
    
        #print (len(cnts))
        ########print(datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"))
        for c in cnts: # зацикляем контуры
            if cv2.contourArea(c) < args["min_area"]: # вычислям ограничивающий прямоугольник
                continue

            # рисуем прямоугольник
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if len(cnts) > 0:
            text = "Occupied"
        else:
            text = "Unoccupied"

        # рисуем текст и время на кадре
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    

        ############


        imgencode=cv2.imencode('.jpg',frame)[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
        i+=1

    del(cap)

@app.route('/calc')
def calc():
     return Response(get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
