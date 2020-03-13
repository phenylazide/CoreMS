import json
from pathlib import Path
from corems.encapsulation.settings.processingSetting import MolecularSearchSettings, TransientSetting
from corems.encapsulation.settings.processingSetting import MassSpectrumSetting
from corems.encapsulation.settings.processingSetting import MassSpecPeakSetting
from corems.encapsulation.settings.processingSetting import GasChromatographSetting
from corems.encapsulation.settings.processingSetting import CompoundSearchSettings


from corems.encapsulation.settings.input.InputSetting import DataInputSetting
from corems.encapsulation.settings.input.InputSetting import DataInputSetting


def get_dict_data_gcms(gcms):

    compoundSearchSettings = {}
    
    for item, value in gcms.molecular_search_settings.__dict__.items():
        if not item.startswith('__'):
            compoundSearchSettings[item] =  value
    
    gasChromatographSetting = {}
   
    for item, value in gcms.chromatogram_settings.__dict__.items():
        if not item.startswith('__'):
            gasChromatographSetting[item] =  value

    return { "CompoundSearch": compoundSearchSettings,
             "GasChromatograph": gasChromatographSetting,
            }            

def get_dict_data_ms(mass_spec):

    MolecularSearchSettings = {}
    
    for item, value in mass_spec.molecular_search_settings.__dict__.items():
        if not item.startswith('__'):
            MolecularSearchSettings[item] =  value
    
    transientSetting = {}
    if mass_spec._transient_settings:
        for item, value in mass_spec.transient_settings.__dict__.items():
            if not item.startswith('__'):
                transientSetting[item] =  value
    
    massSpectrumSetting = {}
    for item, value in mass_spec.settings.__dict__.items():
        if not item.startswith('__'):
            massSpectrumSetting[item] =  value
    
    massSpecPeakSetting = {}
    for item, value in  mass_spec.mspeaks_settings.__dict__.items():
        if not item.startswith('__'):
            massSpecPeakSetting[item] =  value                        
    
    return { "MoleculaSearch": MolecularSearchSettings,
             "Transient": transientSetting,
             "MassSpectrum": massSpectrumSetting,
             "MassSpecPeak": massSpecPeakSetting,
            }

def get_dict_data():
    
    molecularSearchSettings = {}
    for item, value in MolecularSearchSettings.__dict__.items():
        if not item.startswith('__'):
            molecularSearchSettings[item] =  value
    
    transientSetting = {}
    for item, value in TransientSetting.__dict__.items():
        if not item.startswith('__'):
            transientSetting[item] =  value
    
    massSpectrumSetting = {}
    for item, value in MassSpectrumSetting.__dict__.items():
        if not item.startswith('__'):
            massSpectrumSetting[item] =  value
    
    massSpecPeakSetting = {}
    for item, value in MassSpecPeakSetting.__dict__.items():
        if not item.startswith('__'):
            massSpecPeakSetting[item] =  value                        
    
    dataInputSetting = {}
    for item, value in DataInputSetting.__dict__.items():
        if not item.startswith('__'):
            dataInputSetting[item] =  value  

    return { "MoleculaSearch": molecularSearchSettings,
             "Transient": transientSetting,
             "MassSpectrum": massSpectrumSetting,
             "MassSpecPeak": massSpecPeakSetting,
             "DataInput": dataInputSetting,
            }

def set_dict_data_ms(data_loaded, mass_spec_obj):
    
    from copy import deepcopy

    classes = [deepcopy(MolecularSearchSettings), 
               deepcopy(TransientSetting),
               deepcopy(MassSpectrumSetting),
               deepcopy(MassSpecPeakSetting)]
    labels = ["MoleculaSearch", "Transient", "MassSpectrum", "MassSpecPeak"]
    
    label_class = zip(labels, classes)

    if data_loaded:
    
        for label, classe in label_class:
            class_data = data_loaded.get(label)
            # not always we will not all the settings
            # this allow a class data to be none and continue
            # to import the other classes
            if class_data:
                for item, value in class_data.items():
                    setattr(classe, item, value)

    mass_spec_obj.molecular_search_settings = classes[0]
    mass_spec_obj.transient_settings = classes[1]
    mass_spec_obj.settings = classes[2]
    mass_spec_obj.mspeaks_settings = classes[3]
 
def set_dict_data(data_loaded):
    
    import warnings
    labels = ["MoleculaSearch", "Transient", "MassSpectrum", "MassSpecPeak", "DataInput"]
    classes = [MolecularSearchSettings, TransientSetting, MassSpectrumSetting, MassSpecPeakSetting, DataInputSetting]
    
    label_class = zip(labels, classes)
    
    if data_loaded:
    
        for label, classe in label_class:

            class_data = data_loaded.get(label)
            # not always we will not all the settings
            # this allow a class data to be none and continue
            # to import the other classes

            if class_data:
                for item, value in class_data.items():
                    setattr(classe, item, value)
        
    else:
        
        warnings.warn("Could not load the settings, using the defaults values")    

def dump_search_settings_json( filename='SettingsCoreMS.json'):
    
    '''Write JSON file into current directory
    '''        
    data_dict = get_dict_data()

    file_path = Path.cwd() / filename 
    
    with open(file_path, 'w', encoding='utf8', ) as outfile:
            
        import re
        #pretty print 
        output = json.dumps(data_dict, sort_keys=True, indent=4, separators=(',', ': '))
        output = re.sub(r'",\s+', '", ', output)
        
        outfile.write(output)

def load_setting_ms_obj(mass_spec_obj, settings_path=False):   
    
    if settings_path:
        
        file_path = Path(settings_path)

    else:
        
        filename='SettingsCoreMS.json'
        file_path = Path.cwd() / filename 

    if Path.exists:  
        
        with open(file_path, 'r', encoding='utf8',) as stream:
            
            stream_lines = [n for n in stream.readlines() if not '//' in n.strip()]
            jdata = ''.join(stream_lines)
            data_loaded = json.loads(jdata)
            set_dict_data_ms(data_loaded, mass_spec_obj)
    else:
        
        raise FileNotFoundError("Could not locate %s", file_path)   


def load_search_setting_json(settings_path=False):
    
    '''LOAD JSON file from current directory
        
        if setting path:  
            setting_path: PATH 
        else:
            setting_path: False
    '''        
    
    if settings_path:
        
        file_path = Path(settings_path)

    else:
        
        filename='SettingsCoreMS.json'
        file_path = Path.cwd() / filename 

    if Path.exists:  
        
        with open(file_path, 'r', encoding='utf8',) as stream:
            
            stream_lines = [n for n in stream.readlines() if not '//' in n.strip()]
            jdata = ''.join(stream_lines)
            data_loaded = json.loads(jdata)
            set_dict_data(data_loaded)
    else:
        
        raise FileNotFoundError("Could not locate %s", file_path)        
