import cProfile
import time
import logging
import ray


if ray.is_initialized:
    ray.shutdown()
ray.init(logging_level=logging.ERROR)

import random
listKubson = [ random.randint(1, 2000) for _ in range(1000) ]
def bubble_sort(arr):
    n = len(arr)

    # Traverse through all array elements
    for i in range(n):

        # Last i elements are already in place
        for j in range(0, n - i - 1):

            # traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    return arr

@ray.remote
def bubble_sort_dist(arr):
    n = len(arr)

    # Traverse through all array elements
    for i in range(n):

        # Last i elements are already in place
        for j in range(0, n - i - 1):

            # traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    return arr

@ray.remote
def merge(list1, list2):
    result = []
    i = 0
    j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    result += list1[i:]
    result += list2[j:]
    return result

import random
listKubson = [ random.randint(1, 2000) for _ in range(1000) ]
def local():
    bubble_sort(listKubson)

def remote():
    slice_index = len(listKubson) // 4
    slice1 = listKubson[0: slice_index]
    slice2 = listKubson[slice_index: slice_index*2]
    slice3 = listKubson[slice_index*2: slice_index * 3]
    slice4 = listKubson[slice_index*3:]

    slice1 = bubble_sort_dist.remote(slice1)
    slice2 = bubble_sort_dist.remote(slice2)
    slice3 = bubble_sort_dist.remote(slice3)
    slice4 = bubble_sort_dist.remote(slice4)

    slice12 = merge.remote(ray.get(slice1), ray.get(slice2))
    slice34 = merge.remote(ray.get(slice3), ray.get(slice4))
    final_result = merge.remote(ray.get(slice12), ray.get(slice34))

    return ray.get(final_result)

print('local run')

start_timel = time.time()
cProfile.run("local()")
end_timel = time.time()

print('remote run')
start_timer = time.time()
cProfile.run("remote()")
end_timer = time.time()

ray.shutdown()


print("local time:", end_timel - start_timel)
print("remote time:", end_timer - start_timer)
