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


import sampling as samp

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

    points, maps = samp.gen_points(params)
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
