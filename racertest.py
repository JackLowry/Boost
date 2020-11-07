import pygame
import random
import numpy as np
import math
import sys
import re
from pynput.keyboard import Key, Controller
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


class Car(pygame.sprite.Sprite):        #this is object-oriented car stuff, pretty simple
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("car.png")
        #self.image = pygame.Surface([width, height])
        #self.image.fill(color)
        self.rect = self.image.get_rect()
        self.dir = 90
        self.velocityMagnitude = 0
        self.velocityDir = 90
        self.x = 0
        self.y = 0
        self.weight = .05

def get_complex_coords(string):
    c = [float(n) for n in string.split(",")]
    return complex(c[0], -c[1])

def arr_to_complex(arr):
    return complex(arr[0], arr[1])

def start():

    file = open("pi.svg")

    regex = "d=.*?z"
    path = re.search(regex,file.read()).group()
    paths = path[3:].split(" ")

    # SVG STUFF
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
    map_pts= []
    for t in t_space:
        if count != len(starts)-1 and starts[count+1] < t:
            count += 1
        x = instr[count].x(t-starts[count])
        y = -instr[count].y(t-starts[count])
        map_pts.append((x,y))

    print(map_pts)
        
    successes, failures = pygame.init()   #this inits pygame
    #print("{0} successes and {1} failures".format(successes, failures))

    screen = pygame.display.set_mode((1600, 900))  #this launches the window and sets size
    clock = 0
    clock = pygame.time.Clock()     #honestly I forget what this is for
    FPS = 60  # The loop runs this many times a second

    keyboard = Controller()     #for pynput
    myFont = pygame.font.SysFont("Times New Roman",18)      #for displaying text in pygame


    Cars = pygame.sprite.Group()    #creates  a group, makes it easier when there are multiple cars
    car = Car(BLACK,32,64)          #init one car
    car.rect.x=300      #setting car's position
    car.rect.y=800
    car.x = 300
    car.y = 800
    car.weight = .9
    Cars.add(car)       #add this car to that group

    #Some variables for the car, eventually these should probably be in the object, like car.score
    Score = 0
    gas = 0     #either 1 when w is pressed or 0 or -1 when s is pressed
    carPower = .1
        #a 'power' number, basically the acceleration number
    carTopSpeed = 20    #top speed in pixels/tick
    carCornering = 3    #number of degrees it turns per tick of holding a or d
    weight = 1.5   #basically the friction value for the car, as a percentage of the current velocity that will fight its movement

    #Stage Values
    air_resistance = .005
    sliding_friction = .06


    #physics vars, again eventually will be in the object like car.velMag
    velMag = 0
    velDir = 90
    velX = 0
    velY = 0
    
    accMag = 0
    accDir = 90  #degrees
    accX = 0
    accY = 0
    
    weightDir = 0   #opposite of velDir
    frictionX = 0   #opposite of velX
    frictionY = 0   #opposite of velY
    
    path_pt = [None]*500
    for i in range(len(path_pt)):
        path_pt[i] = (300,800)

    run = True
    if(len(sys.argv) == 2 or True):
        pygame.mouse.set_visible(True)
        pressed = False
        pts = []
        while run:
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    run = False
            key_pressed = pygame.key.get_pressed()  #pressed in an array of keys pressed at this tick

            if key_pressed[pygame.K_q]:       #hitting q when in the game will break the loop and close the game
                run = False
                return Score
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

                        pygame.draw.lines(screen, BLACK, True, map_pts, )
                        print(pts)

            else:
                pressed = False

            



            pygame.display.flip()   #actually updates the screen

                    
    else:
        while run:
            for event in pygame.event.get(): 
                if event.type == pygame.QUIT: 
                    run = False
            screen.fill(WHITE)
            clock.tick(FPS)
            gas = 0
            pressed = pygame.key.get_pressed()  #pressed in an array of keys pressed at this tick
            if (pressed[pygame.K_w]):
                gas = 1
            elif (pressed[pygame.K_s]):
                gas = -.3
            elif pressed[pygame.K_q]:       #hitting q when in the game will break the loop and close the game
                run = False
                return Score

            turning_angle = 0
            if(pressed[pygame.K_d]):
                turning_angle = -1*carCornering
                car.dir += -1*carCornering #* ( car.velocityMagnitude / carTopSpeed )
                # accDir += -1*carCornering #degrees, and yes this works
                # accDir = (abs(accDir) % 360) * np.sign(accDir)
                car.dir = car.dir % 360
                x, y = car.rect.center
                copy = pygame.image.load("car.png")
                copy = pygame.transform.rotate(copy,car.dir-90)
                car.image=copy
                car.rect = car.image.get_rect() 
                car.rect.center = (x, y)    #yeah this was weird, but it's the proper way to rotate stuff
            elif(pressed[pygame.K_a]):
                turning_angle = carCornering
                car.dir += carCornering #* ( car.velocityMagnitude / carTopSpeed )
                # accDir += carCornering  #degrees
                # accDir = (abs(accDir) % 360) * np.sign(accDir)
                car.dir = car.dir % 360
                x, y = car.rect.center
                copy = pygame.image.load("car.png")
                copy = pygame.transform.rotate(copy,car.dir-90)
                car.image=copy
                car.rect = car.image.get_rect() 
                car.rect.center = (x, y)  


            path_pt = [(car.rect.centerx, car.rect.centery)] + path_pt[0:998]
            pygame.draw.lines(screen, RED, False, path_pt)
            pygame.draw.lines(screen, BLACK, True, map_pts, width=101)
            
            
            

            


            #air resistance


            #Turning Stuff
                    
            #limit magnitude of car velocity to a certain value
            #car.velocityMagnitude = math.sqrt( math.pow(velX, 2) + math.pow(velY, 2) )
            #if (car.velocityMagnitude > carTopSpeed):
            #    car.velocityMagnitude = carTopSpeed

            #velocityMagnitudeDISPLAY = myFont.render("velocityMagnitude: "+str(car.velocityMagnitude), 1, (0,0,0))
            #screen.blit(velocityMagnitudeDISPLAY,(500,500))

            #renormalize velX and velY according to the new limit

            accMag = gas*carPower
            air_acc = (.5*air_resistance*math.pow(car.velocityMagnitude,2)+.01)*np.sign(car.velocityMagnitude)

            velY = 0
            velX = 0

            centrip_acceleration = 0
            if(turning_angle != 0 and car.velocityMagnitude != 0):
                turning_radius = abs(car.velocityMagnitude*360/(5*turning_angle)/(2*math.pi))
                centrip_acceleration = car.velocityMagnitude*car.velocityMagnitude/turning_radius

            centrip_display = myFont.render("centrip_a: "+str(centrip_acceleration), 1, (0,0,0))
            screen.blit(centrip_display,(500,500))

            if(centrip_acceleration > weight or car.velocityDir != car.dir):
                velY = math.sin( math.radians(car.velocityDir) ) * car.velocityMagnitude
                velX = math.cos( math.radians(car.velocityDir) ) * car.velocityMagnitude
                
                accY = math.sin( math.radians(car.dir) ) * accMag
                accX = math.cos( math.radians(car.dir) ) * accMag

                air_acc_x = math.cos( math.radians(car.velocityDir)) * air_acc
                air_acc_y = math.sin( math.radians(car.velocityDir)) * air_acc


                vel_acc_angle = (car.velocityDir-car.dir) % 360
                vel_perp = math.sin( math.radians(vel_acc_angle))

                velY += accY + sliding_friction*vel_perp*math.sin( math.radians((car.dir-90) % 360)) - air_acc_y
                velX += accX + sliding_friction*vel_perp*math.cos( math.radians((car.dir-90) % 360)) -  air_acc_x
                velY += accY #- (sliding_friction*velY + air_acc_y*.1)*np.sign(velY)w
                velX += accX #- (sliding_friction*velX + air_acc_x*.1)*np.sign(velX)

                car.velocityMagnitude = math.sqrt(velY*velY + velX*velX)
                car.velocityDir = math.degrees(math.atan2(velY, velX))
                print("DRIFTING")
                

                drifting_disp = myFont.render("DRIFTING",  1, RED)
                screen.blit(drifting_disp,(1000,50))


            else:
                car.velocityMagnitude += accMag - air_acc
                car.velocityDir += turning_angle
                velY = math.sin( math.radians(car.velocityDir) ) * car.velocityMagnitude
                velX = math.cos( math.radians(car.velocityDir) ) * car.velocityMagnitude  

            car.velocityDir = car.velocityDir % 360

            if((car.velocityDir > (car.dir-2.5) and car.velocityDir < (car.dir+2.5)) or car.velocityMagnitude == 0):
                car.velocityDir = car.dir

            
            

            #just displaying velocity and accerlation for debugging
            velDisplayX = myFont.render("velx: "+str(velX), 1, (0,0,0))
            velDisplayY = myFont.render("vely: "+str(velY),1,(0,0,0))
            screen.blit(velDisplayX,(500,150))
            screen.blit(velDisplayY,(500,50))

            accXD = myFont.render("accR: "+str(accMag), 1, (0,0,0))
            accYD = myFont.render("accTheta: "+str(accDir),1,(0,0,0))
            screen.blit(accXD,(500,200))
            screen.blit(accYD,(500,100))

            velDisMag = myFont.render("VelMag: "+str(car.velocityMagnitude), 1, (0,0,0))
            velDisDir = myFont.render("VelDir: "+str(car.velocityDir),1,(0,0,0))
            screen.blit(velDisMag,(500,250))
            screen.blit(velDisDir,(500,300))

            accDisMag = myFont.render("air_acc: "+str(air_acc), 1, (0,0,0))
            accDisDir = myFont.render("Car.dir: "+str(car.dir),1,(0,0,0))
            screen.blit(accDisMag,(500,350))
            screen.blit(accDisDir,(500,400))

            #update position of the car
            car.x += velX
            car.y -= velY

            car.rect.centerx = car.x
            car.rect.centery = car.y

        
            
            Cars.draw(screen)   #draws all cars in the group to the screen
            pygame.display.flip()   #actually updates the screen
            
start()     #runs that start fn at the beginning
pygame.quit()       #it only gets here if q is pressed and the loop is broken, so it closes the window
