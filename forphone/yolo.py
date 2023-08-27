# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 10:22:50 2023

@author: zhexu
"""

import os
from timeit import default_timer as timer

import numpy as np
import tensorflow as tf
from tensorflow.compat.v1.keras import backend as K
from tensorflow.keras.layers import Input, Lambda
from tensorflow.keras.models import Model

from nets.yolo4_tiny import yolo_body, yolo_eval
from util.utils import letterbox_image

import Obstacle_avoidance as ob


class YOLO(object):
    _defaults = {
        "model_path"        : 'model_data/yolov4_tiny_weights_voc.h5',
        # "model_path"        : 'C:/Users/zhexu/Desktop/program/yolov4-tiny-tf2-master/logs/best_epoch_weights.h5',
        
        "anchors_path"      : 'model_data/yolo_anchors.txt',
        "classes_path"      : 'model_data/voc_classes.txt',
        "score"             : 0.5,
        "iou"               : 0.3,
        "eager"             : True,
        "max_boxes"         : 100,
        "model_image_size"  : (416, 416)
    }
    

    
    
    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        self.class_names = self._get_class()
        self.anchors = self._get_anchors()
        if not self.eager:
            tf.compat.v1.disable_eager_execution()
            self.sess = K.get_session()
        self.generate()

    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def _get_anchors(self):
        anchors_path = os.path.expanduser(self.anchors_path)
        with open(anchors_path) as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        return np.array(anchors).reshape(-1, 2)

    def generate(self):
        model_path = os.path.expanduser(self.model_path)
        assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'
        
        num_anchors = len(self.anchors)
        num_classes = len(self.class_names)

        self.yolo_model = yolo_body(Input(shape=(None,None,3)), num_anchors//2, num_classes)
        self.yolo_model.load_weights(self.model_path)
        print('{} model, anchors, and classes loaded.'.format(model_path))

        if self.eager:
            self.input_image_shape = Input([2,],batch_size=1)

            inputs = [*self.yolo_model.output, self.input_image_shape]
            outputs = Lambda(yolo_eval, output_shape=(1,), name='yolo_eval',
                arguments={'anchors': self.anchors, 'num_classes': len(self.class_names), 'image_shape': self.model_image_size, 
                'score_threshold': self.score, 'eager': True, 'max_boxes': self.max_boxes})(inputs)
            
            self.yolo_model = Model([self.yolo_model.input, self.input_image_shape], outputs)
        else:
            self.input_image_shape = K.placeholder(shape=(2, ))
            
            self.boxes, self.scores, self.classes = yolo_eval(self.yolo_model.output, self.anchors,
                    num_classes, self.input_image_shape, max_boxes=self.max_boxes,
                    score_threshold=self.score, iou_threshold=self.iou)
 
    @tf.function
    def get_pred(self, image_data, input_image_shape):
        out_boxes, out_scores, out_classes = self.yolo_model([image_data, input_image_shape], training=False)
        return out_boxes, out_scores, out_classes

    def detect_image(self, image, focus):
        labels = []
        place = []
        flag = False
        classname = []

        actual_high_car = 1.5
        actual_high_people = 1.7
        actual_high_bike = 1.2

        pixel_high_car = 0
        pixel_high_people = 0
        pixel_high_bike = 0

        focus_car = 970
        #focus_people = 714
        focus_people = 500
        focus_bike = 514
        
        actual_distance = " "

        actual_distance_car = 0
        actual_distance_people = 0
        actual_distance_bike = 0
        
        start = timer()

        new_image_size = (self.model_image_size[1],self.model_image_size[0])
        boxed_image = letterbox_image(image, new_image_size)
        image_data = np.array(boxed_image, dtype='float32')
        image_data /= 255.

        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.

        if self.eager:
            input_image_shape = np.expand_dims(np.array([image.size[1], image.size[0]], dtype='float32'), 0)
            out_boxes, out_scores, out_classes = self.get_pred(image_data, input_image_shape) 
        else:
            out_boxes, out_scores, out_classes = self.sess.run(
                [self.boxes, self.scores, self.classes],
                feed_dict={
                    self.yolo_model.input: image_data,
                    self.input_image_shape: [image.size[1], image.size[0]],
                    K.learning_phase(): 0
                })

        print('Found {} boxes for {}'.format(len(out_boxes), 'img'))


        out_name = [0]*len(out_boxes)
        
        top, left, bottom, right = 0, 0, 0, 0
        for i, c in list(enumerate(out_classes)):
            
            predicted_class = self.class_names[c]
              
            out_name[i] = self.class_names[c]
            box = out_boxes[i]
            score = out_scores[i]
            
            top, left, bottom, right = box
            top = top - 5
            left = left - 5
            bottom = bottom + 5
            right = right + 5
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))

            label = '{} {:.2f}'.format(predicted_class, score)
            label = label.encode('utf-8')
            
            print(label, top, left, bottom, right)

            if "person" in str(label):
                pixel_high_people = bottom - top
                actual_distance_people = (actual_high_people * focus_people) / pixel_high_people
                actual_distance = round(actual_distance_people,1)
                labels.append("person")
                flag, place = ob.avoidance(top, left, bottom, right, image, focus, actual_distance_people)
                print("distance_people:", actual_distance_people)
                

                
            elif "car" in str(label):
                pixel_high_car = bottom - top
                actual_distance_car = (actual_high_car * focus_car) / pixel_high_car
                actual_distance = round(actual_distance_car,1)
                print("distance_car:", actual_distance_car)
                labels.append("car")
                flag, place = ob.avoidance(top, left, bottom, right, image, focus, actual_distance_car)
                
            elif "bicycle" in str(label) or "motorbike" in str(label):
                pixel_high_bike = bottom - top
                actual_distance_bike = (actual_high_bike * focus_bike) / pixel_high_bike
                actual_distance = round(actual_distance_bike,1)
                print("distance_bike:", actual_distance_bike)
                labels.append("bicycle")
                flag, place = ob.avoidance(top, left, bottom, right, image, focus, actual_distance_bike)
            else:
                actual_distance = "null"
                labels.append("null")
            if flag == True:
                if len(place) == 4:
                    print("obstacle is " + str(out_name[i]))
                    print("Obstacles are %s, %s, %s and %s." % (place[0], place[1], place[2], place[3]))
                if len(place) == 3:
                    print("obstacle is " + str(out_name[i]))
                    print("Obstacles are %s, %s and %s." % (place[0], place[1], place[2]))                    
                if len(place) == 2:
                    print("obstacle is " + str(out_name[i]))
                    print("Obstacles are %s and %s." % (place[0], place[1]))
                if len(place) == 1:
                    print("obstacle is " + str(out_name[i]))
                    print("Obstacles are %s." % place[0])
            
            classname.append(predicted_class)
            

        end = timer()
        print(round(end - start),1) 
#        if len(out_boxes) != 0:
#            j = np.argmax(out_scores)
#            predicted_classes = out_name[j]
#        else:
        if len(out_boxes) == 0:  
           #predicted_classes = 'none'
           classname = 'none'
        return image, classname, place

