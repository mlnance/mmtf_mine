#!/usr/bin/python
__author__ = 'morganlnance'


###########
# IMPORTS #
###########
from mmtf import fetch
import sys
import os
import argparse
try:
    import pandas as pd
except ImportError:
    print '\nI need the Pandas Python module to work.\n'
    sys.exit()


#############
# ARGUMENTS #
#############
parser = argparse.ArgumentParser(description='Use Python, Pandas, and MMTF to get PDB IDs that have sugars.')
parser.add_argument('pdb_id_list', type=str, help='A .txt file of all 4-letter PDB IDs to be checked.')
input_args = parser.parse_args()


################
# DATA HOLDERS #
################
# for handling file download and deleting
curdir = os.getcwd()


# for data frame of data
pdb_names = []
# pulling out PDBs with residues that have either
# -D- or -L in them. Need more refinement after that
pdb_has_D = []
pdb_has_L = []
sugar_names = ['mann', 'fuco', 'gluc', 'gala', 'sial']
pdb_has_sugar_names = []
# for a separate file
description_names = []


##############
# MINE CRAFT #
##############
# read the input file
try:
    with open(input_args.pdb_id_list, 'r') as fh:
        pdb_ids = fh.readlines()
except IOError:
    print '\nYou did not give me an acceptable PDB ID file.\n'
    sys.exit()

# dump a .csv every 20 trials just in case
index = 0
# for each line (PDB ID) in the given file
for pdb_id in pdb_ids:
    # check pdb_id
    pdb_id = pdb_id.strip()

    # fetch the MMTF data of this pdb
    try:
        pdb_data = fetch(pdb_id)
    except:
        print '***** %s was not able to be downloaded' % pdb_id
        continue

    ## for each group in the entity_list of this pdb
    # check the description for each group of the pdb
    # has -L- or -D- as sugars should have these
    for ii in range(len(pdb_data.entity_list)):
        # reset data holders
        has_D = False
        has_L = False

        # pull out description and make it all lowercase
        description = pdb_data.entity_list[ii]['description'].lower()
        # only look at types that are not classified as polymers
        # I think proteins are considered polymers, not glycan chains
        if pdb_data.entity_list[ii]['type'] != 'polymer':
            # remember now checking for lower case version
            # has -L-
            if '-l-' in description:
                has_L = True
            # has -L-
            if '-d-' in description:
                has_D = True
            # sugar names of interest
            for sugar in sugar_names:
                if sugar in description:
                    # if it has a sugar name, add some data
                    # store data for this pdb as it had one section of interest
                    pdb_names.append(pdb_id)
                    pdb_has_L.append(has_L)
                    pdb_has_D.append(has_D)
                    pdb_has_sugar_names.append(True)
                    # store a running list of description names
                    description_names.append(pdb_data.entity_list[ii]['description'])

    ## if we've done enough pdbs, dump temp files
    # dump a .csv every 20 trials just in case
    if index != 0 and index % 50 == 0:
        temp_df = pd.DataFrame()
        temp_df['pdb_name'] = pdb_names
        temp_df['has_sugar_names'] = pdb_has_sugar_names
        temp_df['has_L'] = pdb_has_L
        temp_df['has_D'] = pdb_has_D
        temp_df['type'] = description_names
        # dump a temp .csv file with data
        temp_df.to_csv('mine_pdb_for_carbs.csv')
        # dump a txt file of description names that passed
        with open('mine_description_names.txt', 'w') as fh:
            for name in description_names:
                fh.write(name + '\n')
    if index != 0 and index % 500 == 0:
        print 'Have done %s structures' % index
    index += 1


##############
# STORE DATA #
##############
df = pd.DataFrame()
df['pdb_name'] = pdb_names
df['has_sugar_names'] = pdb_has_sugar_names
df['has_L'] = pdb_has_L
df['has_D'] = pdb_has_D
df['type'] = description_names
df.to_csv('mine_pdb_for_carbs.csv')
# dump a txt file of description names that passed
with open('mine_description_names.txt', 'w') as fh:
    for name in description_names:
        fh.write(name + '\n')
