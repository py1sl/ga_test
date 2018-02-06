"""
"""

import numpy as np
import glob
import os
import argparse


def write_lines(path, lines):
    """ """
    f = open(path, 'w')
    for l in lines:
        f.write(l)
        f.write("\n")
    f.close()


def get_lines(path):
    """    """
    with open(path) as f:
        lines = f.read().splitlines()
    f.close()
    return lines


def chunkify(lst, n):
    return [lst[i::n] for i in np.arange(n)]


def read_input_file(ipath):
    """ """
    idata = [None] * 20
    lines = get_lines(ipath)
    for l in lines:
        l = l.split(":")
        if l[0] == "template":
            idata[0] = l[1]

        if l[0] == "psize":
            idata[1] = int(l[1])

        if l[0] == "ncores":
            idata[2] = l[1]

        if l[0] == "que":
            idata[3] = l[1]

        if l[0] == "njobs":
            idata[4] = int(l[1])

        if l[0] == "mcnp_path":
            idata[5] = l[1]

        if l[0] == "mutate_prob":
            idata[6] = float(l[1])

        if l[0] == "nlayers":
            idata[7] = int(l[1])

        if l[0] == "lstart":
            idata[8] = int(l[1])

    return idata


def get_output_file_list():
    """ """
    return glob.glob("*.ino")


def write_result_header(opath):
    """ """
    header = ["Shield optimising genetic algorithim",
              "Gen, ave fit, ave ndose, ave pdose"]
    write_lines(opath, header)


def update_results(rpath, new_data):
    """ """
    res = get_lines(rpath)
    res.append(new_data)
    write_lines(rpath, res)


def write_control_file(gen, pop, ipath):
    """ """
    lines = ["gen:"+str(gen)]
    lines.append("ipath:" + ipath)
    lines.append("sequences evaluated:")
    for p in pop:
        lines.append(p)
    write_lines("control.txt", lines)


def read_control_file():
    """ """
    lines = get_lines("control.txt")
    in_seq = False
    old_pop = []
    cdata = [None] * 20
    for l in lines:
        if in_seq:
            old_pop.append(l)
        else:
            l = l.split(":")
        if l[0] == "gen":
            cdata[1] = l[1]

        if l[0] == "ipath":
            cdata[0] = l[1]

        if l[0] == "sequences evaluated":
            in_seq = True

    return cdata, old_pop


def gen_tidy(gen, pop):
    """ tidy up previous generation"""
    # check and remove submit script
    try:
        os.remove("submit.sh")
    except FileNotFoundError:
        print("Submit.sh not found")

    # remove extra files
    for f in glob.glob("*.bash"):
        os.remove(f)
    for f in glob.glob("*.err"):
        os.remove(f)
    for f in glob.glob("*.log"):
        os.remove(f)


def create_initial_pop(psize, mcnp_tmp, lstart, nlayers, mats):
    """ """
    i = 0
    pop = []
    while i < psize:
        arr = np.random.randint(0, 10, size=nlayers)
        fname = write_mcnp_file(arr, mcnp_tmp, lstart, nlayers, mats)
        pop.append(fname)
        i = i + 1

    return pop


def write_mcnp_file(arr, mcnp_tmp, lstart, nlayers, mats):
    """ """
    fname = ""
    for i in arr:
        fname = fname + str(i) + "_"
    fname = fname[:-1] + ".in"

    pos = lstart
    while pos < (nlayers + lstart):
        l = mcnp_tmp[pos].split(" ")
        l[1] = str(arr[pos-lstart])
        l[2] = str(mats[arr[pos-lstart]])
        mcnp_tmp[pos] = " ".join(l)
        pos = pos + 1

    write_lines(fname, mcnp_tmp)

    return fname


def write_run_scripts(pop, mpath, que, ncore, njobs):
    """ """
    script_lines = ["GA test", "#BSUB -q " + que, "#BSUB -n " + ncore,
                    "#BSUB -o %J.log", "#BSUB -e %J.err", ""]
    chunks = chunkify(pop, njobs)
    job_list = []
    for i, chunk in enumerate(chunks):
        rlines = []
        fname = "launch" + str(i) + ".bash"
        job_list.append(fname)
        for r in chunk:
            rline = "mpirun -lsf " + mpath + " n=" + r
            rlines.append(rline)
            rmline = "rm " + r + "r"
            rlines.append(rmline)
        write_lines(fname, script_lines + rlines)

    write_submit_script(job_list)


def write_submit_script(jlist):
    """ """
    lines = ["#!/bin/bash", "dos2unix *"]

    for j in jlist:
        lines.append("bsub < " + j)

    write_lines("submit.sh", lines)


def setup_first_gen(ipath):
    """ """
    indata = read_input_file(ipath)
    gen = 0
    mcnp_template = get_lines(indata[0])
    mats_dict = {0: " ", 1: -2.66, 2: -2.3, 3: -5.9, 4: -8.96, 5: -19.3,
                 6: -11.35, 7: -0.93, 8: -7.15, 9: -7.82, 10: -0.998207}
    pop = create_initial_pop(indata[1], mcnp_template, indata[8], indata[7],
                             mats_dict)
    write_run_scripts(pop, indata[5], indata[3], indata[2], indata[4])
    write_result_header("results.txt")

    write_control_file(gen, pop, ipath)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Genetic algorithim setup")
    parser.add_argument("input", help="path to the input file")
    args = parser.parse_args()

    setup_first_gen(args.input)
