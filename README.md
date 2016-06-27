pulsemagstep
============

A tool for calculating voltage steps for a pulse magnetizer.

By Pontus Lurcock (pont at talvi dot net), 2016.

pulsemagstep is free software released under the MIT licence.
See the file COPYING for details.

Background
----------

pulsemagstep is intended to help in planning rock magnetic studies of
remanent coercivity spectra using a pulse magnetizer (a.k.a. impulse
magnetizer).

pulsemagstep was written for use with an ASC Scientific IM-10 impulse
magnetizer. This device does not allow the magnetic field strength to be
set directly by the user. Instead, a calibration table is used to
determine the voltage required to produce a desired field in the
magnetizer, and the user triggers the magnetizer when this voltage is
reached.

pulsemagstep is designed to perform two functions.

1. To calculate a linearly or exponentially spaced set of magnetization
   steps (field strengths).

2. To convert these field strengths to voltages using a calibration table
   for the magnetizer, interpolating between calibration points where
   necessary.

Requirements
------------

pulsemagstep is a Python script which should run under Python 2.7 or
any version of Python 3. In addition to the core Python libraries it
requires the numpy and scipy libraries.

Usage
-----

```
pulsemagstep.py [options] <calibration_file>

Options:
  -h, --help            show this help message and exit
  -i TYPE, --interpolation=TYPE
                        spl spline, pwl piecewise linear, lsq least-squares
  -s N, --steps=N       number of steps
  -m MILLITESLA, --min=MILLITESLA
                        minimum field (mT)
  -a MILLITESLA, --max=MILLITESLA
                        maximum field (mT)
  -d TYPE, --distribution=TYPE
                        point distribution: lin[ear] or exp[onential]
```

The step values are written to the standard output, one per line.
Each line consists of a field strength in millitesla, a tab character,
and a voltage in volts.

Calibration file
----------------

The calibration file is a text file with lines of the form

`<voltage> <field strength>`

The voltage is in volts. The field strength is in millitesla. They are
separated by a single space character. The field strengths and voltages
should be listed in increasing order. Lines beginning with a # character
are ignored, as are blank lines. An example calibration file
`calibration.txt` is provided with the program as a sample of the
format.
