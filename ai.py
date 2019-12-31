import random
import pygame as pg
import os
import neat
import visualize
import time
from neat.math_util import mean, stdev
from neat.six_util import itervalues, iterkeys

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


class LogReporter(neat.reporting.BaseReporter):
    def __init__(self, filename='log.txt'):
        self.filename = filename
        self.generation = None
        self.generation_start_time = None
        self.generation_times = []
        self.num_extinctions = 0

    def start_generation(self, generation):
        with open(self.filename, 'a') as file:
            self.generation = generation
            file.write('\n ****** Running generation {0} ****** \n\n'.format(
                generation))
            self.generation_start_time = time.time()

    def end_generation(self, config, population, species_set):
        ng = len(population)
        ns = len(species_set.species)

        with open(self.filename, 'a') as file:
            file.write(
                'Population of {0:d} members in {1:d} species:\n'.format(
                    ng, ns))
            sids = list(iterkeys(species_set.species))
            sids.sort()
            file.write("   ID   age  size  fitness  adj fit  stag\n")
            file.write("  ====  ===  ====  =======  =======  ====\n")
            for sid in sids:
                s = species_set.species[sid]
                a = self.generation - s.created
                n = len(s.members)
                f = "--" if s.fitness is None else "{:.1f}".format(s.fitness)
                af = "--" if s.adjusted_fitness is None else "{:.3f}".format(
                    s.adjusted_fitness)
                st = self.generation - s.last_improved
                file.write(
                    "  {: >4}  {: >3}  {: >4}  {: >7}  {: >7}  {: >4}\n".
                    format(sid, a, n, f, af, st))

            elapsed = time.time() - self.generation_start_time
            self.generation_times.append(elapsed)
            self.generation_times = self.generation_times[-10:]
            average = sum(self.generation_times) / len(self.generation_times)
            file.write('Total extinctions: {0:d}\n'.format(
                self.num_extinctions))
            if len(self.generation_times) > 1:
                file.write(
                    "Generation time: {0:.3f} sec ({1:.3f} average)\n".format(
                        elapsed, average))
            else:
                file.write("Generation time: {0:.3f} sec\n".format(elapsed))

    def post_evaluate(self, config, population, species, best_genome):
        # pylint: disable=no-self-use
        with open(self.filename, 'a') as file:
            fitnesses = [c.fitness for c in itervalues(population)]
            fit_mean = mean(fitnesses)
            fit_std = stdev(fitnesses)
            best_species_id = species.get_species_id(best_genome.key)
            file.write(' '.join(
                ('Population\'s average fitness:',
                 '{0:3.5f} stdev: {1:3.5f}'.format(fit_mean, fit_std), '\n')))
            file.write(
                'Best fitness: {0:3.5f} - size: {1!r} - species {2} - id {3}\n'
                .format(best_genome.fitness, best_genome.size(),
                        best_species_id, best_genome.key))

    def complete_extinction(self):
        with open(self.filename, 'a') as file:
            self.num_extinctions += 1
            file.write('All species extinct.\n')

    def found_solution(self, config, generation, best):
        with open(self.filename, 'a') as file:
            file.write(' '.join(
                ('\nBest individual in generation {0} meets'.format(
                    self.generation),
                 'fitness threshold - complexity: {0!r}'.format(best.size()),
                 '\n')))

    def species_stagnant(self, sid, species):
        with open(self.filename, 'a') as file:
            file.write(
                "\nSpecies {0} with {1} members is stagnated: removing it\n".
                format(sid, len(species.members)))

    def info(self, msg):
        with open(self.filename, 'a') as file:
            file.write(str(msg) + '\n')


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

        if score > 2_000:
            run = False

        draw_screen()

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                quit()


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

    logger = LogReporter()
    p.add_reporter(logger)

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
