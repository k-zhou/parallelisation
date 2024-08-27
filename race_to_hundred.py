import multiprocessing as mp
import multiprocessing.sharedctypes
from         ctypes import Structure, c_bool, c_int, c_float, c_uint
from             os import cpu_count

import random          as rnd
from           time import time_ns, sleep

class race_to_hundred():

    def worker(self): pass
    def run(self):    pass

    def __init__(self) -> None:
        self.run()
    
    def worker(self, index=0, pass_data=None) -> None:
        if pass_data == None: 
            pass_data = dict()
            pass_data["round"] = 0
        total = 0
        print(f"Worker #{index} starting.")
        while(total < 100):
            period = rnd.random() * 0.5 * 1000000000
            end_time = time_ns() + period
            while time_ns() < end_time: pass
            total += rnd.randint(1,4)
            #print(f"Worker #{index} at {total}")
        print(f"Worker #{index} finishes at {total}")
        
    def run(self, reset=None) -> None:
        cores = cpu_count()
        if cores == None: cores = 1
        # internal containers
        index = 0
        # reset all internal containers
        if not reset == None:
            index = 0
        mn = mp.Manager()
        workers = list([0 for i in range(cores)])
        for i in range(cores):
            workers[i] = mp.Process(target=self.worker, args=[i])
            workers[i].start()
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