import logging
import time
import ray
import random
from random import randint
import numpy as np

if ray.is_initialized:
    ray.shutdown()
ray.init(logging_level=logging.ERROR)
# ray.init(address='auto', ignore_reinit_error=True, logging_level=logging.ERROR)


CALLERS=["A","B","C"]

@ray.remote
class MethodStateCounter :
    def __init__(self) :
        self.invokers={"A" : 0,"B" : 0,"C" : 0}
        self.invoker_list = {"A": [], 'B': [], 'C': []}

    def invoke(self,name) :
        # pretend to do some work here
        time.sleep(0.5)
        # update times invoked
        self.invokers[name]+=1
        self.invoker_list[name].append(random.randint(5, 26))
        # return the state of that invoker
        return self.invokers[name], self.invoker_list[name]

    def get_invoker_state(self,name) :
        # return the state of the named invoker
        return self.invokers[name]

    def get_invoker_llist(self, name):
        return self.invoker_list[name]

    def get_all_invoker_state(self) :
        # reeturn the state of all invokers
        return self.invokers

# Create an instance of our Actor
worker_invoker = MethodStateCounter.remote()
print(worker_invoker)

# Iterate and call the invoke() method by random callers and keep track of who
# called it.

for _ in range(10):
    name = random.choice(CALLERS)
    worker_invoker.invoke.remote(name)

# Invoke a random caller and fetch the value or invocations of a random caller

print('method callers')
for _ in range(1000):
    random_name_invoker = random.choice(CALLERS)
    times_invoked, invoker_list = ray.get(worker_invoker.invoke.remote(random_name_invoker))
    print(f"Named caller: {random_name_invoker} called {times_invoked}")
    print(f"invokers {random_name_invoker} computation list: {invoker_list}")

# Fetch the count of all callers
print(ray.get(worker_invoker.get_all_invoker_state.remote()))