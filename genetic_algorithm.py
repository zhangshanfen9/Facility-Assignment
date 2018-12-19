#!/usr/bin/python
# -*- coding: UTF-8 -*-
import math
import random
from copy import *
import functools
import matplotlib.pyplot as plt

# 参数
CITY_NUM = 105
# CITY_NUM = 150

# 0 -- random change two city
# 1 -- random change k city, k is depended on step
# 2 -- two-opt change
NEIGHBORHOOD_METHOD = 2
CROSS_PRO = 0.6
# VARI_PRO = 0.4
VARI_PRO = 0.3
GROUP_SIZE = 300
STEP_TOTAL = 5000
SELECT_METHOD = 1

NON_LINEAR_MAX_PRO = 0.02

# 0 -- linear grade-based
# 1 -- non-linear grade-based
# 2 -- fitness-based
SELECT_METHOD = 1

group = []

points_x = []
points_y = []

cost_pro = [0]
best_distance_history = []
the_best_way = []
the_best_his = 1000000000
dis_matrix = [[0] * CITY_NUM for i in range(CITY_NUM)]


def euc2d_distance(x1, x2, y1, y2):
    return math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))


def make_distance_matrix():
    with open("lin105.tsp", "r") as f:
    # with open("ch150.tsp", "r") as f:
        s = f.read()
    arr = s.split()
    arr = arr[:-1]
    for i in range(CITY_NUM):
        points_x.append(float(arr[i * 3 + 1]))
        points_y.append(float(arr[i * 3 + 2]))
    for i in range(CITY_NUM):
        for j in range(CITY_NUM):
            dis_matrix[i][j] = euc2d_distance(points_x[i], points_x[j], points_y[i], points_y[j])


def init_way():
    way = []
    for i in range(CITY_NUM):
        way.append(i)
    random.shuffle(way)
    return way


def get_neighbor(way, now_n, total_n):
    if NEIGHBORHOOD_METHOD == 0 or NEIGHBORHOOD_METHOD == 1:
        trans_num = 1
        if NEIGHBORHOOD_METHOD == 1:
            trans_num = int(0.2 * CITY_NUM * (1 - math.sqrt(now_n / total_n)))
            # print(trans_num)
            if trans_num < 1:
                trans_num = 1
        for k in range(trans_num):
            rana = random.randint(0, CITY_NUM - 1)
            ranb = random.randint(0, CITY_NUM - 1)
            way[rana], way[ranb] = way[ranb], way[rana]
    elif NEIGHBORHOOD_METHOD == 2:
        rana = random.randint(0, CITY_NUM - 1)
        ranb = random.randint(0, CITY_NUM - 1)
        while ranb < rana:
            rana = random.randint(0, CITY_NUM - 1)
            ranb = random.randint(0, CITY_NUM - 1)
        temp = way[rana : ranb + 1][:]
        temp.reverse()
        count = 0
        for i in range(rana, ranb + 1):
            way[i] = temp[count]
            count += 1


def get_cost(way):
    res = 0
    for i in range(len(way) - 1):
        res += dis_matrix[way[i]][way[i + 1]]
    res += dis_matrix[way[len(way) - 1]][way[0]]
    return res


def init_group():
    global group
    for _ in range(GROUP_SIZE):
        group.append(init_way())


def sort_function(x, y):
    cx = get_cost(x)
    cy = get_cost(y)
    if cx < cy:
        return -1
    elif cx == cy:
        return 0
    else:
        return 1

def select_group():
    global group
    global cost_pro
    group = sorted(group, key = functools.cmp_to_key(sort_function))
    res = get_cost(group[0])
    temp_group = []
    for _ in range(GROUP_SIZE):
        random_num = random.random()
        for i in range(GROUP_SIZE):
            if random_num >= cost_pro[i] and random_num < cost_pro[i+1]:
                temp_group.append(group[i])
                break

    # print(len(temp_group))
    group = deepcopy(temp_group)
    group = sorted(group, key = functools.cmp_to_key(sort_function))
    return res, group[0]


def cross_over():
    global group
    # print(group)
    for i in range(int(GROUP_SIZE / 5)):
        a = random.randint(0, GROUP_SIZE - 1)
        b = random.randint(0, GROUP_SIZE - 1)
        if random.random() < CROSS_PRO:
            ng1 = OX_crosser(group[a], group[b])
            ng2 = OX_crosser(group[b], group[a])
            group.append(ng1)
            group.append(ng2)


def OX_crosser(w1, w2):
    ran1 = random.randint(0, CITY_NUM - 1)
    ran2 = random.randint(0, CITY_NUM - 1)
    if ran2 < ran1:
        ran1, ran2 = ran2, ran1
    offspring = []
    w1_part = w1[ran1:ran2 + 1]
    w1_part_set = set()
    for wpi in w1_part:
        w1_part_set.add(wpi)
    for i in range(CITY_NUM):
        if len(offspring) == ran1:
            for j in range(len(w1_part)):
                offspring.append(w1_part[j])
        if not w2[i] in w1_part_set:
            offspring.append(w2[i])
    if len(offspring) < CITY_NUM:
        for j in range(len(w1_part)):
            offspring.append(w1_part[j])
    return offspring


def mutation(step, total_step):
    for i in range(GROUP_SIZE):
        if random.random() < VARI_PRO:
            get_neighbor(group[i], step, total_step)


def save_result():
    plt.ioff()
    plt.show()

    with open("E:\\result2_lin105.txt", "w+") as f:
        f.write(str(the_best_way))
        f.write("\n")


def init():
    plt.figure(1)
    plt.figure(2)
    plt.ion()

    total_pro = 0
    if SELECT_METHOD == 0:
        a = 1.8
        b = 2 * (a - 1)
        # linear function
        for i in range(1, GROUP_SIZE + 1):
            pro = (a - b * float(i) / (GROUP_SIZE + 1)) / GROUP_SIZE
            total_pro += pro
            cost_pro.append(total_pro)
    elif SELECT_METHOD == 1:
        # non-linear function
        q = NON_LINEAR_MAX_PRO
        for i in range(1, GROUP_SIZE + 1):
            if i != GROUP_SIZE:
                pro = q * pow(1 - q, i - 1)
            else:
                pro = pow(1 - q, i - 1)
            total_pro += pro
            cost_pro.append(total_pro)


def dynamic_show(step, best_his, best_way):
    print("step %d: best distance: %f" % (step, best_his))

    draw_x = []
    draw_y = []

    # 绘图
    for i in range(CITY_NUM):
        draw_x.append(points_x[best_way[i]])
        draw_y.append(points_y[best_way[i]])
    draw_x.append(points_x[best_way[0]])
    draw_y.append(points_y[best_way[0]])

    plt.figure(1)
    plt.cla()
    plt.title("Current best result:")
    ax = plt.gca()
    # 设置x轴、y轴名称
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    # 画连线图，以x_list中的值为横坐标，以y_list中的值为纵坐标
    # 参数c指定连线的颜色，linewidth指定连线宽度，alpha指定连线的透明度
    ax.plot(draw_x, draw_y, color='r', linewidth=1, alpha=0.6)

    best_distance_history.append(best_his)
    plt.figure(2)
    plt.cla()
    plt.title("Best distance")
    # 画连线图，以x_list中的值为横坐标，以y_list中的值为纵坐标
    # 参数c指定连线的颜色，linewidth指定连线宽度，alpha指定连线的透明度
    plt.plot(best_distance_history)

    plt.pause(0.1)

if __name__ == '__main__':
    init()
    make_distance_matrix()
    init_group()
    step = 0
    while step < STEP_TOTAL:
        step += 1
        best_his, best_solution = select_group()
        if best_his < the_best_his:
            the_best_way = deepcopy(best_solution)
            the_best_his = best_his
        if step % 10 == 0:
            dynamic_show(step, best_his, the_best_way)
        cross_over()
        mutation(step, STEP_TOTAL)
    save_result()