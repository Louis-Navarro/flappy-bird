import random
import pygame as pg

pg.init()

###########
# CLASSES #
###########


class Bird:
    def __init__(self):
        self.x = 150
        self.y = 300

        self.vel = 5

        self.jumps = 0

        self.pressed_space = False

    def update(self):
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
        pg.draw.circle(win, (255, 0, 0), (self.x, self.y), 10)

    @property
    def rect(self):
        return pg.Rect(140, self.y - 10, 20, 20)


class Pipe:
    def __init__(self, x=400):
        self.len = random.randint(50, 350)
        self.rect = pg.Rect(x, 0, 20, self.len)

    def update(self):
        self.rect[0] -= 2

    def draw(self, win):
        pg.draw.rect(win, (0, 255, 0), self.rect)

    def check_collision(self, bird_rect):
        return self.rect.colliderect(bird_rect)


class PipePair(Pipe):
    def __init__(self, pair, x=400):
        super().__init__(x)

        self.top = pair.len + 150
        self.rect = pg.Rect(x, self.top, 20, 600)


#############
# FUNCTIONS #
#############


def create_pipes():
    pipe = Pipe()
    pair = PipePair(pipe)

    return pipe, pair


def update():
    bird.update()

    if pipes[0].rect[0] <= -20:
        pipes.pop(0)
        pipes.pop(0)

    if pipes[-1].rect[0] <= 200:
        new_pipes = create_pipes()
        pipes.extend(new_pipes)


def draw_screen():
    global pipes, bird

    win.fill((0, 0, 0))

    for pipe in pipes:
        pipe.update()
        pipe.draw(win)

        if pipe.check_collision(bird.rect):
            bird = Bird()
            pipes = [*create_pipes()]

    bird.draw(win)

    pg.display.flip()


#############
# VARIABLES #
#############

# Window
win_width = 400
win_height = 600
win = pg.display.set_mode((win_width, win_height))
pg.display.set_caption('Flappy bird')

# Bird
bird = Bird()

# Pipes
pipes = [*create_pipes()]

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
