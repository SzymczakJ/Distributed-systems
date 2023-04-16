import cProfile
import time
import logging
import ray
import random

if ray.is_initialized:
    ray.shutdown()
ray.init(logging_level=logging.ERROR)

listKubson = [ random.randint(1, 2000) for _ in range(1000) ]
dictKubson = {i: random.randint(1, 2000) for i in range(1000)}

obj_ref_list = ray.put(listKubson)
obj_ref_dict = ray.put(dictKubson)

@ray.remote
def process_data():
    list_sum = sum(ray.get(obj_ref_list))
    dict_sum = sum(ray.get(obj_ref_dict))
    return (list_sum, dict_sum)

def dist_func():
    return ray.get(process_data.remote())

print("my task start")
cProfile.run("dist_func()")

ray.shutdown()