def pgf4a4():
    rcParameter = {
        'pgf.texsystem': 'lualatex',
        'text.usetex': True,
        'pgf.rcfonts': False,
        'font.family': 'serif',
        'font.serif': [],
        'font.sans-serif': [],
        'font.monospace': [],
        'font.size': 10,
        'axes.labelsize': 10,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'pgf.preamble': [
            '\\usepackage{amsmath}',
        ]
    }
    return rcParameter


def pgf4a0():
    rcParameter = {
        'pgf.texsystem': 'lualatex',
        'text.usetex': True,
        'pgf.rcfonts': False,
        'font.family': 'serif',
        'font.serif': [],
        'font.sans-serif': [],
        'font.monospace': [],
        'font.size': 17.28,
        'axes.labelsize': 20.74,
        'xtick.labelsize': 17.28,
        'ytick.labelsize': 17.28,
        'lines.linewidth' : 1.0,
        'axes.linewidth': 1.25,
        'xtick.major.size' : 5,
        'xtick.minor.size' : 2,
        'ytick.major.size' : 5,
        'ytick.minor.size' : 2,
        'xtick.major.width' : 0.8,
        'xtick.minor.width' : 0.6,
        'ytick.major.width' : 0.8,
        'ytick.minor.width' : 0.6,
        'legend.fontsize' : 20.74,
        'pgf.preamble': [
            '\\usepackage{amsmath}'
        ]
    }
    return rcParameter


def pgf4beamer():
    rcParameter = {
        'pgf.texsystem': 'lualatex',
        'text.usetex': True,
        'pgf.rcfonts': False,
        'font.family': 'sans-serif',
        'font.serif': [],
        'font.sans-serif': [],
        'font.monospace': [],
        'font.size': 10,
        'axes.labelsize': 10,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'pgf.preamble': [
            '\\usepackage{amsmath}',
        ]
    }
    return rcParameter


media = {
    "a0":     [2331.98808, 72.27, 600],
    "a4":     [418.25555, 72.27, 300],
    "beamer": [269.14662, 72.27, 96],
    "22z":    [1080, 96, 96],
    "12.5z":  [1080, 176, 176]
}


def hxw_dpi(medium, scale, nxm):
    coefs = media[medium]
    inch = coefs[0]/coefs[1]
    span = inch*scale
    h = span*nxm[0]
    w = span*nxm[1]
    dpi = media[medium][2]
    return (w, h), dpi


def sq_dpi(medium, scale):
    coefs = media[medium]
    inch = coefs[0]/coefs[1]
    span = inch*scale
    dpi = media[medium][2]
    return (span, span), dpi
