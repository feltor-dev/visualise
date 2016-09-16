from aux import array2string, loop_minmax
from vis import ccmap
import numpy as np
import matplotlib.pyplot as plt
import itertools
import logging
import json
from netCDF4 import Dataset
log = logging.getLogger(__name__)


class DataObject:
    def __init__(self, filename, variable):
        self.fn = filename
        self.var = variable
        self.get_t_xyz_nsi()
        self.zl = None
        self.grp = {}

    def get_t_xyz_nsi(self):
        with Dataset(self.fn, "r") as data:
            self.nsip = json.loads(data.inputfile)
            self.x = data.variables['x'][:]
            self.y = data.variables['y'][:]
            self.t = t_idx(data, [])
            self.z_min, self.z_max, self.z_ae = z_mme(data, self.var, self.t)

    def set_azl(self, n_lev_auto, n_dec):
        with Dataset(self.fn, "r") as data:
            self.azl = auto_z_levels(data, self.x, self.y, self.var, self.t,
                                     n_lev_auto, n_dec)

    def set_fzl(self, z_levels, n_seg, avleng, n_frame):
        with Dataset(self.fn, "r") as data:
            n_frame = np.floor(n_frame*len(self.t)).astype(int)
            self.fzl = filter_z_levels(data, self.x, self.y, self.var, self.t,
                                       z_levels, n_seg, avleng, n_frame)

    def set_zl_indep(self, n_lev_auto, n_dec, n_seg,
                     avleng, n_frame, n_lev, symflag):
        with Dataset(self.fn, "r") as data:
            self.azl = auto_z_levels(data, self.x, self.y, self.var, self.t,
                                     n_lev_auto, n_dec)
            print("automatic:\n{}".format(self.azl))
            n_frame = np.floor(n_frame*len(self.t)).astype(int)
            self.fzl = filter_z_levels(data, self.x, self.y, self.var, self.t,
                                       self.azl, n_seg,
                                       avleng, n_frame)
            print("filtered:\n{}".format(self.fzl))
            self.zl = spread_z_levels(self.fzl, n_lev, symflag)
            print("spread:\n{}".format(self.zl))

    def set_zl(self, z_levels):
        self.zl = z_levels

    def set_grp(self, key, val):
        self.grp[key] = val

    def set_ewc(self, edge, white, color_span, color_show):
        self.edge = edge
        self.white = white
        self.color_span = color_span
        self.color_show = color_show

    def set_cmap(self, cmap_name):
        xedges = [self.z_min, self.z_max] if self.edge is None else self.grp[self.edge]
        xwhite = [self.z_min, self.z_max] if self.white is None else self.grp[self.white]
        xcolor_span = [-self.z_ae, self.z_ae] if self.color_span is None else self.grp[self.color_span]
        xcolor_show = [self.z_min, self.z_max] if self.color_show is None else self.grp[self.color_show]
        self.cmap, self.norm = ccmap(xedges, xwhite, xcolor_span,
                                     xcolor_show, cmap_str=cmap_name,
                                     n=1024, rgba_grey=[.8, .8, .8, 1.])


# operate on passed netcdf dataset --------------------------------------------
def t_idx(fid, t):
    """
    list(idx) = list_t_idx(fid, t)
                           fid ... handler to netcdf4 dataset
                                t ... (list of) indices (integer)
                                [] means all timesteps
    """
    t_idx = []
    if type(t) is int:
        t_idx.append(t)
    elif np.size(t) == 0:
        t_idx = range(len(fid.variables['time'][:]))
    else:
        t_idx = t
    return t_idx


def z_mme(fid, variable, t_idx):
    """
    float, float, float = zmme(fid, variable, t_idx)
    z_min  z_max  |z_ext|
    """
    data = fid.variables[variable][t_idx[-1]]
    z_min = np.amin(data)
    z_max = np.amax(data)
    for i in t_idx[:-1]:
        data = fid.variables[variable][i]
        data_min = np.amin(data)
        data_max = np.amax(data)
        if data_max > z_max:
            z_max = data_max
        if data_min < z_min:
            z_min = data_min
    z_ext_abs = np.amax(np.absolute((z_min, z_max)))
    return (z_min, z_max, z_ext_abs)


def auto_z_levels(fid, x, y, variable, t_idx, n_cont, n_dec):
    """
    list(float) = auto_z_levels(fid, variable, t_idx, n_cont, n_dec)
                                                      ... # contour lines
                                                              ... # post .
    """
    fig, ax = plt.subplots()
    z_levs = np.ndarray(0)
    for i in t_idx:
        data = fid.variables[variable][i]
        cp = ax.contour(x, y, data, n_cont)
        z_levs = np.concatenate((z_levs, cp.levels), axis=0)
        z_levs = np.sort(np.unique(np.around(z_levs, n_dec)))
    plt.close(fig)
    return z_levs


def filter_z_levels(fid, x, y, variable, t_idx, z_levs, n_seg_degrade,
                    avleng_degrade, n_frame_threshold):
    """
    list(float) = filter_z_levels(fid, variable, t_idx, z_levs, n_seg_degrade,
                                  avleng_degrade, n_frame_threshold)
    """
    fig, ax = plt.subplots()
    qual = np.ones((len(t_idx), len(z_levs)), dtype=np.int8)
    for i in t_idx:
        data = fid.variables[variable][i]
        cp = ax.contour(x, y, data, levels=z_levs)
        for j, level in enumerate(cp.collections):
            n_seg = len(level.get_segments())
            l = 0.
            for path in level.get_segments():
                l = l + np.sum(np.sqrt(np.sum(np.diff(path, axis=0)**2,
                                              axis=1)))   # length of contour
            # degrade ranking
            if n_seg == 0 or n_seg > n_seg_degrade or l/n_seg < avleng_degrade:
                qual[i, j] = 0
    z_levs = z_levs[np.sum(qual, axis=0) >= n_frame_threshold]
    plt.close(fig)
    return z_levs


def symmetric_z_levels(z_levs):
    """
    list(float) = symmetric_z_levels(z_levs)
    """
    z_levs_abs = np.absolute(z_levs)
    z_levs_abs_unique = np.unique(z_levs_abs)
    n = np.zeros(np.size(z_levs_abs_unique), dtype=int)-1
    for i, zau in enumerate(z_levs_abs_unique):
        for za in z_levs_abs:
            if zau == za:
                n[i] += 1
    z_levs = z_levs_abs_unique[n.astype(bool)]
    return z_levs


def spread_z_levels(z_levs, n_cont, symflag):
    """
    list(float) = spread_z_levels(z_levs, n_cont, symflag)
    """
    z_levs_sets = []
    if symflag:
        z_levs_sym = symmetric_z_levels(z_levs)
        z_levs_max = z_levs_sym[-1]
        z_levs_min = -z_levs_max
        for item in z_levs_sym[0:-1]:
            z_levs_sets.append(np.array([-item, item]))
    else:
        z_levs_min = np.amin(z_levs)
        z_levs_max = np.amax(z_levs)
        for item in z_levs[1:-1]:
            z_levs_sets.append(np.array([item]))

    inner = list(itertools.combinations(z_levs_sets, n_cont))
    n = len(inner)
    inner_npa = np.sort(np.squeeze(np.array(inner)).reshape(n, -1),
                        axis=1)
    lv, rv = np.empty((n, 1)), np.empty((n, 1))
    lv.fill(z_levs_min)
    rv.fill(z_levs_max)
    z_levs_npa = np.concatenate((lv, inner_npa, rv), axis=1)
    diff = np.diff(z_levs_npa)
    std = np.std(diff, axis=1)
    z_levs = z_levs_npa[np.argmin(std)]
    return z_levs


def z_levels(fid, x, y, variable, n_levels, n_frames, t_idx,
             symflag, n_lev_auto, n_dec, n_seg, avleng):
    """
    list(float) = zlevels(fid, variable, n_levels, n_frames, t_idx,
                          symflag, n_lev_auto, n_dec, n_seg, avleng)
    """
    z_levs_auto = auto_z_levels(fid, x, y, variable, t_idx, n_lev_auto, n_dec)
    z_levs_filter = filter_z_levels(fid, x, y, variable, t_idx, z_levs_auto,
                                    n_seg, avleng, n_frames)
    z_levs = spread_z_levels(z_levs_filter, n_levels, symflag)

    log.info('z-levels, automatic: '+array2string(z_levs_auto, n_dec))
    log.info('z-levels, filtered:  '+array2string(z_levs_filter, n_dec))
    log.info('z-levels, used:      '+array2string(z_levs, n_dec))
    return z_levs
