# -*- coding: utf-8 -*-
import multiprocessing as mp
import pandas as pd
import filterlib as flt
import blink as blk
import pygame, math
from random import randint
from time import sleep
#from pyOpenBCI import OpenBCIGanglion


def blinks_detector(quit_program, blink_det, blinks_num, blink,):
    def detect_blinks(sample):
        if SYMULACJA_SYGNALU:
            smp_flted = sample
        else:
            smp = sample.channels_data[0]
            smp_flted = frt.filterIIR(smp, 0)
        #print(smp_flted)

        brt.blink_detect(smp_flted, -38000)
        if brt.new_blink:
            if brt.blinks_num == 1:
                #connected.set()
                print('CONNECTED. Speller starts detecting blinks.')
            else:
                blink_det.put(brt.blinks_num)
                blinks_num.value = brt.blinks_num
                blink.value = 1

        if quit_program.is_set():
            if not SYMULACJA_SYGNALU:
                print('Disconnect signal sent...')
                board.stop_stream()


####################################################
    SYMULACJA_SYGNALU = True
####################################################
    mac_adress = 'd2:b4:11:81:48:ad'
####################################################

    clock = pygame.time.Clock()
    frt = flt.FltRealTime()
    brt = blk.BlinkRealTime()

    if SYMULACJA_SYGNALU:
        df = pd.read_csv('dane_do_symulacji/data.csv')
        for sample in df['signal']:
            if quit_program.is_set():
                break
            detect_blinks(sample)
            clock.tick(200)
        print('KONIEC SYGNAŁU')
        quit_program.set()
    else:
        board = OpenBCIGanglion(mac=mac_adress)
        board.start_stream(detect_blinks)

if __name__ == "__main__":


    blink_det = mp.Queue()
    blink = mp.Value('i', 0)
    blinks_num = mp.Value('i', 0)
    #connected = mp.Event()
    quit_program = mp.Event()

    proc_blink_det = mp.Process(
        name='proc_',
        target=blinks_detector,
        args=(quit_program, blink_det, blinks_num, blink,)
        )

    # rozpoczęcie podprocesu
    proc_blink_det.start()
    print('subprocess started')

    ############################################
    # Poniżej należy dodać rozwinięcie programu
    ############################################

    pygame.init()

    gravity = 0.05

    def setVariables() :
        global dead
        dead = False
        global score
        score = -2
        global run
        run = True
        global started
        started = False
        global runs
        runs = 0
        global pipes
        pipes = []
        Bird.x = 250
        Bird.y = 250
        Bird.vel = 0

    win = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Flappy Bird!")
    img = pygame.image.load('patryk.png')
    bg = pygame.image.load('tło.jpg')
    pipe = pygame.image.load('alga2.png')
    ground = pygame.image.load('piasek.jpg')
    font = pygame.font.SysFont('Comic Sans MS', 30)

    class Bird :
        x = 250
        y = 250
        vel = 0

        def update() :
            if started :
                if Bird.y < 475 :
                    Bird.y += Bird.vel
                    Bird.vel += gravity
                else :
                    Bird.y = 475
                    die()
                if Bird.y < 0 :
                    Bird.y = 0
                    Bird.vel = 0
            else :
                Bird.y = 250 + math.sin(runs/10)*15
            Bird.getAngle()

        def jump() :
            Bird.vel = -10

        def getAngle() :
            global bird
            bird = pygame.transform.rotate(img, -3*Bird.vel)

    class Pipe() :
        def __init__(self, dir, x, len) :
            self.dir = dir
            self.x = x
            self.len = len

        def update(self) :
            if self.dir == "UP" :
                win.blit(pipe, (self.x, 600-self.len))
            else :
                win.blit(pygame.transform.rotate(pipe, 180), (self.x, self.len-431))
            if not dead :
                self.x -= 7

        def checkCollide(self) :
            if self.dir == "DOWN" :
                if Bird.x + 48 > self.x and self.x + 75 > Bird.x :
                    if Bird.y + 2 < self.len :
                        die()
            else :
                if Bird.x + 48 > self.x and self.x + 75 > Bird.x :
                    if Bird.y + 45 > 600-self.len :
                        die()

    def pipePair() :
        r = randint(75, 350)
        pipes.append(Pipe("DOWN", 900, r))
        pipes.append(Pipe("UP", 900, 600-(r+125)))
        global score
        score += 1

    def animateGround() :
        win.blit(ground, ((runs%111)*-7, 500))

    def die() :
        global dead
        dead = True
        run = False

    setVariables()

    while run:
        if blink.value == 1:
            if not started :
                started = True
                blink.value = 0
                print("START")
            if not dead :
                Bird.jump()
                blink.value = 0
                print("JUMP!")

        for event in pygame.event.get() :
            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_ESCAPE :
                    run = False
                if event.key == pygame.K_SPACE:
                    if not started :
                        started = True
                    if not dead :
                        Bird.jump()
            elif event.type == pygame.QUIT :
                run = False
        blink.value = 0
        win.blit(bg, (0, 0))
        if runs % 45 == 0 and started :
            pipePair()
        for p in pipes :
            p.update()
            p.checkCollide()
        Bird.update()
        win.blit(bird, (Bird.x,Bird.y))
        animateGround()

        scoreboard = font.render(str(score), False, (0, 0, 0))
        if score > -1 :
            scorebase = pygame.draw.rect(win, (255, 255, 255), (7, 5, len(str(score))*15+10, 35))
            win.blit(scoreboard, (10, 0))
        pygame.display.update()
        if not dead:
            runs += 1
    quit_program.set()
    pygame.quit()

    '''
    while True:
        if blink.value == 1:
            print('BLINK!')
            blink.value = 0
        if 'escape' in event.getKeys():
            print('quitting')
            quit_program.set()
        if quit_program.is_set():
            break
    '''
# Zakończenie podprocesów
    proc_blink_det.join()
