from aux import npin4linspace, loop_minmax
import matplotlib as mpl
import numpy as np
import matplotlib.pyplot as plt
import logging
import matplotlib.lines as lines
from netCDF4 import Dataset
log = logging.getLogger(__name__)


class PlotObject:
    def __init__(self, axis, do):
        self.axis = axis
        self.do = do
        if self.do.zl is None:
            self.plotter = self.dplot
        else:
            self.plotter = self.cplot

    def dplot(self, data, i):
        return pcolorm2axis(data, i, self.do.var,
                            self.axis, self.do.cmap, self.do.norm, self.do.nsip["n"])

    def cplot(self, data, i):
        return contour2axis(data, self.do.var, i, self.do.zl,
                            ["-"], self.axis, self.do.cmap, self.do.norm)

    def plot(self, i):
        with Dataset(self.do.fn, "r") as data:
            return self.plotter(data, i)


class AxisObject:
    def __init__(self, axis):
        self.axis = axis
        self.pos = []
        self.zoom_flag = False
        self.show_xspine_flag = True
        self.show_yspine_flag = True
        self.x_limits = loop_minmax()
        self.y_limits = loop_minmax()

    def add_PlotObject(self, do):
        self.pos.append(PlotObject(self.axis, do))

    def set_extended_limits(self, x, y, n):
        x_extend = coord_extend(x, n)
        y_extend = coord_extend(y, n)
        self.x_limits.set(x_extend[0], x_extend[-1])
        self.y_limits.set(y_extend[0], y_extend[-1])

    def set_limits(self, x, y):
        self.x_limits.set(x[0], x[-1])
        self.y_limits.set(y[0], y[-1])

    def set_zoom(self, limits):
        self.zoom_flag = True
        self.x_mima = self.x_limits.get()
        self.y_mima = self.y_limits.get()
        self.x_limits.reset()
        self.y_limits.reset()
        self.x_limits.set(limits[0], limits[1])
        self.y_limits.set(limits[2], limits[3])

    def remove_xspine(self):
        self.show_xspine_flag = False

    def remove_yspine(self):
        self.show_yspine_flag = False

    def format_axis(self):
        self.axis.cla()
        self.axis.set_xlim(self.x_limits.get())
        self.axis.set_ylim(self.y_limits.get())
        self.axis.set_aspect(1.)

        spine_offset = 0.04
        xspine_len = self.axis.get_xlim()[1]-self.axis.get_xlim()[0]
        yspine_len = self.axis.get_ylim()[1]-self.axis.get_ylim()[0]
        yox = yspine_len/xspine_len
        # zoom = reset axis limits + add // & rounded limits
        if self.zoom_flag:
            break_haxis = 0.004
            break_hperp = 0.015
            dist = 0.01
            line_formatter = dict(color='black', transform=self.axis.transAxes,clip_on=False)
            yu_x, yu_y = (-spine_offset-break_hperp)*yox, 1+break_haxis+dist
            yd_x, yd_y = (-spine_offset-break_hperp)*yox, break_haxis
            xr_x, xr_y = 1+(-break_haxis+dist)*yox, -spine_offset-break_hperp
            xl_x, xl_y = (-break_haxis-dist)*yox  , -spine_offset-break_hperp
            y00 = lines.Line2D([yd_x, (-spine_offset+break_hperp)*yox],
                               [yd_y, -break_haxis], **line_formatter)
            y01 = lines.Line2D([(-spine_offset-break_hperp)*yox, (-spine_offset+break_hperp)*yox],
                               [break_haxis-dist, -break_haxis-dist], **line_formatter)
            y10 = lines.Line2D([(-spine_offset-break_hperp)*yox, (-spine_offset+break_hperp)*yox],
                               [1+break_haxis, 1-break_haxis], **line_formatter)
            y11 = lines.Line2D([yu_x, (-spine_offset+break_hperp)*yox],
                               [yu_y, 1-break_haxis+dist], **line_formatter)
            x00 = lines.Line2D([-break_haxis*yox, break_haxis*yox],
                               [-spine_offset-break_hperp, -spine_offset+break_hperp], **line_formatter)
            x01 = lines.Line2D([xl_x, (break_haxis-dist)*yox],
                               [xl_y, -spine_offset+break_hperp], **line_formatter)
            x10 = lines.Line2D([1-break_haxis*yox, 1+break_haxis*yox],
                               [-spine_offset-break_hperp, -spine_offset+break_hperp], **line_formatter)
            x11 = lines.Line2D([xr_x, 1+(dist+break_haxis)*yox],
                               [xr_y, -spine_offset+break_hperp], **line_formatter)
            text_offset = 0.005
            htext_formatter = dict( transform=self.axis.transAxes, usetex=True, clip_on=False)
        if (self.show_xspine_flag and self.show_yspine_flag):
            self.axis.text(-spine_offset*yox*6, -spine_offset, 'pbc', verticalalignment='center',
                           transform=self.axis.transAxes, usetex=True, clip_on=False)
            self.axis.text(-spine_offset*yox, -spine_offset*6, 'dbc', verticalalignment='bottom',
                           horizontalalignment='center', rotation=90, transform=self.axis.transAxes,
                           usetex=True, clip_on=False)
        if self.show_xspine_flag:
            # x-axis
            self.axis.spines["bottom"].set_position(('axes', -spine_offset))
            self.axis.spines["bottom"].set_smart_bounds(True)
            self.axis.xaxis.set_ticks_position('bottom')
            self.axis.set_xlabel('$x \, [\\rho_s]$')

            xticks = self.axis.get_xticks()
            xlim = self.axis.get_xlim()
            xlim_absmax = np.amax(np.absolute(xlim))
            nticks = []
            for tick in xticks:
                if tick > xlim[0] and tick < xlim[1] and not\
                   np.absolute(tick-xlim[1])<0.05*xlim_absmax and not\
                   np.absolute(tick-xlim[0])<0.05*xlim_absmax:
                    nticks.append(tick)
            self.axis.set_xticks(nticks)
            if self.zoom_flag:
                self.axis.add_line(x00)
                self.axis.add_line(x01)
                self.axis.add_line(x10)
                self.axis.add_line(x11)
                self.axis.text(xl_x, xl_y-text_offset, "{:d}".format(np.around(self.x_mima[0],decimals=0).astype(int)),
                               verticalalignment='top', horizontalalignment='right',  **htext_formatter)
                self.axis.text(xr_x, xr_y-text_offset, "{:d}".format(np.around(self.x_mima[1],decimals=0).astype(int)),
                               verticalalignment='top', horizontalalignment='left', **htext_formatter)

        else:
            self.axis.xaxis.set_major_locator(plt.NullLocator())
            self.axis.spines["bottom"].set_color('none')

        if self.show_yspine_flag:
            # y-axis
            self.axis.spines["left"].set_position(('axes', -spine_offset*yox))
            self.axis.spines["left"].set_smart_bounds(True)
            self.axis.yaxis.set_ticks_position('left')
            self.axis.set_ylabel('$y \, [\\rho_s]$')
            yticks = self.axis.get_yticks()
            ylim = self.axis.get_ylim()
            ylim_absmax = np.amax(np.absolute(ylim))
            nticks = []
            for tick in yticks:
                if tick > ylim[0] and tick < ylim[1] and not\
                   np.absolute(tick-ylim[1])<0.05*ylim_absmax and not\
                   np.absolute(tick-ylim[0])<0.05*ylim_absmax:
                    nticks.append(tick)
            self.axis.set_yticks(nticks)
            if self.zoom_flag:
                self.axis.add_line(y00)
                self.axis.add_line(y01)
                self.axis.add_line(y10)
                self.axis.add_line(y11)
                self.axis.text(yd_x-text_offset*yox, yd_y, "{:d}".format(np.around(self.y_mima[0],decimals=0).astype(int)),
                               verticalalignment='top', horizontalalignment='right', **htext_formatter)
                self.axis.text(yu_x-text_offset*yox, yu_y, "{:d}".format(np.around(self.y_mima[1],decimals=0).astype(int)),
                               verticalalignment='bottom', horizontalalignment='right', **htext_formatter)
        else:
            self.axis.spines["left"].set_color('none')
            self.axis.yaxis.set_major_locator(plt.NullLocator())
        # top & right spines: invisible!
        for loc, spine in self.axis.spines.items():
            if loc in ["right", "top"]:
                spine.set_color('none')





def ccmap(xedges, xwhite, xcolor_span, xcolor_show, cmap_str, n, rgba_grey):
    # [a, b] ---|a|>|b|---> [-a, a]
    xcolor_ext = xcolor_span[np.argmax(np.absolute(xcolor_span))]
    xcolor_symlim = np.sort([np.negative(xcolor_ext), xcolor_ext])
    # create auxiliary linspace:
    limits = np.sort(np.hstack((xedges, xwhite, xcolor_symlim)))
    ls = np.linspace(limits[0], limits[-1], n+1)
    # care for indices only:
    idx = npin4linspace(ls)
    xedges_idx = idx.get(xedges)
    xwhite_idx = idx.get(xwhite)
    xcolorshow_idx = idx.get(xcolor_show)
    xcolorsym_idx = idx.get(xcolor_symlim)
    # symmetric divergent colormap (sdcmap):
    ncolors = np.diff(xcolorsym_idx)+1
    sdcmap = mpl.cm.ScalarMappable(cmap=cmap_str).to_rgba(np.linspace(0, 1,
                                                                      ncolors))
    # create auxiliary array, all white:
    white = [1., 1., 1., 1.]
    black = [0., 0., 0., 1.]
    grey = rgba_grey
    # overlay:
    colarray = np.tile(black, (n, 1))
    dimarray = np.tile(black, (n, 1))
    colarray[xcolorsym_idx[0]:xcolorsym_idx[1]+1] = sdcmap
    for item in [colarray, dimarray]:
        item[0:xwhite_idx[0]] = grey
        item[xwhite_idx[0]:xcolorshow_idx[0]] = white
        item[xcolorshow_idx[1]+1:xwhite_idx[1]+1] = white
        item[xwhite_idx[1]+1:len(ls)] = grey
    colarray = colarray[xedges_idx[0]:xedges_idx[1]+1]
    norm = mpl.colors.Normalize(vmin=ls[xedges_idx[0]],
                                vmax=ls[xedges_idx[1]+1])
    cmap = mpl.colors.LinearSegmentedColormap.from_list('',
                                                        colarray,
                                                        N=len(colarray))
    return cmap, norm





def ccbt(divider, cmap, norm, ticks, label):
    ax = divider.append_axes("top", size='5%', pad=0.1)
    cb = mpl.colorbar.ColorbarBase(ax,
                                   cmap=cmap,
                                   orientation='horizontal',
                                   ticklocation='top',
                                   norm=norm,
                                   label=label)
    ticks_colors = cmap(norm(ticks))
    cb.add_lines(levels=ticks, colors=ticks_colors, linewidths=1)
    cb.set_ticks(ticks)
    cb.set_ticklabels(['{:.2f}'.format(item) for item in ticks])

    ax.tick_params(which="both", labelsize=mpl.rcParams["xtick.labelsize"],
                   width=mpl.rcParams["xtick.major.width"],
                   size=mpl.rcParams["xtick.major.size"])
    cb.outline.set_linewidth(.75)


    return


def ccbr(divider, i, cmap, norm, zlevs, addticks, label):
    ax = divider.append_axes("right", size='5%', pad=0.1+i*.6)
    cb = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm)
    colors_zlevs = cmap(norm(zlevs))
    colors_bg = np.tile(list(cmap(norm(0.))), (len(zlevs), 1))
    cb.add_lines(levels=zlevs, colors=colors_bg, linewidths=7)
    cb.add_lines(levels=zlevs, colors=colors_zlevs, linewidths=5, erase=False)
    ax.text(0.2, 1.03, label, horizontalalignment='left',
            transform=ax.transAxes, usetex=True,
            size=mpl.rcParams['axes.labelsize'])
    ticks = zlevs.tolist()+addticks
    cb.set_ticks(ticks)
    cb.set_ticklabels(['{:.2f}'.format(item) for item in ticks])

    ax.tick_params(which="both", labelsize=mpl.rcParams["xtick.labelsize"],
                   width=mpl.rcParams["xtick.major.width"],
                   size=mpl.rcParams["xtick.major.size"])
    cb.outline.set_linewidth(.75)
    return


def blinda(divider):
    ax = divider.append_axes("top", size='5%', pad=0.1)
    ax.set_axis_off()
    return


def blindr(divider, n):
    for i in range(n):
        ax = divider.append_axes("right", size='5%', pad=0.1+i*0.6)
        ax.set_axis_off()
    return


def coord_extend(x, n):
    dx = np.diff(x[0:n+1])[n-1]
    return np.append(x, x[-1]+dx)


def pcolorm2axis(fid, nt, variable, ax, cmap, norm, n):
    x = fid.variables['x'][:]
    y = fid.variables['y'][:]
    x = coord_extend(x, n)
    y = coord_extend(y, n)
    data = fid.variables[variable][nt]
    axi = ax.pcolormesh(x, y, data,
                        cmap=cmap,
                        norm=norm,
                        rasterized=True)
    return axi


def contour2axis(fid, variable, nt, zlev, contour_linestyle, ax, cmap, norm):
    x = fid.variables['x'][:]
    y = fid.variables['y'][:]
    data = fid.variables[variable][nt]
    axc = ax.contour(x, y, data,
                     levels=zlev,
                     cmap=cmap,
                     norm=norm)
    return axc


def faxis(fid, ax):
    x = fid.variables['x'][:]
    y = fid.variables['y'][:]
    ax.set_xlim(x[0], x[-1])
    ax.set_ylim(y[0], y[-1])
    ax.set_aspect(1.)
    ax.set_xlabel('$x$')
    ax.set_ylabel('$y$')
    adjust_spines(ax)
    ax.text(-.15, -.03, 'dbc', verticalalignment='center',
            transform=ax.transAxes, usetex=True, fontsize=8, clip_on=False)
    ax.text(-.03, -.15, 'pbc', verticalalignment='bottom',
            horizontalalignment='center', rotation=90, transform=ax.transAxes,
            usetex=True, fontsize=8, clip_on=False)


def t_plot(t, t_idx_ref):
    t_idx = []
    if type(t) is int:
        t_idx.append(t)
    elif np.size(t) == 0:
        t_idx = t_idx_ref
    else:
        t_idx = t
    return t_idx
