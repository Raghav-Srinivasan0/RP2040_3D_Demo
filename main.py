import time
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P8
import random
import math

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P8, rotate=360)
display.set_backlight(1.0)
WIDTH, HEIGHT = display.get_bounds()

WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
RED = display.create_pen(255, 0, 0)
BLUE = display.create_pen(0, 0, 255)
ORANGE = display.create_pen(255, 162, 0)

cameraPosition = (0,0,0)
cameraRotation = 0
cameraForward = (0,0,1)
cameraRight = (1,0,0)
cameraUp = (0,1,0)

def moveCamera(offset):
    global cameraPosition
    cameraPosition = (cameraPosition[0]+offset[0],cameraPosition[1]+offset[1],cameraPosition[2]+offset[2])

fov = 90
z_far = 10
z_near = 1
a = WIDTH/HEIGHT
F = math.atan2(fov,2)
q = (z_far)/(z_far-z_near)

print("Width: " + str(WIDTH))
print("Height: " + str(HEIGHT))

def magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def add(u, v):
    return [ u[i]+v[i] for i in range(len(u)) ]

def sub(u, v):
    return [ u[i]-v[i] for i in range(len(u)) ]

def dot(u, v):
    return sum(u[i]*v[i] for i in range(len(u)))

def normalize(v):
    vmag = magnitude(v)
    return [ v[i]/vmag  for i in range(len(v)) ]

def multbyscalar(v,scalar):
    return (v[0]*scalar,v[1]*scalar,v[2]*scalar)

def rotate(point,angle,axis):
    axis = normalize(axis)
    x_f = point[0]*math.cos(angle)+point[0]*axis[0]**2*(1-math.cos(angle))+point[1]*axis[1]*axis[0]*(1-math.cos(angle))+point[1]*axis[2]*math.sin(angle)+point[2]*axis[2]*axis[0]*(1-math.cos(angle))-point[2]*axis[1]*math.sin(angle)
    y_f = point[0]*axis[1]*axis[0]*(1-math.cos(angle))-point[0]*axis[2]*math.sin(angle)+point[1]*math.cos(angle)+point[1]*axis[1]**2*(1-math.cos(angle))+point[2]*axis[1]*axis[2]*(1-math.cos(angle))+point[2]*axis[0]*math.sin(angle)
    z_f = point[0]*axis[0]*axis[2]*(1-math.cos(angle))+point[0]*axis[1]*math.sin(angle)+point[1]*axis[1]*axis[2]*(1-math.cos(angle))-point[1]*axis[0]*math.sin(angle)+point[2]*math.cos(angle)+point[2]*axis[2]**2*(1-math.cos(angle))
    return (x_f,y_f,z_f)

def turnCamera(offset):
    global cameraRotation
    global cameraForward
    global cameraUp
    global cameraRight
    cameraRotation = cameraRotation + offset
    cameraForward = rotate(cameraForward,offset,(0,1,0))
    cameraUp = rotate(cameraUp,offset,(0,1,0))
    cameraRight = rotate(cameraRight,offset,(0,1,0))

def toWindowSpace(point):
    point = rotate(point,cameraRotation,(0,1,0))
    x=point[0]-cameraPosition[0]
    y=point[1]-cameraPosition[1]
    z=point[2]-cameraPosition[2]
    projection_matrix_result = ((a*F*x)/z,(F*y)/z,(z-z_near)*q)
    window_space = ((WIDTH*projection_matrix_result[0])/2+(x+(WIDTH/2)),(HEIGHT*projection_matrix_result[1])/2+(y+(HEIGHT/2)),projection_matrix_result[2])
    return window_space

def drawPoint(point):
    if point[2] < cameraPosition[2]:
        return
    window_space = toWindowSpace(point)
    #print("Point: " + str(round(window_space[0])) + ", " + str(round(window_space[1])))
    display.pixel(round(window_space[0]),round(window_space[1]))

def drawLine(point1,point2):
    window_space1 = toWindowSpace(point1)
    window_space2 = toWindowSpace(point2)
    display.line(round(window_space1[0]),round(window_space1[1]),round(window_space2[0]),round(window_space2[1]))

def drawQuad(point1,point2,point3,point4,fill=True):
    drawLine(point1,point2)
    drawLine(point2,point3)
    drawLine(point3,point4)
    drawLine(point4,point1)

if __name__ == "__main__":
    while True:
        #print(cameraForward)
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(WHITE)
        drawLine((-0.5,0.5,2),(-0.5,-0.5,2))
        drawLine((-0.5,0.5,2),(0.5,0.5,2))
        drawLine((0.5,-0.5,2),(0.5,0.5,2))
        drawLine((0.5,-0.5,2),(-0.5,-0.5,2))
        drawLine((-0.5,0.5,2.5),(-0.5,-0.5,2.5))
        drawLine((-0.5,0.5,2.5),(0.5,0.5,2.5))
        drawLine((0.5,-0.5,2.5),(0.5,0.5,2.5))
        drawLine((0.5,-0.5,2.5),(-0.5,-0.5,2.5))
        drawLine((-0.5,0.5,2),(-0.5,0.5,2.5))
        drawLine((0.5,0.5,2),(0.5,0.5,2.5))
        drawLine((0.5,-0.5,2),(0.5,-0.5,2.5))
        drawLine((-0.5,-0.5,2),(-0.5,-0.5,2.5))
        if button_b.read() and button_a.read():
            moveCamera(multbyscalar(cameraRight,-0.1))
        elif button_y.read() and button_x.read():
            moveCamera(multbyscalar(cameraRight,0.1))
        elif button_b.read():
            turnCamera(-0.1)
        elif button_y.read():
            turnCamera(0.1)
        elif button_x.read():
            #print(multbyscalar(cameraForward,0.1))
            moveCamera(multbyscalar(cameraForward,0.1))
        elif button_a.read():
            #print(multbyscalar(cameraForward,0.1))
            moveCamera(multbyscalar(cameraForward,-0.1))
        display.update()
        time.sleep(0.01)
