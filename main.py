import neat
import player_ai
import tilemap
import pygame
from pygame import locals
import sys
import time
from pathlib import Path
from create_logger import create_logger
import logging

logger = create_logger(name=__name__, level=logging.WARNING)

generation = 0


def genomes(genomes, config):
    nets = []
    bois = []

    logger.debug("Create board")
    matrix = tilemap.Board(block_size=5, blocks_x=100, blocks_y=100)
    matrix.update()

    logger.debug("Create FFNs")
    spawn_x = 3
    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        bois.append(player_ai.Snake(matrix=matrix, spawn_x=spawn_x, spawn_y=matrix.blocks_y-5))
        logger.debug(f"Spawning boi at {spawn_x}, {matrix.blocks_y-5}")
        spawn_x += 20
    logger.debug(f"List of bois: {repr(bois)}")

    logger.debug("Initiate PyGame")
    pygame.init()
    width, height = 500, 500
    screen = pygame.display.set_mode((width, height))
    fps = 0
    clock = pygame.time.Clock()

    global generation
    generation += 1

    logger.debug("Start super loop")
    while True:
        logger.debug("Parse window events")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        logger.debug("Update bois")
        alive = 0
        for index, boi in enumerate(bois):
            logger.debug(f"Updating boi {index+1}/{len(bois)}")
            start_time = time.time()
            boi.update()
            data = boi.get_data()
            logger.debug(f"Time to get data is {round((time.time() - start_time) * 1000)} ms")
            output = nets[index].activate(data)
            i = output.index(max(output))
            logger.debug(f"Time to get output is {round((time.time() - start_time) * 1000)} ms")
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
            if boi.alive:
                alive += 1
                genomes[i][1].fitness += boi.reward()
            else:
                logger.info(f"Boi {index+1} died!")
            logger.debug(f"Time to update boi {index+1} is {round((time.time() - start_time) * 1000)} ms")
            matrix.update()
            screen.blit(matrix, (0, 0))
            pygame.display.flip()

        if alive == 0:
            logger.info(f"No bois are alive! Breaking")
            break

        clock.tick(fps)


if __name__ == "__main__":
    # Set configuration file
    config_path = Path.cwd() / "config-feedforward.txt"
    logger.debug(f"Path to config file is {repr(config_path)}")
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create core evolution algorithm class
    p = neat.Population(config)

    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    logger.debug("Run NEAT")
    # Run NEAT
    p.run(genomes, 1000)
