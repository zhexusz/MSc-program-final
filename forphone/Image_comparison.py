# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 10:22:50 2023

@author: zhexu
"""

import cv2

def aHash(img,shape=(10,10)):
    img = cv2.resize(img, shape)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    s = 0
    hash_str = ''
    for i in range(shape[0]):
        for j in range(shape[1]):
            s = s + gray[i, j]
    avg = s / 100
    for i in range(shape[0]):
        for j in range(shape[1]):
            if gray[i, j] > avg:
                hash_str = hash_str + '1'
            else:
                hash_str = hash_str + '0'
    return hash_str

def cmpHash(hash1, hash2,shape=(10,10)):
    n = 0
    if len(hash1)!=len(hash2):
        return -1
    for i in range(len(hash1)):
        if hash1[i] == hash2[i]:
            n = n + 1
    return n/(shape[0]*shape[1])

def compare(img1, img2):
    hash1 = aHash(img1)
    hash2 = aHash(cv2.imread(img2))
    n = cmpHash(hash1, hash2)
    if n >= 0.77:
        print("We have arrived at distnation.")
        return True
    if n < 0.77:
        return False






