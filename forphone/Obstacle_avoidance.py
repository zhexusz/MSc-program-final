import cv2
import numpy as np  
    
def avoidance(top, left, bottom, right, image, focus, distance):
    image = np.array(image)
    # RGBtoBGR满足opencv显示格式
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    focus = 100
    actual_distance = 1
    actual_high = 1
    pixel = int(focus * actual_high / actual_distance)
    # 焦距focus =（pixel_high * actual_distance）/ actual_high
    hight = image.shape[0]
    width = image.shape[1]    
    

    cy = (top+bottom)/2
    cx = (left+right)/2
    
    count = 0
    flag = False
    place = []
    
    if distance < 6:
    
        if cx > pixel and cx < (width - pixel) and cy > pixel and cy < (hight - pixel):
            if top < pixel:
                count += 1
            if bottom > (hight - pixel):
                count += 1
            if left < (pixel):
                count += 1
            if right > (width - pixel):
                count += 1
            if count >= 1:
                flag = True
                place.append("ahead")
#            if count < 2:
#                flag = True
#                place.append("ahead")
        
        if cx < pixel:
            if top < pixel:
                count += 1
            if bottom > (hight - pixel):
                count += 1
            if right > (pixel):
                count += 1
            if count >= 2:
                flag = True
                place.append("left")
#            if count < 2:
#                flag = True
#                place.append("left")
                
        if cx > (width - pixel):
            if top < pixel:
                count += 1
            if bottom > (hight - pixel):
                count += 1
            if left < (width - pixel):
                count += 1
            if count >= 2:
                flag = True
                place.append("right")
#            if count < 2:
#                flag = True
#                place.append("right")
                
        if cy < (pixel):
            if right > (width - pixel):
                count += 1
            if bottom > (pixel):
                count += 1
            if left < (pixel):
                count += 1
            if count >= 2:
                flag = True
                place.append("top")
#            if count < 2:
#                flag = True
#                place.append("top")
    
        if cy > (hight - pixel):
            if top < (hight - pixel):
                count += 1
            if right > (width - pixel):
                count += 1
            if left < (pixel):
                count += 1
            if count >= 2:
                flag = True
                place.append("bottom")
#            if count < 2:
#                flag = True
#                place.append("bottom")
    if flag == False:
        if distance < 3:
            flag = True
            place.append("ahead1")
    return flag, place    