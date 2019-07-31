# This file handles all aspects of point and lens selection for other files


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
