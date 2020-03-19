import pygame
from os import path
import math
import os

import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(' ')

FPS=60
DIALATION = 60/FPS

# Default Resolution
DEFAULT_screen_x=1920
DEFAULT_screen_y=1080

screen_x=DEFAULT_screen_x
screen_y=DEFAULT_screen_y

debugger=False

ASSETS_PATH="\\assets\\"
def get_image(name):
    Path=os.getcwd() + ASSETS_PATH + name
    return (pygame.image.load(Path))

try:
    icon=get_image("icon.ico")
except:
    ASSETS_PATH = "/assets/"
    print("Unix file structure detected!")
else:
    print("Windows file structure detected!")

pygame.display.set_icon(icon)
pygame.display.set_caption('Hot Potato')

class Platform():
    height=3
    numPieces=14
    speed=.4*DIALATION
    def __init__(self,startingLocation,ID):
        self.ID=ID
        self.y=startingLocation
        #Width of each piece, ensuring there is extra room on each end
        self.pieceWidth = screen_x / (self.numPieces+2)

        self.pieces = []
        for i in range(self.numPieces):
            self.pieces.append(Piece(self.pieceWidth, self.height, (i+1)*self.pieceWidth+2*i-self.numPieces, self.y, i))

    def update(self):
        #print("Platform y:" + str(int(self.y)))
        self.y += self.speed
        #Looping platform back to top
        if self.y > screen_y:
            self.y = 0

        #Updating the pieces
        for piece in self.pieces[:]:
            if piece.health <= 0:
                self.pieces.remove(piece)
            else:
                piece.update(self.y)
   #     for piece in self.pieces:
    #        piece.update(self.y)

class Piece():
    maxHealth=3
    hit=False
    def __init__(self,width,height,x,y,ID):
        self.ID=ID
        self.width=width
        self.height=height
        self.health=self.maxHealth
        self.x=x
        self.y=y

    def update(self,y):
        self.y=y
        #update color based on current health %
        self.color = int(self.health * 255 / self.maxHealth)

        if self.color > 255:
            self.color == 255
        elif self.color < 0:
            self.color = 0
        self.rect = pygame.draw.rect(screen, (self.color,self.color,self.color),(int(self.x),int(self.y),int(self.width),int(self.height)))

class Sprite():
    #Default variables
    GRAVITY_ACCELERATION = .2
    TERMINAL_VELOCITY = 6
    LATERAL_SPEED=0
    
    onGround=False
    willBeOnGround=False

    futurePieces=[]
    futurePlatform=None

    velocity=0
    model=None
    isPlayer=False
    movement=0
    playerDown=False
    bottomSurfHeight=4
    def Move(self):
        if self.onGround:
        #if on ground, move at same speed downwards as platforms to stay on them
            self.y += platforms[0].speed
        #if not on ground, fall
        else:
            if self.playerDown:
                self.velocity -= self.GRAVITY_ACCELERATION * 2
            else:
                self.velocity -= self.GRAVITY_ACCELERATION
            #staying under/at terminal falling velocity
            if self.velocity < -1 * self.TERMINAL_VELOCITY:
                self.velocity = -1 * self.TERMINAL_VELOCITY
            
            self.y -= self.velocity
            


    
    def mainUpdate(self):
        self.bottomRect = screen.blit(self.bottomSurf, (int(self.x),int(self.height+self.y+-self.TERMINAL_VELOCITY)))
        if debugger:
            
            self.futureSurf.fill((0,255,0))
            self.bottomSurf.fill((0,0,255))
        if self.onGround:
            self.futureRect = screen.blit(self.futureSurf, (int(self.x),int(self.y+self.height ) ) )
        else:
            self.futureRect = screen.blit(self.futureSurf, (int(self.x+self.movement),int(self.y - (self.velocity + self.GRAVITY_ACCELERATION) + self.height ) ) )
        
        if self.model != None:
            self.blit = screen.blit(self.model,(int(self.x),int(self.y)))
        else:
            self.blit = pygame.draw.rect(screen, (self.color,self.color,self.color),(int(self.x),int(self.y),int(self.width),int(self.height)))

class Spring(Sprite):
    jumpMult=1.5
    
    color=120
    width=30
    height=20
    springing=0
    sprang=60
    def __init__(self,x,y):
        global springs
        global sprites
        
        sprites.append(self)
        springs.append(self)
        self.DEFAULT_height=self.height
        
        self.TERMINAL_VELOCITY = terminalVelocityCalc(self.height,self.width,self.GRAVITY_ACCELERATION)
        print("Terminal Velocity: ",self.TERMINAL_VELOCITY)
        self.bottomSurf = pygame.Surface((int(self.width),int(self.TERMINAL_VELOCITY+Platform.height)), pygame.SRCALPHA)
        self.futureSurf = pygame.Surface((int(self.width),int(self.TERMINAL_VELOCITY+Platform.height)), pygame.SRCALPHA)

        self.x=x
        self.y=y

    def update(self):
        #make this a trapezoid ideally, right now its just two triangles
        #self.shape=pygame.draw.polygon(screen,(80,100,120),[(self.x,self.y),(self.x+self.width,self.y),(self.x,self.y+self.height),(self.x+self.width,self.y+self.height)])
        
        self.Move()
        
        if self.springing > 0:
            self.springing -= 1
            self.y += self.DEFAULT_height/self.sprang
            self.height -= self.DEFAULT_height/self.sprang
        elif self.height != self.DEFAULT_height:
            self.height = self.DEFAULT_height
            self.y -= self.DEFAULT_height
            
        self.mainUpdate()

class Dragon(Sprite):
    model = get_image("biggererDragon.png")
    width, height = model.get_size()
    def __init__(self,x,y):
        self.x, self.y=x,y
        
    def update(self):
        self.mainUpdate()

class Fire(Sprite):
    #model = None #for now
    #width, height = model.get_size()
    def __init__(self,x,y):
        self.x=x
        self.y=y
    
def jumpHeight(height,gravity):
  # t = time j = initialJumpVelocity h = jumpHeight g = gravityAccelerationConstant
  #  h=t(j-tg/2)
  # t=0,2j/g make h=0, thus vertex is j/g, or (0 + 2j/g) / 2
  # j^2/2g = h
  # sqrt(2gh) = j

  # input intended height and gravity constant, output initial velocity needed

    return math.sqrt(2 * height * gravity)

def terminalVelocityCalc(height,width,gravity):
    # height * width = mass (roughly in a 2 dimensional space)
    # sqrt(mass * gravityAccelerationConstant)

    return math.sqrt(height*width*gravity)

class Player(Sprite):
    isPlayer=True
    model = get_image("potato.png")
    width, height = model.get_size()
    
    LATERAL_SPEED = 8

    lateral=0
    movement=0
    jumps=0
    def __init__(self,x,y):
        global sprites
        sprites.append(self)
        self.x,self.y=x,y
        
        self.TERMINAL_VELOCITY = terminalVelocityCalc(self.height,self.width,self.GRAVITY_ACCELERATION)
        print("Terminal Velocity: ",self.TERMINAL_VELOCITY)
        self.bottomSurf = pygame.Surface((int(self.width),int(self.TERMINAL_VELOCITY+Platform.height)), pygame.SRCALPHA)
        self.futureSurf = pygame.Surface((int(self.width),int(self.TERMINAL_VELOCITY+Platform.height)), pygame.SRCALPHA)
        self.jumpVelocity=int(jumpHeight(self.height*2,self.GRAVITY_ACCELERATION))

    def update(self):
        
        self.Move()

        if self.onGround:
            #Resetting on ground
            self.jumps=0
        else:
            while self.lateral >= 1:
                self.x += 1
                self.lateral-=1
                self.movement+=1
            while self.lateral <= -1:
                self.x-=1
                self.lateral+=1
                self.movement-=1
        self.mainUpdate()       
        self.movement=0
    def jump(self):
        self.onGround=False
        #If player has already jumped once, hard set velocity to jumpVelocity
        if self.jumps > 0:
            self.velocity = self.jumpVelocity
        else:
            if self.velocity >= 0:
                self.velocity += self.jumpVelocity
            else:
                self.velocity = self.jumpVelocity
        self.jumps+=1
        
    def user_input(self,events,pressed):
        
        global done
        for event in events:
            if event.type == pygame.QUIT:
                done=True
                break
            elif event.type == pygame.KEYDOWN:
            
                if event.key == pygame.K_DOWN:
                    self.playerDown=True
                else:
                    self.playerDown=False
                if event.key == pygame.K_ESCAPE:
                    done=True
                    break
                if ((event.key == pygame.K_UP or event.key == pygame.K_w) or event.key == pygame.K_SPACE):
                    if self.onGround or self.jumps == 1:
                        self.jump()
                        
        if not self.onGround:
            if pressed[pygame.K_LEFT] or pressed[pygame.K_a]: 
                self.lateral-=self.LATERAL_SPEED

            if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]: 
                self.lateral+=self.LATERAL_SPEED

def main():
    global screen
    global player
    global clock
    global done
    global platforms
    global debugger
    global DIALATION
    global springs
    global sprites
    
    springs=[]
    sprites=[]
    platforms=[]
    #Given number of platforms, setting equal distance between each one
    numPlatforms=5
    distBetweenPlatforms = screen_y / numPlatforms
    print("numPlatforms: ",numPlatforms)
    new_platform=screen_y-distBetweenPlatforms
    for i in range(numPlatforms):
        new_platform -= distBetweenPlatforms
        platforms.append(Platform(new_platform,i))

    print("initializing pygame")

    pygame.init()
    clock=pygame.time.Clock()

    #Adjusting sprite constants to resolution size and fps
    #Dialation is set to fps/60 (ideal 60 fps) * current resolution / default resolution
    spriteClasses=[Spring,Player,Dragon]
    resolutionRatio=screen_x/DEFAULT_screen_x
    DIALATION*=resolutionRatio
    for sprite in spriteClasses:
    
        sprite.LATERAL_SPEED *= DIALATION
        sprite.GRAVITY_ACCELERATION *= DIALATION
        sprite.TERMINAL_VELOCITY *= DIALATION
        
        sprite.width = sprite.width * resolutionRatio
        sprite.height = sprite.height * resolutionRatio
        
        #if sprite isn't just a built in rectangle, transform model
        if sprite.model != None:
            print("Scaling " + str(sprite).split(".")[1].split("\'")[0] + " Model.")
            sprite.model=pygame.transform.scale(sprite.model, (int(sprite.width), int(sprite.height)))

    #Initializing player
    player=Player(200,5)
    Spring(400,10)
    
    print("Y: ",player.height," X: ",player.width)
    print("Jump Height: " + str(player.jumpVelocity))

    # Font is default with None, size 24
    font = pygame.font.Font(None, 24)
    
    #initial categorization of sprites into their corresponding list because i can't be bothered
   # for sprite in sprites:
    #    if isinstance(sprite, Spring) and sprite not in springs:
    #        springs.append(sprite)
    
    ##########################
    #Main frame by frame loop#
    ##########################
    done=False
    dragon=Dragon((screen_x-Dragon.width)/2,-20)
    temp=0
    while not done:

        screen.fill((20,20,0))

        if debugger:
            text = font.render("Vertical Velocity:" + str(int(player.velocity)) + " player.jumps: " + str(player.jumps) + " Player on Ground?:" + str(player.onGround), True, (0, 128, 0))
            screen.blit(text,(0,0))
        
        for platform in platforms:
            platform.update()

        # every keypress or event per frame, used for lateral movement
        events = pygame.event.get()       
        # every change in keypress status, used for jumping
        pressed = pygame.key.get_pressed()              

        player.user_input(events,pressed)
        for sprite in sprites:
            sprite.justFallen=False
            sprite.update()
        # testing if springs should activate on player, propelling them upwards
        for spring in springs:
            if spring.blit.colliderect(player.bottomRect):
                spring.springing=spring.sprang
                player.velocity = player.jumpVelocity*spring.jumpMult
                if player.onGround:
                    player.onGround=False

        for sprite in sprites:

            # if sprite goes off screen, put it back to the top like a platform. Player isn't so fortunate
            if sprite.y > screen_y:
                if not sprite.isPlayer:
                    sprite.y = 0
                else:
                    sprites.remove(sprite)
                    print("Player fell off the screen!")
                    done=True
                    break
            # turn x around if off screen
            if sprite.x > screen_x:
                sprite.x=0
            elif sprite.x <= 0:
                sprite.x=screen_x
            
            # checking whether sprite should be on ground when it isn't
            if not (sprite.onGround or sprite.justFallen) and sprite.velocity <= 0:
            # If fast enough for bottomRect to pass straight through piece and it didn't detect something 
            # last frame already, use future model for collisions this frame. else use normal bottomRect
                if sprite.velocity <= -1 * (Platform.height + sprite.bottomSurfHeight) and not sprite.willBeOnGround:
                    sprite.tempRect = sprite.futureRect
                else:
                    sprite.tempRect = sprite.bottomRect
                    
                for platform in platforms:
                    for piece in platform.pieces:
                        # if piece was told by futureRect to be hit, reset future variables and put sprite on piece
                        if piece.ID in sprite.futurePieces and platform.ID == sprite.futurePlatform:
                            piece.hit=True
                            sprite.y=piece.y-sprite.height
                            sprite.willBeOnGround=False
                            sprite.futurePieces.remove(piece.ID)

                        # if there is a collision while falling
                        elif sprite.tempRect.colliderect(piece.rect):
                            # if futureRect is handling collisions, set future variables for next frame's collision
                            if sprite.tempRect == sprite.futureRect:
                                sprite.willBeOnGround=True
                                sprite.futurePieces.append(piece.ID)
                                sprite.futurePlatform=platform.ID
                            # otherwise, set this piece to hit for the current frame
                            elif sprite.tempRect == sprite.bottomRect:
                                piece.hit=True

                        if piece.hit:
                            piece.health-=1
                            piece.hit=False
                            # If piece won't break, put player on ground 
                            if piece.health != 0:
                                print("<" + str(sprite).split(".")[1] + ' Just hit ' + str(piece).split(".")[1])
                                sprite.onGround=True
                                sprite.velocity=0

                            # else if piece will break, say it and test if any other sprites should fall
                            else:
                                print(str(sprite).split(".")[1] + " Just broke ",str(piece).split(".")[1])
                                for otherSprite in sprites:
                                    # test only for sprites besides the current one, and ones that are already falling
                                    if otherSprite is not sprite and otherSprite.onGround:
                                        if otherSprite.futureRect.colliderect(piece.rect) or int(otherSprite.y+otherSprite.height) == int(platform.y):
                                            print("And that sprite is on at least one of the pieces that just broke!")
                                            # check for if this other sprite is on any other piece that would keep it from falling that isn't set to be destroyed as well
                                            for otherPiece in platform.pieces:
                                                if (otherSprite.futureRect.colliderect(otherPiece.rect) and otherPiece != piece) and not (otherPiece.hit and otherPiece.health == 1):
                                                    print("its got another piece to stick to though, so it isn't falling")
                                                    break
                                            else:
                                                print(str(otherSprite).split(".")[1] + " is also falling!")
                                                otherSprite.onGround=False
                                                otherSprite.justFallen=True

                    if sprite.futurePieces == []:
                        sprite.futurePlatform=None
        dragon.blit=screen.blit(dragon.model,(int(dragon.x),int(dragon.y)))
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    #If run without startup menu, default to lowest resolution and debugging mode
    debugger=True
    screen_x=1024
    screen_y=576
    screen = pygame.display.set_mode((screen_x,screen_y))
    main()