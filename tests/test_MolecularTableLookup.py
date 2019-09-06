__author__ = "Yuri E. Corilo"
__date__ = "Jul 22, 2019"

import time, sys, os, pytest
sys.path.append(".")
from enviroms.encapsulation.Constants import Atoms
from enviroms.molecular_id.calc.MolecularLookupTable import  MolecularCombinations
from enviroms.encapsulation.settings.molecular_id.MolecularIDSettings import MoleculaLookupTableSettings


def create_lookup_table(LookupTableSettings):
    
    dict_molecular_lookup_table = MolecularCombinations().runworker(LookupTableSettings)
    
    #for molecular_formulas in dict_molecular_lookup_table.get('O10').get('RADICAL').get(602):
    #    print( molecular_formulas.class_label)
    #    print( molecular_formulas.to_string)
    #    print( molecular_formulas.mz_theor)
    #    for isotopologue in molecular_formulas.isotopologues:
    #        print("isotopologue", isotopologue.to_string)
        #print( molecular_formulas.atoms)
        #print( molecular_formulas.ion_type)
        #print( molecular_formulas.ion_charge)
    return dict_molecular_lookup_table      

def test_molecular_lookup_table():    
    
    LookupTableSettings = MoleculaLookupTableSettings()
    #margin_error needs to be optimized by the data rp and sn
    #min_mz,max_mz  needs to be optimized by the data
    LookupTableSettings.min_mz = 200
    LookupTableSettings.max_mz = 1000
    # C, H, N, O, S and P atoms are ALWAYS needed in the dictionary
    #the defaults values are defined at the encapsulation MolecularSpaceTableSetting    
    LookupTableSettings.usedAtoms['C'] = (1,90)
    
    #some atoms has more than one valence state and the most commun will be used
    # adduct atoms needs valence 0
    LookupTableSettings.usedAtoms['Cl'] = (0,0)
    possible_valences = Atoms.atoms_valence.get('Cl')
    valence_one = possible_valences[0]
    # if you want to specify it in needs to be changed here
    # otherwise it will use the lowest valence, PS needs insure propagation to isotopologues
    MoleculaLookupTableSettings.used_atom_valences['Cl'] =  valence_one

    time0 = time.time()
    
    dict_molecular_lookup_table = create_lookup_table(LookupTableSettings)
    
    time1 = time.time()
    
    print("create the molecular lookup table took %.2f seconds", time1-time0)
    
    