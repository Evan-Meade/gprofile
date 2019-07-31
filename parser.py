# This file interprets a glafic .input file, resolves variables, and maps time delays over a given
# 3D range by calling glafic


import sys
import os
import numpy as np
import time as t
import subprocess
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt


points = []
maps = []
current = ""
new = ""
config_file = "config.input"
temporary_file = "temp.input"
dat_file = "out_point.dat"


def main():

    global points, maps, current, new
    start_time = t.time()

    with open(config_file, 'w+') as config:
        with open(sys.argv[1], 'r') as template:
            for line in template:
                if line[:11] == "**SHIFTER**":
                    params = line[12:].split(" ")
                    config.writelines("**PLACEHOLDER**\n")
                    current = "**PLACEHOLDER**\n"
                else:
                    config.writelines(line)

            template.close()
        config.close()

    points, maps = gen_points(params)
    results = np.zeros([int(params[6]), int(params[7]), int(params[8])], dtype=float)

    for i in range(0, len(points)):
        update_config(i)
        time = second_image()
        results[maps[i][0]][maps[i][1]][maps[i][2]] = time

    os.remove(config_file)
    os.remove(dat_file)
    print(f"\n{results}")
    end_time = t.time()
    print(f"\nPoints Calculated: {len(points)}\nTime elapsed (sec): {end_time - start_time}")

    visualize(results)


# Takes in arguments for a 3D range (redshift, x (as), y (as)) and returns a list of points at the
# specified grid size
def gen_points(params):
    # breaks down 3D range into end points and grid size from list
    zo = float(params[0])
    xo = float(params[1])
    yo = float(params[2])
    zf = float(params[3])
    xf = float(params[4])
    yf = float(params[5])
    zg = int(params[6])
    xg = int(params[7])
    yg = int(params[8])

    # List which will contain strings for points to be run through glafic
    point_list = []
    map_list = []

    # Calculating step size
    if zg > 1:
        zs = (zf - zo) / (zg - 1)
    else:
        zs = 0
    if xg > 1:
        xs = (xf - xo) / (xg - 1)
    else:
        xs = 0
    if yg > 1:
        ys = (yf - yo) / (yg - 1)
    else:
        ys = 0
    dig = 2

    # Iterating over 3D grid of test points and appending to point_list
    for zd in range(0, zg):
        for xd in range(0, xg):
            for yd in range(0, yg):
                zc = zo + zd * zs
                xc = xo + xd * xs
                yc = yo + yd * ys

                point_list.append(f"point {round(zc, dig)} {round(xc, dig)} {round(yc, dig)}\n")
                map_list.append([zd, xd, yd])

    # Returns list of all points to be tested
    return point_list, map_list


def update_config(pos):

    global points, maps, current, new
    new = points[pos]

    with open(temporary_file, 'w') as temp:
        with open(config_file, 'r') as config:
            for line in config:
                if line == current:
                    temp.writelines(new)
                else:
                    temp.writelines(line)
            config.close()
        temp.close()

    os.rename(temporary_file, config_file)

    current = new


def run_glafic():
    results = subprocess.check_output(f"glafic {config_file}", shell=True)


def second_image():
    run_glafic()
    next_time = grab_time()
    return next_time


def grab_time():

    output = np.loadtxt(dat_file)
    print(output)

    next_time = -1.0
    if output[0][0] > 1:
        min_time = -1
        for i in range(1, len(output)):
            val = output[i][3]
            if val > 0 and (min_time < 0 or val < min_time):
                min_time = val
        next_time = min_time

    return next_time


def visualize(results):
    for i in range(0, len(results)):
        df = pd.DataFrame(results[i])
        heatmap = sns.heatmap(df)
        plt.show()


if __name__ == "__main__":
    main()
