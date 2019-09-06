__author__ = "Yuri E. Corilo"
__date__ = "Jul 22, 2019"

import sys, pytest
sys.path.append(".")
from enviroms.encapsulation.Constants import Atoms
from enviroms.molecular_id.factory.MolecularFormulaFactory import MolecularFormula    


from copy import deepcopy

def test_molecular_formula():
    
    '''test the MolecularFormula class and the calculation of isotopologues'''
    
    formula_dict = {'C':10, 'H':0, 'O':10,'Cl':2, 'IonType': 'Radical'}
    
    ion_charge = 1 
    formula_obj = MolecularFormula(formula_dict, ion_charge)
    print("ion_type", formula_obj.ion_type)
    assert round(formula_obj.mz_theor,2) == round(349.886303060457,2)
    
    min_abudance, current_abundance = 1,1 
    print(min_abudance, current_abundance)
    isotopologues = list(formula_obj.isotopologues(0.01, current_abundance))
    
    assert round(isotopologues[0].mz_theor,2) == round(351.883352980637,2)
    assert round(isotopologues[0].prop_ratio,2) == round(0.6399334750069298,2)
    assert isotopologues[0].to_string == 'C10 O10 Cl1 37Cl1'
    
    '''
    for isotopologue_obj in formula_obj.isotopologues(0.01, current_abundance):
        
        print("formula:", isotopologue_obj.to_string, 
              "mz_theor:", isotopologue_obj.mz_theor,
              "prprop_ratio:", isotopologue_obj.prop_ratio)
      '''

if __name__ == "__main__":
      test_molecular_formula()
   

    