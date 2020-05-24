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

sound_library={}
def play_sound(name):
    global sound_library
    sound = sound_library.get(name)
    if sound == None:
        sound = pygame.mixer.Sound(os.getcwd() + ASSETS_PATH + name)
        sound.set_volume(.025)
    sound.play()

pygame.display.set_icon(icon)
pygame.display.set_caption('Hot Potato')

platformSpeed=1.75*TIME_DIALATION
class Platform():
    height=3
    numPieces=14
    speed=platformSpeed
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
        self.speed=platformSpeed
        self.y += self.speed
        #Looping platform back to top
        if self.y > screen_y:
            self.y = 0

        #Updating the pieces
        for piece in self.pieces:
            if not piece.broken:
                if piece.health <= 0:
                    piece.broken=True
                    for sprite in sprites:
                        if sprite.onGround and sprite.futureRect.colliderect(piece.rect):
                            # check for if this sprite is on any other piece that would keep it from falling that isn't set to be destroyed as well
                            for otherPiece in self.pieces:
                                if (sprite.futureRect.colliderect(otherPiece.rect) and otherPiece != piece) and otherPiece.health > 0:
                                    break
                            else:
                                sprite.onGround=False
                                sprite.pieces=[]
                                sprite.platform=None
                    if piece.fire != None:
                        fires.remove(piece.fire)
                        piece.fire=None
                else:
                    if piece.fire != None:
                        piece.fire.update()
                    piece.update(self.y)
                

class Piece():
    maxHealth=3
    health=maxHealth
    hit=False
    fire=None
    broken=False
    def __init__(self,width,height,x,y,ID):
        self.ID=ID
        self.width=width
        self.height=height
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
    pieces=[]
    platform=None
    velocity=0
    model=None
    isPlayer=False
    movement=0
    playerDown=False
    bottomSurfHeight=4
    pieceDamage=1
    persistent=True
    justFallen=False
    effects={}
    blit=None
    effectMult=1
    def __init__(self,x,y):
        global sprites
        sprites.append(self)
        self.x,self.y=x,y
        self.setSurfs()
        try:
            self.secondInit()
        except AttributeError:
            pass

    def setSurfs(self):
        self.TERMINAL_VELOCITY = terminalVelocityCalc(self.height,self.width,self.GRAVITY_ACCELERATION)
        self.bottomSurf = pygame.Surface((int(self.width),4), pygame.SRCALPHA)
        self.futureSurfHeight=self.TERMINAL_VELOCITY+Platform.height
        self.futureSurf = pygame.Surface((int(self.width),int(self.futureSurfHeight)), pygame.SRCALPHA)
        self.jumpVelocity=int(jumpHeight(self.height*2,self.GRAVITY_ACCELERATION))

    def Move(self):
        global platformSpeed
        if self.onGround:
        #if on ground, move at same speed downwards as platforms to stay on them
            self.y += platformSpeed
        #if not on ground, fall
        else:
            if self.platform != None or len(self.pieces) != 0:
                self.pieces=[]
                self.platform=None
            # if sprite is a player holding down, triple its downward accleration
            if self.playerDown:
                if self.velocity > 0:
                    self.velocity /= 2
                self.velocity -= self.GRAVITY_ACCELERATION * 3
            else:
                self.velocity -= self.GRAVITY_ACCELERATION
            #staying under/at terminal falling velocity
            if self.velocity < -1 * self.TERMINAL_VELOCITY:
                self.velocity = -1 * self.TERMINAL_VELOCITY
            self.y -= self.velocity*self.effectMult

    def mainUpdate(self):
        for effect in list(self.effects):
            self.effects[effect].update()
        self.bottomRect = screen.blit(self.bottomSurf, (int(self.x),int(self.height+self.y-2)))
        if debugger:
            self.futureSurf.fill((0,255,0))
            self.bottomSurf.fill((0,0,255))
        if self.onGround:
            self.futureRect = screen.blit(self.futureSurf, (int(self.x),int(self.y+self.height-2 ) ) )
        else:
            self.futureRect = screen.blit(self.futureSurf, (int(self.x+self.movement),int(self.y - self.velocity - self.futureSurfHeight + self.GRAVITY_ACCELERATION + self.height ) ) )
        if self.model != None:
            self.blit = screen.blit(self.model,(int(self.x),int(self.y)))
        else:
            self.blit = pygame.draw.rect(screen, self.color,(int(self.x),int(self.y),int(self.width),int(self.height)))

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
    moreFireballTimer=0
    going=True
    fireball=None
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
        global fires
        global boss
        
        if self.x >= screen_x:
            boss=None
        elif self.x < int((screen_x-self.width)/2):
            self.x+=3
        else:
            self.going=False
            self.direction = 2
        if not self.going and self.breathFire:
            self.fireball=Fireball(self.x + self.width/2,self.y + self.height/2)
            self.breathFire=False
        if self.fireball is not None:
            if self.fireball not in sprites and self.x >= int((screen_x-self.width)/2):
                self.x+=3
                self.direction=1
                self.going=True
        self.timer+=1
        if self.timer == self.timerMax:
            if not self.going:
                self.moreFireballTimer+=1
                if self.moreFireballTimer == 15:
                    self.breathFire=True
                    self.moreFireballTimer=0
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
    
    persistent=False
    pieceThrough=False
    pieceDamage=Piece.maxHealth
    def secondInit(self):
        self.width = int(self.width/self.origWidth * self.smallWidth)
        self.height = int(self.height/self.origHeight * self.smallHeight)
        self.sheet=makeSheet(self.model,self.width,self.height)
        self.animation=itertools.cycle(self.sheet)

        self.LATERAL_SPEED = random.randint(4,10)
        self.direction=random.choice([-1,1])
        self.LATERAL_SPEED *= self.direction

        self.setSurfs()

    def pieceInteraction(self,piece,platform):
        if not platform.pieces[piece].fire:
            fires.append( Fire(platform,piece) )
        if not self.pieceThrough:
            
            if piece+1 != len(platform.pieces):
                if not platform.pieces[piece+1].fire:
                    fires.append ( Fire(platform,piece+1 ))
            
            if piece != 0:
                if not platform.pieces[piece-1].fire:
                    fires.append ( Fire(platform,piece-1 ))

            self.pieceThrough=True

    def update(self):

        self.Move()

        if self.pieceThrough:
            self.pieceDamage=0

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
                if (self.platform.pieces.index(self.piece) + 1 == len(self.platform.pieces) ):
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
                if 1 not in dontMove and self.platform.pieces[self.location+1].health <= 0:
                        dontMove.append(1)
                if -1 not in dontMove and self.platform.pieces[self.location-1].health <= 0:
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

class Pickup(Sprite):
    pieceDamage=0
    width, height = 30,20
    persistent=False
    health=1
    timerMax=60
    timer=0
    active=False
    def secondInit(self):
        global pickups
        pickups.append(self)
    @classmethod
    def rockInit(cls,x,y):
        inst=cls(x,y)
        inst.health=3
        inst.pieceDamage=2
        inst.color = (105,105,105)
        inst.active = None
        return inst
    def rockEffect(self,sprite):
        if not self.onGround:
            sprite.effects["RockStun"]=Effect.stunInit(120,self,sprite,"RockStunSlow")
    @classmethod
    def anvilInit(cls,x,y):
        inst=cls(x,y)
        inst.health=1
        inst.color = (153,163,255)
        inst.active = inst.anvilEffect
        return inst
    def anvilEffect(self,sprite):
        global platforms
        if self.onGround:
            self.health-=1
            if bool(random.getrandbits(1)):
                for piece in self.platform.pieces:
                    piece.health = piece.maxHealth
                    piece.broken = False
                    piece.y=self.platform.y
                    particleEffects.append(tuple(ParticleEffect((65,105,255),.045,piece.x,piece.y,piece.width,piece.height,platformSpeed*2,60,0)))
                    if piece.fire != None:
                        piece.fire=None
            else:
                for piece in self.pieces:
                    for platform in platforms:
                        for otherPiece in platform.pieces:
                            if platform.pieces.index(otherPiece) == self.platform.pieces.index(piece):
                                otherPiece.health=otherPiece.maxHealth
                                otherPiece.broken = False
                                otherPiece.y=platform.y
                                particleEffects.append(tuple(ParticleEffect((65,105,255),.045,otherPiece.x,otherPiece.y,otherPiece.width,otherPiece.height,platformSpeed*2,60,0)))
                                if otherPiece.fire != None:
                                    otherPiece.fire=None
    @classmethod
    def springInit(cls,x,y):
        inst=cls(x,y)
        inst.health=2
        inst.color = (255,200,145)
        inst.active = inst.springEffect
        inst.jumpMult = 1.5
        inst.pieceDamage=1
        inst.defHeight = inst.height
        return inst
    def springEffect(self,sprite):
        if self.timer == 0:
            self.health -= 1
            self.timer = 1
            if sprite.velocity > sprite.jumpVelocity/2:
                sprite.velocity += sprite.jumpVelocity*self.jumpMult*.75
            else:
                sprite.velocity = sprite.jumpVelocity*self.jumpMult
            if sprite.onGround:
                sprite.onGround=False
    def update(self):
        global pickups
        if self.health <= 0:
            pickups.remove(self)
            sprites.remove(self)
            return
        self.Move()
        if self.timer < self.timerMax and self.timer > 0:
            self.timer += 1
            self.y += self.defHeight/self.timerMax
            self.height -= self.defHeight/self.timerMax
        elif self.timer == self.timerMax:
            self.timer=0
            self.y -= self.defHeight
            self.height += self.defHeight
        self.mainUpdate()

class Ghost():
    model = get_image('ghost2.png')
    width, height = model.get_size()
    origWidth, origHeight = width, height
    smallWidth, smallHeight = (width/3), (height/4)
    speed = 1.4
    slowAmount=.5
    colliders=[]
    timerMax=int(24*TIME_DIALATION)
    timer=timerMax-1
    direction=None
    def __init__(self,x,y,initialTarget=None):
        enemies.append(self)
        self.x,self.y=x,y
        self.center=self.x+self.width/2,self.y+self.height/2
        self.target=initialTarget
        if type(self.target) is tuple:
            self.targetX,self.targetY=initialTarget
        else:
            self.targetX,self.targetY=int((self.target.x+self.target.width)/2),int((self.target.y+self.target.height)/2)
        
        self.width = int(self.width/self.origWidth * self.smallWidth)
        self.height = int(self.height/self.origHeight * self.smallHeight)
        self.sheet=makeSheet(self.model,self.width,self.height)
        
        self.downIter=itertools.cycle(self.sheet[0:3])
        self.leftIter=itertools.cycle(self.sheet[3:6])
        self.rightIter=itertools.cycle(self.sheet[6:9])
        self.upIter=itertools.cycle(self.sheet[9:12])
        
    def chase(self):
        self.center=self.x+self.width/2,self.y+self.height/2
        if type(self.target) is not tuple:
            self.targetX,self.targetY=int(self.target.x+(self.target.width/2)),int(self.target.y+(self.target.height/2))
        if self.center[0] > self.targetX and self.center[0] - self.targetX >= 1:
            self.x-=self.speed
            if self.direction != self.leftIter:
                self.timer=self.timerMax
            self.direction=self.leftIter
        elif self.center[0] < self.targetX and self.targetX - self.center[0] >= 1:
            self.x+=self.speed
            if self.direction != self.rightIter:
                self.timer=self.timerMax
            self.direction=self.rightIter
        elif self.center[1] > self.targetY and self.center[1] - self.targetY >= 1:
            self.y-=self.speed
            if self.direction != self.upIter:
                self.timer=self.timerMax
            self.direction=self.upIter
        elif self.center[1] < self.targetY and self.targetY - self.center[1] >= 1:
            self.y+=self.speed+platformSpeed
            if self.direction != self.downIter:
                self.timer=self.timerMax
            self.direction=self.downIter
        
    def effect(self,sprite):
        try:
            sprite.effects["GhostSlow"]
        except KeyError:
            sprite.effects["GhostSlow"] = Effect.slowInit(120,self,sprite,.4,.75,"GhostSlow")
            #particleEffects.append(tuple(ParticleEffect((65,105,255),.025,sprite.x,sprite.y,sprite.width,sprite.height,platformSpeed,60,0)))
        else:
            if sprite.effects["GhostSlow"].duration - sprite.effects["GhostSlow"].timer > 10:
                sprite.effects["GhostSlow"].reset()

    def update(self):
        for sprite in self.colliders:
            self.effect(sprite)
        self.timer+=1
        self.chase()
        if self.timer >= self.timerMax:
            self.model=next(self.direction)
            self.timer=0
        self.blit = screen.blit(self.model,(int(self.x),int(self.y)))

def ParticleEffect(color,concentration,x,y,width,height,velocity,lifeSpan,lateralVelocity):
    border=1
    for i in range(int((width+border*2)*(height+border*2)*concentration)):
        newParticle=Particle(x-border+random.randint(0,int(width+border*2)),y-border+random.randint(0,int(height+border*2)),color,velocity,lateralVelocity,lifeSpan)
        newParticle.update()
        yield newParticle

class Particle():
    width,height=1,1
    def __init__(self,x,y,color,velocity,lateralVelocity,lifeSpan):
        self.color=color
        self.x=x
        self.y=y
        if velocity != 0:
            self.velocity = random.uniform(velocity/2,velocity)
        else:
            self.velocity=0
        self.lateralVelocity=lateralVelocity
        self.lifeSpan=lifeSpan
    def update(self):
        self.x += self.lateralVelocity
        self.y += self.velocity
        self.lateralVelocity *= .8
        self.lifeSpan-=1
        self.blit = pygame.draw.rect(screen, self.color,(int(self.x),int(self.y),int(self.width),int(self.height)))

class Effect():
    mult=1
    def __init__(self,duration,source,target,key):
        self.duration=duration
        self.timer=duration
        self.source=source
        self.target=target
        self.key=key
        
    def update(self):
        if not self in self.target.effects.values():
            self.target.effectMult/=self.mult
        self.timer-=1
        if self.timer % 10 == 0:
            particleEffects.append(tuple(ParticleEffect(self.particleColor,.010,self.target.x,self.target.y,self.target.width,self.target.height,2,20,0)))
        if self.timer > 0:
            self.effect()
        else:
            self.target.effectMult/=self.mult
            del self.target.effects[self.key]

    def reset(self):
        self.target.effectMult/=self.mult
        self.timer=self.duration
        self.mult=1

    @classmethod
    def slowInit(cls,duration,source,target,strength,final,key):
        inst = cls(duration, source, target, key)
        inst.strength = strength
        inst.final = final
        inst.effect = inst.slow
        inst.change = final - strength

        inst.particleColor = (65,105,255)
        return inst

    def slow(self):
        self.target.effectMult/=self.mult
        if self.mult != self.final:
            self.mult=self.strength+self.change*(self.duration-self.timer)/self.duration
        self.target.effectMult*=self.mult
        
    @classmethod
    def stunInit(cls,duration,source,target,key):
        inst = cls(duration, source, target, key)
        inst.effect = inst.stun
        inst.particleColor = (230,230,250)
        return inst

    def stun(self):
        self.target.stunned=True
        if self.timer == 1:
            for effect in self.target.effects:
                if effect.effect == effect.stun:
                    break
            else:
                self.target.stun=False

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
    maxJumps=2
    maxExtraJumpTimer=120
    extraJumpTimer=maxExtraJumpTimer
    stun=False
    
    def secondInit(self):
        global player
        global distBetweenPlatforms
        player=self
        self.jumpVelocity=int(jumpHeight(distBetweenPlatforms,self.GRAVITY_ACCELERATION))
    def update(self):
        self.Move()
        if self.extraJumpTimer != self.maxExtraJumpTimer:
            self.extraJumpTimer += 1
        if self.onGround:
            #Resetting on ground
            self.jumps=0
        else:
            self.x += self.lateral*self.effectMult
            self.lateral=0
        self.mainUpdate()
    def jump(self):
        
        self.onGround=False
        #If player has already jumped once, hard set velocity to jumpVelocity
        if self.jumps >= 1:
            play_sound("wind.wav")
            self.velocity = self.jumpVelocity*self.effectMult
        else:
            if self.velocity >= 0:
                self.velocity += self.jumpVelocity*self.effectMult
            else:
                self.velocity = self.jumpVelocity*self.effectMult
        self.jumps+=1
        
    def user_input(self,events,pressed):
        global done
        for event in events:
            if event.type == pygame.QUIT:
                done=True
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done=True
                    break
                if self.stun:
                    if event.key == pygame.K_r:
                        main()
                else:
                    if ((event.key == pygame.K_UP or event.key == pygame.K_w) or event.key == pygame.K_SPACE):
                        if self.extraJumpTimer != self.maxExtraJumpTimer:
                            self.extraJumpTimer=self.maxExtraJumpTimer
                            self.jump()
                        elif self.onGround or self.jumps == self.maxJumps-1:
                            self.jump()
                            #print("player jumped at time "+str(int(mainTimer/FPS)))
        if not self.onGround and not self.stun:
            if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
                self.playerDown=True
            else:
                self.playerDown=False
            if pressed[pygame.K_LEFT] or pressed[pygame.K_a]: 
                self.lateral-=self.LATERAL_SPEED
            if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]: 
                self.lateral+=self.LATERAL_SPEED
scaled=False
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
    global pickups
    global FPS
    global platformSpeed
    global mainTimer
    global enemies
    global particleEffects
    global scaled
    global distBetweenPlatforms
    pickups=[]
    springs=[]
    sprites=[]
    platforms=[]
    fires=[]
    enemies=[]
    particleEffects=[]
    boss=None
    
    #Given number of platforms, setting equal distance between each one
    numPlatforms=5
    distBetweenPlatforms = screen_y / numPlatforms
    platformSpeed=distBetweenPlatforms/120
    print("platform speed",platformSpeed)
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
    spriteClasses=[Player,Dragon,Fire,Fireball,Pickup,Ghost]
    resolutionRatio=screen_y/DEFAULT_screen_y
    DIALATION=resolutionRatio*TIME_DIALATION
    if not scaled:
        scaled=True
        print("\n###Scaling sprite models###")
        for sprite in spriteClasses:
            try:
                sprite.LATERAL_SPEED *= DIALATION
                sprite.GRAVITY_ACCELERATION *= DIALATION
                sprite.TERMINAL_VELOCITY *= DIALATION
            except AttributeError:
                pass
            sprite.width *= resolutionRatio
            sprite.height *= resolutionRatio

            #if sprite isn't just a built in rectangle, transform model
            if sprite.model != None:
                print(str(sprite).split(".")[1].split("\'")[0])
                sprite.model=pygame.transform.scale(sprite.model, (int(sprite.width), int(sprite.height)))
    print("###\n")
    #Initializing player
    Player(random.randint(10+int(screen_x/(Platform.numPieces+2)),int(screen_x-screen_x/(Platform.numPieces+2))-10),5)
    # Font is default with None, size 24
    font = pygame.font.Font(None, 24)
    
    done=False
    print("\n###Running Main Loop###\n")
    mainTimer=0
    events=0
    bosses=0
    Ghost(random.randint(0,int(screen_x-Ghost.width)),random.randint(0,int(screen_y-Ghost.height)),player)
    
    ##########################
    #Main frame by frame loop#
    ##########################
    while not done:
        mainTimer+=1
        if int(mainTimer) >= FPS*5*(events+1):
            platformSpeed+=.01
            if boss != None:
                pass
            events +=1
            if (random.randint(0,6+bosses) == 1 or events == 1) and boss == None:
                event="boss"
            else:
                #when theres more events this will be an actual choice
                event=random.choice(("pickup","pickup"))
            if event == "boss":
                bosses+=1
                boss=random.choice((Dragon(),Dragon()))
            if event == "pickup":
                random.choice((Pickup.springInit,Pickup.anvilInit,Pickup.rockInit))(random.randint(int(platforms[0].pieceWidth)+10,screen_x-10-int(platforms[0].pieceWidth)),random.randint(-100,10))
        screen.fill((20,20,0))

        if debugger:
            text = font.render("Vertical Velocity:" + str(int(player.velocity)) + " Player on Ground?:" + str(player.onGround) + " fps: " + str(int(clock.get_fps())), True, (0, 128, 0))
            screen.blit(text,(0,0))

        for platform in platforms:
            platform.update()

        # every keypress or event per frame, used for lateral movement
        pyGameEvents = pygame.event.get()       
        # every change in keypress status, used for jumping
        pressed = pygame.key.get_pressed()              
        player.user_input(pyGameEvents,pressed)

        #Time display
        text = font.render("Time: " + str(int(mainTimer/FPS)), True, (0,128,0))
        screen.blit(text,(screen_x-90,10))
        
        for enemy in enemies:
            enemy.update()
            
        for effect in particleEffects:
            if effect != ():
                if effect[0].lifeSpan <= 0:
                    particleEffects.remove(effect)
                    break
                for particle in effect:
                    particle.update()
                
                
        if boss != None:
            boss.update()

        for sprite in sprites:
            sprite.update()
            
        for sprite in sprites:
            if sprite.blit != None:
                amIFalling=True
                for enemy in enemies:
                    if sprite.blit.colliderect(enemy.blit):
                        if sprite not in enemy.colliders:
                            enemy.colliders.append(sprite)
                    elif sprite in enemy.colliders and not sprite.blit.colliderect(enemy.blit):
                        enemy.colliders.remove(sprite)
                for pickup in pickups[:]:
                    #if the sprite isn't a pickup and collides with a pickup, activate the pickup
                    if sprite not in pickups and pickup.blit != None:
                        if pickup.blit.colliderect(sprite.bottomRect) and pickup.active != None:
                            pickup.active(sprite)
                # if sprite goes off screen, put it back to the top like a platform. Player isn't so fortunate
                if sprite.y > screen_y:
                    if sprite.persistent:
                        sprite.y = 0
                    else:
                        if sprite.isPlayer:
                            tempFont = pygame.font.Font(None, 48)
                            text=tempFont.render("press r to restart or escape to quit", True, (219,84,97))
                            screen.blit(text,(screen_x/2 - text.get_width()/2 ,screen_y/2 - text.get_height()/2 ))
                            player.stun=True
                        else:
                            sprites.remove(sprite)
                # turn x around if off screen
                if sprite.x > screen_x:
                    sprite.x=0
                elif sprite.x <= 0:
                    sprite.x=screen_x
                if not sprite.onGround and sprite.platform != None:
                    sprite.platform=None
                    sprite.pieces=[]
                # checking whether sprite should be on ground when it isn't
                if (not sprite.onGround) and (sprite.velocity <= 0):# or sprite.willBeOnGround):
                # If fast enough for bottomRect to pass straight through piece and it didn't detect something 
                # last frame already, use future model for collisions this frame. else use normal bottomRect
                    if sprite.velocity <= -1*(Platform.height + sprite.bottomSurfHeight):
                        sprite.tempRect = sprite.futureRect
                    else:
                        sprite.tempRect = sprite.bottomRect
                    for platform in platforms:
                        for piece in platform.pieces:
                            if not piece.broken:
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
                                        sprite.y=piece.y-sprite.height
                                if piece.hit:
                                    # if the piece has fire on it and the sprite hitting it isn't a fireball, douse that fire
                                    if not (piece.fire == None or isinstance(sprite, Fireball)):
                                        fires.remove(piece.fire)
                                        piece.fire = None
                                    # if sprite has a pieceInteraction method, call it.
                                    if callable(getattr(sprite, "pieceInteraction", None)):
                                        sprite.pieceInteraction(platform.pieces.index(piece),platform)
                                    piece.health-=sprite.pieceDamage
                                    piece.hit=False
                                    # If piece won't break, put player on ground 
                                    if piece.health > 0:
                                        if isinstance(sprite, Player):
                                            play_sound("jumpland.wav")
                                        amIFalling=False
                                        sprite.pieces.append(piece)
                                        sprite.platform=platform
                                        #print("<" + str(sprite).split(".")[1] + ' Just hit ' + str(piece).split(".")[1])
                                    else:
                                        pass
                                        #print(str(sprite).split(".")[1] + " Just broke ",str(piece).split(".")[1])

                            if sprite.futurePieces == [] and sprite.futurePlatform != None:
                                sprite.futurePlatform=None
                elif sprite.willBeOnGround or sprite.futurePieces != [] or sprite.futurePlatform != None:
                    sprite.willBeOnGround=False
                    sprite.futurePieces=[]
                    sprite.futurePlatform=None
                if not amIFalling:
                    sprite.onGround=True
                    particleEffects.append(tuple(ParticleEffect((200,120,120),.015*sprite.velocity*-1,sprite.x,sprite.y+sprite.height-sprite.bottomSurfHeight,sprite.width,sprite.bottomSurfHeight,platformSpeed*2,60,0)))
                    sprite.velocity=0
                
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    #If run without startup menu, default to lowest resolution and debugging mode
    debugger=True
    screen_x=1024
    screen_y=576
    screen = pygame.display.set_mode((screen_x,screen_y))
    main()