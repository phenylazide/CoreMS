__author__ = "Yuri E. Corilo"
__date__ = "Jul 29, 2019"


import os
from os.path import join
from enviroms.encapsulation.constant.Constants import Labels
from enviroms.encapsulation.settings.molecular_id.MolecularIDSettings import MoleculaLookupTableSettings, MoleculaSearchSettings
from enviroms.mass_spectrum.input.TextMassList import Read_MassList
from enviroms.molecular_id.calc.MolecularLookupTable import  MolecularCombinations

class SearchMolecularFormulas:
     
    '''
    runworker()
    '''
    
    def __init__(self, first_hit=False):
        
        self.first_hit = first_hit

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        
        return False

    def run_worker_ms_peaks(self, ms_peaks, mass_spectrum_obj, settings):

        settings.usedAtoms
        
        print (settings.hc_filter)
        
        last_dif = 0
        
        last_error = 0
        
        closest_error = 0

        error_average = MoleculaSearchSettings.mz_error_average
        
        nbValues = 0

        settings.min_mz =  min(ms_peaks, key=lambda m: m.mz_exp).mz_exp
    
        settings.max_mz = max(ms_peaks, key=lambda m: m.mz_exp).mz_exp
        
        min_abundance = mass_spectrum_obj.min_abundance

        dict_molecular_lookup_table = MolecularCombinations().runworker(settings)

        classes = list(dict_molecular_lookup_table.keys())

        for ms_peak in  ms_peaks:

            if self.first_hit:
                #print('hell yeah')
                if ms_peak.is_assigned: continue
            
            nominal_mz  = ms_peak.nominal_mz_exp
            '''
            waiting for python 3.8 release to set mass_spectrum_obj and dict_molecular_lookup_table on share memory
            pool = multiprocessing.Pool(number_of_process)
            args = [ (dict_molecular_lookup_table.get(classe).get(ion_type).get(nominal_mz), min_abundance, mass_spectrum_obj, ms_peak_mz_exp, ms_peak_abundance)  for classe in classes ]
            pool.map(SearchMolecularFormulaWorker(), args)

            pool.close()
            pool.join()
            '''
            for classe in classes:
                
                possible_formulas = list()    
                #we might need to increase the search space to -+1 m_z 
                if MoleculaSearchSettings.isRadical:
                
                    ion_type = Labels.radical_ion
                    
                    formulas = dict_molecular_lookup_table.get(classe).get(ion_type).get(nominal_mz)
                    
                    if formulas:
                        
                        possible_formulas.extend(formulas)

                if MoleculaSearchSettings.isProtonated:
                
                    ion_type = Labels.protonated_de_ion

                    formulas = dict_molecular_lookup_table.get(classe).get(ion_type).get(nominal_mz)
                    
                    if formulas:
                        
                        possible_formulas.extend(formulas)

                if possible_formulas:
                    
                    SearchMolecularFormulaWorker().find_formulas(possible_formulas, min_abundance, mass_spectrum_obj, ms_peak, last_error, last_dif, closest_error, error_average, nbValues)
    

    def run_worker_ms_peak(self, ms_peak, mass_spectrum_obj, settings):
        '''
        waiting for python 3.8 release to set mass_spectrum_obj and dict_molecular_lookup_table on share memory (redis?)
        pool = multiprocessing.Pool(number_of_process)
        args = [ (dict_molecular_lookup_table.get(classe).get(ion_type).get(nominal_mz), min_abundance, mass_spectrum_obj, ms_peak_mz_exp, ms_peak_abundance)  for classe in classes ]
        pool.map(SearchMolecularFormulaWorker(), args)

        pool.close()
        pool.join()
        '''

        settings.min_mz = ms_peak.mz_exp-1
    
        settings.max_mz = ms_peak.mz_exp+1
        
        last_dif = 0
        
        last_error = 0
        
        closest_error = 0

        error_average = MoleculaSearchSettings.mz_error_average
        
        nbValues = 0

        min_abundance = mass_spectrum_obj.min_abundance

        dict_molecular_lookup_table = MolecularCombinations().runworker(settings)

        classes = list(dict_molecular_lookup_table.keys())

        nominal_mz  = ms_peak.nominal_mz_exp      
        
        for classe in classes:
            
            possible_formulas = list()    
            #we might need to increase the search space to -+1 m_z 
            if MoleculaSearchSettings.isRadical:
            
                ion_type = Labels.radical_ion
                
                formulas = dict_molecular_lookup_table.get(classe).get(ion_type).get(nominal_mz)
                
                if formulas:
                    
                    possible_formulas.extend(formulas)

            if MoleculaSearchSettings.isProtonated:
            
                ion_type = Labels.protonated_de_ion

                formulas = dict_molecular_lookup_table.get(classe).get(ion_type).get(nominal_mz)
                
                if formulas:
                    
                    possible_formulas.extend(formulas)
            
            
            if possible_formulas:
                
                SearchMolecularFormulaWorker().find_formulas(possible_formulas, min_abundance, 
                                                                mass_spectrum_obj, ms_peak, 
                                                                last_error, last_dif, 
                                                                closest_error, error_average, 
                                                                nbValues, )
        
    def run_worker_mass_spectrum(self, mass_spectrum_obj, settings):

        
        #number_of_process = multiprocessing.cpu_count()

        '''loading this on a shared memory would be better than having to serialize it for every process
            waiting for python 3.8 release'''
        last_dif = 0
    
        last_error = 0
        
        closest_error = 0

        error_average = MoleculaSearchSettings.mz_error_average
        
        nbValues = 0

        settings.min_mz = mass_spectrum_obj.min_mz_exp
    
        settings.max_mz = mass_spectrum_obj.max_mz_exp
        
        min_abundance = mass_spectrum_obj.min_abundance

        dict_molecular_lookup_table = MolecularCombinations().runworker(settings)

        classes = list(dict_molecular_lookup_table.keys())

        print(len(mass_spectrum_obj))
        
        for ms_peak in sorted(mass_spectrum_obj, key=lambda m :m.mz_exp):

            if self.first_hit:
                #print('hell yeah')
                if ms_peak.is_assigned: continue

            #print(ms_peak) 
            nominal_mz  = ms_peak.nominal_mz_exp
            
            '''
            waiting for python 3.8 release to set mass_spectrum_obj and dict_molecular_lookup_table on share memory
            pool = multiprocessing.Pool(number_of_process)
            args = [ (dict_molecular_lookup_table.get(classe).get(ion_type).get(nominal_mz), min_abundance, mass_spectrum_obj, ms_peak_mz_exp, ms_peak_abundance)  for classe in classes ]
            pool.map(SearchMolecularFormulaWorker(), args)

            pool.close()
            pool.join()
            '''
            for classe in classes:
               
                possible_formulas = list()    
                #we might need to increase the search space to -+1 m_z 
                if MoleculaSearchSettings.isRadical:
                
                    ion_type = Labels.radical_ion
                    
                    
                    formulas = dict_molecular_lookup_table.get(classe).get(ion_type).get(nominal_mz)
                   
                    if formulas:
                        possible_formulas.extend(formulas)

                if MoleculaSearchSettings.isProtonated:
                
                    ion_type = Labels.protonated_de_ion

                    formulas = dict_molecular_lookup_table.get(classe).get(ion_type).get(nominal_mz)
                    
                    if formulas:
                        
                        possible_formulas.extend(formulas)

                if possible_formulas:
                    
                    SearchMolecularFormulaWorker().find_formulas(possible_formulas, min_abundance, mass_spectrum_obj, ms_peak, last_error, last_dif, closest_error, error_average, nbValues)
            
class SearchMolecularFormulaWorker:

    
    # needs this wraper to pass the class to multiprocessing
    def __call__(self, args):

        return self.find_formulas(*args)  # ,args[1]

    def set_last_error(self, error, last_error, last_dif, closest_error, error_average, nbValues ):
        
        
        if MoleculaSearchSettings.error_method == 'distance':
            
            dif = error - last_error
            if dif < last_dif:
                last_dif = dif
                closest_error = error
                MoleculaSearchSettings.min_mz_error = closest_error - MoleculaSearchSettings.mz_error_range
                MoleculaSearchSettings.max_mz_error = closest_error + MoleculaSearchSettings.mz_error_range

        elif MoleculaSearchSettings.error_method == 'lowest':
            
            if error < last_error:
                MoleculaSearchSettings.min_mz_error = error - MoleculaSearchSettings.mz_error_range
                MoleculaSearchSettings.max_mz_error = error + MoleculaSearchSettings.mz_error_range
                last_error = error
                
        
        elif MoleculaSearchSettings.error_method == 'symmetrical':
               
               MoleculaSearchSettings.min_mz_error = MoleculaSearchSettings.mz_error_average - MoleculaSearchSettings.mz_error_range
               MoleculaSearchSettings.max_mz_error = MoleculaSearchSettings.mz_error_average + MoleculaSearchSettings.mz_error_range
        
        elif MoleculaSearchSettings.error_method == 'average':

                nbValues += 1
                error_average = error_average + ((error - error_average) / nbValues)
                MoleculaSearchSettings.min_mz_error =  error_average - MoleculaSearchSettings.mz_error_range
                MoleculaSearchSettings.max_mz_error =  error_average + MoleculaSearchSettings.mz_error_range    
                
                
        else:
            #using set MoleculaSearchSettings.min_mz_error and max_mz_error range
            pass

        '''returns the error based on the selected method at MoleculaSearchSettings.method
        '''    
        return last_error, last_dif, closest_error, error_average, nbValues        
        
    def find_formulas(self, possible_formulas, min_abundance, 
                      mass_spectrum_obj, ms_peak, 
                      last_error, last_dif, 
                      closest_error, error_average, 
                      nbValues):
        '''
        # uses the closest error the next search (this is not ideal, it needs to use confidence
        # metric to choose the right candidate then propagate the error using the error from the best candidate
        # it needs to add s/n to the equation
        # it need optimization to define the mz_error_range within a m/z unit since it is directly 
        # proportional with the mass, and inversially proportinal to the rp. 
        # It's not linear, i.e., sigma ∝ mass 
        # the idea it to correlate sigma to resolving power, signal to noise and sample complexity per mz unit
        # method='distance'
        '''

        min_mz_error = MoleculaSearchSettings.min_mz_error
        max_mz_error = MoleculaSearchSettings.max_mz_error
        min_abun_error = MoleculaSearchSettings.min_abun_error
        max_abun_error = MoleculaSearchSettings.max_abun_error

        #f = open("abundance_error.txt", "a+")    
        ms_peak_mz_exp, ms_peak_abundance = ms_peak.mz_exp, ms_peak.abundance
        #min_error = min([pmf._calc_assigment_mass_error(ms_peak_mz_exp) for pmf in possible_formulas])
        
        for possible_formula in possible_formulas:
            
            if possible_formula:
                
                error = possible_formula._calc_assigment_mass_error(ms_peak_mz_exp)
                
                if  min_mz_error <= error <= max_mz_error:
                    
                    #update the error
                    last_error, last_dif, closest_error, error_average, nbValues  = self.set_last_error(error, last_error, last_dif, closest_error, error_average, nbValues)    
                    
                    #add molecular formula match to ms_peak
                    ms_peak.add_molecular_formula(possible_formula)
                    
                    #calculates and look for isotopologues
                    isotopologues = possible_formula.isotopologues(min_abundance, ms_peak_abundance)
                    
                    for isotopologue_formula in isotopologues:
                        
                        #move this outside to impove preformace
                        #we need to increase the search space to -+1 m_z 
                        first_index, last_index = mass_spectrum_obj.get_nominal_mz_frist_last_indexes(isotopologue_formula.mz_nominal_theo)
                        
                        for ms_peak_iso in mass_spectrum_obj[first_index:last_index]:
                            
                            error = isotopologue_formula._calc_assigment_mass_error(ms_peak_iso.mz_exp)    
                            
                            #need to define error distribution for abundance measurements
                            if  min_mz_error <= error <= max_mz_error:
                                    
                                    abundance_error = isotopologue_formula._calc_abundance_error(ms_peak_abundance,ms_peak_iso.abundance )            
                                    # margin of error was set empirically/ needs statistical calculation
                                    #  of margin of error for the measurement of the abundances
                                    if min_abun_error <= abundance_error <= max_abun_error:
                                        
                                        #update the error   
                                        last_error, last_dif, closest_error, error_average, nbValues  = self.set_last_error(error, last_error, last_dif, closest_error, error_average, nbValues)    
                                        
                                        #add molecular formula match to ms_peak
                                        ms_peak_iso.add_molecular_formula(isotopologue_formula)
                                        
                                        #add mspeaks mono isotopic index to the isotopologue MolecularFormula obj
                                        isotopologue_formula.mspeak_index_mono_isotopic = ms_peak.index
                                        
                                        #add mspeaks isotopologue index to the mono isotopic MolecularFormula obj
                                        possible_formula.mspeak_indexes_isotopologues.append(ms_peak_iso.index)
                                        
                                        
                                                  