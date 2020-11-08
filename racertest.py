import pygame
import random
import numpy as np
import math
import sys
import re
from pynput.keyboard import Key, Controller
from inputs import devices
from inputs import get_gamepad
import _thread

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255,0,0)
GRAY = (220,220,200)

class Line:

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.path_length = ((self.end.imag - self.start.imag)**2 + (self.end.real-self.start.real)**2)**1/2


    def set_size(self, size):
        self.size=size

    def x(self, t):
        return (self.end.real-self.start.real)*t/self.size +self.start.real

    def y(self, t):
        return (self.end.imag-self.start.imag)*t/self.size + self.start.imag

    def get_path_length(self):
        return self.path_length

class CBezier:
    N = np.linspace(0,1,1001)
    length_at_t = [None]*1000

    def __init__(self, start, end, c1, c2):
        self.start = start
        self.end = end
        self.c1 = c1
        self.c2 = c2
        self.size = 1
        self.path_length = 0

        for i in range(len(self.N)-1):
            l_start_x = self.x(self.N[i])
            l_start_y = self.y(self.N[i])
            l_end_x = self.x(self.N[i+1])
            l_end_y = self.y(self.N[i+1])

            l = Line(complex(l_start_x, l_start_y), complex(l_end_x,l_end_y))
            self.path_length+=l.get_path_length()
            self.length_at_t[i] = self.path_length

        #print(self.length_at_t)


    def set_size(self, size):
        self.size=size

    def x(self, t):
        t = t/self.size
        return (1-t)**3*self.start.real + 3*(1-t)**2*t*self.c1.real +3*(1-t)*t**2*self.c2.real + t**3*self.end.real

    def y(self, t):
        t = t/self.size
        return (1-t)**3*self.start.imag + 3*(1-t)**2*t*self.c1.imag +3*(1-t)*t**2*self.c2.imag + t**3*self.end.imag

    def get_path_length(self):
        return ((self.c2.real-self.c1.real)**2 + (self.c2.imag - self.c1.imag)**2)**1/2

run = True
analogAccelerationFlag = False  #set to false for now, set true when analog is there
analogTurning = 0


#multithreading the analog inputs
def geteventThread(car):
    global run
    #global gas
    global analogAccelerationFlag
    global analogTurning
    while (run):
        events = get_gamepad()
        for event in events:
            analogAccelerationFlag = True
            if (event.code == "ABS_RZ"):
                print("ACCELERATING WITH MAGNITUDE ", event.state / 255)
                car.gas = event.state/255
            elif (event.code == "ABS_Z"):
                print("\tDECELERATING WITH MAGNITUDE ", -1 * (event.state/255)/3)
                car.gas = -1 * (event.state/255)/3
            if (event.code == "ABS_X"):
                analogTurning = event.state / 32800


class Box(pygame.sprite.Sprite):

    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, color, width, height, theta, cx, cy):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        print(width, height)
        img_tmp = pygame.Surface([width, height],pygame.SRCALPHA)
        print(theta)
        img_tmp.fill(color)
        self.image = pygame.transform.rotate(img_tmp,math.degrees(-theta))

        self.theta = theta

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.rect.centerx = cx
        self.rect.centery = cy


class Car(pygame.sprite.Sprite):        #this is object-oriented car stuff, pretty simple
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self)
        carName = random.randrange(1, 20, 1)
        self.carFile = "carSprites/" + str(carName) + "_70.png"
        img= pygame.image.load(self.carFile)
        self.width = 39 #actual 55
        self.height = 56 #actual 82
        self.image = pygame.Surface([self.width,self.height], pygame.SRCALPHA)
        self.image.blit(img, (0,0))
        #self.image = pygame.Surface([width, height])
        #self.image.fill(color)
        self.rect = self.image.get_rect()
        self.dir = 90
        self.velocityMagnitude = 0
        self.velocityDir = 90
        self.x = 0
        self.y = 0
        self.weight = .05
        self.leftTop = (0, 0)
        self.rightTop = (0, 0)
        self.leftBottom = (0, 0)
        self.rightBottom = (0, 0)
        self.gas = 0
        self.carPower = 0.15
        self.carCornering = 3
        self.weight=3.5
        self.air_resistance = 0.005
        self.sliding_friction = 0.3
        self.accMag = 0
        self.drift = False
        self.score = 0
        self.alive = True

    def update(self, gas, turning, screen, bg):
        #aprint(gas)
        screen.blit(bg, (self.rect.x-30, self.rect.y-30), (self.rect.x-30, self.rect.y-30, self.rect.width*2, self.rect.height*2))
    
        if(self.velocityDir>self.dir-2.5 and self.velocityDir<self.dir+2.5):
            self.drift = False

        turning_angle = 0
        #DIGITAL TURNING LOGIC
        if(abs(self.velocityMagnitude)>1 & turning != 0):
            turning_angle = self.carCornering*turning
            self.dir += self.carCornering*turning #* ( self.velocityMagnitude / carTopSpeed )
            self.dir = self.dir % 360     

            x, y = self.rect.center
            img = pygame.image.load(self.carFile)
            copy = pygame.Surface([self.width,self.height], pygame.SRCALPHA)
            copy.blit(img, (0,0))
            copy = pygame.transform.rotate(copy,self.dir-90)
            self.image=copy
            self.rect = self.image.get_rect() 
            self.rect.center = (x, y)    #yeah this was weird, but it's the proper way to rotate stuff


        #print(len(path_pt))
        # pygame.draw.line(screen, WHITE, path_pt[498], path_pt[499])
        # path_pt = [(self.rect.centerx, self.rect.centery)] + path_pt[0:499]
        # r = pygame.draw.line(screen, (0, 255, 0), path_pt[0], path_pt[1])
        # print(r.center)
    
        accMag = gas*self.carPower
        air_acc = (.5*self.air_resistance*math.pow(self.velocityMagnitude,2)+.01)*np.sign(self.velocityMagnitude)

        velY = 0
        velX = 0

        centrip_acceleration = 0

        if(turning_angle != 0 and self.velocityMagnitude != 0):
            turning_radius = abs(self.velocityMagnitude*360/(5*turning_angle)/(2*math.pi))
            centrip_acceleration = self.velocityMagnitude*self.velocityMagnitude/turning_radius

        # centrip_display = myFont.render("centrip_a:" + str(centrip_acceleration), 1, (0,0,0))
        # fg.blit(centrip_display, (500,500))

        if(centrip_acceleration > self.weight):
            self.drift = True


        if(centrip_acceleration > self.weight or self.drift):
            velY = math.sin( math.radians(self.velocityDir) ) * self.velocityMagnitude
            velX = math.cos( math.radians(self.velocityDir) ) * self.velocityMagnitude
            
            accY = math.sin( math.radians(self.dir) ) * accMag
            accX = math.cos( math.radians(self.dir) ) * accMag

            air_acc_x = math.cos( math.radians(self.velocityDir)) * air_acc
            air_acc_y = math.sin( math.radians(self.velocityDir)) * air_acc


            vel_acc_angle = (self.velocityDir-self.dir) % 360
            vel_perp = math.sin( math.radians(vel_acc_angle))

            velY += accY + self.sliding_friction*vel_perp*math.sin( math.radians((self.dir-90) % 360)) - air_acc_y
            velX += accX + self.sliding_friction*vel_perp*math.cos( math.radians((self.dir-90) % 360)) -  air_acc_x
            velY += accY #- (sliding_friction*velY + air_acc_y*.1)*np.sign(velY)w
            velX += accX #- (sliding_friction*velX + air_acc_x*.1)*np.sign(velX)

            self.velocityMagnitude = math.sqrt(velY*velY + velX*velX)
            self.velocityDir = math.degrees(math.atan2(velY, velX))
            
            # drifting_disp = myFont.render("DRIFTING", 1, RED)
            # screen.blit(drifting_disp, (1000,50))

            #ddddaaaaaprint("drifting")
                

        else:
            self.drift = False
            self.velocityMagnitude += accMag - air_acc
            self.velocityDir += turning_angle
            velY = math.sin( math.radians(self.velocityDir) ) * self.velocityMagnitude
            velX = math.cos( math.radians(self.velocityDir) ) * self.velocityMagnitude  

        self.velocityDir = self.velocityDir % 360

        if((self.velocityDir > (self.dir-2.5) and self.velocityDir < (self.dir+2.5)) or self.velocityMagnitude == 0):
            self.velocityDir = self.dir

        #update position of the car
        self.x += velX
        self.y -= velY

        self.rect.centerx = self.x
        self.rect.centery = self.y
        run = False

        if(not updateHitbox(self, screen)):
            print('ded')
            self.alive = False
            return self.score

        #Decreasing score by 1 per tick alive
        self.score -= 1
        return None



        #Some variables for the car, eventually these should probably be in the object, like car.score
    # Score = 0

    # #OVERRIDDEN BY GLOBAL VARIABLE GAS, CONTROLLED BY CONTROLLER.
    # # gas = 0     #either 1 when w is pressed or 0 or -1 when s is pressed

    # carPower = .15
    #     #a 'power' number, basically the acceleration number
    # carTopSpeed = 20    #top speed in pixels/tick
    # carCornering = 3    #number of degrees it turns per tick of holding a or d
    # weight = 1.9   #basically the friction value for the car, as a percentage of the current velocity that will fight its movement

    # #Stage Values
    # air_resistance = .005
    # sliding_friction = .3


    # #physics vars, again eventually will be in the object like car.velMag
    # 
    # 
    # velX = 0
    # velY = 0
    
    # accMag = 0
    # accDir = 90  #degrees
    # accX = 0
    # accY = 0
    # drift = False
    # weightDir = 0   #opposite of velDir
    # frictionX = 0   #opposite of velX
    # frictionY = 0   #opposite of velY



def get_complex_coords(string):
    c = [float(n) for n in string.split(",")]
    return complex(c[0], -c[1])

def arr_to_complex(arr):
    return complex(arr[0], arr[1])

def updateHitbox(car, screen):
    #store the center of the vehicle for future reference.

    #These values are hardcoded for now, but they are the dimensions of the car
    height = car.height
    width = car.width

    rect_points = [(car.x-width/2, car.y+height/2), (car.x+width/2, car.y+height/2), (car.x+width/2, car.y-height/2), (car.x-width/2, car.y-height/2)]
    r_rect_points = [None]*4
    for i in range(len(rect_points)):
        #p = (x, y)
        p = rect_points[i]
        p = (p[0]-car.x, p[1]-car.y)
        theta = math.radians(90-car.dir)
        p= (p[0]*math.cos(theta) - p[1]*math.sin(theta), p[1]*math.cos(theta) + p[0]*math.sin(theta))
        r_rect_points[i] = (p[0]+car.x, p[1]+car.y)
        if screen.get_at((int(r_rect_points[i][0]),int(r_rect_points[i][1]))) == (255, 255, 255, 255):
            return False
        pygame.draw.circle(screen, RED, r_rect_points[i], 5)

    return True

def draw_map(scrn, map_pts):
    circle_r = 100
    checkpoint_num = 0
    checkpoint_dist = 100
    for i in range(len(map_pts)):
        pygame.draw.circle(scrn, BLACK, (map_pts[i][0], map_pts[i][1]), circle_r)

    cp_box = []

    dist = 0
    for i in range(1, len(map_pts)):
        x = map_pts[i][0]
        y = map_pts[i][1]

        
        x_p = map_pts[i-1][0]
        y_p = map_pts[i-1][1]
        dx = x-x_p
        dy = y-y_p
        dist += math.sqrt(dx*dx + dy*dy)
        checkpoints = pygame.sprite.Group()

        if(dist >= checkpoint_num*checkpoint_dist):
            rect_angle = math.atan2(dy,dx)
            #print("angle:", rect_angle)
            width = 10
            height = circle_r*2
            # rect_points = [(x-width/2, y+height/2), (x+width/2, y+height/2), (x+width/2, y-height/2), (x-width/2, y-height/2)]
            # r_rect_points = [None]*4
            # for i in range(len(rect_points)):
            #     #p = (x, y)
            #     p = rect_points[i]
            #     p = (p[0]-x, p[1]-y)
            #     p= (p[0]*math.cos(rect_angle) - p[1]*math.sin(rect_angle), p[1]*math.cos(rect_angle) + p[0]*math.sin(rect_angle))
            #     r_rect_points[i] = (p[0]+x, p[1]+y)
            color = (0,0,255)
            if(checkpoint_num == 0):
                color = (200,200,200)
            #r = pygame.draw.polygon(scrn, color, r_rect_points)
            cp = Box(color, width, height, rect_angle, x, y)
            checkpoints.add(cp)
            checkpoint_num += 1
        checkpoints.draw(scrn)

def load_map(svg_file, screen):
    file = open(svg_file)
    #print(file.read())
    #print(file.read())
    regex = "d=.*?z"
    #print(re.search(regex,file.read()))
    path = re.search(regex,file.read()).group()
    paths = path[3:].split(" ")
    #print(paths)


    coords = complex(0,0)
    i = 0
    total_length = 0
    instr = []
    while i < len(paths):
        if paths[i] == "M":
            coords = get_complex_coords(paths[i+1])
            i+=2
        elif paths[i] == "L":
            end = get_complex_coords(paths[i+1])
            line = Line(coords, end)
            instr.append(line)
            total_length += line.get_path_length()
            coords = end
            i+=2
        elif paths[i] == "C":
            end= get_complex_coords(paths[i+3])
            curve = CBezier(coords, end, get_complex_coords(paths[i+1]), get_complex_coords(paths[i+2]))
            instr.append(curve)
            total_length += curve.get_path_length()
            coords = end
            i+=4
        else:
            i+=1


    starts = []
    curr_length = 0

    for i in instr:
        s=i.get_path_length()/total_length
        i.set_size(s)
        starts.append(curr_length)
        curr_length += s


    count = 0
    t_space = np.linspace(0,1,10001)
    x=[]
    y=[]
    map_pts = []
    for t in t_space:
        if count != len(starts)-1 and starts[count+1] < t:
            count += 1
        x.append(instr[count].x(t-starts[count]))
        y.append(instr[count].y(t-starts[count]))
        map_pts.append((x[len(x)-1], -y[len(y)-1]))

    print("Hello:", map_pts[0])

    #print(map_pts)
    draw_map(screen, map_pts)
    return map_pts

def save_map(pts, C_1, C_2):
    file_str = "<?xml version='1.0' encoding='UTF-8' standalone='no'?>\n<svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='900px' width='1600px'>\n<path style='fill:none; stroke:black'\nd='"
    post_str = "' />\n</svg>"
    svg_str = "M " + str(pts[0][0]) + "," + str(pts[0][1])
    for i in range(1, len(pts)):
        svg_str += " C " + str(C_1[i-1][0]) + "," + str(C_1[i-1][1]) + " " + str(C_2[i-1][0]) + "," + str(C_2[i-1][1]) + " " + str(pts[i][0]) + "," + str(pts[i][1])
    n = len(C_1)-1
    svg_str += " C " + str(C_1[n][0]) + "," + str(C_1[n][1]) + " " + str(C_2[n][0]) + "," + str(C_2[n][1]) + " " + str(pts[0][0]) + "," + str(pts[0][1]) + " z"
    file_str = file_str + svg_str + post_str
    file = open('test.svg', 'w')
    file.write(file_str)
    file.close()



def start():

    #print(map_pts)
    global run
    #global gas
    global analogAccelerationFlag
    global analogTurning

        
    successes, failures = pygame.init()   #this inits pygame
    #print("{0} successes and {1} failures".format(successes, failures))
    screenx = 1600
    screeny = 900
    screen = pygame.display.set_mode((screenx, screeny))  #this launches the window and sets size
    bg = pygame.Surface((screenx, screeny), pygame.SRCALPHA)
    bg.fill(WHITE)
    map_pts = load_map("test.svg", bg)
    #pygame.draw.circle(bg, RED, (800, 450), 500)
    screen.blit(bg, (0,0))

    clock = 0
    clock = pygame.time.Clock()     #honestly I forget what this is for
    FPS = 60  # The loop runs this many times a second

    keyboard = Controller()     #for pynput
    myFont = pygame.font.SysFont("Times New Roman",18)      #for displaying text in pygame
    cars = 1
    Cars = pygame.sprite.Group()    #creates  a group, makes it easier when there are multiple carsa

    for i in range(0, cars):
        car = Car(BLACK,32,64)          #init one car
        car.rect.x=map_pts[0][0]     #setting car's position
        car.rect.y=map_pts[0][1]
        car.x = map_pts[0][0]
        car.y = map_pts[0][1]
        dx = map_pts[1][0] - map_pts[0][0]
        dy = map_pts[1][1] - map_pts[0][1]
        #this should probably be moved somewhere:
        car.dir = math.atan2(dy,dx)
        car.velocityDir = car.dir
        car.weight = 1.9
        Cars.add(car)       #add this car to that group

        img = pygame.image.load(car.carFile)
        copy = pygame.Surface([car.width,car.height], pygame.SRCALPHA)
        copy.blit(img, (0,0))
        copy = pygame.transform.rotate(copy,car.dir-90)
        car.image=copy
        car.rect = car.image.get_rect() 
        car.rect.center = (car.x, car.y)    #yeah this was weird, but it's the proper way to rotate stuff


    run = True
    if(len(sys.argv) == 2 ):
        pygame.mouse.set_visible(True)
        pressed = False
        pts = []
        C_1 = []
        C_2 = []
        n = []
        while run:

            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    run = False
            key_pressed = pygame.key.get_pressed()  #pressed in an array of keys pressed at this tick

            if key_pressed[pygame.K_q]:       #hitting q when in the game will break the loop and close the game
                if(n >= 3):
                    save_map(pts, C_1,C_2)
                run = False
                return car.score
            clock.tick(FPS)
            left_pressed, middle_pressed, right_pressed = pygame.mouse.get_pressed()
            if(left_pressed):
                if(not pressed):
                    screen.fill(WHITE)
                    mouse_pos = pygame.mouse.get_pos()
                    print(mouse_pos)
                    pts.append(np.array([mouse_pos[0], mouse_pos[1]]))
                    pressed = True

                    pts_rect = []
                    for p in pts:
                        r = pygame.draw.circle(screen, RED, (p[0], p[1]), 5)
                        pts_rect.append(r)

                    n = len(pts)
                    #print(pts)
                    if(n >= 3):
                        A = [0] + [1]*(n-2) + [2]
                        B = [2] + [4]*(n-2) + [7]
                        C = [1]*(n-1) + [0]
                        D = [pts[0] + 2*pts[1]]
                        for i in range(1, n-1):
                            D.append(4*pts[i] + 2*pts[i+1])
                        D.append(8*pts[n-1] + pts[0])
                        #print(D)

                        for i in range(1, n) :
                            W = A[i] / B[i-1]
                            B[i] = B[i] - W*C[i-1]
                            D[i] = D[i] - W*D[i-1]
                        
                        C_1 = [None]*n

                        C_1[n-1] = D[n-1] / B[n-1]

                        for i in range(n-2, -1, -1):
                            C_1[i] = (D[i] - C[i]*C_1[i+1])/B[i]
                            print(i)

                        C_2 = [None]*n
                        for i in range(0, n-1):
                            C_2[i] = 2*pts[i+1] - C_1[i+1]
                        C_2[n-1] = 2*pts[0]-C_1[0]


                        instr = []
                        total_length = 0
                        for i in range(len(pts)-1):
                            end= arr_to_complex(pts[i+1])
                            start = arr_to_complex(pts[i])
                            curve = CBezier(start, end, arr_to_complex(C_1[i]), arr_to_complex(C_2[i]))
                            instr.append(curve)
                            total_length += curve.get_path_length()

                        end= arr_to_complex(pts[0])
                        start = arr_to_complex(pts[n-1])
                        curve = CBezier(start, end, arr_to_complex(C_1[n-1]), arr_to_complex(C_2[n-1]))
                        instr.append(curve)
                        total_length += curve.get_path_length()

                        

                        starts = []
                        curr_length = 0

                        for i in instr:
                            s=i.get_path_length()/total_length
                            i.set_size(s)
                            starts.append(curr_length)
                            curr_length += s

                        count = 0
                        t_space = np.linspace(0,1,10001)
                        map_pts= []
                        for t in t_space:
                            if count != len(starts)-1 and starts[count+1] < t:
                                count += 1
                            x = instr[count].x(t-starts[count])
                            y = instr[count].y(t-starts[count])
                            map_pts.append((x,y))

                        print("length:", len(map_pts))

                        draw_map(screen, map_pts)


            else:
                pressed = False

            pygame.display.flip()   #actually updates the screen
                    
    else:
        
        #PRINTS ALL CONNECTED DEVICES
        for device in devices:
            print(device)

        try:
           _thread.start_new_thread(geteventThread, (car))
        except:
           print("Error: unable to start thread")

        while run:
            
            #COLLECT DIGITAL ACCELERATION (KEYBOARD)
            pressed = pygame.key.get_pressed()  #pressed in an array of keys pressed at this tick
            gas = 0
            if(sum(pressed) != 0):  #check if there are any keyboard inputs at all. if there are none, use controller.
                analogAccelerationFlag = False
            #print("VALUE OF ACCELERATION FLAG: ", analogAccelerationFlag)
            if (analogAccelerationFlag == False and pressed[pygame.K_w]):
                gas = 1
            elif (analogAccelerationFlag == False and pressed[pygame.K_s]):
                gas = -.3
            # EXIT CONDITION (ALWAYS A KEYBOARD PRESS) [we can also make the home button on controller exit later]
            elif pressed[pygame.K_q]:  # hitting q when in the game will break the loop and close the game
                run = False
                #reset flag to false for next frame in case switch back to keyboard

            turning = 0
            if(pressed[pygame.K_d]):
                turning = -1
            elif(pressed[pygame.K_a]):
                turning = 1
            

            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    run = False
            clock.tick(FPS)
            if (analogAccelerationFlag == False):
                car.gas = 0

            scores = [0]*cars
            still_alive = False
            for i, car in enumerate(Cars):
                if(car.alive):
                    still_alive = True
                    score = car.update(gas, turning, screen, bg)
                    if(score is not None):
                        scores[i] = score
            
            if(not still_alive):
                run = False
            #Cars.update(gas, turning, screen, bg)
            Cars.draw(screen)   #draws all cars in the group to the screen
            # plot the left corner.
            
            #screen.blit(bg, (0,0))
            pygame.display.flip()   #actually updates the screen
            
start()     #runs that start fn at the beginning
pygame.quit()       #it only gets here if q is pressed and the loop is broken, so it closes the window
