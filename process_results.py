# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 13:35:19 2017

@author: gai72996
"""

import numpy as np
import matplotlib.pyplot as plt


def get_lines(path):
    """ reads file at path and returns a list with 1 entry per line """
    with open(path) as f:
        lines = f.read().splitlines()
    f.close()
    return lines


def find_line(text, lines, num):
    """finds a index of the line in lines where the text is present in
       the first num characters
    """
    i = 0
    for l in lines:
        i = i + 1
        if l[0:num] == text:
            return i - 1
    # TODO: add a catch if it doesnt find any match


def get_tally_res(lines, tnum):
    """reads the lines and extracts the final tally results"""
    # reduce to only the final result set
    term_line = find_line("      run terminated when", lines, 25)
    lines = lines[term_line:]

    # reduce to only the tally results section
    res_start_line = find_line("1tally       " + tnum, lines, 15)
    particle_type = lines[res_start_line+2][24:33]
    nps_value = lines[res_start_line][28:40]
    tal_type = lines[res_start_line + 1][22]
    lines = lines[res_start_line + 1:]
    tal_end_line = find_line("1tally", lines, 6)
    lines = lines[:tal_end_line-1]

    # depending on tally type choose what to do now
    if tal_type == "4" or tal_type == "6":

        # if volume type, need to find how which cells
        cells = []
        vols = []
        if "volumes" in lines[4]:
            for l in lines[4:]:
                if l == "":
                    break

                elif "cell:" in l:
                    l = l.strip()
                    l = l.split()
                    data = l[1:]
                    for c in data:
                        cells.append(c)
        # now need to get actual data
        c_count = 0
        while c_count < len(cells):
            ph = lines[9][17:28]
            err = lines[9][29:35]
            c_count = c_count + 1

    return ph, err




