#!/usr/bin/python
# -*- coding: UTF-8 -*-
import math
import random
from copy import *
import xlwt
import time
# import functools
# import matplotlib.pyplot as plt

TIME_SAVE_STEP = 1800
STEP_TOTAL = 10000
MAX_NUM = 100000000
NEIGHBOR_METHOD = 2
# 0 -- change two customers selections
# 1 -- generate a new assignment
# 2 -- random change a customer's selection
CROSS_METHOD = 0
# 0 -- exchange one part
# 1 -- every bits has probability exchange
UNIFORM_PRO = 0.4
MUTATION_METHOD = 0
# 0 -- mutate a indivadual
VARI_PRO = 0.4
# 1 -- mutate a bit gene
# VARI_PRO = 0.006
INITIAL_GROUP_NUM = 200
GROUP_NUM = 200
LAMADA = 220


facility_num = 0
customer_num = 0
facility_capacity = []
facility_cost = []
allocating_cost = []
customer_demand = []
group = []

best_cost = MAX_NUM
best_solution = []
best_step = -1
same_cost = MAX_NUM
same_step = -1

xls_record = []

def get_data(index):
    global facility_num
    global customer_num
    global facility_capacity
    global facility_cost
    global allocating_cost
    global customer_demand
    with open('Instances/p' + str(index), 'r')as f:
        lines = f.read()
    arr = lines.replace('.', ' ').replace(chr(0), '').replace('\n', ' ').split()
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

def get_neighbor(assign):
    if NEIGHBOR_METHOD == 0:
        res = deepcopy(assign)
        rana = random.randint(0, customer_num - 1)
        ranb = random.randint(0, customer_num - 1)
        temp = res[rana]
        res[rana] = res[ranb]
        res[ranb] = temp
        return res
    elif NEIGHBOR_METHOD == 1:
        res = init_assignment()
        while not is_assign_valid(res):
            res = init_assignment()
        return res
    elif NEIGHBOR_METHOD == 2:
        res = deepcopy(assign)
        rana = random.randint(0, customer_num - 1)
        res[rana] = random.randint(0, facility_num - 1)
        return res

def init_group():
    global group
    for _ in range(INITIAL_GROUP_NUM):
        group.append(init_assignment())


# def sort_function(x, y):
#     cx = get_cost(x)
#     cy = get_cost(y)
#     if cx < cy:
#         return -1
#     elif cx == cy:
#         return 0
#     else:
#         return 1


def select_group():
    global group
    min_ind, min_cost, group_cost = get_group_cost()
    curr_best_solution = group[min_ind]
    # 2 players competition
    temp_group = []
    for _ in range(GROUP_NUM):
        a = random.randint(0, len(group) - 1)
        b = random.randint(0, len(group) - 1)
        if group_cost[a] < group_cost[b]:
            temp_group.append(group[a])
        else:
            temp_group.append(group[b])
    group = temp_group
    return min_cost, curr_best_solution
    

def get_group_cost():
    min_ind = 0
    min_cost = MAX_NUM
    group_cost = []
    for i in range(len(group)):
        tcost = get_cost(group[i])
        group_cost.append(tcost)
        if min_cost > tcost:
            min_cost = tcost
            min_ind = i
    return min_ind, min_cost, group_cost

def cross_over():
    global group
    temp_group = []
    for i in range(int(LAMADA / 2)):
        a = random.randint(0, len(group) - 1)
        b = random.randint(0, len(group) - 1)
        c1, c2 = [], []
        if CROSS_METHOD == 0:
            c1, c2 = OX_crosser(group[a], group[b])
        elif CROSS_METHOD == 1:
            c1, c2 = uniform_crosser(group[a], group[b])
        temp_group.append(c1[:])
        temp_group.append(c2[:])
    group += temp_group[:]

def uniform_crosser(w1, w2):
    offspring1 = deepcopy(w1)
    offspring2 = deepcopy(w2)
    for i in range(len(w1)):
        ran = random.random()
        if ran < UNIFORM_PRO:
            temp = offspring1[i]
            offspring1[i] = offspring2[i]
            offspring2[i] = temp
    return offspring1, offspring2

def OX_crosser(w1, w2):
    ran1 = random.randint(0, facility_num - 1)
    ran2 = random.randint(0, facility_num - 1)
    if ran2 < ran1:
        ran1, ran2 = ran2, ran1
    offspring1 = deepcopy(w1)
    offspring2 = deepcopy(w2)
    for i in range(ran1, ran2 + 1):
        temp = offspring1[i]
        offspring1[i] = offspring2[i]
        offspring2[i] = temp
    # print(offspring1, offspring2)
    return offspring1, offspring2


def mutation():
    global group
    if MUTATION_METHOD == 0:
        for i in range(len(group)):
            if random.random() < VARI_PRO:
                group[i] = get_neighbor(group[i])
    elif MUTATION_METHOD == 1:
        for i in range(len(group)):
            for j in range(customer_num):
                if random.random() < VARI_PRO:
                    group[i][j] = random.randint(0, facility_num - 1)


def init():
    global facility_num
    global customer_num
    global facility_capacity
    global facility_cost
    global allocating_cost
    global customer_demand
    global group

    global best_cost
    global best_solution
    global best_step

    global same_cost
    global same_step

    same_cost = MAX_NUM
    same_step = -1
    facility_num = 0
    customer_num = 0
    facility_capacity = []
    facility_cost = []
    allocating_cost = []
    customer_demand = []
    group = []

    best_cost = MAX_NUM
    best_solution = []
    best_step = -1

    # total_pro = 0
    # if SELECT_METHOD == 0:
    #     a = 1.8
    #     b = 2 * (a - 1)
    #     # linear function
    #     for i in range(1, GROUP_NUM + 1):
    #         pro = (a - b * float(i) / (GROUP_NUM + 1)) / GROUP_NUM
    #         total_pro += pro
    #         cost_pro.append(total_pro)
    # elif SELECT_METHOD == 1:
    #     # non-linear function
    #     q = NON_LINEAR_MAX_PRO
    #     for i in range(1, GROUP_NUM + 1):
    #         if i != GROUP_NUM:
    #             pro = q * pow(1 - q, i - 1)
    #         else:
    #             pro = pow(1 - q, i - 1)
    #         total_pro += pro
    #         cost_pro.append(total_pro)


def check():
    assert len(facility_capacity) == facility_num
    assert len(facility_cost) == facility_num
    assert len(customer_demand) == customer_num
    assert len(allocating_cost) == facility_num
    assert len(allocating_cost[0]) == customer_num

def save_result(ins):
    res1 = str(best_cost) + '\n'
    res2 = ''
    res3 = ''
    fset = set()
    for i in range(customer_num):
        res3 += str(best_solution[i] + 1) + ' '
        fset.add(best_solution[i])
    res3 += '\n'
    for i in range(facility_num):
        if i in fset:
            res2 += '1 '
        else:
            res2 += '0 '
    res2 += '\n'
    with open("Result/genetic_algorithm_details", "a") as f:
        f.write(res1 + res2 + res3)
    
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 1, 'Result')
    sheet.write(0, 2, 'Time(s)')

    for i in range(len(xls_record)):
        sheet.write(i + 1, 0, xls_record[i][0])
        sheet.write(i + 1, 1, xls_record[i][1])
        sheet.write(i + 1, 2, xls_record[i][2])
    
    book.save('Result/genetic_algorithm_xls/genetic_algorithm_result.xls' + str(ins) + '.xls')
    


if __name__ == '__main__':
    # test
    # facility_num = 5
    # LAMADA = 4
    # group = [[1,2,3,4,5], [6,7,8,9,10]]
    # cross_over()
    # print(group)

    for ins in range(1, 72):
        start = time.time()
        init()
        get_data(ins)
        check()
        init_group()
        for step in range(STEP_TOTAL):
            if step - same_step > TIME_SAVE_STEP:
                break
            min_cost, curr_best_solution = select_group()
            if step % 10 == 0:
                print("running instance: %d, step %d: min cost: %d" % (ins, step, min_cost))
            if min_cost < best_cost:
                best_solution = deepcopy(curr_best_solution)
                best_cost = min_cost
            if min_cost != same_cost:
                same_step = step
                same_cost = min_cost
            cross_over()
            mutation()
        running_time = time.time() - start
        xls_record.append(['p' + str(ins), best_cost, running_time])
        save_result(ins)
        