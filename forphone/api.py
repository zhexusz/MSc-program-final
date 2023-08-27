# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 13:24:40 2023

@author: zhexu
"""

from flask import Flask, request, jsonify
import json

import time
import cv2

import numpy as np
from PIL import Image
from yolo import YOLO

import Obstacle_avoidance as ob
import Image_comparison as im

yolo = YOLO()

destination = "dest/test.jpg"

capture = cv2.VideoCapture(0)
if not capture.isOpened():
    print("Camera not found or cannot be opened.")
    capture.release()
    exit()

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Test succeess.'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(data)
    username = data.get('username')
    password = data.get('password')

    if username == "qwe" and password == "asd":
        response = {"success": True, "message": "Login successful"}
    else:
        response = {"success": False, "message": "Invalid credentials"}

    return jsonify(response)

@app.route('/send', methods=['POST'])
def receive_message():
    data = request.form.get('message')
    
    if data == 'start':
        print('Received "start" message')
        return 'Message received successfully', 200
    else:
        return 'Invalid message', 400

@app.route('/get', methods=['POST'])
def receive_get():
    data = request.form.get('message')
    place = []
    if data == 'get':
        print('Received "get" message')
        

        
        fps = 0.0

        t1 = time.time()
        for i in range(2):
            ref, frame = capture.read() # capture = cv2.VideoCapture(0)
        
        scale_up_x = 1
        scale_up_y = 1
        scaled_f_up = cv2.resize(frame, None, fx = scale_up_x, fy = scale_up_y, interpolation = cv2.INTER_LINEAR)
        scaled_f_up = cv2.cvtColor(scaled_f_up,cv2.COLOR_BGR2RGB)
        scaled_f_up = Image.fromarray(np.uint8(scaled_f_up))
        scaled_f_up, predicted_classes, place= yolo.detect_image(scaled_f_up, capture.get(cv2.CAP_PROP_FOCUS), )  # 数据在后三个变量中
        scaled_f_up = np.array(scaled_f_up)
        scaled_f_up = cv2.cvtColor(scaled_f_up, cv2.COLOR_RGB2BGR)
        fps = (fps + (1. / (time.time() - t1))) / 2
        print("fps = %.2f" % fps)
        scaled_f_up = cv2.putText(scaled_f_up, "fps = %.2f" % fps, (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        arrive = im.compare(scaled_f_up, destination)
        
        # capture.release()
        # cv2.destroyAllWindows()
        print(predicted_classes)
        response_data = {
        "arrive": arrive,
        "predicted_classes": predicted_classes,  
        "place": place,
        }

        json_response = json.dumps(response_data)

        return json_response, 200
    else:
        return 'Invalid message', 400

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0')



