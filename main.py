import neat
from pathlib import Path
import player_ai
import tilemap
import sys
import pygame
from pygame import locals

generation = 0


def genomes(genomes, config):
    nets = []
    bois = []

    matrix = tilemap.Board(block_size=50)
    matrix.update()
    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        bois.append(player_ai.Snake(matrix=matrix, spawn_x=5, spawn_y=5))

    pygame.init()
    width, height = 500, 500
    screen = pygame.display.set_mode((width, height))
    fps = 30
    clock = pygame.time.Clock()

    global generation
    generation += 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        for index, boi in enumerate(bois):
            boi.update()
            output = nets[index].activate(boi.get_data())
            i = output.index(max(output))
            if i == 0:
                boi.up()
            elif i == 1:
                boi.right()
            elif i == 2:
                boi.down()
            elif i == 3:
                boi.left()
            else:
                pass
            boi.update()

        alive = 0
        for i, boi in enumerate(bois):
            if boi.alive:
                alive += 1
                boi.update()
                genomes[i][1].fitness += boi.reward()

        if alive == 0:
            break

        screen.blit(matrix, (0, 0))

        pygame.display.flip()
        clock.tick(fps)

        # TODO: Fix getting stuck and not updating display


if __name__ == "__main__":
    # Set configuration file
    config_path = Path.cwd() / "config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create core evolution algorithm class
    p = neat.Population(config)

    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    p.run(genomes, 1000)
