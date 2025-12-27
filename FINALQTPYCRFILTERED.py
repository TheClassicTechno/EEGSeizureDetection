#https://github.com/techno-jules/EEG_READER_VISUALIZER
#Created by Julia Huang
import numpy as np
import eeghdf
import pyqtgraph as pg
from qtpy.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QLineEdit
import gzip
import eegvis.stacklineplot as stacklineplot
from scipy.signal import butter, lfilter
import eegml_signal.filters as esfilters
def load_EEG(eeg_name):
    DATADIR = "eegs" #use relative path

    EEGFILE = DATADIR+"/" + eeg_name
    
    eegf = eeghdf.Eeghdf(EEGFILE)

    return eegf

#global variables
quantization_level=4 
sectotal=1000
num_sections=100
eeg_name = "absence_epilepsy.eeg.h5" 
chan_number = 5 #channel #5 for EEG #show more channels afterwards, one channel shown at a time
eegf= load_EEG(eeg_name)
sample_rate = eegf.sample_frequency

def apply_lowpass_filter(signal, cutoff_freq, sampling_freq):
    nyquist_freq = 0.5 * sampling_freq
    normalized_cutoff = cutoff_freq / nyquist_freq
    b, a = butter(1, normalized_cutoff, btype='low')
    filtered_signal = lfilter(b, a, signal)
    return filtered_signal

def apply_highpass_filter(signal, cutoff_freq, sampling_freq):
    nyquist_freq = 0.5 * sampling_freq
    normalized_cutoff = cutoff_freq / nyquist_freq
    b, a = butter(1, normalized_cutoff, btype='high', analog=False)
    filtered_signal = lfilter(b, a, signal)
    return filtered_signal
# %%
import numpy.typing
# see numpy.org/devdocs/reference/typing.html

# %%
def compress_ratio(arr, quant=quantization_level):
    """@arr is a integer numpy array often signed or unsigned int8 or int16

    """    

    assert (arr.dtype == np.uint16) or (arr.dtype == np.int16) or (arr.dtype ==np.int8) or \
           (arr.dtype == np.uint8) or (arr.dtype == np.int32) or (arr.dtype == np.uint32)
    nbytes = arr.dtype.itemsize  
    nbits = 8 * nbytes 
    rshift = nbits - quant
    shifted_arr = np.right_shift(arr, rshift)
   
    shifted_arr_bytes = bytes(shifted_arr.data)
    comp_arrbytes = gzip.compress(shifted_arr_bytes)

    return len(shifted_arr_bytes) / len(comp_arrbytes)

def compress_ratio_floatarray(arr, quant=quantization_level):
    """@arr is a floating point numpy array
    requantized floating array. converted float array to int array
    """       
    minval = np.min(arr)
    maxval = np.max(arr)
    totalrange = maxval-minval
    meanval = np.mean(arr)
    if quantization_level <= 8:
        intdtype = np.uint8
        q = 8
    elif quantization_level <= 16:
        intdtype = np.uint16 
        q = 16
    elif quantization_level <=32:
        q =32 

    else:
        raise Exception('unhandled quantization level')   
    
    newarr = ((2**q)-0.001) * (arr - minval)/totalrange #0 and 1
    newarr = newarr.astype(intdtype)
    rshift = q - quant
    shifted_arr = np.right_shift(newarr, rshift)

    shifted_arr_bytes = bytes(shifted_arr.data)
    comp_arrbytes = gzip.compress(shifted_arr_bytes)

    return len(shifted_arr_bytes) / len(comp_arrbytes)

samp_freq=eegf.sample_frequency

hp_limit= 0.3
lp_limit = 50 
lowpass = esfilters.fir_lowpass_firwin_ff(
            fs=samp_freq, cutoff_freq=lp_limit, numtaps=int(samp_freq / 4.0)
        )
 

highpass = esfilters.fir_highpass_firwin_ff(
            fs=samp_freq, cutoff_freq=hp_limit, numtaps=int(samp_freq)
        )



def get_window(eeg):
    win_size_sec =1
    ii=30
    return eeg.rawsignals[:,int((ii*win_size_sec)*eeg.sample_frequency):int((ii+1)*win_size_sec*eeg.sample_frequency)]
  
thiswindow = get_window(eegf)
lowpassed = lowpass(thiswindow)

class SignalGrapher(QMainWindow):
    
    def __init__(self):
        super().__init__()
        #self.quantization_level=8
        central_widget = QWidget()
        self.setGeometry(100, 100, 3800, 3000)
        
        layout = QVBoxLayout(central_widget)
        self.label = QLabel("Welcome to the EEG Signal Grapher QTPY App! Made by Julia Huang")
        self.label.setStyleSheet("font-size: 12pt; font-weight: bold; color: purple; margin: 1px; background-color: pink;")

        self.label2 = QLabel("Current User Settings: | EEG Name: "+eeg_name+" | EEG Channel # Shown: "+str(chan_number)+" | Quantization Level: "+str(quantization_level)+" | # Secs of EEG to Display: "+str(sectotal)+" | # Sections to Calculate CR: "+str(num_sections))
        self.label2.setStyleSheet("font-size: 10pt; font-weight: bold; color: blue; background-color: pink;")
       

        self.button1 = QPushButton("Display Numerical Compression Ratios")
        self.button1.setStyleSheet("font-size: 10pt; font-weight: bold; color: blue; margin: 1px; background-color: #F1BDFF;")
        self.button1.clicked.connect(self.show_message)
        self.lineedit1 = QLineEdit()
        self.lineedit2 = QLineEdit()
        
        self.plot_widget1 = pg.PlotWidget() #sin wave
        self.plot_widget2 = pg.PlotWidget() #sin wave
        self.plot_widget3 = pg.PlotWidget() #sin wave
        self.plot_widget4 = pg.PlotWidget() #CR
        self.plot_widget5 = pg.PlotWidget() #CR
        self.plot_widget6 = pg.PlotWidget() #CR   

        layout.addWidget(self.label)
        layout.addWidget(self.label2)
      
        layout.addWidget(self.plot_widget4) #low pass filtered eeg graph CR
        layout.addWidget(self.plot_widget5) #high pass filtered eeg graph CR
        layout.addWidget(self.button1) #compression ratio numerical calculations
        layout.addWidget(self.plot_widget6) #low AND high pass filtered eeg graph CR

        self.left_button = QPushButton("Left 10 Seconds")
        self.left_button.clicked.connect(self.move_left)
       

        self.right_button = QPushButton("Right 10 Seconds")
        self.right_button.clicked.connect(self.move_right)
      

        self.left_button.setStyleSheet("font-size: 10pt; font-weight: bold; color: blue; margin: 1px; background-color: #F1BDFF;")
        self.right_button.setStyleSheet("font-size: 10pt; font-weight: bold; color: blue; margin: 1px; background-color: #F1BDFF;")

        self.current_x_range = (0, sectotal/50) #custom x-range for zoomed in graphs

        # Set the central widget
        self.setCentralWidget(central_widget)

        # Generate the custom signals
        self.generate_signals()

        # Plot the signals
        self.plot_signals()

    def move_left(self):
        tick_range = 10
        self.current_x_range = (self.current_x_range[0] - tick_range, self.current_x_range[1] - tick_range)

        self.plot_signals()

    def move_right(self):
        tick_range = 10
        self.current_x_range = (self.current_x_range[0] + tick_range, self.current_x_range[1] + tick_range)

        self.plot_signals()

    def show_message(self):
        
        message = "<p style='font-size: 20px; color: purple; font-weight: 800; text-align: center; background-color: #ECA6FF;'>Compression Ratio Calculations \n "
        message+="<p style='font-size: 16px; color: blue;'>CR of Each EEG Section: \n </p>" 
        
        message+="\n " + str(self.CR) + "\n \n"
        message+="<p style='font-size: 16px; color: blue;'>Average Combined CR of entire EEG file: </p>" 
        message += str(self.CRsAvg) + "\n "
        QMessageBox.information(self, "Compression Ratio Calculations", message)
  

    def generate_signals(self):
        fs = 1000  # Sampling frequency (Hz)
        f_signal = 10  # Signal frequency (Hz)
        f_signal2 = 20
        f_signal3 = 30
        self.sinx = np.arange(0, 1, 1/fs)  # Time vector
        self.signal=np.sin(2*np.pi*f_signal*self.sinx)+np.sin(2*np.pi*f_signal2*self.sinx)+np.sin(2*np.pi*f_signal3*self.sinx)
        
        # Generate low-frequency noise
        f_noise_low = 2  # Low-frequency noise frequency (Hz)
        noise_low = np.sin(2 * np.pi * f_noise_low * self.sinx)

        # Generate high-frequency noise
        f_noise_high = 200  # High-frequency noise frequency (Hz)
        noise_high = np.sin(2 * np.pi * f_noise_high * self.sinx) #change frequency of sine wave

        # Add noise to the original signal
        x_with_noise = self.sinx  + 0.1 * noise_low + 0.05 * noise_high #adding additive noise
       
        # Apply filters to the noisy signal
        cutoff_freq_lowpass = 30  # Low-pass filter cutoff frequency (Hz)
        cutoff_freq_highpass = 80  # High-pass filter cutoff frequency (Hz)
        x_lowpass = apply_lowpass_filter(x_with_noise, cutoff_freq_lowpass, fs)
        x_highpass = apply_highpass_filter(x_with_noise, cutoff_freq_highpass, fs)
        self.signal2=x_lowpass
        self.signal3=x_highpass
        eegf=load_EEG(eeg_name)
       
        self.num_secs_list = []
        self.bysecs=int(sectotal/num_sections)
        
        for x in range(self.bysecs, sectotal, self.bysecs):
            self.num_secs_list.append(x)
            x+=self.bysecs
        
        self.eeg_sections = []
        eeg_sections_string = []
        for x in range(num_sections):
            self.eeg_sections.append(x)
            eeg_sections_string.append("eeg"+str(x))
            
        #create list of eeg portions to do low pass then compression ratio 
        self.eeg_list_CR = []
        for x in eeg_sections_string:
            if x == "eeg0":
            
                self.firstsignal = (eegf.rawsignals[chan_number, 0:int(sample_rate*self.num_secs_list[0])] )
           
        self.eeg_list_CR.append(self.firstsignal)

        for x in self.num_secs_list:
        
            self.eeg_list_CR.append(lowpass(eegf.rawsignals[chan_number, int(sample_rate * x):int(sample_rate*(x+self.bysecs))]))


        #create list of eeg portions to do high pass then compression ratio 
        self.eeg_list_CRH = []
        for x in eeg_sections_string:
            if x == "eeg0":
            
                self.firstsignal = (eegf.rawsignals[chan_number, 0:int(sample_rate*self.num_secs_list[0])] )
           
        self.eeg_list_CRH.append(self.firstsignal)

        for x in self.num_secs_list:
       
            self.eeg_list_CRH.append(highpass(eegf.rawsignals[chan_number, int(sample_rate * x):int(sample_rate*(x+self.bysecs))]))

        #create list of eeg portions to do low AND high pass then compression ratio    
        self.eeg_list_CRHL = []
        for x in eeg_sections_string:
            if x == "eeg0":
            
                self.firstsignal = (eegf.rawsignals[chan_number, 0:int(sample_rate*self.num_secs_list[0])] )
           
        self.eeg_list_CRHL.append(self.firstsignal)

        for x in self.num_secs_list:
           
            self.eeg_list_CRHL.append(highpass(lowpass(eegf.rawsignals[chan_number, int(sample_rate * x):int(sample_rate*(x+self.bysecs))])))
       
        self.eeg_list = []
        for x in eeg_sections_string:
            if x == "eeg0":
               
                self.firstsignal = (eegf.rawsignals[chan_number, 0:int(sample_rate*self.num_secs_list[0])] )
           
        self.eeg_list.append(self.firstsignal)

        for x in self.num_secs_list:
          
            self.eeg_list.append((eegf.rawsignals[chan_number, int(sample_rate * x):int(sample_rate*(x+self.bysecs))]))
        first_numsecs = eegf.rawsignals[chan_number, 0:int(sample_rate*sectotal)]
        
        self.compression_samplerate=0.1
        self.seg_compare = []
        
        for x in self.eeg_sections: #do CR of low passed EEG
            self.seg_compare.append(compress_ratio_floatarray(self.eeg_list_CR[x], quant=quantization_level)) #filtering produce float array

        self.seg_compare=np.array(self.seg_compare)
        self.t2 = np.arange(self.seg_compare.shape[0])/self.compression_samplerate 
        
        self.t = np.arange(first_numsecs.shape[0])/sample_rate 

        #self.t is for eeg signals, self.t2 is for compress ratio low passed EEG graph
        self.seg_compare2 = []
        
        for x in self.eeg_sections: #do CR of high passed EEG
            self.seg_compare2.append(compress_ratio_floatarray(self.eeg_list_CRH[x], quant=quantization_level)) #filtering produce float array

        self.seg_compare2=np.array(self.seg_compare2)
        self.t3 = np.arange(self.seg_compare2.shape[0])/self.compression_samplerate #time or x axis for high passed eeg CR


        self.seg_compare3 = []
        
        for x in self.eeg_sections: #do CR of low AND high passed EEG
            self.seg_compare3.append(compress_ratio_floatarray(self.eeg_list_CRHL[x], quant=quantization_level)) #filtering produce float array

        self.seg_compare3=np.array(self.seg_compare3)
        self.t4 = np.arange(self.seg_compare3.shape[0])/self.compression_samplerate #time or x axis for high AND low passed eeg CR
        
        self.signalLOW= self.seg_compare #compress ratio low pass!
        self.signalHIGH = self.seg_compare2 #compress ratio high pass!
        self.signalHIGHLOW = self.seg_compare3 #compress ratio high AND LOW pass!
    
       
    def plot_signals(self):
        # Clear the previous plot
        self.plot_widget1.clear()
        self.plot_widget2.clear()
        self.plot_widget3.clear()
        self.plot_widget4.clear()
        self.plot_widget5.clear()
        self.plot_widget6.clear()

        # Plot the sin wave signals
        self.plot_widget1.plot(x=self.sinx, y=self.signal, pen='c')
        self.plot_widget1.disableAutoRange()
        self.plot_widget1.setTitle("3 Sin Waves Signal")
        self.plot_widget1.setLabel('left', 'Amplitude')
        self.plot_widget1.setLabel('bottom', 'Time')

        self.plot_widget2.plot(x=self.sinx, y=self.signal2, pen='r')
        self.plot_widget2.disableAutoRange()
        self.plot_widget2.setTitle("Sin Wave Signal Low Pass Filter")
        self.plot_widget2.setLabel('left', 'Amplitude')
        self.plot_widget2.setLabel('bottom', 'Time')

        self.plot_widget3.plot(x=self.sinx, y=self.signal3, pen='y')
        self.plot_widget3.disableAutoRange()
        self.plot_widget3.setTitle("Sin Wave High Pass Filter")
        self.plot_widget3.setLabel('left', 'Amplitude')
        self.plot_widget3.setLabel('bottom', 'Time')
     

        #filtered graphs' CR below

        self.plot_widget4.plot(x=self.t2, y=self.signalLOW, pen='w')
        self.plot_widget4.setYRange(3, 8)
        self.plot_widget4.setXRange(0, sectotal, padding=0.11)
        self.plot_widget4.setTitle((f"CR of Low Passed EEG of {num_sections} sections in secs: {eeg_name}"))
        self.plot_widget4.setLabel('left', 'compression ratio')
        self.plot_widget4.setLabel('bottom', 'seconds')

        self.plot_widget5.plot(x=self.t3, y=self.signalHIGH, pen='r')
        self.plot_widget5.setYRange(3, 8)
        self.plot_widget5.setXRange(0, sectotal, padding=0.11)
        self.plot_widget5.setTitle((f"CR of High Passed EEG of {num_sections} sections in secs: {eeg_name}"))
        self.plot_widget5.setLabel('left', 'compression ratio')
        self.plot_widget5.setLabel('bottom', 'seconds')
        self.plot_widget5.setXLink(self.plot_widget4) 
        
        self.plot_widget6.plot(x=self.t4, y=self.signalHIGHLOW, pen='y')
        self.plot_widget6.setYRange(3, 8)
        self.plot_widget6.setXRange(0, sectotal, padding=0.11)
        self.plot_widget6.setTitle((f"CR of High AND LOW Passed EEG of {num_sections} sections in secs: {eeg_name}"))
        self.plot_widget6.setLabel('left', 'compression ratio')
        self.plot_widget6.setLabel('bottom', 'seconds')
        self.plot_widget6.setXLink(self.plot_widget5)

        # Refresh the plots
        self.plot_widget1.autoRange()
        self.plot_widget2.autoRange()
        self.plot_widget3.autoRange()
     
        #calculate numerical CRs of EEG portions below
      
        self.CR = self.seg_compare
 
        self.CRsAvg = sum(self.CR) / len(self.CR)
        
# Create the application
app = QApplication([])

# Create a QtPy application window
window = SignalGrapher()
window.setWindowTitle("EEG Signal Grapher Final by Julia Huang")
window.resize(800, 600)

# Show the window
window.show()

# Start the application event loop
app.exec_()
