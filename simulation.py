import random
import time
import threading
import pygame
import sys


# Default values of signal timers
defaultGreen = {0:10, 1:10, 2:10, 3:10}
defaultRed = 150
defaultYellow = 5

#Signal States
signalStates =['green', 'red', 'yellow']

#Coordinates of vehicle start
lanes = {
    'lane1_up':[257,563],
    'lane1_right':[0,288],
    'lane1_left':[1000,275],
    'lane1_down':[244,0],
    'lane2_down':[693,0],
    'lane2_up':[707,563],
    }
global stop_points 
stop_points =  {'stop1_up':[257,310], 'stop1_right':[240,250], 'stop1_left':[260,275], 'stop1_down':[244,0]}
vehicles = []
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of signal image
signalCoods = [(275,240),(205,475),(210,305),(230,239),(655,180),(655,310),(275,310),(730,310),(730,180)]
pedestrianSignal = [(165,220)]
turnSignal = [(278,300),(290, 295)]

# Gap between vehicles
stoppingGap = 40    # stopping gap
movingGap = 15   # moving gap

pygame.init()
simulation = pygame.sprite.Group()


signals = []
noOfSignals = 9


#speeds = {'car':2.25, 'bus':1.8, 'truck':1.8, 'bike':2.5}  # average speeds of vehicles

#Navigation bar
class Navbar:
    def __init__(self, x, y, width, height, text, color=(255, 255, 255), highlight_color=(200, 200, 200), action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.highlight_color = highlight_color
        self.highlighted = False
        self.action = action
    def draw(self, surface, font):
        color = self.highlight_color if self.highlighted else self.color
        pygame.draw.rect(surface, color, self.rect)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action is not None:
                    self.action()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.highlighted = self.rect.collidepoint(event.pos)
        return False

#Button that start the simulation
class StartButton:
    def __init__(self, parent, width, height, text, color=(255, 255, 255), highlight_color=(200, 200, 200), action=None):
        self.parent = parent
        self.width = width
        self.height = height
        self.color = color
        self.highlight_color = highlight_color
        self.text = text
        self.action = action
        self.highlighted = False
        
        # Position the button within the parent Navbar
        button_width = 100
        button_height = 30
        x = parent.rect.x + (parent.rect.width - button_width) // 2
        y = parent.rect.y + (parent.rect.height - button_height) // 2
        self.rect = pygame.Rect(x, y, button_width, button_height)
    
    def draw(self, surface, font):
        color = self.highlight_color if self.highlighted else self.color
        pygame.draw.rect(surface, color, self.rect)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action is not None:
                    self.action()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.highlighted = self.rect.collidepoint(event.pos)
        return False    


class TrafficSignal:
    def __init__(self,x,y,direction, state, red_span, yellow_span, green_span):
        self.x = x
        self.y = y
        self.direction = direction
        self.state = state 
        self.red_span = red_span
        self.yellow_span = yellow_span
        self.green_span = green_span 
        self.last_change = time.time()   
        
        if self.state == 'red':            
            self.image = pygame.image.load(f"./images/{self.direction}/red_light_{self.direction}.png")            
        elif self.state == 'yellow':
            self.image = pygame.image.load(f"./images/{self.direction}/yellow_light_{self.direction}.png")
        elif self.state == 'green':
            self.image = pygame.image.load(f"./images/{self.direction}/green_light_{self.direction}.png")
        
      
   
    def changeState(self):
        self.elapsed_time = time.time() - self.last_change
        if self.state == 'red' and self.elapsed_time >= self.red_span:
            self.state = 'green'
            self.image = self.image = pygame.image.load(f"./images/{self.direction}/green_light_{self.direction}.png")
            self.last_change = time.time()
        elif self.state == 'green' and self.elapsed_time >= self.green_span:
            self.state = 'yellow'
            self.image = pygame.image.load(f"./images/{self.direction}/yellow_light_{self.direction}.png")
            self.last_change = time.time()
        elif self.state == 'yellow' and self.elapsed_time >= self.yellow_span:
            self.state = 'red'
            self.image = pygame.image.load(f"./images/{self.direction}/red_light_{self.direction}.png")
            self.last_change = time.time()       
            
    def render(self, screen):
        screen.blit(self.image,(self.x,self.y))

class PedestrianSignal:
    def __init__(self,x,y,direction, state, red_span, green_span):
        self.x = x
        self.y = y
        self.direction = direction
        self.state = state
        self.red_span = red_span
        self.green_span = green_span
        self.image = pygame.image.load(f"./images/{self.direction}/pedestrian_{self.state}.png")
        self.last_change = time.time()
    def transform(self):
        elapsed_time = time.time() - self.last_change
        if self.state == 'red' and elapsed_time >= self.red_span:
            self.state = 'green'
            self.image = pygame.image.load(f"./images/{self.direction}/pedestrian_{self.state}.png")
            self.last_change = time.time()
        elif self.state == 'green' and elapsed_time >= self.green_span:
            self.state = 'red'
            self.image = pygame.image.load(f"./images/{self.direction}/pedestrian_{self.state}.png")
            self.last_change = time.time()
    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))    
            
class TurnSignal:
    def __init__(self,x,y,direction,turn,state,red_span, green_span):
        self.x = x
        self.y = y
        self.direction = direction
        self.turn = turn
        self.state = state
        self.red_span = red_span        
        self.green_span = green_span
        self.image_on = pygame.image.load(f"./images/{self.direction}/turn_signal_up_{self.turn}.png")
        self.image_off = pygame.image.load(f"./images/{self.direction}/turn_signal_up_off.png")
        self.image = self.image_on
        self.last_change = time.time()     
     
    def transform(self):
        self.elapsed_time = time.time() - self.last_change
        if self.state == 'red' and self.elapsed_time >= self.red_span:
            print("kavlika")
            self.state = 'green'            
            self.last_change = time.time()
        elif self.state == 'green' and self.elapsed_time >= self.green_span:
            print("kavlika red") 
            self.state = 'red'            
            self.last_change = time.time()      
           
    def render(self, screen):
        change_image = int(self.elapsed_time)
        if change_image % 2 == 0 or change_image % 3 == 0 or change_image % 4 == 0 or change_image % 5 == 0:
            if self.image == self.image_on:
                self.image = self.image_off
            else:
                self.image = self.image_on
        if self.state == 'green':
            screen.blit(self.image, (self.x, self.y))                            
            
            
class Vehicle(pygame.sprite.Sprite):
    def __init__(self,type, x, y,speed,direction):
        super().__init__()  
        self.type = type             
        self.x = x
        self.y = y
        self.direction = direction
        path = f"./images/{direction}/{type}.png"
        self.image = pygame.image.load(path)
        self.speed = speed
        self.stopped = False
        self.red_light_speed = 0.3
              
             
    def move(self,state):
        # move the vehicle based on its speed and lane
        if self.direction == 'right':
            if state == 'green':                
                self.stopped = False
                self.x += self.speed
                stop_points[f'stop1_{self.direction}'][1] = 230  
            else:
                if self.x + self.image.get_rect().width + self.red_light_speed +15 < stop_points[f'stop1_{self.direction}'][0] + 10:
                    self.x += self.red_light_speed
                elif self.x > stop_points[f'stop1_{self.direction}'][0] and not self.stopped:
                    self.x += self.speed
                elif not self.stopped:
                    self.stopped = True
                    
                    if stop_points[f'stop1_{self.direction}'][0] - self.image.get_rect().width + 35 > 230:
                        stop_points[f'stop1_{self.direction}'][0] -= self.image.get_rect().width + 15

        elif self.direction == 'down':
            if state == 'green':                
                self.stopped = False
                self.y += self.speed
                stop_points[f'stop1_{self.direction}'][1] = 265   
            else:
                if self.y + self.image.get_rect().height + self.red_light_speed -15 < stop_points[f'stop1_{self.direction}'][1] - 10:
                    self.y += self.red_light_speed
                elif self.y > stop_points[f'stop1_{self.direction}'][1] and not self.stopped:
                    self.y += self.speed
                elif not self.stopped:
                    self.stopped = True
                    
                    if stop_points[f'stop1_{self.direction}'][1] + self.image.get_rect().height - 35 > 20:
                        stop_points[f'stop1_{self.direction}'][1] -= self.image.get_rect().height - 15
        elif self.direction == 'left':
            if state == 'green':                
                self.stopped = False
                self.x -= self.speed
                stop_points[f'stop1_{self.direction}'][1] = 260  
            else:
                if self.x - self.image.get_rect().width - self.red_light_speed - 15 > stop_points[f'stop1_{self.direction}'][0] - 10:
                    self.x -= self.red_light_speed
                elif self.x < stop_points[f'stop1_{self.direction}'][0] and not self.stopped:
                    self.x -= self.speed
                elif not self.stopped:
                    self.stopped = True
                    
                    if stop_points[f'stop1_{self.direction}'][0] + self.image.get_rect().width - 35 < 250:
                        stop_points[f'stop1_{self.direction}'][0] += self.image.get_rect().width + 15

        elif self.direction == 'up':
            if state == 'green':                
                self.stopped = False
                self.y -= self.speed
                stop_points[f'stop1_{self.direction}'][1] = 310   
            else:
                if self.y - self.image.get_rect().height - self.red_light_speed +15 > stop_points[f'stop1_{self.direction}'][1] + 10:
                    self.y -= self.red_light_speed
                elif self.y < stop_points[f'stop1_{self.direction}'][1] and not self.stopped:
                    self.y -= self.speed
                elif not self.stopped:
                    self.stopped = True
                    
                    if stop_points[f'stop1_{self.direction}'][1] + self.image.get_rect().height + 35 < 555:
                        stop_points[f'stop1_{self.direction}'][1] += self.image.get_rect().height + 15

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Generating vehicles in the simulation
def generateVehicles():
    while(True):
        # Generating vehicles
        
        type = random.randint(0, 3)
        direction = 3 #random.randint(0, 3)
        '''if directionNumbers[direction] == 'right':
            vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[0]][0],lanes[list(lanes.keys())[0]][1],2,directionNumbers[direction]))
        elif directionNumbers[direction] == 'left':
            vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[1]][0],lanes[list(lanes.keys())[1]][1],2,directionNumbers[direction]))
        elif directionNumbers[direction] == 'up':
            vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[2]][0],lanes[list(lanes.keys())[2]][1],2,directionNumbers[direction]))
        elif directionNumbers[direction] == 'down':
            vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[3]][0],lanes[list(lanes.keys())[3]][1],2,directionNumbers[direction]))
        '''
        vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[0]][0],lanes[list(lanes.keys())[0]][1],1,'up'))
        vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[1]][0],lanes[list(lanes.keys())[1]][1],1,'right'))
        vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[3]][0],lanes[list(lanes.keys())[3]][1],1,'down'))
        vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[2]][0],lanes[list(lanes.keys())[2]][1],1,'left'))
        vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[4]][0],lanes[list(lanes.keys())[4]][1],1,'down'))
        vehicles.append(Vehicle(vehicleTypes[type],lanes[list(lanes.keys())[5]][0],lanes[list(lanes.keys())[5]][1],1,'up'))
        time.sleep(1.5)


class Main:
    
   

    # Colours 
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize 
    screenWidth = 1000
    screenHeight = 563
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('./intersection_background.png')
    night_background  = pygame.image.load('./night_background.png')
    screen = pygame.display.set_mode(screenSize)
    
    #Navigation Bar
    navbar = Navbar(0,0,screenWidth,50,"ΠΛΗ ΠΡΟ")

    #Start button and stop button
    start_button = StartButton(navbar,100,30, "Start", action=None)
    start_button.rect.x = 50 # Adjust the x value to position the button horizontally within the Navbar
    start_button.rect.y = 10 # Adjust the y value to position the button vertically within the Navbar

    stop_button = StartButton(navbar,100,30, "Stop", action=None)
    stop_button.rect.x = 200 # Adjust the x value to position the button horizontally within the Navbar
    stop_button.rect.y = 10 # Adjust the y value to position the button vertically within the Navbar

    #Off button night mode
    off_button = StartButton(navbar,100,30, "Off", action=None)
    off_button.rect.x = 300 # Adjust the x value to position the button horizontally within the Navbar
    off_button.rect.y = 10 # Adjust the y value to position the button vertically within the Navbar
    
    #For night mode
    pulsatingYellow = pygame.image.load('./images/signals/pulsating.png')  
    
    #Font
    font = pygame.font.Font(None, 30)

    #Generate the signals   
    
    signal_right = TrafficSignal(signalCoods[2][0],signalCoods[2][1],'right','red',15,5,10)
    #'''signal_ped1 = PedestrianSignal(170, 220, 'up', 'red', 15,15)
    #########################################################
    signal_left = TrafficSignal(signalCoods[0][0],signalCoods[0][1],'left','red',15,5,10)
    #########################################################
    signal_up = TrafficSignal(signalCoods[6][0],signalCoods[6][1],'up','green',15,5,10)
    signal2_up = TrafficSignal(725,305,'up','green',15,5,10)     
    turnsignal_up_right = TurnSignal(turnSignal[1][0]-25,turnSignal[1][1],'up','right','green',10,15)
    #########################################################
    signal_down = TrafficSignal(signalCoods[3][0],signalCoods[3][1],'down','green',15,5,10)
    signal2_down = TrafficSignal(680,240,'down','green',15,5,10)
    
    #Generate vehicles
    thread = threading.Thread(name="generateVehicles",target=generateVehicles, args=()) 
    thread.daemon = True
    thread.start()
        
    pulsating = False
    waiting = True 
      
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif stop_button.handle_event(event):
                    waiting = True
            elif off_button.handle_event(event):
                    pulsating = not pulsating
        screen.blit(background,(0,0))   # display background in simulation
        navbar.draw(screen, font)       # display navigation bar
        start_button.draw(screen, font) #display start button
        stop_button.draw(screen, font) #display stop button
        off_button.draw(screen, font) #display off button
        
        #Displays the signals
        #for signal in signals:
        #############################
        
        
        #signal_ped1.render(screen)
        #signal_ped1.transform()
        #############################
        
        #############################
        
        
        
        #############################
         
        
        #The simulation stops until the start button is pressed
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif start_button.handle_event(event):
                    waiting = False            
            pygame.display.update()
        #############################
        signal_up.render(screen)
        signal_up.changeState() 

        signal2_up.render(screen)
        signal2_up.changeState()
        #############################
        signal_down.render(screen)
        signal_down.changeState()  
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        signal2_down.render(screen)
        signal2_down.changeState()       
        #############################
        signal_right.render(screen)
        signal_right.changeState()
        ############################
        signal_left.render(screen)
        signal_left.changeState() 
        turnsignal_up_right.transform()
        turnsignal_up_right.render(screen)
        #Displays the vehicles
        for vehicle in vehicles:
            
                    
            vehicle.render(screen)
            if vehicle.direction == 'up':
                vehicle.move(signal_up.state)
            elif vehicle.direction == 'right':
                vehicle.move(signal_right.state)
            elif vehicle.direction == 'down':
                vehicle.move(signal_down.state)
            elif vehicle.direction == 'left':
                vehicle.move(signal_left.state)
            if vehicle.x > screenWidth :
                vehicles.remove(vehicle) 
            if vehicle.y > screenHeight or vehicle.y < 0 :
                vehicles.remove(vehicle)
            if 563 - stop_points[f'stop1_{vehicle.direction}'][1] < 30 and vehicle.y > stop_points[f'stop1_{vehicle.direction}'][1]:
                vehicles.remove(vehicle)
        pygame.display.update()      
            
Main()