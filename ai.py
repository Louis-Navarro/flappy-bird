import random
import pygame as pg
import os
import neat

pg.init()

###########
# CLASSES #
###########


class Bird:
    def __init__(self):
        self.x = 150
        self.left = self.x - 10
        self.y = 300

        self.score = 0

        self.vel = 5
        self.jumps = 0
        self.pressed_space = False

    def jump(self):
        if not self.jumps:
            self.pressed_space = True
            self.vel = -6
            self.jumps += 1

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


def draw_screen():
    global pipes, score, run

    win.fill((0, 0, 0))

    if len(birds) > 0:
        if 0 < birds[0].x - 20 - pipes[0].rect[0] < 3:
            score += 1

        if pipes[0].rect[0] <= -20:
            pipes.pop(0)
            pipes.pop(0)

        pipe_ind = 0
        if pipes[0].rect[0] < 120:
            pipe_ind = 2

        if pipes[-1].rect[0] <= 200:
            new_pipes = create_pipes()
            pipes.extend(new_pipes)

        for pipe in pipes:
            pipe.update()
            pipe.draw(win)

            for i, bird in enumerate(birds):
                if pipe.check_collision(bird.rect):
                    ge[i].fitness -= 1
                    birds.pop(i)
                    nets.pop(i)
                    ge.pop(i)

        for i, bird in enumerate(birds):
            ge[i].fitness += 0.1

            bird.update()

            distance_top = abs(bird.y - pipes[pipe_ind].rect[3])
            distance_down = abs(bird.y - pipes[pipe_ind + 1].rect[1])
            output = nets[i].activate((bird.y, distance_top, distance_down))

            if output[0] > 0.5:
                bird.jump()

            bird.draw(win)

            if 0 < bird.x - 20 - pipes[0].rect[0] < 3:
                ge[i].fitness += 5

            if bird.y >= 590 or bird.y < 0:
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)

        text = font.render(f'Score: {score}', True, (255, 255, 255))
        win.blit(text, (5, 10))

        text = font.render(f'Generation: {gen}', True, (255, 255, 255))
        win.blit(text, (5, 30))

        text = font.render(f'Alive: {len(birds)}', True, (255, 255, 255))
        win.blit(text, (5, 50))

    else:
        run = False

    pg.display.flip()


#############
# VARIABLES #
#############

# Window
win_width = 400
win_height = 600
win = pg.display.set_mode((win_width, win_height))
pg.display.set_caption('Flappy bird')

# Font
font = pg.font.SysFont('flappybirdy', 24)

# Game
score = 0
gen = 0

#############
# MAIN LOOP #
#############


def main(genomes, config):
    global nets, ge, birds, run, pipes, gen

    gen += 1

    pipes = [*create_pipes()]
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird())
        g.fitness = 0
        ge.append(g)

    run = True
    clock = pg.time.Clock()

    while run:
        clock.tick(60)

        draw_screen()

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                quit()


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(main, 50)
    print(f'Winner is : {winner}')


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
