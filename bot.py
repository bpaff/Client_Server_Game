'''
INF 123 Midterm Part 1
By Brian Paff
94135229
'''
from time import sleep
from network import Handler, poll
from random import randint




######################## Model #########################
def collide_boxes(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    return x1 < x2 + w2 and y1 < y2 + h2 and x2 < x1 + w1 and y2 < y1 + h1
    

class Model():
    bot_ate_pellet = False
    cmd_directions = {'up': (0, -1),
                      'down': (0, 1),
                      'left': (-1, 0),
                      'right': (1, 0)}
    
    def __init__(self,):
        self.borders = [[0, 0, 2, 300],
                        [0, 0, 400, 2],
                        [398, 0, 2, 300],
                        [0, 298, 400, 2]]
        self.pellets = [ [randint(10, 380), randint(10, 280), 5, 5]
                        for _ in range(4) ]
        self.game_over = False
        self.mydir = self.cmd_directions['down'] # start direction: down
        self.mybox = [200, 150, 10, 10] # start in middle of the screen
    
    def initialize(self, borders, pellets, mybox):
        self.borders = borders
        self.pellets = pellets
        self.game_over = False
        self.mydir = self.cmd_directions['down'] # start direction: down
        self.mybox = mybox # start in middle of the screen
        
    def do_cmd(self, cmd):
        if cmd == 'quit':
            self.game_over = True
        else:
            self.mydir = self.cmd_directions[cmd]
            
    def update_server(self, mybox, pels):
        self.pellets = pels
        
    def grew(self, serv_me):
        x1, y1, w1, h1 = serv_me
        x2, y2, w2, h2 = self.mybox
        if w1 > w2:
            self.bot_ate_pellet = True
    
    def update(self):
        # move me
        self.mybox[0] += self.mydir[0]
        self.mybox[1] += self.mydir[1]
        # potential collision with a border
        for b in self.borders:
            if collide_boxes(self.mybox, b):
                self.mybox = [200, 150, 10, 10]
        # potential collision with a pellet
        '''for index, pellet in enumerate(self.pellets):
            if collide_boxes(self.mybox, pellet):
                self.mybox[2] *= 1.2
                self.mybox[3] *= 1.2
                self.pellets[index] = [randint(10, 380), randint(10, 280), 5, 5]
                #print "**** Bot ate a pellet ****"'''
                
################### RANDOM CONTROLLER #####################

'''class RandomBotController():
    def __init__(self, m):
        self.m = m
        self.cmds = ['up', 'down', 'left', 'right']
        
    def poll(self):
        self.m.do_cmd(choice(self.cmds))
'''       
################### CONTROLLER #############################
class SmartBotController():
    def __init__(self, m):
        self.m = m
        
    def poll(self):
        p = self.m.pellets[0] # always target the first pellet
        b = self.m.mybox
        if p[0] > b[0]:
            cmd = 'right'
        elif p[0] + p[2] < b[0]: # p[2] to avoid stuttering left-right movement
            cmd = 'left'
        elif p[1] > b[1]:
            cmd = 'down'
        else:
            cmd = 'up'
        self.m.do_cmd(cmd)
        msg = {'input': cmd}
        client.do_send(msg)
        
        
        

################### CONSOLE VIEW #############################

class ConsoleView():
    printed_connected = False
    def __init__(self, m):
        self.m = m
        self.frame_freq = 20
        self.frame_count = 0
        
    def display(self):
        if client.connected == True:
            if self.printed_connected == False:
                self.printed_connected = True
                print "**** Connected to the server ****"
        if client.connected == False:
            if self.printed_connected == True:
                self.printed_connected = False
                print "**** Disconnected from the server ****"
        if model.bot_ate_pellet == True:
            model.bot_ate_pellet = False
            print "**** Bot ate a pellet ****"
        self.frame_count += 1
        if self.frame_count == self.frame_freq:
            self.frame_count = 0
            #b = self.m.mybox
            #print 'Position: %d, %d' % (b[0], b[1])


################### PYGAME VIEW #############################
# this view is only here in case you want to see how the bot behaves

import pygame

class PygameView():
    
    def __init__(self, m):
        self.m = m
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        
    def display(self):
        pygame.event.pump()
        screen = self.screen
        borders = [pygame.Rect(b[0], b[1], b[2], b[3]) for b in self.m.borders]
        pellets = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in self.m.pellets]
        b = self.m.mybox
        myrect = pygame.Rect(b[0], b[1], b[2], b[3])
        screen.fill((0, 0, 64)) # dark blue
        pygame.draw.rect(screen, (0, 191, 255), myrect) # Deep Sky Blue
        [pygame.draw.rect(screen, (255, 192, 203), p) for p in pellets] # pink
        [pygame.draw.rect(screen, (0, 191, 255), b) for b in borders] # red
        pygame.display.update()
        
################## Client ############################
class Client(Handler):
    connected = False
    def on_close(self):
        global keep_going
        keep_going = False
        
    def on_msg(self, msg):
        play = msg['players']
        myname = msg['myname']
        bord = msg['borders']
        me = play[myname]
        pellets = msg['pellets']
        model.update()
        model.grew(me)
        model.initialize(bord, pellets, me)
        if self.connected == False:
            self.connected = True
        #make it so if the size of yourself(after being sent back from the server) 
        #is bigger than youself now, then update your size and print a message
        sizew = me[3]
        if sizew > model.mybox[3]:
            print "merp"
            model.update_server(self.me, self.pellets) 
            
################### LOOP #############################


client = Client('localhost', 8888)
client.do_send({'input': 'join'})
model = Model()
c = SmartBotController(model)
v = ConsoleView(model)
v2 = PygameView(model)
#print "**** Connected to the server ****"
while not model.game_over:
    sleep(0.02)
    c.poll()
    poll()
    #model.update()
    v.display()
    v2.display()