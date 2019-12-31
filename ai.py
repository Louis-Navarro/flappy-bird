import random
import pygame as pg
import os
import neat
import visualize

pg.init()

###########
# CLASSES #
###########


class Bird:
    def __init__(self):
        self.x = 90
        self.left = self.x - 10
        self.y = 300

        self.score = 0

        self.vel = 5
        self.jumps = 0
        self.pressed_space = False

        self.images = [
            pg.image.load('assets/bird-upflap.png'),
            pg.image.load('assets/bird-midflap.png'),
            pg.image.load('assets/bird-downflap.png')
        ]
        self.im_ind = 0

    def jump(self):
        if not self.jumps:
            self.pressed_space = True
            self.vel = -6
            self.jumps += 1

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
    def __init__(self, x=288):
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
    def __init__(self, pair, x=288):
        super().__init__(x)

        self.im = pg.image.load('assets/pipe.png')

        self.top = pair.len + 150
        self.pos[1] = self.top


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
    win.blit(bg, (0, 0))

    if len(birds) > 0:
        if 0 < birds[0].x - pipes[0].pos[0] < 3:
            score += 1

        if pipes[0].pos[0] <= -20:
            pipes.pop(0)
            pipes.pop(0)

        pipe_ind = 0
        if pipes[0].pos[0] < 56:
            pipe_ind = 2

        if pipes[-1].pos[0] <= 88:
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
            bird.update()

            distance_top = abs(bird.y - pipes[pipe_ind].len)
            distance_down = abs(bird.y - pipes[pipe_ind + 1].top)
            output = nets[i].activate((bird.y, distance_top, distance_down))

            if output[0] > 0.5:
                bird.jump()

            bird.draw(win)

            if 0 < bird.x - pipes[0].pos[0] < 3:
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
        score = 0
        run = False

    pg.display.flip()


def eval_genomes(genomes, config):
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
    # clock = pg.time.Clock()

    while run:
        # clock.tick(60)

        draw_screen()

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                quit()

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

# Game
score = 0
gen = 0

#############
# MAIN LOOP #
#############


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50)
    print(f'Winner is : {winner}')

    node_names = {
        0: 'TanH',
        -1: 'Distance to bottom pipe',
        -2: 'Distance to top pipe',
        -3: 'Bird Y-Position'
    }

    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, False, True)
    visualize.plot_species(stats, True)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
