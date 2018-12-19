#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
from copy import deepcopy

STEP_TOTAL = 100000
MAX_NUM = 100000000
NEIGHBOR_METHOD = 0
# 0 -- change two customers selections
# 1 -- generate a new assignment
facility_num = 0
customer_num = 0
facility_capacity = []
facility_cost = []
allocating_cost = []
customer_demand = []

def get_data(index):
    with open('Instances/p' + str(index), 'r')as f:
        lines = f.read()
    arr = lines.replace('.', ' ').replace('\n', ' ').split()
    for i in range(len(arr)):
        arr[i] = int(arr[i])
    facility_num, customer_num = arr[0], arr[1]
    facility_capacity, facility_cost = [], []
    ind = 2
    for i in range(facility_num):
        facility_capacity.append(arr[ind])
        facility_cost.append(arr[ind + 1])
        ind += 2
    customer_demand = []
    for i in range(customer_num):
        customer_demand.append(arr[ind])
        ind += 1
    # ac[f, c]
    allocating_cost = []
    for i in range(facility_num):
        temp = []
        for j in range(customer_num):
            temp.append(arr[ind])
            ind += 1
        allocating_cost.append(temp)
    return facility_num, customer_num, facility_capacity, facility_cost, allocating_cost, customer_demand  


def init_assignment():
    global customer_num
    global facility_num
    assign = []
    for i in range(customer_num):
        assign.append(random.randint(0, facility_num - 1))
    return assign

def get_cost(assign):
    if not is_assign_valid(assign):
        return MAX_NUM
    cost = 0
    fset = set()
    for i in range(customer_num):
        fset.add(assign[i])
        cost += allocating_cost[assign[i]][i]
    for i in range(facility_num):
        if i in fset:
            cost += facility_cost[i]
    return cost


def is_assign_valid(assign):
    real_facility_capacity = [0] * facility_num
    for i in range(customer_num):
        real_facility_capacity[assign[i]] += customer_demand[i]
    for i in range(facility_num):
        if real_facility_capacity[i] > facility_capacity[i]:
            return False
    return True

def get_neighbor(assign, method):
    if method == 0:
        res = deepcopy(assign)
        rana = random.randint(0, customer_num - 1)
        ranb = random.randint(0, customer_num - 1)
        temp = res[rana]
        res[rana] = res[ranb]
        res[ranb] = temp
        return res
    elif method == 1:
        res = init_assignment()
        while not is_assign_valid(res):
            res = init_assignment()
        return res

if __name__ == '__main__':
    facility_num, customer_num, \
    facility_capacity, facility_cost, \
    allocating_cost, customer_demand = get_data(1)

    best_assign = init_assignment()
    while not is_assign_valid(best_assign):
        best_assign = init_assignment()
    best_cost = get_cost(best_assign)
    for step in range(STEP_TOTAL):
        if step % 10 == 0:
            print("step: %d, best cost:%d"%(step, best_cost))
        temp_assign = get_neighbor(best_assign, NEIGHBOR_METHOD)
        while not is_assign_valid(temp_assign):
            temp_assign = get_neighbor(best_assign, NEIGHBOR_METHOD)
        temp_cost = get_cost(temp_assign)
        if temp_cost < best_cost:
            best_cost = temp_cost
            best_assign = temp_assign