import os
import sys
import glob
import json
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib as mpl


def pgf4a0line():
    rcParameter = {
        'pgf.texsystem': 'lualatex',
        'text.usetex': True,
        'pgf.rcfonts': False,
        'font.family': 'serif',
        'font.serif': [],
        'font.sans-serif': [],
        'font.monospace': [],
        'font.size': 20.74,
        'axes.labelsize': 20.74,
        'xtick.labelsize': 17.28,
        'ytick.labelsize': 17.28,
        'lines.linewidth' : 1.0,
        'axes.linewidth': 1.25,
        'xtick.major.size' : 5,
        'xtick.minor.size' : 2,
        'xtick.major.width' : 0.8,
        'xtick.minor.width' : 0.6,
        'legend.fontsize' : 20.74,
        'pgf.preamble': [
            '\\usepackage{amsmath}',
        ]
    }
    return rcParameter

rcParameter = pgf4a0line()
mpl.rcParams.update(rcParameter)

def wxh_cm(w):
    w = w/2.54
    return (w, w/1.618)

def save_pgf(filename):
    plt.savefig(filename, facecolor='none',
                edgecolor='none', bbox_inches='tight', dpi=600)

path_data = "/path/to/data/"
os.chdir(path_data)

prefices = ["muz2_az_", "muz2p5_az_", "muz5_az_", "muz10_az_", "muz20_az_"]
mu_j = np.array([2, 2.5, 5.0, 10.0, 20.0])
a_j = np.array([1.e-3, 2.e-3, 5.e-3, 1.e-2, 2.e-2, 5.e-2, 1.e-1, 2.e-1, 5.e-1])

vel_x__max = []
t_vel_x__max = []
for prefix in prefices:
    v_max, t_max = [], []
    for i, val in enumerate(a_j):
        filename = prefix+"{}_analysed.nc".format(i)
        with Dataset(filename, "r") as data:
            v_max.append(np.amax(data["electrons_analysed"]["velX"][:]))
            t_max.append(data["time"][np.argmax(data["electrons_analysed"]["velX"][:])])
    vel_x__max.append(np.array(v_max))
    t_vel_x__max.append(np.array(t_max))

marker = ["ko", "kD", "kv", "ks", "k^"]
# raw: a_j : vel_x__max(n_e)
fig, ax = plt.subplots(figsize=wxh_cm(25))
for i, val in enumerate(mu_j):
    ax.plot(a_j, vel_x__max[i], marker[i], markeredgewidth=0.0,
            label="$\\mu_j = {}$".format(mu_j[i]))
ax.set_xscale("log")
ax.set_yscale("log")

leg = ax.legend(loc="lower left", numpoints = 1)
leg.get_frame().set_linewidth(0.0)

ax.set_xlim(5.5E-4, 1.4E+0)
ax.set_ylim(0.008, 0.062)
dax = 0.03
ax.spines['bottom'].set_position(('axes', -dax*1.618))
ax.spines['left'].set_position(('axes', -dax))
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
# Ticks
major_xticks = [1.E-3, 1.E-2, 1.E-1, 1.E+0]
minor_xticks = [2.E-3, 5.E-3, 2.E-2, 5.E-2, 2.E-1, 5.E-1]
major_yticks = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06]
ax.set_xticks(major_xticks)
ax.set_yticks(major_yticks)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
for tick in minor_xticks:
    ax.axvline(tick, linestyle=':', color='k', alpha=0.7) # vertical lines
ax.grid(which="major")
ax.grid(which='major', alpha=0.9)
ax.set_xlabel("$a_z \; [\,]$")
ax.set_ylabel("$v^x_{max} \; [1/\\varrho_s]$", labelpad=15)
save_pgf("/home/e3r/oepg_poster2016/scale.pgf")

plt.show()
