import logging

import ray
import random


if ray.is_initialized:
    ray.shutdown()
ray.init(logging_level=logging.ERROR)

N_WORKERS = 4
N_SAMPLES = 10000

@ray.remote
class ParameterSever:
    def __init__(self):
        self.in_count = 0

    def get_params(self):
        # Return current gradients
        return self.in_count

    def calc_pi(self):
        return self.in_count / N_SAMPLES * 4

    def update_in(self, val):
        # Update the gradients
        self.in_count += val

@ray.remote
def worker(ps):         # It takes an actor handle or instance as an argument
    return [ps.update_in.remote(rand_pi()) for _ in range(N_SAMPLES // N_WORKERS)]


def rand_pi():
    x = random.random()
    y = random.random()
    if x * x + y * y <= 1:
        return 1
    else:
        return 0


param_server = ParameterSever.remote()
print(param_server)

workers = [worker.remote(param_server) for _ in range(N_WORKERS)]

ray.get(workers)

print(ray.get(param_server.calc_pi.remote()))