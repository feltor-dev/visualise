import os
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.axes_grid1 import make_axes_locatable
from aux import loop_minmax, flatten_unique, flatten, unique_ordered, parse_path, listify
from vis import ccbt, ccbr, blinda, blindr, t_plot, AxisObject
from pdata import spread_z_levels, DataObject
from print_parameter import pgf4a4, pgf4a0, pgf4beamer, hxw_dpi
from rw_config import read_json, logger, EvalConfig
import matplotlib.lines as lines

path, cfname, prefix = parse_path(sys.argv[1])
os.chdir(path)
config = read_json(cfname)
conf = EvalConfig(config)
log = logger(conf.jobname, True)

if conf.output == "pgf":
    if conf.medium == "a4":
        rcParameter = pgf4a4()
    if conf.medium == "a0":
        rcParameter = pgf4a0()
    if conf.medium == "beamer":
        rcParameter = pgf4a4()
    mpl.rcParams.update(rcParameter)

log.info("\n#--------------------------------------------------#")      #
log.info("working directory: {}".format(path))                          #
log.info("config file {} parsed successfully!\n".format(cfname))        #

# do[file][variable].t, *.z_min, *.z_max, *.z_ae
do = {}
for fn in conf.fn_var:
    do[fn] = {}
    for var in conf.fn_var[fn]:
        do[fn][var] = DataObject(fn, var)
        log.info("initialised data objects for: {}: {}".format(fn, var))#


# set normalisation groups
minmax = loop_minmax()
for grp in conf.grp_fn_var:
    minmax.reset()
    for fn in conf.grp_fn_var[grp]:
        for var in conf.grp_fn_var[grp][fn]:
            minmax.set(do[fn][var].z_min, do[fn][var].z_max)
    for fn in conf.grp_fn_var[grp]:
        for var in conf.grp_fn_var[grp][fn]:
            do[fn][var].set_grp(grp, minmax.get())
    log.info("normalised to: {}".format(grp))                           #


removie = []
# not normed z-levels: do[file][variable].zl
for fn in conf.nozlgrp_fn_var:
    for var in conf.nozlgrp_fn_var[fn]:
        log.info("calculate z-levels for: {}: {} ...".format(fn, var))  #
        cpc = conf.config[fn][var]["cplot"]
        try:
            do[fn][var].set_zl_indep(cpc["n_lev_auto"], cpc["n_dec"],
                                     cpc["n_seg"], cpc["av_leng"],
                                     cpc["n_frame"], cpc["n_lev"],
                                     cpc["symflag"])
        except Exception:
            removie.append((fn, var))
            continue


# z-levels normalisation
for grp in conf.zlgrp_fn_var:
    azl_pool = []
    for fn in conf.zlgrp_fn_var[grp]:
        for var in conf.zlgrp_fn_var[grp][fn]:
            cpc = conf.config[fn][var]["cplot"]
            try:
                do[fn][var].set_azl(cpc["n_lev_auto"], cpc["n_dec"])
                azl_pool.append(do[fn][var].azl)
            except Exception:
                removie.append((fn, var))
                continue
    azl_pool = np.sort(flatten_unique(azl_pool))
    fzl_pool = []
    for fn in conf.zlgrp_fn_var[grp]:
        for var in conf.zlgrp_fn_var[grp][fn]:
            cpc = conf.config[fn][var]["cplot"]
            try:
                do[fn][var].set_fzl(azl_pool, cpc["n_seg"],
                                    cpc["av_leng"], cpc["n_frame"])
                fzl_pool.append(do[fn][var].fzl)
            except Exception:
                removie.append((fn, var))
                continue
    cpc = conf.config[fn][var]["cplot"]
    fzl = flatten(fzl_pool)
    fzl = sorted(fzl, key=fzl.count, reverse=True)
    n_add2choose = 1
    if cpc["symflag"]:
        n = cpc["n_lev"]*2 + 1 + n_add2choose
    else:
        n = cpc["n_lev"] + 1 + n_add2choose
    fzl = unique_ordered(fzl)[0:n]
    szl = spread_z_levels(fzl, cpc["n_lev"], cpc["symflag"])
    for fn in conf.zlgrp_fn_var[grp]:
        for var in conf.zlgrp_fn_var[grp][fn]:
            do[fn][var].set_zl(szl)


# set cmap edges from normalisation
for fn in conf.fn_var_cbar:
    for var in conf.fn_var_cbar[fn]:
        do[fn][var].set_ewc(*conf.fn_var_cbar[fn][var])


# create cmaps
for fn in conf.fn_var:
    for var in conf.fn_var[fn]:
        do[fn][var].set_cmap(conf.config[fn][var]["cmap_name"])
        log.info("created cmaps for: {}: {}".format(fn, var))           #


log.info("#- - - - - - - - - - - - - - - - - - - - - - - - - #\n")      #
conf.removie_fn_var(removie)
# setup figure
hxw, dpi = hxw_dpi(conf.medium, conf.scale, conf.subplots)
n_blindr = conf.n_right
n_blindt = conf.n_top
for movie in conf.mf:
    print("movie: ", conf.mf[movie])
    fig, ax = plt.subplots(*conf.subplots, figsize=hxw)
    ax = listify(ax)
    axo = []
    for i, axis in enumerate(conf.mf[movie]):
        print(conf.mf[movie])
        axo.append(AxisObject(ax[i]))
        div = make_axes_locatable(ax[i])
        n_top, n_right = 0, 0
        for fn in axis:
            for var in axis[fn]:
                dos = do[fn][var]
                cos = conf.config[fn][var]
                axo[i].add_PlotObject(dos)
                if dos.zl is None:
                    axo[i].set_limits(dos.x, dos.y)
                    if cos["show_cbar"]:
                        ccbt(div, dos.cmap, dos.norm,
                             np.linspace(dos.z_min, dos.z_max, 4),
                             label=cos["label"])
                        n_top = n_top + 1
                else:
                    axo[i].set_extended_limits(dos.x, dos.y, dos.nsip["n"])
                    if cos["show_cbar"]:
                        ccbr(div, n_right, dos.cmap,
                             dos.norm, dos.zl, [], label=cos["label"])
                        n_right = n_right + 1
                if cos["zoom"] != []:
                    axo[i].set_zoom(cos["zoom"])
                if not cos["show_xspine"]:
                    axo[i].remove_xspine()
                if not cos["show_yspine"]:
                    axo[i].remove_yspine()
        if n_top == 0:
            blinda(div)
        for j in range(n_blindr-n_right+1):
            blindr(div, j)
        log.info("created axis-object for subplot #{:d}: {}: {}".format(i, fn, var))#


    # plot
    def update(i):
        log.info('frame  #'+str(i+1), extra={'same_line': True})
        for j, axis in enumerate(ax):
            axo[j].format_axis()
            for plotter in axo[j].pos:
                plotter.plot(i)
        time_text = ax[0].text(0.02, 0.95, 'time = %.1f $[\Omega_i]$' % dos.t[i],
                               transform=ax[0].transAxes)
        return ax, fig

    t = t_plot(conf.t_plot, dos.t)
    outfname = os.path.splitext(movie)[0]
    if conf.output == "mp4":
        anim = animation.FuncAnimation(fig, update, t, interval=20)
        filename_video = path+"/"+outfname+".mp4"
        anim.save(filename_video, writer="ffmpeg", dpi=dpi,
                  extra_args=['-vcodec', 'libx264', '-preset',
                              'veryslow', '-qp', '0'])
    elif conf.output == "screen":
        anim = animation.FuncAnimation(fig, update, t,
                                       interval=20, repeat=False)
        plt.show()
    elif conf.output == "pgf":
        os.makedirs(os.getcwd()+"/"+outfname, exist_ok=True)
        for i in t:
            update(i)
            filename_pgf = os.getcwd()+"/"+outfname+"/nt_"+str(i)+".pgf"
            plt.savefig(filename_pgf, facecolor='none',
                        edgecolor='none', bbox_inches='tight', dpi=dpi)
log.info("#--------------------------------------------------#")        #
