from os              import cpu_count #sched_getaffinity
##from multiprocessing import Process, Queue
##from multiprocessing.sharedctypes import Value, Array
import multiprocessing   as mp
import multiprocessing.sharedctypes
from ctypes          import Structure, c_bool, c_int, c_float

from random          import random, randrange, choice
#import numpy             as np

### This is an experiment in preparation for converting another
### project to use parallelisation

DIMENSIONS          = 2
FALLBACK_CORE_COUNT = 2
ROUNDS_OF_ITERATION = 50
    
class RandomWalkIterInput(Structure):
    _fields_ = [("coordinates", c_int * DIMENSIONS)]

class RandomWalkIterResult(Structure):
    _fields_ = [("success", c_bool), ("coordinates", c_int * DIMENSIONS)]

class RandomWalkIterResult_d(Structure):
    _fields_ = [("success", c_bool), ("dimension", c_int), ("target", c_int)]

def worker(inputs=RandomWalkIterInput((0,0)), outputs=RandomWalkIterResult(False,(0,0))) -> None:
    acceptance = random() < 0.05
    if acceptance:
        move                = list([0 for i in range(DIMENSIONS)])
        move[randrange(start=0, stop=DIMENSIONS)] = choice([-1, 1])
        print(f"                      Core {inputs.coordinates[0]} Success: {move}") # debug
        outputs.success     = True
        outputs.coordinates = tuple(move)
    else:
        outputs.success     = False
        outputs.coordinates = (0, 0)

def worker_d(inputs=dict(), outputs=RandomWalkIterResult_d(False, 0, 0)):
    acceptance = random() < 0.05
    if acceptance:
        dim                 = randrange(start=0, stop=DIMENSIONS)
        target              = choice([-1, 1]) + inputs[dim]
        outputs.success     = True
        outputs.dimension   = dim
        outputs.target      = target
        p_arr    = ['-' for i in range(DIMENSIONS)]
        p_arr[dim] = target
        print(f"\t\tFound acceptance {p_arr}")
    else:
        outputs.success     = False
        outputs.dimension   = 0 
        outputs.target      = 0

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

    manager = mp.Manager()
    d       = manager.dict()
    # inputs         = mp.sharedctypes.Array(RandomWalkIterInput,  \
    #                                       [RandomWalkIterInput((i, 0))           for i in range(cores)], lock=False)
    # outputs        = mp.sharedctypes.Array(RandomWalkIterResult, \
    #                                       [RandomWalkIterResult((False, (0, 0))) for i in range(cores)], lock=False)
    # workers        = [mp.Process(target=worker, args=(inputs[i], outputs[i]))    for i in range(cores)]

    location       = mp.Manager().dict([(i, 0) for i in range(DIMENSIONS)])
    print(f"location {location}")
    outputs_d      = mp.sharedctypes.Array(RandomWalkIterResult_d, \
                                          [RandomWalkIterResult_d((False, (0, 0))) for i in range(cores)], lock=False)
    print(outputs_d)
    workers_d      = [mp.Process(target=worker_d, args=(location, outputs_d[i])) for i in range(cores)]
    
    i              = 0 # successful iterations
    k              = 0 # all iterations
    while i < ROUNDS_OF_ITERATION:
        for j in range(cores):
            workers_d[j].run()
        for j in range(cores):
            r = outputs_d[j]
            if r.success:
                
                old_loc = [location[i] for i in range(DIMENSIONS)]
                location[r.dimension] = r.target
                new_loc = [location[i] for i in range(DIMENSIONS)]
                print(f"Iteration [{i}]\\{k} Move: from {old_loc} to {new_loc} - core {j}")
                ### Probability calculation says 1 - 0.95^12 = 0,4596 , so roughly
                ### 1/2 of the total iterations succeed
                
                i        += 1
                break
        k += 1
    print("----- Closing processes. -----")            
    for j in range(cores):
        workers_d[j].close()
    print(f"--------- This SHOULD be the end. ---------")
