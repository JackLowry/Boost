import pygame
import random
import numpy as np
import math
from pynput.keyboard import Key, Controller
from inputs import devices
from inputs import get_gamepad
import _thread

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255,0,0)
GRAY = (220,220,200)

run = True
gas = 0;
analogAccelerationFlag = False  #set to false for now, set true when analog is there
analogTurning = 0

def geteventThread():
    global run
    global gas
    global analogAccelerationFlag
    global analogTurning
    while (run):
        events = get_gamepad()
        for event in events:
            analogAccelerationFlag = True
            if (event.code == "ABS_RZ"):
                print("ACCELERATING WITH MAGNITUDE ", event.state / 255)
                gas = event.state/255
            elif (event.code == "ABS_Z"):
                print("\tDECELERATING WITH MAGNITUDE ", -1 * (event.state/255)/3)
                gas = -1 * (event.state/255)/3
            if (event.code == "ABS_X"):
                analogTurning = event.state / 32800


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

def start():
    global run
    global gas
    global analogAccelerationFlag
    global analogTurning
        
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
    car.weight = 3.5
    Cars.add(car)       #add this car to that group

    #Some variables for the car, eventually these should probably be in the object, like car.score
    Score = 0

    #OVERRIDDEN BY GLOBAL VARIABLE GAS, CONTROLLED BY CONTROLLER.
    # gas = 0     #either 1 when w is pressed or 0 or -1 when s is pressed

    carPower = .15
        #a 'power' number, basically the acceleration number
    carTopSpeed = 20    #top speed in pixels/tick
    carCornering = 3    #number of degrees it turns per tick of holding a or d
    weight = 1.9   #basically the friction value for the car, as a percentage of the current velocity that will fight its movement

    #Stage Values
    air_resistance = .005
    sliding_friction = .3


    #physics vars, again eventually will be in the object like car.velMag
    velMag = 0
    velDir = 90
    velX = 0
    velY = 0
    
    accMag = 0
    accDir = 90  #degrees
    accX = 0
    accY = 0
    drift = False
    weightDir = 0   #opposite of velDir
    frictionX = 0   #opposite of velX
    frictionY = 0   #opposite of velY
    
    path_pt = [None]*500
    for i in range(len(path_pt)):
        path_pt[i] = (300,800)

    #PRINTS ALL CONNECTED DEVICES
    for device in devices:
        print(device)

    try:
        _thread.start_new_thread(geteventThread, ())
    except:
        print("Error: unable to start thread")

    while run:
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT: 
                run = False
        screen.fill(WHITE)
        clock.tick(FPS)
        if (analogAccelerationFlag == False):
            gas = 0

        #COLLECT DIGITAL ACCELERATION (KEYBOARD)
        pressed = pygame.key.get_pressed()  #pressed in an array of keys pressed at this tick

        if(sum(pressed) != 0):  #check if there are any keyboard inputs at all. if there are none, use controller.
            analogAccelerationFlag = False
        print("VALUE OF ACCELERATION FLAG: ", analogAccelerationFlag)
        if (analogAccelerationFlag == False and pressed[pygame.K_w]):
            gas = 1
        elif (analogAccelerationFlag == False and pressed[pygame.K_s]):
            gas = -.3
        # EXIT CONDITION (ALWAYS A KEYBOARD PRESS) [we can also make the home button on controller exit later]
        elif pressed[pygame.K_q]:  # hitting q when in the game will break the loop and close the game
            run = False
            return Score
            #reset flag to false for next frame in case switch back to keyboard

        gasPrinter = myFont.render("GAS: " + str(gas), 1, (0, 0, 0))
        screen.blit(gasPrinter, (500, 0))


        if(car.velocityDir>car.dir-2.5 and car.velocityDir<car.dir+2.5):
            drift = False

        turning_angle = 0
        #DIGITAL TURNING LOGIC
        if(pressed[pygame.K_d]):
            if(abs(car.velocityMagnitude)>1):
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
            if(abs(car.velocityMagnitude)>1):
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

        #ANALOG TURNING LOGIC

        print("ANALOG TURNING POWER: ", analogTurning)
        if(analogAccelerationFlag == True):
            if (abs(car.velocityMagnitude) > 1):
                turning_angle = carCornering * analogTurning * (-1)
                car.dir += carCornering * analogTurning * (-1)  # * ( car.velocityMagnitude / carTopSpeed )
                # accDir += -1*carCornering #degrees, and yes this works
                # accDir = (abs(accDir) % 360) * np.sign(accDir)
            car.dir = car.dir % 360
            x, y = car.rect.center
            copy = pygame.image.load("car.png")
            copy = pygame.transform.rotate(copy, car.dir - 90)
            car.image = copy
            car.rect = car.image.get_rect()
            car.rect.center = (x, y)  # yeah this was weird, but it's the proper way to rotate stuff


        path_pt = [(car.rect.centerx, car.rect.centery)] + path_pt[0:998]
        pygame.draw.lines(screen, RED, False, path_pt)

        
        
        

        


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

        if(centrip_acceleration > weight):
            drift = True


        if(centrip_acceleration > weight or drift):
            velY = math.sin( math.radians(car.velocityDir) ) * car.velocityMagnitude
            velX = math.cos( math.radians(car.velocityDir) ) * car.velocityMagnitude
            
            accY = math.sin( math.radians(car.dir) ) * accMag
            accX = math.cos( math.radians(car.dir) ) * accMag

            air_acc_x = math.cos( math.radians(car.velocityDir)) * air_acc
            air_acc_y = math.sin( math.radians(car.velocityDir)) * air_acc


            vel_acc_angle = (car.velocityDir-car.dir) % 360
            vel_perp = math.sin( math.radians(vel_acc_angle))

            velY += accY + sliding_friction*vel_perp*math.sin( math.radians((car.dir-90) % 360)) - air_acc_y
            velX += accX + sliding_friction*vel_perp*math.cos( math.radians((car.dir-90) % 360)) - air_acc_x
            velY += accY #- (sliding_friction*velY + air_acc_y*.1)*np.sign(velY)w
            velX += accX #- (sliding_friction*velX + air_acc_x*.1)*np.sign(velX)

            car.velocityMagnitude = math.sqrt(velY*velY + velX*velX)
            car.velocityDir = math.degrees(math.atan2(velY, velX))
            print("DRIFTING")
            

            drifting_disp = myFont.render("DRIFTING",  1, RED)
            screen.blit(drifting_disp,(1000,50))


        else:
            drift = False
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
