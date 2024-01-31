#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python script for making an OTU to Taxonomy assignment conversion table.



Created on Fri Oct 29 10:20:48 2021

Last Edited on Wed January 31, 2024

@author: hinakoterauchi
"""

### COPY PASTA from IoW_OTUtoTaxaTableKey.ipynb

## Importing necessary packages: 
import pandas as pd
import re
import numpy as np

# Object Oriented Programming to make OTU renaming key table:
## Class OTUname:
class OTUname():
    '''
    Stores the full name of each OTU as well as each taxa level
    '''
    
    def __init__(self, fullName, OTUnumber="", 
                Kingdom="", Phylum="",
                Class="", Order="", Family="",
                 Genus="", Species="",
                samples={}, 
                taxlvlDict=None):
        
        self.fullName = fullName
        
        # creating the dictionary of class method fxns:
        if taxlvlDict is None:
            taxlvlRef = {"0":self.set_kingdom,
                         "1":self.set_phylum, 
                         "2":self.set_class,
                         "3":self.set_order,
                         "4":self.set_family,
                         "5":self.set_genus,
                         "6":self.set_species}
        self.taxlvlDict = taxlvlRef
        
    ## set the numbered OTU as OTUnumber:
    def set_OTUnumber(self, number):
        self.OTUnumber="_".join(["OTU",str(number)])
        return self
    
    ## Functions to set values for each taxonomy levels:
    
    def set_kingdom(self, kingdom):
        self.Kingdom=kingdom
        return self
    
    def set_phylum(self, phylum):
        self.Phylum=phylum
        return self
    
    def set_class(self, Class):  #Capitalize! 
        self.Class=Class
        return self
    
    def set_order(self, order):
        self.Order=order
        return self
    
    def set_family(self, family):
        self.Family=family
        return self
    
    def set_genus(self, genus):
        self.Genus=genus
        return self
    
    def set_species(self, species):
        self.Species=species
        return self
    
    
## Function to get original full names:
def get_ogFullNames(csv_file):
    '''
    To be used 1st on a csv file with QIIME2 output taxa names as its column names
        - Must start with "D_0_"
    
    Reads in all the column names and selects for those that start with "D_0_"
    
    Usage: get_ogFullNames(csv_imported_as_df)
    
    Input: csv file with columns that include non-taxa names
    Output: list of taxa names as string
    '''
    # get the column names that starts with "D_0_":
    r = re.compile("D_0_*")
    taxaFullNames = list(filter(r.match, csv_file.columns))
    
    return taxaFullNames # returns list of fullname str 


## Function to make the object class otu: 
def make_classOTU(fullNames):
    '''
    Use after `get_ogFullNames()` using its output
    Takes the full taxa names and makes class object for each 
    
    Usage: make_classOTU(list_of_full_names)
    
    Input: output list of full taxa names from `get_ogFullNames()`
    Output: list of class objects for each OTU in the input list 
    '''
    # List to store results:
    otu_obj = []

    # go thru each taxa name and create a class object: 
    for n in range(len(fullNames)):
        otu = OTUname(fullNames[n], OTUnumber=(n+1))
        # append to the list:
        otu_obj.append(otu)
        
    return otu_obj  # list of object class otu


## Function to get and store the numbered otu:
def get_numberedOTU(otuclasslist):
    '''
    Take list of OTU class objects and assign them OTU numbers
    
    Usage: get_numberedOTU(list_of_OTU_class_objects)
    
    Input: output list of class objects from `make_classOTU()`
    Output: input OTU class list changed in place (no direct output) 
    '''
    # go through numbers of class obj list:
    for num in range(len(otuclasslist)):
        otuclasslist[num].set_OTUnumber(num+1)
        
    #return otuclasslist -no need to return it since changed in place


## function to separate the full names:
def split_fullname(classObj):
    '''
    Takes single class object with fullName & splits them 
    
    Usage: called within `set_taxalvl()`
    
    Input: list of OTU as class object
    Output: list of split up full names 
    '''
    
    # Splitting at "D_":
    splitNames=re.split("D_|.D_", classObj.fullName)
    
    # get rid of any blank strings: 
    splitNames = list(filter(None, splitNames))

    return splitNames # a list of names with numbers attached 
                      # ie) '0__Bacteria'


## Function to split the taxa level number from the name:
def split_each_taxalvl(splitName):
    '''
    takes one item from split_fullname() output
    and split into number & taxon name
    
    Usage: called within `set_taxalvl()`
    
    Input: single value in the output from `split_fullname()`
    Output: numerical level and its associated taxa
    '''
    
    splitlist = re.split("__|\.__", splitName)
    leveltaxa = list(filter(lambda x: re.search('[0-9]|[a-zA-Z]', x), splitlist))

    if len(leveltaxa) == 2:
        level, taxa = leveltaxa
        return level, taxa
        # filter() out any blank strings
        # level & taxa both str
    
    else:
        return "none"
        # if there aren't 2 items, it's taxa assignment limit


## function to assign taxonomic level: (closure dictionary)
def assign_taxa(item, level, taxa):
    '''
    takes outputs from split_each_taxalvl()
    Uses closure dictionary to assign taxonomic level
    to appropriate category of class obj
    
    Usage: called within `set_taxalvl()`
    
    Input: individual iterating OTU & outputs from `split_each_taxalvl()`
    Output: function that will assign the appropriate taxa name
    '''
    
    # make the appropriate function based on taxa level input:
    assignFxn = item.taxlvlDict[level]
    
    #Use the function to assign appropriate taxonomic name:
    return assignFxn(taxa)


## Overall function to iterate through each taxonomy level and set each taxonomic level assignment for corresponding class object:
def set_taxalvl(classObjList):
    '''
    calls `split_fullname()`, `split_each_taxalvl`, & `assign_taxa()`
    iterate thru each item in list of OTU as class object
    
    Usage: set_taxalvl(OTU_as_class_obj_List)
    
    Input: list of OTU as class object after `get_numberedOTU()`
    Output: changed in place - no new output
    '''
    # iterate thru each class obj:
    for item in classObjList:
        
        # split up fullname into each levels:
        splitNameList = split_fullname(item)
        
        # Go through each item and assign them accordingly:
        for name in splitNameList:
            
            splitresult = split_each_taxalvl(name)
            
            if splitresult == "none":
                break
                
            else: 
                level, taxa = splitresult
            
                # assign to whichever taxonomic level:
                assign_taxa(item, level, taxa)

    
## Turn the object list into a dataframe that can be saved: 
def classList_to_df(classObjList):
    '''
    takes the list of class obj and turns it into a dataframe
    
    Usage: classList_to_df(list_of_OTU_as_class_objects)
    
    Input: split class obj list from `set_taxalvl()`
    Output: a dataframe of the input list 
    '''
    taxaTableKey = pd.DataFrame([vars(otu) for otu in classObjList], 
                                dtype=str)
    
    taxaTableKey=taxaTableKey.drop(columns="taxlvlDict")

    return taxaTableKey





