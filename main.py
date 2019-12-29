import random
import pygame as pg

pg.init()

###########
# CLASSES #
###########


class Bird:
    def __init__(self):
        self.x = 90
        self.y = 300

        self.vel = 5

        self.jumps = 0
        self.pressed_space = False

        self.images = [
            pg.image.load('assets/bird-upflap.png'),
            pg.image.load('assets/bird-midflap.png'),
            pg.image.load('assets/bird-downflap.png')
        ]
        self.im_ind = 0

    def update(self):
        self.im_ind += 1
        if self.im_ind > 15:
            self.im_ind = 0

        if self.jumps:
            if self.jumps < 6:
                self.jumps += 1

            elif self.jumps <= 10:
                self.jumps += 1
                self.vel += 1

            elif self.jumps < 15:
                self.jumps += 1

            elif self.jumps == 15:
                self.jumps = 0

        elif self.vel < 7:
            self.vel += 1

        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE] and not (self.jumps or self.pressed_space):
            self.pressed_space = True
            self.vel = -6
            self.jumps += 1

        elif not keys[pg.K_SPACE]:
            self.pressed_space = False

        self.y += self.vel

    def draw(self, win):
        index = self.im_ind // 5
        im = self.images[index if index != 3 else 1]
        im = pg.transform.rotate(im, 5 * -self.vel)

        win.blit(im, (self.x, self.y))

    @property
    def rect(self):
        return pg.Rect(self.x, self.y, 34, 24)


class Pipe:
    def __init__(self, x=400):
        self.len = random.randint(42, 320)
        self.pos = [x, -(320 - self.len)]

        self.im = pg.image.load('assets/pipe.png')
        self.im = pg.transform.rotate(self.im, 180)

    def update(self):
        self.pos[0] -= 2

    def draw(self, win):
        win.blit(self.im, self.pos)

    def check_collision(self, bird_rect):
        rect = pg.Rect(*self.pos, *self.im.get_size())
        return rect.colliderect(bird_rect)


class PipePair(Pipe):
    def __init__(self, pair, x=400):
        super().__init__(x)

        self.im = pg.image.load('assets/pipe.png')

        self.pos[1] = pair.len + 150


#############
# FUNCTIONS #
#############


def create_pipes():
    pipe = Pipe()
    pair = PipePair(pipe)

    return pipe, pair


def update():
    global score

    bird.update()

    if pipes[0].pos[0] <= -20:
        pipes.pop(0)
        pipes.pop(0)

    if pipes[-1].pos[0] <= 200:
        new_pipes = create_pipes()
        pipes.extend(new_pipes)

    if 0 < bird.x - pipes[0].pos[0] < 3:
        score += 1


def draw_screen():
    global pipes, bird, score

    win.fill((0, 0, 0))
    win.blit(bg, (0, 0))

    for pipe in pipes:
        pipe.update()
        pipe.draw(win)

        if pipe.check_collision(bird.rect):
            bird = Bird()
            pipes = [*create_pipes()]
            score = 0

    if bird.y >= 590:
        bird = Bird()
        pipes = [*create_pipes()]
        score = 0

    text = font.render(f'Score: {score}', True, (255, 255, 255))
    win.blit(text, (5, 10))

    bird.draw(win)

    pg.display.flip()


#############
# VARIABLES #
#############

# Window
win_width = 288
win_height = 512

win = pg.display.set_mode((win_width, win_height))
pg.display.set_caption('Flappy bird')

bg = pg.image.load('assets/background.png')

# Font
font = pg.font.SysFont('flappybirdy', 24)

# Bird
bird = Bird()

# Pipes
pipes = [*create_pipes()]

# Game
score = 0

#############
# MAIN LOOP #
#############

run = True
clock = pg.time.Clock()

while run:
    clock.tick(60)

    for e in pg.event.get():
        if e.type == pg.QUIT:
            run = False

    update()
    draw_screen()

pg.quit()
