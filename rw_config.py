import logging
import json
import glob
from copy import deepcopy
from aux import flatten_unique
import os

def add(dic_io, dic_ref):
    for key in dic_ref:
        dic_io.setdefault(key, dic_ref[key])


class EvalConfig:
    def __init__(self, config):
        self.config = config
        self.fn = self.getexpand_fn()
        self.parse_defaults()
        self.subplots = config["subplots"]
        self.serial = config["serial"]
        self.medium = config["medium"]
        self.scale = config["scale"]
        self.n_top = config["n_top"]
        self.n_right = config["n_right"]
        self.jobname = config["jobname"]
        self.output = config["output"]
        self.t_plot = config["t_plot"]
        self.fn_var = self.get_fn_var()
        self.cplot_fn_var = self.get_cplot_fn_var()
        self.grp_fn_var = self.get_grp_fn_var()
        self.fn_var_cbar = self.get_fn_var_cbar()
        self.zlgrp_fn_var, self.nozlgrp_fn_var = self.get_zlgrp_fn_var()
        self.mf = self.get_movframe()

    def getexpand_fn(self):
        fns = [fn for fn in self.config if ".nc" in fn]
        for fn in fns:
            fn_glob = glob.glob(fn)
            if fn_glob[0] != fn:
                for file_glob in fn_glob:
                    self.config[file_glob] = self.config[fn]
                del self.config[fn]
        return list(set(([fn for fn in self.config if ".nc" in fn])))

    def parse_defaults(self):
        for fn in self.fn:
            for var in self.config[fn]:
                add(self.config[fn][var], self.config["var_default"])
                if "cplot" in self.config[fn][var]:
                    add(self.config[fn][var]["cplot"], self.config["cplot"])

    def get_fn_var(self):
        fn_var = {}
        for fn in self.fn:
            var_per_file = []
            for var in self.config[fn]:
                var_per_file.append(var)
            fn_var[fn] = var_per_file
        return fn_var

    def get_cplot_fn_var(self):
        cplots = {}
        for fn in self.fn:
            var_per_file = []
            for var in self.config[fn]:
                if "cplot" in self.config[fn][var]:
                    var_per_file.append(var)
            if var_per_file:
                cplots[fn] = var_per_file
        return cplots

    def get_grp_fn_var(self):
        grps = []
        for fn in self.fn:
            for var in self.config[fn]:
                grps.append(self.config[fn][var]["grps"])
        grps = flatten_unique(grps)
        grp_fn_var = {}
        for grp in grps:
            grp_fn_var[grp] = {}
            for fn in self.fn:
                var_per_file = []
                for var in self.config[fn]:
                    if grp in self.config[fn][var]["grps"]:
                        var_per_file.append(var)
                if var_per_file:
                    grp_fn_var[grp][fn] = list(set(var_per_file))
            if not grp_fn_var[grp]:
                del grp_fn_var[grp]
        return grp_fn_var

    def get_fn_var_cbar(self):
        fn_var_cbar = {}
        for fn in self.fn:
            fn_var_cbar[fn] = {}
            for var in self.config[fn]:
                for i, val in enumerate(self.config[fn][var]["cbar"]):
                    if val is "":
                        self.config[fn][var]["cbar"][i] = None
                fn_var_cbar[fn][var] = self.config[fn][var]["cbar"]
        return fn_var_cbar

    def get_movframe(self):
        mf = {}
        if self.serial:
            for fn in self.fn:
                mf[fn], idx = [], []
                for var in self.config[fn]:
                    idx.append(self.config[fn][var]["spn"])
                idx = list(set(idx))
                for i in idx:
                    var_per_idx = []
                    for var in self.config[fn]:
                        if self.config[fn][var]["spn"] == i:
                            var_per_idx.append(var)
                    if var_per_idx:
                        mf[fn].append({fn: var_per_idx})
        else:
            idx = []
            for fn in self.fn:
                for var in self.config[fn]:
                    if "spn" in self.config[fn][var]:
                        idx.append(self.config[fn][var]["spn"])
                idx = list(set(idx))
            mf["mixed"] = []
            for i in idx:
                fn_per_idx = {}
                for fn in self.fn:
                    var_per_fn = []
                    for var in self.config[fn]:
                        if "spn" in self.config[fn][var]:
                            if self.config[fn][var]["spn"] == i:
                                var_per_fn.append(var)
                    if var_per_fn:
                        fn_per_idx[fn] = var_per_fn
                mf["mixed"].append(fn_per_idx)
        return mf

    def removie_fn_var(self, removie):
        mf_cached = deepcopy(self.mf)
        for movie in self.mf:
            for i, axis in enumerate(self.mf[movie]):
                for fn in axis:
                    for var in axis[fn]:
                        if (fn, var) in removie:
                            mf_cached[movie][i][fn].remove(var)
                            if not mf_cached[movie][i][fn]:
                                del mf_cached[movie][i][fn]
                            print("z-level warning: ", self.mf, fn, var)
        self.mf = mf_cached

    def get_zlgrp_fn_var(self):
        no_zlgrp_fn_var = {}
        grps = []
        for fn in self.cplot_fn_var:
            var_per_file = []
            for var in self.cplot_fn_var[fn]:
                z_lev_grp = self.config[fn][var]["cplot"]["z_lev_grp"]
                if z_lev_grp:
                    grps.append(z_lev_grp)
                else:
                    var_per_file.append(var)
            if var_per_file:
                no_zlgrp_fn_var[fn] = list(set(var_per_file))
        grps = flatten_unique(grps)
        zlgrp_fn_var = {}
        for grp in grps:
            zlgrp_fn_var[grp] = {}
            for fn in self.cplot_fn_var:
                var_per_file = []
                for var in self.cplot_fn_var[fn]:
                    if grp in self.config[fn][var]["cplot"]["z_lev_grp"]:
                        var_per_file.append(var)
                if var_per_file:
                    zlgrp_fn_var[grp][fn] = list(set(var_per_file))
            if not zlgrp_fn_var[grp]:
                del zlgrp_fn_var[grp]
        return zlgrp_fn_var, no_zlgrp_fn_var


# log 2 file & console --------------------------------------------------------
class ConsoleHandler(logging.StreamHandler):
    """
    A handler class which allows the cursor to stay on
    one line for selected messages
    """
    on_same_line = False

    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            same_line = hasattr(record, 'same_line')
            if self.on_same_line and not same_line:
                self.terminator = '\n'
                stream.write(self.terminator)
            stream.write(msg)
            if same_line:
                self.terminator = '\r'
                self.on_same_line = True
            else:
                self.terminator = '\n'
                self.on_same_line = False

            stream.write(self.terminator)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def logger(logfile, log2console_flag):
    """
    handle = get_logger(logfile, log2console_flag):
    handle.level(message)
    """
    if log2console_flag:
        level_console = "INFO"
    else:
        level_console = "WARNING"
    log2console = ConsoleHandler()
    log2console.setLevel(level_console)
    log2file = logging.FileHandler(logfile)
    log2file.setFormatter(logging.Formatter('%(name)s: %(message)s'))
    log2file.setLevel("DEBUG")

    log = logging.getLogger('')
    log.setLevel("DEBUG")
    log.addHandler(log2console)
    log.addHandler(log2file)
    return log
# -----------------------------------------------------------------------------


def read_json(configfile):
    """
    dict = read_json(configfile)
                     configfile ... path to .json
    """
    with open(configfile, encoding='UTF-8') as inputfile:
        conf = json.load(inputfile)
    return conf
