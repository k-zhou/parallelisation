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
class random_walk_v2():

    def __init__(self) -> None:
        self.cores          = cpu_count()
        if self.cores == None: self.cores = FALLBACK_CORE_COUNT
        print(f"{self.cores} CPU core(s)\n" + \
            "--------------")
        self.location       = mp.Manager().dict([(i, 0) for i in range(DIMENSIONS)])
        self.inputs  = self.location
        self.outputs = mp.sharedctypes.Array(RandomWalkIterResult_d, \
        [RandomWalkIterResult_d((False, 0, 0)) for i in range(self.cores)], lock=False)
        print("outputs: ", self.outputs)
        
        print(f"location {self.location}")
        self.workers_d      = [mp.Process(target=self.worker_d, args=[i]) for i in range(self.cores)]

    def worker_d(self, i=0) -> None:
        acceptance = random() < 0.05
        if acceptance:
            dim                      = randrange(start=0, stop=DIMENSIONS)
            target                   = choice([-1, 1]) + self.inputs[dim]
            self.outputs[i].success     = True
            self.outputs[i].dimension   = dim
            self.outputs[i].target      = target
            p_arr      = ['-' for i in range(DIMENSIONS)]
            p_arr[dim] = target
            print(f"\t\tFound acceptance {p_arr}")
        else:
            self.outputs[i].success     = False
            self.outputs[i].dimension   = 0 
            self.outputs[i].target      = 0

    def run(self) -> None:
        
        i              = 0 # successful iterations
        k              = 0 # all iterations
        while i < ROUNDS_OF_ITERATION:
            for j in range(self.cores):
                self.workers_d[j].run()
            for j in range(self.cores):
                r = self.outputs[j]
                if r.success:
                    
                    old_loc = [self.location[i] for i in range(DIMENSIONS)]
                    self.location[r.dimension] = r.target
                    new_loc = [self.location[i] for i in range(DIMENSIONS)]
                    print(f"Iteration [{i}]\\{k} Move: from {old_loc} to {new_loc} - core {j}")
                    ### Probability calculation says 1 - 0.95^12 = 0,4596 , so roughly
                    ### 1/2 of the total iterations succeed
                    
                    i        += 1
                    break
            k += 1
        print("----- Closing processes. -----")            
        for j in range(self.cores):
            self.workers_d[j].close()
        print(f"--------- This SHOULD be the end. ---------")
