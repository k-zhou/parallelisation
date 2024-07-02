from os              import cpu_count #sched_getaffinity
from multiprocessing import Process, Queue
from multiprocessing.sharedctypes import Value, Array
from ctypes          import Structure, c_bool, c_float
from random          import random, randrange, choice
import numpy             as np

DIMENSIONS = 2

class RandomWalkIterResult(Structure):
##    _fields_ = [("success", c_bool), ("x", c_float), ("y", c_float)]
    _fields_ = [("success", c_bool), ("coordinates", 2*c_float)]

def worker(input=[], output=[]) -> None:
    global DIMENSIONS
    move              = np.array([0 for i in range(DIMENSIONS)])
    move[randrange(start=0, stop=DIMENSIONS)] = choice([-1, 1])
    acceptance     = random() < 0.05
    if acceptance:
        print(f"{input[0]} Success {move}")
        output.append((True,  move ))
    else:
        output.append((False, np.array([0,0])))


def random_walk() -> None:
    # cores          = len(sched_getaffinity(0))
    cores          = cpu_count()
    if cores == None: cores = 2
    print(f"{cores} CPU core(s)")

    input          = [[i] for i in range(cores)]
    outputs        = Array([[] for i in range(cores)])
    workers        = [Process(target=worker, args=(input[i], outputs[i])) for i in range(cores)]

    global DIMENSIONS
    location       = np.array([0 for i in range(DIMENSIONS)])

##    for p in workers:
##        p.start()
    
    i              = 0
    while i < 3: # TODO: 
        # q              = Queue()
        for j in range(cores):
            p = workers[j]
            p.args=(input[j], outputs[j])
            p.run()
##        for j in range(cores):
##            p = workers[j]
##            p.join()
##            print("-------------------------------")
        for j in range(cores):
            r = outputs[j][0]
            print(r, type(r)) # debug
            if r[0]:
                
                new_loc  = location + r[1]
                print(f"[{i}] Move: from {location} to {new_loc}")
                location = new_loc
                i        += 1
                for j in range(cores):
                    outputs[j].clear()
                    print(f"after clearing {i}", outputs[j])
                break
    
    # Done processing, stop processes
##    for p in workers:
##        p.kill()
