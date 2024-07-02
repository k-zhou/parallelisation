from os              import cpu_count #sched_getaffinity
##from multiprocessing import Process, Queue
##from multiprocessing.sharedctypes import Value, Array
import multiprocessing   as mp
from ctypes          import Structure, c_bool, c_int, c_float

from random          import random, randrange, choice
import numpy             as np

DIMENSIONS          = 2
FALLBACK_CORE_COUNT = 2
class RandomWalkIterInput(Structure):
    _fields_ = [("coordinates", 2*c_int)]

class RandomWalkIterResult(Structure):
##    _fields_ = [("success", c_bool), ("x", c_float), ("y", c_float)]
    _fields_ = [("success", c_bool), ("coordinates", 2*c_int)]

def worker(inputs=[], outputs=[]) -> None:
    global DIMENSIONS
    move              = np.array([0 for i in range(DIMENSIONS)])
    move[randrange(start=0, stop=DIMENSIONS)] = choice([-1, 1])
    acceptance     = random() < 0.05
    if acceptance:
        print(f"Core {inputs[0]} Success: {move}")
        outputs.append((True,  move ))
    else:
        outputs.append((False, np.array([0,0])))


def random_walk() -> None:
    
    cores          = 4 #cpu_count() #debug TODO: 
    global FALLBACK_CORE_COUNT
    if cores == None: cores = FALLBACK_CORE_COUNT
    print(f"{cores} CPU core(s)\n" + \
           "--------------")

##    inputs         = mp.sharedctypes.Array([[i] for i in range(cores)])
##    outputs        = mp.sharedctypes.Array(RandomWalkIterResult, [[ ] for i in range(cores)])
    inputs         = [[i] for i in range(cores)]
    outputs        = [[ ] for i in range(cores)]
    workers        = [mp.Process(target=worker, args=(inputs[i], outputs[i])) for i in range(cores)]

    global DIMENSIONS
    location       = np.array([0 for i in range(DIMENSIONS)])
    
    i              = 0
    while i < 3: # TODO: 
        for j in range(cores):
            p = workers[j]
            p.args=(inputs[j], outputs[j])
            p.run()
        for j in range(cores):
            r = outputs[j][0]
            print(j, r, type(r)) # debug
            if r[0]:
                
                new_loc  = location + r[1]
                print(f"Iteration [{i}] Move: from {location} to {new_loc}")
                location = new_loc
                i        += 1
                for j in range(cores):
                    outputs[j].clear()
##                    print(f"after clearing {i}-{j}", outputs[j])
                break
    print("----- Closing processes. -----")            
    for j in range(cores):
        workers[j].close()
    print(f"--------- This SHOULD be the end. ---------")
