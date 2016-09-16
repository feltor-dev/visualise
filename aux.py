import logging
import os
import json
import glob
import numpy as np
import matplotlib as mpl
log = logging.getLogger(__name__)


def array2string(x, n_dec):
    """
    string = convert_array2string(x, n_dec):
    """
    arraystr = np.array2string(x, precision=n_dec,
                               separator=',', suppress_small=True)
    return arraystr


class npin4linspace:
    def __init__(self, ls):
        self.__ls = ls

    def get(self, x):
        idx = []
        for value in flatten([x]):
            bmask = self.__ls <= value
            idx.append(np.count_nonzero(bmask[:-1])-1)
        return np.array(idx)


def parse_path(filepath):
    path, filename = os.path.split(filepath)
    if path == "":
        path = "./"
    prefix = os.path.splitext(os.path.basename(filename))[0]
    return path, filename, prefix


class loop_minmax:
    def __init__(self):
        self.__min = None
        self.__max = None
        self.__flag = True

    def reset(self):
        self.__init__()

    def set(self, min, max):
        if self.__flag:
            self.__min = min
            self.__max = max
            self.__flag = False
        else:
            if min < self.__min:
                self.__min = min
            if max > self.__max:
                self.__max = max

    def get(self):
        return self.__min, self.__max


def flatten(list_in):
    return [item for sublist in list_in for item in sublist]


def flatten_unique(list_in):
    return list(set([item for sublist in list_in for item in sublist]))


def unique_ordered(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def listify(val):
    if len(np.shape(val)) == 0:
        val = [val]
    return val
