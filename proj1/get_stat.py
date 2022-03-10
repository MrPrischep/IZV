#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# IZV project, part 1
# Author: Kozhevnikov Dmitrii
# Login: xkozhe00
from matplotlib.colors import LogNorm
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import matplotlib as mpl
from matplotlib import cm
import sys
# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

from download import DataDownloader

def plot_stat(data_source,
              fig_location=None,
              show_figure=False):
    """ The function processes data from the dictionary and builds a diagram based on the received data """
    
    regions = (list(data_source["region"]))                                                     # take regions
    uniqueRegions = (np.unique(regions))                                                        # take unique regions
    numbers = list(data_source["p24"])                                                          # take data from "p24"
    regionAndNumber = np.stack([regions, numbers])      
    uniqueNumbersInRegions, count1 = np.unique(regionAndNumber, return_counts=True, axis=1)     # control unique data by regions

    uniqueNumbersInRegions1 = uniqueNumbersInRegions.tolist()

    # a bad solution for working with lists
    listOfCounts = []
    procentListOfCounts = []
    uniqueRegionsList = uniqueRegions.tolist()

    listOf0 = [0 for _ in range(len(uniqueRegionsList))]                                        # values 0
    listOf1 = [0 for _ in range(len(uniqueRegionsList))]                                        # values 1
    listOf2 = [0 for _ in range(len(uniqueRegionsList))]                                        # values 2
    listOf3 = [0 for _ in range(len(uniqueRegionsList))]                                        # values 3
    listOf4 = [0 for _ in range(len(uniqueRegionsList))]                                        # values 4
    listOf5 = [0 for _ in range(len(uniqueRegionsList))]                                        # values 5

    for index, number in enumerate(uniqueNumbersInRegions[1]):
            if number == "0":
                listOf0[uniqueRegionsList.index(uniqueNumbersInRegions1[0][index])] = count1[index]
            elif number == "1":
                listOf1[uniqueRegionsList.index(uniqueNumbersInRegions1[0][index])] = count1[index]
            elif number == "2":
                listOf2[uniqueRegionsList.index(uniqueNumbersInRegions1[0][index])] = count1[index]
            elif number == "3":
                listOf3[uniqueRegionsList.index(uniqueNumbersInRegions1[0][index])] = count1[index]
            elif number == "4":
                listOf4[uniqueRegionsList.index(uniqueNumbersInRegions1[0][index])] = count1[index]
            elif number == "5":
                listOf5[uniqueRegionsList.index(uniqueNumbersInRegions1[0][index])] = count1[index]

    # list of counts
    listOfCounts.append(listOf0)
    listOfCounts.append(listOf5)
    listOfCounts.append(listOf4)
    listOfCounts.append(listOf3)
    listOfCounts.append(listOf2)
    listOfCounts.append(listOf1)

    procListOf0 = listOf0.copy()
    procListOf1 = listOf1.copy()
    procListOf2 = listOf2.copy()
    procListOf3 = listOf3.copy()
    procListOf4 = listOf4.copy()
    procListOf5 = listOf5.copy()

    # list of procent
    procentListOfCounts.append(procListOf0)
    procentListOfCounts.append(procListOf5)
    procentListOfCounts.append(procListOf4)
    procentListOfCounts.append(procListOf3)
    procentListOfCounts.append(procListOf2)
    procentListOfCounts.append(procListOf1)

    # taking procents
    for i in range(6):
        for j in range(len(uniqueRegionsList)):
            try:
                procentListOfCounts[i][j] = round(procentListOfCounts[i][j] * 100 / sum(listOfCounts[i]))
            except:
                sys.exit("Deleni nulou")
    
    nehody = ["Zadna uprava", "Nevyznacena", "Prenosne dopravni znacky", "Dopravnimi znacky", "Semafor mimo provoz", "Prerusovana zluta"]

    # creating graphs
    fig, (ax1, ax2) = plt.subplots(figsize=(8, 11), nrows=2)

    ax1.set_title("Absolutne")
    cmap1 = mpl.cm.get_cmap("viridis").copy()
    ax1.imshow(listOfCounts, norm=LogNorm(vmin=10**0, vmax=10**6), cmap=cmap1)
    xaxis = np.arange(len(uniqueRegions))
    yaxis = np.arange(len(nehody))
    ax1.set_xticks(xaxis)
    ax1.set_yticks(yaxis)
    ax1.set_xticklabels(uniqueRegions)
    ax1.set_yticklabels(nehody)
    cbar = fig.colorbar(cm.ScalarMappable(norm=LogNorm(vmin=10**0, vmax=10**6), cmap=cmap1), ax=ax1, label="Pocet nehod", shrink=0.4)
    cbar.cmap.set_under('white')
    cbar.set_label('Pocet nehod')

    ax2.set_title("Relativne vuci pricine")
    ax2.set_xticks(xaxis)
    ax2.set_yticks(yaxis)
    ax2.set_xticklabels(uniqueRegions)
    ax2.set_yticklabels(nehody)
    cmap2 = mpl.cm.get_cmap("plasma").copy()
    cax2 = ax2.imshow(procentListOfCounts, vmin=0.00001, vmax=100, cmap=cmap2)
    cbar2 = fig.colorbar(cax2, ax=ax2, label="Pocet nehod", shrink=0.4)
    cbar2.cmap.set_under('white')
    cbar2.set_label('Podil nehod pro danou pricinu [%]')
    fig.tight_layout()

    if fig_location:
        (dirname, filename) = os.path.split(fig_location)
		#create folder if doesnt exist
        if dirname:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        plt.savefig(fig_location, format='pdf')

    if show_figure == True:
        plt.show()

# TODO pri spusteni zpracovat argumenty
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IZV project: part1')
    parser.add_argument('--fig_location', dest='fig_location',help="Folder to store image")
    parser.add_argument('--show_figure', action='store_true',help="Show figure in window")
    args = parser.parse_args()
    #data_source = DataDownloader().get_dict(["KVK", "OLK", "JHM", "PHA", "JHC"])
    data_source = DataDownloader().get_dict()
    plot_stat(data_source, args.fig_location, args.show_figure)