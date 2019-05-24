from itertools import cycle
import random
import sys
import brain

import pygame
from pygame.locals import *


NUMBER_GENERATION = 10
FPS = 30
SCREENWIDTH  = 288
SCREENHEIGHT = 512
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES,HITMASKS = {}, {}

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)


try:
    xrange
except NameError:
    xrange = range


class Bird():
    def __init__(self):
        self.score = 0
        self.dead = False
        self.posx = self.posy = 0
        self.realScore = 0
        self.realIdx = -1
        # player velocity, max velocity, downward accleration, accleration on flap
        self.playerVelY = -9  # player's velocity along Y, default same as playerFlapped
        self.playerMaxVelY = 10  # max vel along Y, max descend speed
        self.playerMinVelY = -8  # min vel along Y, max ascend speed
        self.playerAccY = 1  # players downward accleration
        self.playerRot = 45  # player's rotation
        self.playerVelRot = 3  # angular speed
        self.playerRotThr = 20  # rotation threshold
        self.playerFlapAcc = -9  # players speed on flapping
        self.playerFlapped = False  # True when player flaps

players = []

def getBestScore():
    max_score = 0
    for playerIdx in range(len(players)):
        max_score = max(max_score, players[playerIdx].score)
    return max_score
def flap(playerIdx):
    if players[playerIdx].posy > -2 * IMAGES['player'][0].get_height():
        players[playerIdx].playerVelY = players[playerIdx].playerFlapAcc
        players[playerIdx].playerFlapped = True
#        SOUNDS['wing'].play()
def main():
    brain.init()
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird')

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    # game over sprite
    IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    #SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    #SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    #SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    #SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    #SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    while True:
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), False, True),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        HITMASKS['pipe'] = (
            getHitmask(IMAGES['pipe'][0]),
            getHitmask(IMAGES['pipe'][1]),
        )

        # hitmask for player
        HITMASKS['player'] = (
            getHitmask(IMAGES['player'][0]),
            getHitmask(IMAGES['player'][1]),
            getHitmask(IMAGES['player'][2]),
        )
        while True:
            movementInfo = showWelcomeAnimation()
            crashInfo = mainGame(movementInfo)

            #for playerIdx in range(len(players)):
             #   print("Player ", playerIdx , "score",players[playerIdx].score)
            brain.produce_new_generation(players)
     #       exit(0)



def showWelcomeAnimation():
    """Shows welcome screen animation of flappy bird"""
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}

    basex = -((-basex + 4) % baseShift)
    playerShm(playerShmVals)

    # draw sprites
    SCREEN.blit(IMAGES['background'], (0,0))
    SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
    SCREEN.blit(IMAGES['base'], (basex, BASEY))

    pygame.display.update()
    FPSCLOCK.tick(FPS)
    #SOUNDS['wing'].play()
    return {
            'playery': playery + playerShmVals['val'],
            'basex': basex,
            'playerIndexGen': playerIndexGen,
        }


def mainGame(movementInfo):
    global players;
    players = []
    for i in range(brain.NUMBER_OF_BIRDS):
        players.append(Bird())
    for i in range(brain.NUMBER_OF_BIRDS):
        players[i].realIdx = i
    for i in range(len(players)):
        players[i].posx, players[i].posy = int(SCREENWIDTH * 0.2), movementInfo['playery']
    playerIndex = 0
    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 300 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 300 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4
    iteration = 0



    while True:
        iteration = iteration+ 1
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                flap(0)
        # check for crash here
        all_player_dead = True
        for playerIdx in range(len(players)):
            if players[playerIdx].dead == False:
                all_player_dead = False
                crashTest = checkCrash({'x':  players[playerIdx].posx, 'y':  players[playerIdx].posy, 'index': playerIndex},
                                       upperPipes, lowerPipes)
                if crashTest[0]:
                    players[playerIdx].dead = True
                    players[playerIdx].realScore = iteration+1.0/(abs(players[playerIdx].posy-lowerPipes[0]['y'])+1)
                    if(players[playerIdx].posy < 0):
                        players[playerIdx].realScore -= 1000;

                   # print("Player " , playerIdx , " has died")
        if all_player_dead == True:
            return {
                'y': players[0].posy,
                'groundCrash': crashTest[1],
                'basex': basex,
                'upperPipes': upperPipes,
                'lowerPipes': lowerPipes,
                'score': getBestScore(),
            }

        # check for score
        for playerIdx in range(len(players)):
            if players[playerIdx].dead == True:
                continue;
            playerMidPos =  players[playerIdx].posx + IMAGES['player'][0].get_width() / 2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
                if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                    players[playerIdx].score += 1
                   # SOUNDS['point'].play()

        basex = -((-basex + 100) % baseShift)

        for playerIdx in range(len(players)):
            if players[playerIdx].dead == True:
                continue;
            # rotate the player
            if players[playerIdx].playerRot > -90:
                players[playerIdx].playerRot -= players[playerIdx].playerVelRot

            # player's movement
            if players[playerIdx].playerVelY < players[playerIdx].playerMaxVelY and not players[playerIdx].playerFlapped:
                players[playerIdx].playerVelY += players[playerIdx].playerAccY
            if players[playerIdx].playerFlapped:
                players[playerIdx].playerFlapped = False
                # more rotation to cover the threshold (calculated in visible rotation)
                players[playerIdx].playerRot = 45

            playerHeight = IMAGES['player'][playerIndex].get_height()
            players[playerIdx].posy += min(players[playerIdx].playerVelY, BASEY -  players[playerIdx].posy - playerHeight)

        # move pipes to left
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))


        for player_index in range(brain.NUMBER_OF_BIRDS):
           # network_input = np.array([[0, lowerPipes[0]['y'],players[player_index].posy]])
            #if players[player_index].posy+40 > lowerPipes[0]['y']:
             #   flap(player_index)
            state = brain.getState(player_index, players[player_index].posy,lowerPipes[0]['x'],lowerPipes[0]['y'])
            if state == True:
                flap(player_index)


        #print("X " , lowerPipes[0]['x'], " Y " , lowerPipes[0]['y']," Playerpos ",players[0].posy)
        for uPipe, lPipe in zip(upperPipes, lowerPipes):


            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        # print score so player overlaps the score

        showScore(getBestScore())

        # Player rotation has a threshold
        for i in range(len(players)):
            if players[i].dead == True:
                continue;
            visibleRot = players[i].playerRotThr
            if players[i].playerRot <= players[i].playerRotThr:
                visibleRot = players[i].playerRot
            playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
            SCREEN.blit(playerSurface, ( players[i].posx,  players[i].posy))

        pygame.display.update()
        FPSCLOCK.tick(FPS)




def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1


def getRandomPipe():
    """returns a randomly generated pipe"""
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 200

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
    ]


def showScore(score):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += IMAGES['numbers'][digit].get_width()

    Xoffset = (SCREENWIDTH - totalWidth) / 2

    for digit in scoreDigits:
        SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES['numbers'][digit].get_width()


def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collders with base or pipes."""
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

if __name__ == '__main__':
    main()
