from os              import cpu_count #sched_getaffinity
##from multiprocessing import Process, Queue
##from multiprocessing.sharedctypes import Value, Array
import multiprocessing   as mp
import multiprocessing.sharedctypes
from ctypes          import Structure, c_bool, c_int, c_float

from random          import random, randrange, choice
import numpy             as np

### This is an experiment in preparation for converting another
### project to use paralellisation

DIMENSIONS          = 2
FALLBACK_CORE_COUNT = 2
    
class RandomWalkIterInput(Structure):
    _fields_ = [("coordinates", c_int * DIMENSIONS)]

class RandomWalkIterResult(Structure):
    _fields_ = [("success", c_bool), ("coordinates", c_int * DIMENSIONS)]

def worker(inputs=RandomWalkIterInput((0,0)), outputs=RandomWalkIterResult(False,(0,0))) -> None:
    move              = np.array([0 for i in range(DIMENSIONS)])
    move[randrange(start=0, stop=DIMENSIONS)] = choice([-1, 1])
    acceptance     = random() < 0.05
    if acceptance:
        print(f"                      Core {inputs.coordinates[0]} Success: {move}") # debug
        outputs.success     = True
        outputs.coordinates = tuple(move)
    else:
        outputs.success     = False
        outputs.coordinates = (0, 0)


def random_walk() -> None:
    
    cores          = cpu_count()
    if cores == None: cores = FALLBACK_CORE_COUNT
    print(f"{cores} CPU core(s)\n" + \
           "--------------")
    
    ### The main takeaway from this experiment is this:
    ### Paralellisation in Python requires the use of shared memory.
    ### This means even a standard array of items cannot be written to by
    ### separate processes without utilising some specific mechanisms
    ### such as multiprocessing.sharedctypes.Array or .Value

    ### This then necessiates the use of the ctypes module and its
    ### C datatypes
    inputs         = mp.sharedctypes.Array(RandomWalkIterInput,  \
                                          [RandomWalkIterInput((i, 0))           for i in range(cores)], lock=False)
    outputs        = mp.sharedctypes.Array(RandomWalkIterResult, \
                                          [RandomWalkIterResult((False, (0, 0))) for i in range(cores)], lock=False)
    workers        = [mp.Process(target=worker, args=(inputs[i], outputs[i])) for i in range(cores)]

    global DIMENSIONS
    location       = np.array([0 for i in range(DIMENSIONS)])
    
    i              = 0 # successful iterations
    k              = 0 # all iterations
    while i < 100:
        for j in range(cores):
            workers[j].run()
        for j in range(cores):
            r = outputs[j]
            if r.success:
                
                new_loc  = location + r.coordinates[:]
                print(f"Iteration [{i}]\\{k} Move: from {location} to {new_loc}")
                ### Probability calculation says 1 - 0.95^12 = 0,4596 , so roughly
                ### 1/2 of the total iterations succeed
                location = new_loc
                i        += 1
                break
        k += 1
    print("----- Closing processes. -----")            
    for j in range(cores):
        workers[j].close()
    print(f"--------- This SHOULD be the end. ---------")
