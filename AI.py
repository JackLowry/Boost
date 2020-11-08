import pygame
import os
import math
import sys
import random
import neat


generation = 0
def run_car(genomes, config):
    global generation
    # Init NEAT
    nets = []
    cars = []

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0


        #Somehow need to initiate the 200 cars here I think?
        #cars.append(Car())

    #Call game loop for one generation
    generation+=1
    #basically need to do: from racertest.py run start()
    #in racertest: for index, car in enumerate(cars):
    #                 output = nets[index].activate(car.get_data())
    #Then, in the loop, something like this, break loop when all dead
    #  remain_cars = 0
    #     for i, car in enumerate(cars):
    #         if car.alive:
    #             remain_cars += 1
    #             car.update(map)   #like draw the car, or add it to Cars group, or remove dead cars from Cars group
    #             genomes[i][1].fitness += car.get_reward()

    #     # check
    #     if remain_cars == 0:
    #         break

    ##Put this, so it only draws the alive cars
    # for car in cars:
    #         if car.alive:
    #             car.draw(screen)
    ##somewhere, print generation var

if __name__ == "__main__":
    config_path = "./config"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    p.run(run_car, 1000)