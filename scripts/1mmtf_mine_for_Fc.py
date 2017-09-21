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
pdb_has_fc = []
pdb_has_antibody = []
pdb_has_immunoglobulin = []
descriptions = []


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
        has_fc = False
        has_antibody = False
        has_immunoglobulin = False

        # pull out description and make it all lowercase
        description = pdb_data.entity_list[ii]['description']
        description_lower = pdb_data.entity_list[ii]['description'].lower()
        # if fc shows up in the description name
        if 'fc' in description_lower:
            has_fc = True
        if 'antibody' in description_lower:
            has_antibody = True
        if 'immunoglobulin' in description_lower:
            has_immunoglobulin = True
        if has_fc or has_antibody or has_immunoglobulin:
            pdb_names.append(pdb_id)
            descriptions.append(description)
            pdb_has_fc.append(has_fc)
            pdb_has_antibody.append(has_antibody)
            pdb_has_immunoglobulin.append(has_immunoglobulin)

    ## if we've done enough pdbs, dump temp files
    # dump a .csv every 20 trials just in case
    if index != 0 and index % 50 == 0:
        temp_df = pd.DataFrame()
        temp_df['pdb_name'] = pdb_names
        temp_df['has_Fc'] = pdb_has_fc
        temp_df['has_antibody'] = pdb_has_antibody
        temp_df['has_immunoglobulin'] = pdb_has_immunoglobulin
        temp_df['description'] = descriptions
        # dump a temp .csv file with data
        temp_df.to_csv('mine_pdb_for_Fc.csv')
    if index != 0 and index % 500 == 0:
        print 'Have done %s structures' % index
    index += 1


##############
# STORE DATA #
##############
df = pd.DataFrame()
df['pdb_name'] = pdb_names
df['has_Fc'] = pdb_has_fc
df['has_antibody'] = pdb_has_antibody
df['has_immunoglobulin'] = pdb_has_immunoglobulin
df['description'] = descriptions
df.to_csv('mine_pdb_for_Fc.csv')
