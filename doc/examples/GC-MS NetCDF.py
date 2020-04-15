import warnings
warnings.filterwarnings("ignore")

import sys
sys.path.append("./")

from pathlib import Path
from multiprocessing import Pool

from numpy import array, polyfit, poly1d
from PySide2.QtWidgets import QFileDialog, QApplication
from PySide2.QtCore import Qt

from corems.molecular_id.input.nistMSI import ReadNistMSI
from corems.mass_spectra.input.andiNetCDF import ReadAndiNetCDF
from corems.molecular_id.search.compoundSearch import LowResMassSpectralMatch
from corems.encapsulation.settings.processingSetting import CompoundSearchSettings

def sql_database(file_location):
    
    print(file_location)

    sqlLite_obj = ReadNistMSI(file_location).get_sqlLite_obj()

    min_max_rt = (18.037, 18.037)

    min_max_ri = (1637.30, 1737.30)

    sqlLite_obj.query_min_max_ri((1637.30, 1638.30))
    sqlLite_obj.query_min_max_rt((17.111, 18.111))
    sqlLite_obj.query_min_max_ri_and_rt((1637.30, 1638.30),(17.111, 18.111))

def get_gcms(file_path):
    
    reader_gcms = ReadAndiNetCDF(file_path)
	
    reader_gcms.run()
    
    gcms = reader_gcms.get_gcms_obj()

    gcms.process_chromatogram()

    return gcms

def get_reference_dict():

    app = QApplication(sys.argv)
    file_dialog = QFileDialog()
    file_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
    file_path = file_dialog.getOpenFileName(None, "FAMES REF FILE", filter="*.cdf")[0]
    file_dialog.close()
    app.exit()
    
    if not file_path:
        return  None
    else:
        
        ref_file_path = Path.cwd() / "tests/tests_data/gcms/" / "FAMES_REF.MSL"

        gcms = get_gcms(file_path)

        #gcms.plot_gc_peaks()   

        #gcms.plot_processed_chromatogram()
        
        #matplotlib.pyplot.show()

        lowResSearch = LowResMassSpectralMatch(gcms, ref_file_path, calibration=True)

        lowResSearch.run()

        dict_ri_rt = {}

        list_of_compound_obj = {}

        for gcms_peak in gcms:

            # has a compound matched
            if gcms_peak:
                
                compound_obj = gcms_peak.highest_ss_compound
                
                if not compound_obj.ri in dict_ri_rt.keys():
                    
                    dict_ri_rt[compound_obj.ri] = [(gcms_peak.mass_spectrum.rt, compound_obj)]
    
                else:
                    
                    dict_ri_rt[compound_obj.ri].append((gcms_peak.mass_spectrum.rt, compound_obj))
                
                print(compound_obj.name, gcms_peak.mass_spectrum.rt, compound_obj.spectral_similarity_score)
        
        ris = [i for i in  dict_ri_rt.keys()]
        rts = [max(i, key = lambda c: c[1].spectral_similarity_score)[0] for i in dict_ri_rt.values()]
        
        rt_ri_pairs = list(zip(rts, ris)) 
        
        print(rt_ri_pairs)

        return rt_ri_pairs
        
def run(args):
    
    file_path, ref_file_path, ref_dict = args
    gcms = get_gcms(file_path)
    
    for gcms_peak in gcms:
        
        gcms_peak.calc_ri(ref_dict)
        
    lowResSearch = LowResMassSpectralMatch(gcms, ref_file_path)
    
    lowResSearch.run()

    return gcms

def calibrate_and_search(out_put_file_name, cores):
    
    import csv
    
    ref_dict = get_reference_dict()
    
    if ref_dict:
        
        file_dialog = QFileDialog()
        file_dialog.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        if file_dialog:
            
            file_locations = file_dialog.getOpenFileNames(None, "Standard Compounds Files", filter="*.cdf")
            ref_file_path = Path.cwd() / "tests/tests_data/gcms/" / "PNNLMetV20191015.MSL"
            file_dialog.close()
            
            # run in multiprocessing mode
            p = Pool(cores)
            args = [(file_path, ref_file_path, ref_dict) for file_path in file_locations[0]]
            gcmss = p.map(run, args)
            #gcmss = [run(args[0])]
            
            for gcms in gcmss:
                
                #gcms.to_csv(out_put_file_name)
                gcms.to_excel(out_put_file_name, highest_score=False)
                #gcms.to_pandas(out_put_file_name)
                
                #df = gcms.get_dataframe()
                #json_data = gcms.to_json()
                
                #print(json_data)

                #gcms.plot_processed_chromatogram()
                
                #gcms.plot_gc_peaks()

                #gcms.plot_chromatogram()

                #gcms.plot_smoothed_chromatogram()

                #gcms.plot_baseline_subtraction()

                #gcms.plot_detected_baseline()

                #matplotlib.pyplot.show()

       
if __name__ == '__main__':                           
    import matplotlib
    matplotlib.use('TkAgg')

    cores = 4
    out_put_file_name = 'Group 6_Standards'
    calibrate_and_search(out_put_file_name, cores)


