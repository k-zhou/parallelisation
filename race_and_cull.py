import multiprocessing as mp
import multiprocessing.sharedctypes
from         ctypes import Structure, c_bool, c_int, c_float, c_uint
from             os import cpu_count

import random          as rnd
from           time import time_ns, sleep

'''
Runs many accumulators in parallel. 
The first to reach the goal will mark its index and then the main loop
stops all the others and prints their status.
'''

class race_and_cull():

    def worker(self): pass
    def run(self):    pass

    def __init__(self) -> None:
        self.goal      = 200
        self.max_incr  = 8
        self.mn        = mp.Manager()
        self.pass_data = self.mn.dict()
        self.stop_flag = mp.sharedctypes.Value(c_int, -1)
    
    def worker(self, index=0, pass_data=None) -> None:
        if pass_data == None: 
            pass_data = dict()
            pass_data["round"] = 0
        total = 0
        print(f"Worker #{index} starting.")
        while(total < self.goal):
            if not self.stop_flag.value == -1: 
                print(f"Forcibly stopping {index:3}")
                return
            sleep(rnd.random() * 0.25)
            total += rnd.randint(1, self.max_incr)
        if self.stop_flag.value == -1:
            print(f"Should modify {self.stop_flag.value}, ", end='')
            self.stop_flag.value = index # remember to specify you're editing the .value and not the wrapper itself
            print(f"Now {self.stop_flag.value}")
        print(f"Worker #{index} finishes at {total}\n{self.stop_flag}\n{self.stop_flag.value}")
        
    def run(self, reset=None) -> None:
        cores = cpu_count()
        if cores == None: cores = 1
        # internal containers
        index = 0
        # reset all internal containers
        if not reset == None:
            index = 0
        
        workers = list([0 for i in range(cores)])
        for i in range(cores):
            workers[i] = mp.Process(target=self.worker, args=[i, self.pass_data])
            workers[i].start()
        print("Now waiting...")
        while self.stop_flag.value == -1: 
            pass
        print("Continuing...")
        workers[self.stop_flag.value].join()
        #sleep(1)
        for i in range(cores):
            workers[i].join() # reminder: Do not use terminate() with Pipes and Queues
            print(workers[i], workers[i].is_alive())
        sleep(1)
        print()
        for i in range(cores):
            print(workers[i], workers[i].is_alive())
    ## Note that using start() will run them in parallel while run() will run them in serial
    ## no idea why atm
    ## Also you could simply call
    '''
    for i in range(cores):
        mp.Process(target=worker, args=[i]).start()
    '''
    ## this will not work
    '''
    for i in range(cores):
        workers[i].run()
    '''