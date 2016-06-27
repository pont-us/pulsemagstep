#!/usr/bin/python

'''
pulsemagstep is free software released under the MIT licence.
See the file COPYING for details.
By Pontus Lurcock (pont at talvi dot net), 2016.
'''

from scipy import polyfit
import scipy.interpolate
from numpy import arange
from math import log10
from optparse import OptionParser
import matplotlib.pyplot as plt

def pick_desired_fields(start, end, number, exponential=False):
    if not exponential:
        span = end-start
        step = span/float(number-1)
        values = arange(start, end+step, step)
        return values
    else:
        values = pick_desired_fields(log10(start), log10(end), number, False)
        vs2 = [round(10**logfield, 1) for logfield in values]
        return vs2

def make_calibration(input_file):
    calib = []
    with open(input_file, "r") as fh:
        for line in fh.readlines():
            if line == "\n" or line[0] == "#": continue
            (voltage, field) = line.strip().split(" ")
            calib.append((float(voltage), float(field))) # mT
    return calib

def interpolate_segment(field, calib):
    if (field < calib[0][1] or field > calib[-1][1]):
        return -1
    s = 0
    while (calib[s][1] < field):
        s = s + 1
    scale = (calib[s][0] - calib[s-1][0]) / (calib[s][1] - calib[s-1][1])
    return calib[s-1][0] + scale * (field - calib[s-1][1])

def interpolate_pwl(fields, calib):
    result = []
    for field in fields:
        result.append((field, interpolate_segment(field, calib)))
    return result

def interpolate_spline(fields, calib):
    (volts, mt) = zip(*calib)
    tck = scipy.interpolate.splrep(mt, volts, s=0.0)
    result = []
    for xval in fields:
        try:
            yval = scipy.interpolate.splev(xval,tck,der=0)
        except:
            yval = -1.0E30
        result.append((xval, yval))
    return result

def interpolate_lsq(fields, calib):
    (volts, mt) = zip(*calib)
    (slope, intercept) = polyfit(mt, volts, 1)
    result = []
    for field in fields:
        result.append((field, field * slope + intercept))
    return result

def interpolate(fields, technique, calib):
    if technique=='lsq':
        result = interpolate_lsq(fields, calib)
    elif technique=='spl':
        result = interpolate_spline(fields, calib)
    elif technique=='pwl':
        result = interpolate_pwl(fields, calib)
    return result

def make_graph(calib, results, technique):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    calib_xy = tuple(zip(*calib))
    results_yx = tuple(zip(*results))
    ymin = min(calib[0][1], results[0][0])
    ymax = max(calib[-1][1], results[-1][0])
    ys = range(int(ymin), int(ymax+1))
    interp_results = interpolate(ys, technique, calib)
    ax.plot(tuple(zip(*interp_results))[1], ys, color="cyan", label="calibration curve")
    ax.plot(results_yx[1], results_yx[0], "+", mec="black", mew=0.5, label="interpolated step")
    ax.plot(calib_xy[0], calib_xy[1], "o", mfc="none", mec="red", label="calibration point")
    ax.legend(loc="best")
    plt.savefig("test.pdf")

def main():

    usage = "usage: %prog [options] <calibration_file>"
    parser = OptionParser(usage = usage)
    parser.add_option("-i", "--interpolation", dest="interp", default="spl",
                      help="spl spline, pwl piecewise linear, lsq least-squares",
                      metavar="TYPE")
    parser.add_option("-s", "--steps", dest="steps", default="35",
                      help="number of steps",
                      metavar="N")
    parser.add_option("-m", "--min", dest="min", default="3.3",
                      help="minimum field (mT)",
                      metavar="MILLITESLA")
    parser.add_option("-a", "--max", dest="max", default="1000",
                      help="maximum field (mT)",
                      metavar="MILLITESLA")
    parser.add_option("-g", "--graph", dest="graph", default=None,
                      help="produce a PDF graph of the calibration and steps",
                      metavar="FILENAME")
    parser.add_option("-d", "--distribution", dest="dist", default="exp",
                      help="step distribution: lin[ear] or exp[onential]",
                      metavar="TYPE")
    (opt, args) = parser.parse_args()

    if len(args) != 1:
        print("Incorrect number of arguments.")
        print(usage)
        return
    
    calibration_file = args[0]
    
    calib = make_calibration(calibration_file)
    
    desired_fields =  pick_desired_fields(float(opt.min),
                                          float(opt.max),
                                          float(opt.steps),
                                          opt.dist.startswith('e'))
    results = interpolate(desired_fields, opt.interp, calib)
    
    for result in results:
        print('%6.1f\t%5.1f' % (result[0], result[1]))

    if opt.graph:
        make_graph(calib, results, opt.interp)

if __name__ == "__main__":
    main()
