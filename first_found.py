from os              import cpu_count
from multiprocessing.sharedctypes import Value, Array
import multiprocessing   as mp
import multiprocessing.sharedctypes
from ctypes          import Structure, c_bool, c_int, c_float
from random          import random, randrange, choice
from time            import sleep

'''
Starts multiple processes that sleep for a random time.
The first to wake up records itself as the round's winner.
Repeats for a set number of rounds.
'''


FALLBACK_CORE_COUNT = 2
ROUNDS_OF_ITERATION = 20

class first_found():

    def worker(index=0) -> None: pass

    def __init__(self) -> None:
        self.cores          = cpu_count()
        if self.cores == None: self.cores = FALLBACK_CORE_COUNT
        print(f"{self.cores} CPU core(s)\n" + \
            "--------------")
        self.workers = [mp.Process(target=self.worker) for i in range(self.cores)]
        
        self.found  = mp.sharedctypes.Value(c_bool, False)
        self.finder = mp.sharedctypes.Value(c_int, -1)
        #self.ready  = mp.sharedctypes.Value(c_bool, True)

    def worker(self, index=0) -> None:
        t = random()/10
        print(f"[{index:3d}]: {t}")    
        sleep(t)
        if not self.found.value:
            self.found.value  = True
            self.finder.value = index
            #print(f">> {index} finds.")

    def run(self) -> None:
        arr = list(range(ROUNDS_OF_ITERATION))
        for element in arr:
            #self.ready.value = False
            self.found.value  = False
            print(f"______ Round {element} begins: {self.found.value} {self.finder.value} ______")
            for i in range(self.cores):
                worker = mp.Process(target=self.worker, args=[i])
                self.workers[i] = worker
                worker.start()
            while not self.found.value: pass
            for i in range(self.cores):
                self.workers[i].join()
            print(f"------ Round {element} ends: {self.found.value} {self.finder.value} ------")
            
