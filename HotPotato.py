import pygame
from os import path
import math
import os
import itertools
import ctypes
import random

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(' ')

FPS=60
TIME_DIALATION = 60/FPS

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


def makeSheet(sheet, width, height):
    
    totalWidth, totalHeight = sheet.get_size()
    column=int(totalWidth/width)
    row=int(totalHeight/height)
    x=0
    y=0
    images=[]
    for j in range(row):
        for i in range(column):
            rect = pygame.Rect( x+i*width,y+j*height,width,height )
            image = pygame.Surface(rect.size)
            image.blit(sheet,(0,0),rect)
            image.set_colorkey(0, pygame.RLEACCEL)
            images.append(image)
    return images
    
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
    speed=.4*TIME_DIALATION
    def __init__(self,startingLocation,ID):
        self.ID=ID
        self.y=startingLocation
        #Width of each piece, ensuring there is extra room on each end
        self.pieceWidth = screen_x / (self.numPieces+2)
        
        self.border=2
        self.pieces = []
        for i in range(self.numPieces):
            self.pieces.append(Piece(self.pieceWidth, self.height, (i+1)*self.pieceWidth+self.border*i-self.numPieces, self.y, i))

    def update(self):
        self.y += self.speed
        #Looping platform back to top
        if self.y > screen_y:
            self.y = 0

        #Updating the pieces
        for piece in self.pieces[:]:
            if piece.health <= 0:
                
                for sprite in sprites:
                    if sprite.onGround and sprite.futureRect.colliderect(piece.rect):
                            # check for if this other sprite is on any other piece that would keep it from falling that isn't set to be destroyed as well
                            for otherPiece in self.pieces:
                                    if (sprite.futureRect.colliderect(otherPiece.rect) and otherPiece != piece) and otherPiece.health > 0:
                                        break
                            else:
                                sprite.onGround=False
                if piece.fire != None:
                    fires.remove(piece.fire)                
                self.pieces.remove(piece)
                
            else:
                piece.update(self.y)


class Piece():
    maxHealth=3
    hit=False
    fire=None
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
    pieceDamage=1
    persistent=True
    def __init__(self,x,y):
        global sprites
        sprites.append(self)
        self.x,self.y=x,y
        
        self.TERMINAL_VELOCITY = terminalVelocityCalc(self.height,self.width,self.GRAVITY_ACCELERATION)
        print("Terminal Velocity: ",self.TERMINAL_VELOCITY)
        self.bottomSurf = pygame.Surface((int(self.width),4), pygame.SRCALPHA)
        self.futureSurfHeight=self.TERMINAL_VELOCITY+Platform.height
        self.futureSurf = pygame.Surface((int(self.width),int(self.futureSurfHeight)), pygame.SRCALPHA)
        try:
            self.secondInit()
        except AttributeError:
            pass
            
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
        self.bottomRect = screen.blit(self.bottomSurf, (int(self.x),int(self.height+self.y-2)))
        if debugger:
            self.futureSurf.fill((0,255,0))
            self.bottomSurf.fill((0,0,255))
        if self.onGround:
            self.futureRect = screen.blit(self.futureSurf, (int(self.x),int(self.y+self.height ) ) )
        else:
            self.futureRect = screen.blit(self.futureSurf, (int(self.x+self.movement),int(self.y - self.velocity - self.futureSurfHeight + self.GRAVITY_ACCELERATION + self.height ) ) )
        
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
    def secondInit(self):
        global springs
        springs.append(self)
        self.DEFAULT_height=self.height

    def update(self):
        #make this a trapezoid ideally, right now its just two triangles
        #self.shape=pygame.draw.polygon(screen,(80,100,120),[(self.x,self.y),(self.x+self.width,self.y),(self.x,self.y+self.height),(self.x+self.width,self.y+self.height)])
        
        self.Move()
        
        if self.springing > 0:
            self.springing -= 1
            self.y += self.DEFAULT_height/self.sprang
            self.height -= self.DEFAULT_height/self.sprang
        if self.height != self.DEFAULT_height and self.springing == 0:
            self.height = self.DEFAULT_height
            self.y -= self.DEFAULT_height
            
        self.mainUpdate()

class Dragon():
    model = get_image("dragon.png")
    #sheet dimensions
    width, height = model.get_size()
    width*=2
    height*=2
    model=pygame.transform.scale(model, (int(width), int(height)))

    origWidth, origHeight = width, height
    #individual sprite dimensions
    smallWidth, smallHeight = 191*2, 161*2
    
    direction=1
    animations=[]
    
    timerMax=int(16*TIME_DIALATION)
    timer=timerMax-1
    breathFire=True
    def __init__(self):
    
        #setting width/height to sprite dimensions 
        self.width = int(self.width/self.origWidth * self.smallWidth)
        self.height = int(self.height/self.origHeight * self.smallHeight)
        self.sheet=makeSheet(self.model,self.width,self.height)
        
        self.upIter=itertools.cycle(self.sheet[0:3])
        self.rightIter=itertools.cycle(self.sheet[3:6])
        self.downIter=itertools.cycle(self.sheet[6:9])
        self.leftIter=itertools.cycle(self.sheet[9:12])

        self.animations=[self.upIter,self.rightIter,self.downIter,self.leftIter]
        
        self.x=-1 * self.width
        self.y=-40

    def update(self):
        if self.x < int((screen_x-self.width)/2):
            self.x+=3
            if self.x >= screen_x:
                boss=None
        else:
            if self.breathFire:
                self.direction = 2
                self.fireball=Fireball(self.x + self.width/2,self.y + self.height/2)
                self.breathFire=False
            if self.fireball not in sprites:
                self.x+=3
                self.direction=1
            
        
        self.timer+=1
        if self.timer == self.timerMax:
            self.timer=0
            self.model=next(self.animations[self.direction])
        self.blit = screen.blit(self.model,(int(self.x),int(self.y)))

class Fireball(Sprite):
    model = get_image("fireball.png")
    width, height = model.get_size()
    width*=.8
    height*=.8
    model=pygame.transform.scale(model, (int(width), int(height)))

    origWidth, origHeight = width, height
    smallWidth, smallHeight = (width/6), (height/4)
    
    timerMax=(int(12*TIME_DIALATION))
    timer=timerMax-1
    LATERAL_SPEED = 8
    persistent=False
    pieceThrough=False
    pieceDamage=3
    def secondInit(self):
        self.width = int(self.width/self.origWidth * self.smallWidth)
        self.height = int(self.height/self.origHeight * self.smallHeight)
        self.sheet=makeSheet(self.model,self.width,self.height)
        self.animation=itertools.cycle(self.sheet)
        
        self.direction=random.choice([-1,1])
        self.LATERAL_SPEED *= self.direction
        
        self.TERMINAL_VELOCITY = terminalVelocityCalc(self.height,self.width,self.GRAVITY_ACCELERATION)
        print("Terminal Velocity: ",self.TERMINAL_VELOCITY)
        self.bottomSurf = pygame.Surface((int(self.width),4), pygame.SRCALPHA)
        self.futureSurfHeight=self.TERMINAL_VELOCITY+Platform.height
        self.futureSurf = pygame.Surface((int(self.width),int(self.futureSurfHeight)), pygame.SRCALPHA)
        
    def pieceInteraction(self,piece,platform):
        if not platform.pieces[piece].fire:
            fires.append( Fire(platform,piece) )
            if self.pieceThrough:
                self.pieceDamage=0
            else:
                self.pieceThrough=True

    def update(self):
        self.Move()
        if self.onGround:
            self.LATERAL_SPEED=0
        
        self.x += int(self.LATERAL_SPEED)
        if self.LATERAL_SPEED > 0:
            self.LATERAL_SPEED -= self.GRAVITY_ACCELERATION / 2
        elif self.LATERAL_SPEED < 0:
            self.LATERAL_SPEED += self.GRAVITY_ACCELERATION / 2
        
        self.timer+=1
        if self.timer == self.timerMax:
            self.timer=0
            self.model=next(self.animation)
        self.mainUpdate()

class Fire():
    model = get_image('fire.png')
    width, height = model.get_size()
    width/=2
    height/=2
    model=pygame.transform.scale(model, (int(width), int(height)))

    origWidth, origHeight = width, height
    smallWidth, smallHeight = int(130/2), int(151/2)
    
    timerMax=int(18*TIME_DIALATION)
    timer=timerMax-1
    decay=0
    grow=0
    direction=0
    def __init__(self,platform,location):
        self.piece = platform.pieces[location]
        self.piece.fire=self
        self.location=location
        self.platform=platform
        self.width = int(self.width/self.origWidth * self.smallWidth)
        self.height = int(self.height/self.origHeight * self.smallHeight)
       
        self.x = self.piece.x + (self.piece.width - self.width)/2
        self.y = self.piece.y - self.height
        
        self.animations=[itertools.cycle(makeSheet(self.model,self.width,self.height))]
        
        if random.random() < 0.5:  
            next(self.animations[0])
    def update(self):

        self.location=self.platform.pieces.index(self.piece)
        global fires
        self.timer+=1
        if self.timer == self.timerMax:
            self.timer=0

            if self.grow == 2:
                self.grow=0
                dontMove=[]

                # if fire is at end of platform, don't spread there
                if (self.platform.pieces.index(self.piece) == len(self.platform.pieces) - 1):
                    dontMove.append(1)
                # if fire is at beginning of platform, don't move there
                elif self.platform.pieces.index(self.piece) == 0:
                    dontMove.append(-1)

                # if there is already a fire at ahead or behind, don't spread there
                for fire in fires:
                    if fire.platform == self.platform:
                        if fire.location + 1 == self.location:
                            dontMove.append(-1)
                        elif fire.location -1 == self.location:
                            dontMove.append(1)
                # only spread on pieces that are adjacent to current piece            
                if self.platform.pieces[self.location+1].x - self.platform.border != self.piece.x+self.piece.width:
                        dontMove.append(1)
                if self.platform.pieces[self.location-1].x + self.platform.pieces[self.location-1].width + self.platform.border != self.piece.x:
                        dontMove.append(-1)

                if 1 in dontMove and -1 in dontMove:
                    move=0
                elif 1 in dontMove:
                    move=-1
                elif -1 in dontMove:
                    move=1
                else:
                    move=random.choice([-1,1])
                
                if move != 0:
                    fires.append(Fire(self.platform,move+self.location) )

            if self.decay == 8:
                self.decay=0
                self.grow+=1
                self.piece.health-=1
                if self.piece.health == 0:
                    return
            self.decay+=1

            self.model=next(self.animations[self.direction])
        self.y = self.piece.y - self.height
        self.blit = screen.blit(self.model,(int(self.x),int(self.y)))

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
    persistent=False
    def secondInit(self):
    
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
            
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
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
    global TIME_DIALATION
    global springs
    global sprites
    global fires
    global boss
    
    springs=[]
    sprites=[]
    platforms=[]
    fires=[]
    boss=None
    
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
    
    spriteClasses=[Spring,Player,Dragon,Fire,Fireball]
    
    resolutionRatio=screen_x/DEFAULT_screen_x
    DIALATION=resolutionRatio*TIME_DIALATION
    for sprite in spriteClasses:
        try:
            sprite.LATERAL_SPEED *= DIALATION
            sprite.GRAVITY_ACCELERATION *= DIALATION
            sprite.TERMINAL_VELOCITY *= DIALATION
        except AttributeError:
            pass
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
    
    ##########################
    #Main frame by frame loop#
    ##########################
    done=False
    boss=Dragon()
   # fires.append(Fire(platforms[0],2))
   # fireball=Fireball(200,20)
    while not done:

        screen.fill((20,20,0))

        if debugger:
            text = font.render("Vertical Velocity:" + str(int(player.velocity)) + " Player on Ground?:" + str(player.onGround) + " fps: " + str(int(clock.get_fps())), True, (0, 128, 0))
            screen.blit(text,(0,0))

        for platform in platforms:
            platform.update()
        for fire in fires:
            fire.update()

        # every keypress or event per frame, used for lateral movement
        events = pygame.event.get()       
        # every change in keypress status, used for jumping
        pressed = pygame.key.get_pressed()              
        player.user_input(events,pressed)

        if boss != None:
            boss.update()

        for sprite in sprites:
            sprite.justFallen=False
            sprite.update()

        # testing if springs should activate on player, propelling them upwards
        for spring in springs:
            if spring.blit.colliderect(player.bottomRect) and spring.springing == 0:
                spring.springing=spring.sprang
                player.velocity = player.jumpVelocity*spring.jumpMult
                if player.onGround:
                    player.onGround=False

        for sprite in sprites:

            # if sprite goes off screen, put it back to the top like a platform. Player isn't so fortunate
            if sprite.y > screen_y:
                if sprite.persistent:
                    sprite.y = 0
                else:
                    sprites.remove(sprite)
                    if sprite.isPlayer:
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

                        # if there is a collision while falling and there aren't any collisions being handled this frame
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
                            if piece.fire != None and not isinstance(sprite, Fireball):
                                fires.remove(piece.fire)
                                piece.fire = None
                            if callable(getattr(sprite, "pieceInteraction", None)):
                                sprite.pieceInteraction(platform.pieces.index(piece),platform)

                            piece.health-=sprite.pieceDamage
                            piece.hit=False
                            # If piece won't break, put player on ground 
                            if piece.health > 0:
                                print("<" + str(sprite).split(".")[1] + ' Just hit ' + str(piece).split(".")[1])
                                sprite.onGround=True
                                sprite.velocity=0

                            # else if piece will break, say it and test if any other sprites should fall
                            else:
                                print(str(sprite).split(".")[1] + " Just broke ",str(piece).split(".")[1])
                       #         for otherSprite in sprites:
                        #            # test only for sprites besides the current one, and ones that are already falling
                        #            if otherSprite is not sprite and otherSprite.onGround:
                        #                if otherSprite.futureRect.colliderect(piece.rect):
                        #                    print("another sprite is on at least one of the pieces that just broke!")
                        #                    # check for if this other sprite is on any other piece that would keep it from falling that isn't set to be destroyed as well
                         #                   for otherPiece in platform.pieces:
                        #                            if (otherSprite.futureRect.colliderect(otherPiece.rect) and otherPiece != piece) and ( (otherPiece.hit or otherPiece.ID in sprite.futurePieces) and otherPiece.health <= sprite.pieceDamage):
                         #                               print("its got another piece to stick to though, so it isn't falling")
                         #                               break
                         #                   else:
                         #                       print(str(otherSprite).split(".")[1] + " is also falling!")
                          #                      otherSprite.onGround=False
                         #                       otherSprite.justFallen=True

                    if sprite.futurePieces == []:
                        sprite.futurePlatform=None

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    #If run without startup menu, default to lowest resolution and debugging mode
    debugger=True
    screen_x=1024
    screen_y=576
    screen = pygame.display.set_mode((screen_x,screen_y))
    main()