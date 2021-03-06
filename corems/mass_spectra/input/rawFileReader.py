import numpy
import multiprocessing
from threading import Thread
import sys
import clr

from corems.encapsulation.constant import Labels
from corems.mass_spectrum.factory.MassSpectrumClasses import MassSpecProfile, MassSpecCentroid
from corems.mass_spectra.factory.LC_Class import LCMSBase
from corems.encapsulation.factory.parameters import default_parameters

from threading import Thread
import multiprocessing
import numpy
import pandas as pd

from tqdm import tqdm

sys.path.append("./ext_lib")
clr.AddReference("ThermoFisher.CommonCore.RawFileReader")
from ThermoFisher.CommonCore.RawFileReader import RawFileReaderAdapter

__author__ = "Yuri E. Corilo"
__date__ = "July 9, 2019"


class ImportLCMSThermoMSFileReader(Thread):

    """     Read FULL mode spectra only from raw file data and store it return a LC-MS class
    *  Default behavior is to load all scans numbers

    *  set start_scan_number  and final_scan_number to change it before calling start(), or run()
    """

    def __init__(self, file_location):

        Thread.__init__(self)

        self.iRawDataPlus = RawFileReaderAdapter.FileFactory(file_location)

        self.res = self.iRawDataPlus.SelectInstrument(0, 1)

        self.lcms = LCMSBase(file_location)

        self._initial_scan_number = self.iRawDataPlus.RunHeaderEx.FirstSpectrum

        self._final_scan_number = self.iRawDataPlus.RunHeaderEx.LastSpectrum

        self.file_location = file_location

    @property
    def initial_scan_number(self):
        return self._initial_scan_number

    @property
    def final_scan_number(self):
        return self._final_scan_number

    def run(self):
        '''thread will automatically process mass spectrum
        use the get_mass_spectra class to import without processing mass spectrum'''

        d_parameters = default_parameters(self.file_location)
        self._import_mass_spectra(d_parameters)

        # return self.lcms

    def get_mass_spectra(self, auto_process=True):

        d_parameters = default_parameters(self.file_location)
        self._import_mass_spectra(d_parameters, auto_process=auto_process)
        return self.lcms

    def check_load_success(self):
        """ 0 if successful; otherwise, see Error Codes on MSFileReader Manual """
        if self.res == 0:

            self.break_it = False
            return True
        else:

            raise ImportError(str(self.res))

    def get_filter_for_scan_num(self, scan_number):
        """Returns the closest matching run time that corresponds to scan_number for the current
        controller. This function is only supported for MS device controllers.
        e.g.  ['FTMS', '-', 'p', 'NSI', 'Full', 'ms', '[200.00-1000.00]']
        """
        scan_label = self.iRawDataPlus.GetScanEventStringForScanNumber(
            scan_number)

        return str(scan_label).split()

    def check_full_scan(self, scan_number):
        # scan_filter.ScanMode 0 = FULL
        scan_filter = self.iRawDataPlus.GetFilterForScanNumber(scan_number)

        return scan_filter.ScanMode == 0

    def get_polarity_mode(self, scan_number):

        polarity_symbol = self.get_filter_for_scan_num(scan_number)[1]

        if polarity_symbol == "+":

            return 1
            # return "POSITIVE_ION_MODE"

        elif polarity_symbol == "-":

            return -1

        else:

            raise Exception("Polarity Mode Unknown, please set it manually")

    def get_scan_header(self, scan):
        '''
        Get full dictionary of scan header meta data, i.e. AGC status, ion injection time, etc.
        '''
        header = self.iRawDataPlus.GetTrailerExtraInformation(scan)
        header_dic = {}
        for i in numpy.arange(header.Length):
            header_dic.update({header.Labels[i]:header.Values[i]})
        return header_dic

    def get_data(self, scan, d_parameter, scan_type):

        if scan_type == "Centroid":

            centroidStream = self.iRawDataPlus.GetCentroidStream(scan, False)

            noise = list(centroidStream.Noises)

            baselines = list(centroidStream.Baselines)

            rp = list(centroidStream.Resolutions)

            magnitude = list(centroidStream.Intensities)

            mz = list(centroidStream.Masses)

            # charge = scans_labels[5]
            array_noise_std = (numpy.array(noise) - numpy.array(baselines)) / 3
            l_signal_to_noise = numpy.array(magnitude) / array_noise_std

            d_parameter["baselise_noise_std"] = numpy.average(array_noise_std)

            d_parameter["baselise_noise_std_std"] = numpy.average(array_noise_std)

            data_dict = {
                Labels.mz: mz,
                Labels.abundance: magnitude,
                Labels.rp: rp,
                Labels.s2n: l_signal_to_noise,
            }

        else:

            scanStatistics = self.iRawDataPlus.GetScanStatsForScanNumber(scan)

            profileStream = self.iRawDataPlus.GetSegmentedScanFromScanNumber(
                scan, scanStatistics)

            magnitude = list(profileStream.Intensities)

            mz = list(profileStream.Positions)

            data_dict = {
                Labels.mz: mz,
                Labels.abundance: magnitude,
            }

        return data_dict

    def is_profile_scan_for_scan_num(self, scan_number):

        scanStatistics = self.iRawDataPlus.GetScanStatsForScanNumber(
            scan_number)

        isCentroid = scanStatistics.IsCentroidScan

        return bool(not isCentroid)

    def get_summed_mass_spectrum(self, initial_scan_number, final_scan_number=None,
                                 auto_process=True,pd_method=True,pd_merge_n=100): 

        d_params = default_parameters(self.file_location)

        # assumes scans is full scan or reduced profile scan

        d_params["label"] = Labels.thermo_profile

        if type(initial_scan_number) is list:
            d_params["polarity"] = self.get_polarity_mode(initial_scan_number[0])

            scanrange = initial_scan_number
        else:
            d_params["polarity"] = self.get_polarity_mode(initial_scan_number)

            if final_scan_number == None:
                final_scan_number = self._final_scan_number

            scanrange = range(initial_scan_number, final_scan_number + 1)

        if pd_method:

            def sort_sum_df(df):
                """
                Nested function to sort dataframe and sum rows with exact matching indexes (m/z)
                """
                df = df.sort_index()
                df = df.groupby(level=0).sum()
                return df

            # initialise empty Pandas series
            big_df = pd.Series(index=[],dtype='float64')

            for scan_number in tqdm(scanrange):
                scanStatistics = self.iRawDataPlus.GetScanStatsForScanNumber(scan_number)
                segmentedScan = self.iRawDataPlus.GetSegmentedScanFromScanNumber(scan_number, scanStatistics)
                
                tmp_df = pd.Series(index=list(segmentedScan.Positions),
                                    dtype='float64',data=list(segmentedScan.Intensities))
                big_df = big_df.append(tmp_df) 
                
                #this allows you to merge/sum the values earlier, however it slows down a lot
                #limited benefit unless running into memory issues
                #for complex data it is necessary to stop the iterations getting too slow
                if scan_number%pd_merge_n==0:
                    big_df = sort_sum_df(big_df)    

            big_df = sort_sum_df(big_df)
            data_dict = {
                    Labels.mz: list(big_df.index.values),
                    Labels.abundance: list(big_df.values),
                }

        else:
            all_mz = dict()

            for scan_number in tqdm(scanrange):
                
                scanStatistics = self.iRawDataPlus.GetScanStatsForScanNumber(scan_number)
                
                segmentedScan = self.iRawDataPlus.GetSegmentedScanFromScanNumber(scan_number, scanStatistics)

                len_data = segmentedScan.Positions.Length

                for i in range(len_data):

                    mz = segmentedScan.Positions[i]
                    abundance = segmentedScan.Intensities[i]

                    if mz in all_mz:
                        all_mz[mz] = all_mz[mz] + abundance    
                    else: 
                        all_mz[mz] = abundance

            mz_all = []
            abun_all = []

            for mz in sorted (all_mz) : 
                mz_all.append(mz)
                abun_all.append(all_mz[mz])


            data_dict = {
                    Labels.mz: mz_all,
                    Labels.abundance: abun_all,
                }

        print('Summed. Now Processing.')
        
        mass_spec = MassSpecProfile(data_dict, d_params, auto_process=auto_process)

        return mass_spec

    def _import_mass_spectra(self, d_params, auto_process=True):

            # if self.check_load_success():
        """get number of scans"""

        list_Tics = list()

        list_RetentionTimeSeconds = list()

        list_scans = list()

        for scan_number in range(self.initial_scan_number, self.final_scan_number + 1):

            "only import FULL scans it ignores all others"

            scanStatistics = self.iRawDataPlus.GetScanStatsForScanNumber(
                scan_number)

            d_params["label"] = Labels.thermo_profile

            d_params["polarity"] = self.get_polarity_mode(scan_number)

            d_params["rt"] = self.iRawDataPlus.RetentionTimeFromScanNumber(
                scan_number)

            d_params["scan_number"] = scan_number

            list_RetentionTimeSeconds.append(d_params.get("rt"))

            list_Tics.append(scanStatistics.TIC)

            list_scans.append(scan_number)

            if self.check_full_scan(scan_number):

                data_dict = self.get_data(scan_number, d_params, "Profile")

                print("loading profile scan number: ", scan_number)

                mass_spec = MassSpecProfile(
                    data_dict, d_params, auto_process=auto_process)

                self.lcms.add_mass_spectrum(mass_spec)

            else:

                data_dict = self.get_data(scan_number, d_params, "Centroid")

                print("loading centroid scan number: ", scan_number)

                mass_spec = MassSpecCentroid(data_dict, d_params)

                self.lcms.add_mass_spectrum(mass_spec)

        #pool = multiprocessing.Pool(5)
        #result = pool.starmap(MassSpecCentroid, results)
        # for ms in result:
        # self.lcms.add_mass_spectrum(ms)

        self.lcms.retention_time(list_RetentionTimeSeconds)
        self.lcms.tic = list_Tics
        self.lcms.scans_number = list_scans

    def get_lcms(self):
        """get_lc_ms_class method should only be used when using this class as a Thread, 
        otherwise use the run() method to return the LCMS class"""

        if self.lcms.get(self._initial_scan_number):
            return self.lcms
        else:
            self.run()

            if self.lcms.get(self._initial_scan_number):

                return self.lcms
            else:
                raise Exception("returning a empty LCMS class")

    def get_tic(self,plot=False):
        """
        Reads the TIC values for each scan from the Thermo headers
        Returns a pandas dataframe of Scans, TICs, and Times
        (Optionally) plots the TIC chromatogram.
        """
        first_scan = self._initial_scan_number
        final_scan = self._final_scan_number
        scanrange = range(first_scan,final_scan+1)

        ms_tic = pd.DataFrame(index=scanrange,columns=['TIC','Time'])
        for scan in scanrange:
            scanStatistics = self.iRawDataPlus.GetScanStatsForScanNumber(scan)
            ms_tic.loc[scan,'TIC'] = scanStatistics.TIC
            ms_tic.loc[scan,'Time'] = scanStatistics.StartTime
        
        if plot:
            import matplotlib.pyplot as plt #maybe better in top of file?
            fig,ax = plt.subplots(figsize=(6,3))
            ax.plot(ms_tic['Time'],ms_tic['TIC'])
            ax.set_xlabel('Time (min)')
            ax.set_ylabel('TIC')
            plt.show()
            return ms_tic,fig
        return ms_tic

    def get_best_scans_idx(self,stdevs=2,method='mean',plot=False):
        '''
        Method to determine the best scan indexes for selective co-addition
        Based on calculating the mean (default) of the TIC values
        and setting an upper limit above/below that within X standard deviations.
        Mean or median makes limited difference, it seems.
        Empirically, 1-2 stdevs enough to filter out the worst datapoints.
        Optionally, plot the TIC with horizontal lines for the standard dev cutoffs.
        '''
        tic = self.get_tic()

        if method=='median':
            tic_median = tic['TIC'].median()
        elif method =='mean':
            tic_median = tic['TIC'].mean()
        else:
            print("Method "+print(str(method))+" undefined")

        tic_std = tic['TIC'].std()

        upperlimit = tic_median-(stdevs*tic_std)
        lowerlimit = tic_median+(stdevs*tic_std)

        tic_filtered = tic[(tic['TIC']>upperlimit)&
                            (tic['TIC']<lowerlimit)]
        scans = list(tic_filtered.index.values)

        if plot:
            import matplotlib.pyplot as plt
            fig,ax = plt.subplots(figsize=(8,4))
            ax.plot(tic['Time'],tic['TIC'])
            ax.axhline(y=upperlimit,c='r')
            ax.axhline(y=lowerlimit,c='r')
            return fig, scans
        else:
            return scans



