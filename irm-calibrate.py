#!/usr/bin/python

from scipy import polyfit
import scipy.interpolate
from numpy import arange
from math import log10

from optparse import OptionParser

parser = OptionParser(usage = "usage: %prog [options] inputfile")
parser.add_option("-i", "--interpolation", dest="interp", default="spl",
                  help="spl spline, pwl piecewise linear, lsq least-squares",
                  metavar="TYPE")
parser.add_option("-c", "--calibration", dest="calib", default='',
                  help="file containing field vs. voltage calibration data",
                  metavar="FILE")
parser.add_option("-s", "--steps", dest="steps", default='35',
                  help="number of steps",
                  metavar="N")
parser.add_option("-m", "--min", dest="min", default='3.3',
                  help="minimum field (mT)",
                  metavar="MILLITESLA")
parser.add_option("-a", "--max", dest="max", default='1000',
                  help="maximum field (mT)",
                  metavar="MILLITESLA")
parser.add_option("-d", "--distribution", dest="dist", default='exp',
                  help="point distribution: lin[ear] or exp[onential]",
                  metavar="TYPE")
(opt, args) = parser.parse_args()

calib_string = \
'''0 0
10 0.29
15 0.42
20 0.56
25 0.70
50 1.43
75 2.16
100 2.89
150 4.35
200 5.81
250 7.27
300 8.71
350 10.15
375 10.80
400 11.49'''

#desired_fields = range(5, 100, 5) + range(100, 200, 10) + \
#    range(200, 600, 50) + range(600, 1000, 100) + [1000]
#desired_fields = map(float, desired_fields)

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

calib = []
for line in calib_string.split('\n'):
    (voltage, field) = line.split(' ')
    calib.append((float(voltage), float(field) * 100)) # mT

def interpolate_segment(field):
    if (field < calib[0][1] or field > calib[-1][1]):
        return -1
    s = 0
    while (calib[s][1] < field):
        s = s + 1
    scale = (calib[s][0] - calib[s-1][0]) / (calib[s][1] - calib[s-1][1])
    return calib[s-1][0] + scale * (field - calib[s-1][1])

def interpolate_pwl(fields):
    result = []
    for field in desired_fields:
        result.append((field, interpolate_segment(field)))
    return result

def interpolate_spline(fields):
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

def interpolate_lsq(fields):
    (volts, mt) = zip(*calib)
    (slope, intercept) = polyfit(mt, volts, 1)
    result = []
    for field in fields:
        result.append((field, field * slope + intercept))
    return result

def interpolate(fields, technique):
    if technique=='lsq':
        result = interpolate_lsq(fields)
    elif technique=='spl':
        result = interpolate_spline(fields)
    elif technique=='pwl':
        result = interpolate_pwl(fields)
    return result

desired_fields =  pick_desired_fields(float(opt.min), float(opt.max),
                                      float(opt.steps),
                                      opt.dist.startswith('e'))
results = interpolate(desired_fields, opt.interp)

for result in results:
    print '%6.1f\t%5.1f' % (result[0], result[1])
