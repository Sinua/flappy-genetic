
from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import Dense, Activation
from tensorflow.python.keras.optimizers import SGD

import numpy as np
import random
players_model = []
generation = 1
NUMBER_OF_BIRDS = 30

def create_model():
    model = Sequential()
    model.add(Dense(5, input_shape=(3,),activation='sigmoid'))
    model.add(Dense(1,activation='sigmoid'))
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss="mse", optimizer=sgd, metrics=["accuracy"])
    return model

def init():
    global players_model
    for player in range(0, NUMBER_OF_BIRDS):
        players_model.append(create_model())
        players_model[player]._make_predict_function()

def produce_new_generation(playersList):
    global  generation;
    generation = generation +1
    ############## Calculate FitnessScore
    print("Generation ", generation)
    playersList.sort(key=lambda x: x.score, reverse=True)
    change_weights(0,playersList)

def change_weights(layer,playersList):
    new_weights = []
    for counter in range(0,NUMBER_OF_BIRDS//2):
        idx_1 = playersList[random.randint(0,5)].realIdx
        idx_2 = playersList[random.randint(0,5)].realIdx
        new_weights1,new_weights2 = model_crossover(idx_1, idx_2,layer)
        updated_weights1 = model_mutate(new_weights1)
        updated_weights2 = model_mutate(new_weights2)
        new_weights.append(updated_weights1)
        new_weights.append(updated_weights2)
    global players_model
    for i in range(0,NUMBER_OF_BIRDS):
        players_model[i].layers[layer].set_weights(new_weights[i])

def model_mutate(weights):
    for xi in range(len(weights)):
        for yi in range(len(weights[xi])):
            if (type(weights[xi][yi]) != np.float32):
                for zi in range(len(weights[xi][yi])):
                    if random.uniform(0, 1) > 0.99:
                        change = random.uniform(-0.5 , +0.5)
                        weights[xi][yi][zi] += change
                    if random.uniform(0, 1) > 0.9999:
                        change = random.uniform(-2, 2)
                        weights[xi][yi][zi] *= change
    return weights

def model_crossover(model_idx1, model_idx2,layer):
    global players_model
    weights1 = players_model[model_idx1].layers[layer].get_weights()
    weights2 = players_model[model_idx2].layers[layer].get_weights()
    weightsnew1 = weights1
    weightsnew2 = weights2
    weightsnew1[0] =  weights2[0]
    weightsnew2[0] = weights1[0]
    return weightsnew1, weightsnew2

SCREENHEIGHT = 512

def getState(player_index,height,dist,pipe_height):
    global players_model
    neural_input = np.asarray([height,pipe_height,dist<70])
    neural_input = np.atleast_2d(neural_input)
    output_prob = players_model[player_index].predict(neural_input,1)[0]
    if output_prob[0] <= 0.5:
       return 1
    return 0
