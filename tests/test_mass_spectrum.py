__author__ = "Yuri E. Corilo"
__date__ = "Jul 25, 2019"


import sys
import time
from pathlib import Path
sys.path.append('.')

from numpy import array
from matplotlib import pyplot
import pytest

from corems.transient.input.brukerSolarix import ReadBrukerSolarix
from corems.encapsulation.settings.processingSetting import MassSpectrumSetting, TransientSetting

def test_create_mass_spectrum():
    
    file_location = Path.cwd() /  "ESI_NEG_SRFA.d"

    bruker_reader = ReadBrukerSolarix(file_location)

    TransientSetting.apodization_method = 'Hamming'
    bruker_transient = bruker_reader.get_transient()

    TransientSetting.apodization_method = 'Blackman'
    TransientSetting.number_of_truncations = 1
    bruker_transient = bruker_reader.get_transient()
    
    mass_spectrum_obj = bruker_transient.get_mass_spectrum( plot_result=False, auto_process=True)

    MassSpectrumSetting.threshold_method = 'signal_noise'
    mass_spectrum_obj = bruker_transient.get_mass_spectrum( plot_result=False, auto_process=True)

    MassSpectrumSetting.threshold_method = 'relative_abundance'
    mass_spectrum_obj = bruker_transient.get_mass_spectrum( plot_result=False, auto_process=True)
      
    mass_spectrum_obj.freq_exp
    mass_spectrum_obj.dir_location
    mass_spectrum_obj.resolving_power
    mass_spectrum_obj.signal_to_noise
    mass_spectrum_obj.max_abundance
    mass_spectrum_obj.filter_by_mz(200, 1000)
    mass_spectrum_obj.reset_indexes()
    mass_spectrum_obj.filter_by_abundance(0, 1000)
    mass_spectrum_obj.reset_indexes()
    mass_spectrum_obj.filter_by_max_resolving_power(12, 3)
    mass_spectrum_obj.reset_indexes()
    mass_spectrum_obj.filter_by_min_resolving_power(15, 3)
    mass_spectrum_obj.reset_indexes()
    mass_spectrum_obj.get_mz_and_abundance_peaks_tuples()
    mass_spectrum_obj.get_masses_count_by_nominal_mass()
    mass_spectrum_obj.resolving_power_calc(12,1)
    mass_spectrum_obj._f_to_mz()
    mass_spectrum_obj.number_average_molecular_weight(profile=True)
    
    mass_spectrum_obj.reset_cal_therms(mass_spectrum_obj.Aterm,mass_spectrum_obj.Bterm,mass_spectrum_obj.Cterm)
    
    mass_spectrum_obj.reset_indexes()

    kendrick_group_index = mass_spectrum_obj.kendrick_groups_indexes()

    mass_spectrum_obj.reset_indexes()
    
    return mass_spectrum_obj, kendrick_group_index
    

        
if __name__ == "__main__":

    mass_spectrum_obj, kendrick_group_index = test_create_mass_spectrum()
    mass_spectrum_obj.plot_profile_and_noise_threshold()
    pyplot.show()
    
    '''
    for kmd, most_abun_kendrick_group_index in  kendrick_group_index.items():
    
        print(kmd)
        mz = [mass_spectrum_obj[i].mz_exp for i in most_abun_kendrick_group_index ]
        abun =  [mass_spectrum_obj[i].abundance for i in most_abun_kendrick_group_index ]

        pyplot.plot(mass_spectrum_obj.mz_exp_profile, mass_spectrum_obj.abundance_profile, zorder=-1)
        pyplot.scatter(mz, abun, c='r', zorder=1)
        
        pyplot.show()

        mz = array(mz)
        dmz = mz - mz[-1]
        print(dmz)
        #pyplot.stem(mz, abun)
        
        kmd = [mass_spectrum_obj[i].kmd for i in most_abun_kendrick_group_index ]
        knm =  [mass_spectrum_obj[i].knm for i in most_abun_kendrick_group_index ]

        
        pyplot.scatter(knm, kmd)
        pyplot.show()
    '''