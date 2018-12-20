#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
from copy import deepcopy
import xlwt
import time

TIME_SAVE_STEP = 30000
# TIME_SAVE_STEP = 5000
STEP_TOTAL = 200000
MAX_NUM = 100000000
NEIGHBOR_METHOD = 0
# 0 -- change two customers selections(neighbor)
# 1 -- generate a new assignment(greedy)
# 2 -- random change a customer's selection(neighbor)
facility_num = 0
customer_num = 0
facility_capacity = []
facility_cost = []
allocating_cost = []
customer_demand = []

best_cost = MAX_NUM
best_solution = []
best_step = -1

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
        # while not is_assign_valid(res):
        #     res = init_assignment()
        return res
    elif NEIGHBOR_METHOD == 2:
        res = deepcopy(assign)
        rana = random.randint(0, customer_num - 1)
        res[rana] = random.randint(0, facility_num - 1)
        return res

def init():
    global facility_num
    global customer_num
    global facility_capacity
    global facility_cost
    global allocating_cost
    global customer_demand

    global best_cost
    global best_solution
    global best_step

    facility_num = 0
    customer_num = 0
    facility_capacity = []
    facility_cost = []
    allocating_cost = []
    customer_demand = []

    best_cost = MAX_NUM
    best_solution = []
    best_step = -1


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
    with open("Result/greedy_algorithm_details", "a") as f:
        f.write(res1 + res2 + res3)
    
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('sheet1', cell_overwrite_ok=True)
    sheet.write(0, 1, 'Result')
    sheet.write(0, 2, 'Time(s)')

    for i in range(len(xls_record)):
        sheet.write(i + 1, 0, xls_record[i][0])
        sheet.write(i + 1, 1, xls_record[i][1])
        sheet.write(i + 1, 2, xls_record[i][2])
    
    book.save('Result/greedy_algorithm2_xls/greedy_algorithm_result.xls' + str(ins) + '.xls')
    

def check():
    assert len(facility_capacity) == facility_num
    assert len(facility_cost) == facility_num
    assert len(customer_demand) == customer_num
    assert len(allocating_cost) == facility_num
    assert len(allocating_cost[0]) == customer_num


if __name__ == '__main__':
    for ins in range(1, 72):
        start = time.time()
        init()
        get_data(ins)
        check()
        best_solution = init_assignment()
        while not is_assign_valid(best_solution):
            best_solution = init_assignment()
        best_cost = get_cost(best_solution)
        for step in range(STEP_TOTAL):
            if step - best_step > TIME_SAVE_STEP:
                break
            if step % 2000 == 0:
                print("running instance: %d, step: %d, min cost:%d"%(ins, step, best_cost))
            temp_assign = get_neighbor(best_solution, NEIGHBOR_METHOD)
            while not is_assign_valid(temp_assign):
                temp_assign = get_neighbor(best_solution, NEIGHBOR_METHOD)
            temp_cost = get_cost(temp_assign)
            if temp_cost < best_cost:
                best_cost = temp_cost
                best_solution = temp_assign
                best_step = step
        running_time = time.time() - start
        xls_record.append(['p' + str(ins), best_cost, running_time])
        save_result(ins)