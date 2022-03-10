#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# IZV project, part 1
# Author: Kozhevnikov Dmitrii
# Login: xkozhe00

import numpy as np
import zipfile
from os import path, mkdir, listdir
import requests
from bs4 import BeautifulSoup
import re, os, sys, gzip, pickle
import csv
import requests
from io import TextIOWrapper

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).


class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cacheFilename = cache_filename

        self.regionDataDict = {
        	'PHA': None,
        	'STC': None,
        	'JHC': None,
        	'PLK': None,
        	'ULK': None,
        	'HKK': None,
        	'JHM': None,
        	'MSK': None,
        	'OLK': None,
        	'ZLK': None,
        	'VYS': None,
        	'PAK': None,
        	'LBK': None,
        	'KVK': None
        }

    def download_data(self): 
        """ Function for downloading data from a website """    
        # create folder if it not exist
        if self.folder not in listdir():
            mkdir(self.folder)

        # processing data from the page
        with requests.Session() as session:
            
            mainPage = session.get(self.url)                                                    # take page by url
            beatSoup = BeautifulSoup(mainPage.text, 'html.parser')                              # parsing page
            buttons = beatSoup.find_all('button')                   

            # search for links to download data
            for button in buttons:
                href = self.url + re.search("\'(.*)\'", button['onclick']).group()[1:-1]
                nameOfFile = re.search("\/(.*)\'", button['onclick']).group()[1:-1]

                # checking the data for availability on the computer
                if path.isfile(path.join(self.folder + '/' + nameOfFile)):
                    print("Download file ", nameOfFile, "is exist. Skipping")

                # downloading data
                else:
                    print("Download file ", nameOfFile)
                    req = requests.get(href)

                    with open(path.join(self.folder, nameOfFile), 'wb') as zip:
                        zip.write(req.content)

    def parse_region_data(self, region):
        """ Function parsering data and return a dictionary """

        # check folder
        if not os.path.exists(self.folder) or not os.listdir(self.folder):
            self.download_data()
        
        regionName = self.regions.get(region)                                                       # take regions names

        # control names of regions
        if regionName == None:
            sys.exit("Incorrect region code")

        regionName = regionName + '.csv'                                                            # name for region-file
        listOfLists = [[] for _ in range(64)]

        # data types
        types = ["i8","i8","i8","M8","U8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8",
		"i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8",
		"i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","i8","f8","f8","f8","f8","f8","f8","U16",
		"U16","U16","U16","U16","U16","U16","U16","U16","i8","i8","U16","i8"]
        
        # parse data from zip-files
        for file in os.scandir(self.folder):

            if file.path.endswith(".zip"):

                with zipfile.ZipFile(file, 'r') as myZip:

                    with myZip.open(regionName, 'r') as myFile:                                        
                                               
                        reader = csv.reader(TextIOWrapper(myFile, 'cp1250'), delimiter=';')              # encoding="cp1250"

                        for row in reader:

                            for index, item in enumerate(row):
                                
                                if item == "" or item == "XX" or item == "A:" or item == "B:" or item == "D:" or item == "E:" or item == "F:" or item == "G:":           # swap bad symbols
                                    listOfLists[index].append("-1")

                                else:
                                    item = item.replace(",", ".")
                                    listOfLists[index].append(item)
                        
                        myZip.close()

        # data processing and dictionary creation                
        for listIndex, oneList in enumerate(listOfLists):
            listOfLists[listIndex] = np.asarray(oneList, dtype=types[listIndex])

        itemsCount = len(listOfLists[0])
        npRegion = np.full(itemsCount, region)
        myDict = {"region": npRegion}

        for i in range(64):
            myDict[self.headers[i]] = listOfLists[i]
        
        return myDict
                    
    def get_dict(self, regions=None):
        """ Function for getting a combined and creating cache and return dictionary """

        if regions == None:
            regions = self.regions.keys()


        regionDict = {}
        listArr = []

        # getting data and creating cache
        for region in regions:

            if(self.regionDataDict.get(region) != None):
                #print("IF")
                data = self.regionDataDict.get(region)
                regionDict = data
                listArr.append((regionDict))

            elif(os.path.exists(self.folder + '/' + self.cacheFilename.format(region))):
                #print("ELIF")
                with gzip.open(self.folder + '/' + self.cacheFilename.format(region), 'rb') as file:
                    data = pickle.load(file)

                regionDict = data
                listArr.append((regionDict))
                file.close()

            else:
                #print("ELSE")
                data = self.parse_region_data(region)

                with gzip.open(self.folder + '/' + self.cacheFilename.format(region), 'wb') as file:
                    pickle.dump(data, file)

                self.regionDataDict[region] = data
                regionDict = data
                listArr.append((regionDict))
                file.close()
        
        resultDict = listArr[0]
        newHeaders = self.headers.copy()
        newHeaders.insert(0, "region")
        
        for rlist in listArr[1:]:
            for key in newHeaders:
                resultDict[key] = np.append(resultDict[key], rlist[key])
    
        return resultDict
                


# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)
if __name__ == "__main__":
    #start_time = time.time()       time-test
    data = DataDownloader()

    print("Dowload data for:")
    reg = ['OLK', 'ZLK', 'VYS']
    if reg == None or reg == []:
        reg = data.regions.keys()
    print("Regions parsed: ", ', '.join(reg))

    a = data.get_dict(reg)
    
    print("Columns are: ")
    print(len(a.keys()))
    print("Number of records:")
    print(len(list(a.values())[0]))

    # print("--- %s seconds ---" % (time.time() - start_time))
