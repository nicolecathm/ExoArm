# CLASSIFIER USING MATCH FILTERING

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
import math
from scipy.signal import find_peaks
from scipy.signal import convolve

def align_signal(data):
        # may have to align for flex and for extend
        # convolve and take the best of the two

    ## ALIGN FOR FLEXION
    max_height = PEAK_HEIGHT_FLX
    peaks, _ = find_peaks(data, height= max_height) # find maximum peak
    if len(peaks)>0:
        peak = peaks[0]
        # plt.plot(np.arange(0,len(data)) - peak, data, color = 'r')
        if peak > MID:
            gap = peak - MID
            end_buffer = [DC_COMPONENT for i in range(gap)]
            flex_new_wave = data[gap:]
            flex_new_wave = np.append(flex_new_wave , end_buffer)

        elif peak <= MID:
            gap = MID - peak
            end_buffer = [DC_COMPONENT for i in range(gap)]
            flex_new_wave = end_buffer
            flex_new_wave = np.append(flex_new_wave , data[:100-gap])
    else:
        flex_new_wave = data # IF NO PEAKS ARE FOUND AT THE SPECIFIED HEIGHT, RETURN ORIGINAL WAVE

    ## ALIGN FOR EXTEND
    max_height = PEAK_HEIGHT_EXT
    peaks, _ = find_peaks([-val for val in data], height= -max_height) # negate data to find minimum
    if len(peaks)>0:
        peak = peaks[0]
        # plt.plot(np.arange(0,len(data)) - peak, data, color = 'r')
        if peak > MID:
            gap = peak - MID
            end_buffer = [DC_COMPONENT for i in range(gap)]
            ext_new_wave = data[gap:]
            ext_new_wave = np.append(ext_new_wave , end_buffer)

        elif peak <= MID:
            gap = MID - peak
            end_buffer = [DC_COMPONENT for i in range(gap)]
            ext_new_wave = end_buffer
            ext_new_wave = np.append(ext_new_wave , data[:100-gap])
    else:
        ext_new_wave = data # IF NO PEAKS ARE FOUND AT THE SPECIFIED HEIGHT, RETURN ORIGINAL WAVE

    return flex_new_wave, ext_new_wave

def generate_data_lists(excel_file, TRAINING_DATA_COUNT):
    # GET EACH FILENAME AND CORRESPONDING INDEXES
    flexion_startindexes = []
    sustain_startindexes = []
    extension_startindexes = []
    rest_startindexes = []
    for sheet in range(0, TRAINING_DATA_COUNT):
        curr_sheet = pd.read_excel(excel_file, sheet)
        filenames.append(curr_sheet['FILENAMES'][0])
        flexion_startindexes.append(((curr_sheet['FLEXION'].dropna()).astype(int)).tolist())
        sustain_startindexes.append(((curr_sheet['SUSTAIN'].dropna()).astype(int)).tolist())
        extension_startindexes.append(((curr_sheet['EXTENSION'].dropna()).astype(int)).tolist())
        rest_startindexes.append(((curr_sheet['REST'].dropna()).astype(int)).tolist())

    # READ IN DATA FROM EACH FILE
    data = []
    for i,filename in enumerate(filenames):
        data.append(pd.read_csv(filename, delimiter='\t', usecols=[1])) # COL 1 is NON TIME COL
    # 
    #           DATA PREPROCESSING #################################
    # 

    # TURN DATA INTO NUMPY ARRAY AND SMOOTH WITH EMA
    np_data = []
    expected = 0
    actual = 0
    for curr_array in data:
        d = curr_array.iloc[:,0].to_numpy()
        emg_data_ema = []
        for pt in d:
            actual = alpha * pt + (1 - alpha) * actual
            emg_data_ema += [actual]
        np_data.append(emg_data_ema)


    # # ENSURE DATA SEPARATED
    # for npd in np_data:
    #     plt.plot(npd)
    #     # plt.show()
    # plt.title("ALL TRAINING SIGNALS")
    # plt.show()

    # 
    # SHOW THE SEPARATION BETWEEN FEATURES #################################
    # IS NOT SHOWING THE EMA FILTERED WAVES
    #

    # for index_index in range(0, TRAINING_DATA_COUNT):
    #     for i in extension_startindexes[index_index]:
    #         plt.plot(data[index_index].iloc[:,0][ int(i) : int(i) + window_size], color = 'green')
    #     for i in flexion_startindexes[index_index]:
    #         plt.plot(data[index_index].iloc[:,0][ int(i) : int(i) + window_size], color = 'red')
    #     for i in sustain_startindexes[index_index]:
    #         plt.plot(data[index_index].iloc[:,0][ int(i) : int(i) + window_size], color = 'purple')
    #     for i in rest_startindexes[index_index]:
    #         plt.plot(data[index_index].iloc[:,0][ int(i) : int(i) + window_size], color = 'orange')
    #     plt.title("FLEXION - RED , EXTENSION - GREEN, SUSTAIN - PURPLE, REST - ORANGE")
    #     plt.show()


    # GENERATE FEATURE ARRAYS
    FLEXION_DATA = []
    EXTENSION_DATA = []
    SUSTAIN_DATA = []
    REST_DATA = []
    for index_index in range(0, TRAINING_DATA_COUNT):
        for i in flexion_startindexes[index_index]:
            FLEXION_DATA.append(np_data[index_index][ i : i + window_size])

        for i in extension_startindexes[index_index]:
            EXTENSION_DATA.append(np_data[index_index][ i : i + window_size])

        for i in sustain_startindexes[index_index]:
            SUSTAIN_DATA.append(np_data[index_index][ i : i + window_size])

        for i in rest_startindexes[index_index]:
            REST_DATA.append(np_data[index_index][ i : i + window_size])


    return FLEXION_DATA, EXTENSION_DATA, REST_DATA, SUSTAIN_DATA

#
#  SPECIFY NUMBER OF TRAINING DATA FILES #################################
#

# CONSTANTS
window_size = 100
alpha = 0.1
DC_COMPONENT = 305 # unfiltered: 300 , used for edge cases
# DC_COMPONENT = 0 # filtered: 0

MID = window_size//2 # AT WHAT POINT TO ALIGN PEAKS, 50 is halfway into window

PEAK_HEIGHT_FLX = 335
PEAK_HEIGHT_EXT = 295 # WILL BE NEGATED

POOR_PREDICTION_THRESHOLD = 0


# excel_file = "../data/filenames-indexes_lpfilter.xlsx" # FOR TRAINING
excel_file = "../data/filenames-indexes.xlsx" # FOR TRAINING
TRAINING_DATA_COUNT = 1
test_file_realtime = '../data/CoolTerm Capture 2023-02-13 18-31-26.txt' # FOR MODELING REALLY GOOD ACCURACY


filenames = []

FLEXION_DATA, EXTENSION_DATA, REST_DATA, SUSTAIN_DATA = generate_data_lists(excel_file, TRAINING_DATA_COUNT)
REST_DATA += SUSTAIN_DATA # COMBINE THE TWO


# classifier key
flexion = 0
extension = 1
sustain = 2
rest = 3


# GENERATE FLEXION FILTER

FLEX_FILTER = np.arange(0,window_size)
A_FLEX_FILTER = np.arange(0,window_size)

for y, data in enumerate(FLEXION_DATA):
    # SAVE UNALIGNED FILTER TO RUNNING AVG
    for i, el in enumerate(data):
        FLEX_FILTER[i] += el

    # CREATE HIGH PEAK ALIGNED FILTER, SAVE FILTER TO RUNNING AVG
    flex_new_wave, _ = align_signal(data)
    # plt.plot(flex_new_wave)
    for i, el in enumerate(flex_new_wave):
        A_FLEX_FILTER[i] += el

# plt.title("ALL FLEX SIGNALS")
# plt.show() 

# GENERATE EXTENSION FILTER

EXT_FILTER = np.arange(0,window_size)
A_EXT_FILTER = np.arange(0,window_size)

for y, data in enumerate(EXTENSION_DATA):
    # SAVE UNALIGNED FILTER TO RUNNING AVG
    for i, el in enumerate(data):
        EXT_FILTER[i] += el

    # CREATE HIGH PEAK ALIGNED FILTER, SAVE FILTER TO RUNNING AVG
    _, ext_new_wave = align_signal(data)
    # plt.plot(ext_new_wave)
    for i, el in enumerate(ext_new_wave):
        A_EXT_FILTER[i] += el
# plt.title("ALL EXT SIGNALS")
# plt.show() 

# GENERATE REST FILTER

RST_FILTER = np.arange(0,window_size)
A_RST_FILTER = np.arange(0,window_size)

for y, data in enumerate(REST_DATA):
    # SAVE UNALIGNED FILTER TO RUNNING AVG
    for i, el in enumerate(data):
        RST_FILTER[i] += el

    # CREATE HIGH PEAK ALIGNED FILTER, SAVE FILTER TO RUNNING AVG
    _, rst_new_wave = align_signal(data) # IF NO PEAKS, SHOULD MOST LIKELY BE REST, ORIGINAL SIGNAL, EITHER OUTPUT VALID
    # plt.plot(rst_new_wave) # USE FOR PRUNING DATA
    # plt.title(y+1)
    # plt.ylim((250,350))
    # plt.show()
    for i, el in enumerate(rst_new_wave):
        A_RST_FILTER[i] += el

# plt.title("ALL RST SIGNALS")
# plt.show() 

#
#  AVERAGE FILTERS
#
for i, data in enumerate(FLEX_FILTER):
    FLEX_FILTER[i] = data/len(FLEXION_DATA)
    A_FLEX_FILTER[i] = A_FLEX_FILTER[i]/len(FLEXION_DATA)

for i, data in enumerate(EXT_FILTER):
    EXT_FILTER[i] = data/len(EXTENSION_DATA)
    A_EXT_FILTER[i] = A_EXT_FILTER[i]/len(EXTENSION_DATA)

for i, data in enumerate(RST_FILTER):
    RST_FILTER[i] = data/len(REST_DATA)
    A_RST_FILTER[i] = A_RST_FILTER[i]/len(REST_DATA)

#
# PLOT FILTERS FOR FLEXION & EXTENSION
#

plt.plot(FLEX_FILTER, color = 'b')
plt.plot(A_FLEX_FILTER, color = 'r')
plt.legend(["UNALIGNED", "ALIGNED"])
plt.title("FLEXION FILTERS")
plt.ylim((250,350))
plt.show()

plt.plot(EXT_FILTER, color = 'b')
plt.plot(A_EXT_FILTER, color = 'r')
plt.legend(["UNALIGNED", "ALIGNED"])
plt.title("EXTENSION FILTERS")
plt.ylim((250,350))
plt.show()

plt.plot(RST_FILTER, color = 'b')
plt.plot(A_RST_FILTER, color = 'r')
plt.legend(["UNALIGNED", "ALIGNED"])
plt.title("REST FILTERS")
plt.ylim((250,350))
plt.show()


#
#   TEST PREDICTIONS WITH SELECTED DATA, NOT REAL-TIME SIMULATION
#

pred = []
PASS = 0
FAIL = 0
COUNT = len(EXTENSION_DATA) + len(FLEXION_DATA) + len(REST_DATA)

##
## PROBLEM IS WITH DIFFERENTIATING BW REST AND OTHER CLASSIFICATIONS...
##


print('\nEXTENSION DATA')
for d in EXTENSION_DATA:
    # pred += [np.convolve(d,FLEX_FILTER, mode = 'valid')]
    # plt.plot(np.convolve(d, EXT_FILTER))
    flx_aligned, ext_aligned = align_signal(d) # ALIGN AS YOU CONVOLVE
    out_flx_aligned = convolve(flx_aligned, FLEX_FILTER, mode = 'full') # CONVOLVE FLX ALIGNED W/ FLX FILTER & EXT ALIGNED W/ EXT FILTER
    out_ext_aligned = convolve(ext_aligned, EXT_FILTER, mode = 'full')
    out_rst_aligned = convolve(ext_aligned, RST_FILTER, mode = 'full') # CONVOLVE RST FILTER WITH EITHER ALIGNMENT
    
    MAX_FLX = np.average(out_flx_aligned)
    MAX_EXT = np.average(out_ext_aligned)
    MAX_RST = np.average(out_rst_aligned)

    # PRED = np.max([MAX_FLX, MAX_EXT, MAX_RST])
    PRED = np.max([MAX_FLX, MAX_EXT]) # ONLY USE BELOW ALGORITHM TO PREDICT REST?

    print(f'{MAX_FLX:.2e}, {MAX_EXT:.2e}, {MAX_RST:.2e}')
    AVG_DIFF = np.average(np.abs(np.diff([MAX_FLX, MAX_EXT, MAX_RST])))
    print(f'AVG DIFFERENCE: {AVG_DIFF}')

    DIFF_EXT_RST = np.diff([MAX_RST, MAX_EXT])
    DIFF_FLX_RST = np.diff([MAX_RST, MAX_FLX])
    print(DIFF_FLX_RST)
    print(DIFF_EXT_RST)
    if (DIFF_FLX_RST < AVG_DIFF) and (DIFF_EXT_RST < AVG_DIFF):
        PRED = MAX_RST

    if PRED == MAX_FLX:
        print(f'FAIL: PREDICT FLX {np.max(out_flx_aligned):.2e}')
        FAIL += 1
    elif PRED == MAX_EXT:
        print(f'PASS: PREDICT EXT {np.max(out_flx_aligned):.2e}')
        PASS += 1
    elif PRED == MAX_RST: # REST CASE
        print(f'FAIL: PREDICT RST {np.max(out_rst_aligned):.2e}')
        FAIL += 1

    plt.plot(out_flx_aligned, 'r')
    plt.plot(out_ext_aligned, 'b')
    plt.plot(out_rst_aligned, 'y')
    plt.title("FLX (red) , EXT (blue) PREDICTION & RST (yellow) \n on EXTENSION DATA ")
plt.show()

print('\nREST DATA')
for d in REST_DATA:
    # pred += [np.convolve(d,FLEX_FILTER, mode = 'valid')]
    # plt.plot(np.convolve(d, EXT_FILTER))
    flx_aligned, ext_aligned = align_signal(d) # ALIGN AS YOU CONVOLVE
    out_flx_aligned = convolve(flx_aligned, FLEX_FILTER, mode = 'full') # CONVOLVE FLX ALIGNED W/ FLX FILTER & EXT ALIGNED W/ EXT FILTER
    out_ext_aligned = convolve(ext_aligned, EXT_FILTER, mode = 'full')
    out_rst_aligned = convolve(ext_aligned, RST_FILTER, mode = 'full') # CONVOLVE RST FILTER WITH EITHER ALIGNMENT

    MAX_FLX = np.average(out_flx_aligned) # MAX OR AVERAGE? TRYING AVERAGE
    MAX_EXT = np.average(out_ext_aligned)
    MAX_RST = np.average(out_rst_aligned)

    PRED = np.max([MAX_FLX, MAX_EXT])

    print(f'{MAX_FLX:.2e}, {MAX_EXT:.2e}, {MAX_RST:.2e}')
    AVG_DIFF = np.average(np.abs(np.diff([MAX_FLX, MAX_EXT, MAX_RST])))
    print(f'AVG DIFFERENCE: {AVG_DIFF}')

    DIFF_EXT_RST = np.diff([MAX_RST, MAX_EXT])
    DIFF_FLX_RST = np.diff([MAX_RST, MAX_FLX])
    print(DIFF_FLX_RST)
    print(DIFF_EXT_RST)
    if (DIFF_FLX_RST < AVG_DIFF) and (DIFF_EXT_RST < AVG_DIFF):
        PRED = MAX_RST

    if PRED == MAX_FLX:
        print(f'FAIL: PREDICT FLX {np.max(out_flx_aligned):.2e}')
        FAIL += 1
    elif PRED == MAX_EXT:
        print(f'FAIL: PREDICT EXT {np.max(out_flx_aligned):.2e}')
        FAIL += 1
    elif PRED == MAX_RST: # REST CASE
        print(f'PASS: PREDICT RST {np.max(out_rst_aligned):.2e}')
        PASS += 1

    plt.plot(out_flx_aligned, 'r')
    plt.plot(out_ext_aligned, 'b')
    plt.plot(out_rst_aligned, 'y')
    plt.title("FLX (red) , EXT (blue) PREDICTION & RST (yellow) \n on REST DATA ")
plt.show()

print('\nFLEXION DATA')
for d in FLEXION_DATA:
    # pred += [np.convolve(d,FLEX_FILTER, mode = 'valid')]
    # plt.plot(np.convolve(d, EXT_FILTER))
    flx_aligned, ext_aligned = align_signal(d) # ALIGN AS YOU CONVOLVE
    out_flx_aligned = convolve(flx_aligned, FLEX_FILTER, mode = 'full') # CONVOLVE FLX ALIGNED W/ FLX FILTER & EXT ALIGNED W/ EXT FILTER
    out_ext_aligned = convolve(ext_aligned, EXT_FILTER, mode = 'full')
    out_rst_aligned = convolve(ext_aligned, RST_FILTER, mode = 'full') # CONVOLVE RST FILTER WITH EITHER ALIGNMENT

    MAX_FLX = np.average(out_flx_aligned)
    MAX_EXT = np.average(out_ext_aligned)
    MAX_RST = np.average(out_rst_aligned)

    PRED = np.max([MAX_FLX, MAX_EXT])

    print(f'{MAX_FLX:.2e}, {MAX_EXT:.2e}, {MAX_RST:.2e}')
    AVG_DIFF = np.average(np.abs(np.diff([MAX_FLX, MAX_EXT, MAX_RST])))
    print(f'AVG DIFFERENCE: {AVG_DIFF}')

    DIFF_EXT_RST = np.diff([MAX_RST, MAX_EXT])
    DIFF_FLX_RST = np.diff([MAX_RST, MAX_FLX])
    print(DIFF_FLX_RST)
    print(DIFF_EXT_RST)
    if (DIFF_FLX_RST < AVG_DIFF) and (DIFF_EXT_RST < AVG_DIFF):
        PRED = MAX_RST

    if PRED == MAX_FLX:
        print(f'PASS: PREDICT FLX {np.max(out_flx_aligned):.2e}')
        PASS += 1
    elif PRED == MAX_EXT:
        print(f'FAIL: PREDICT EXT {np.max(out_flx_aligned):.2e}')
        FAIL += 1
    elif PRED == MAX_RST: # REST CASE
        print(f'FAIL: PREDICT RST {np.max(out_rst_aligned):.2e}')
        FAIL += 1

    plt.plot(out_flx_aligned, 'r')
    plt.plot(out_ext_aligned, 'b')
    plt.plot(out_rst_aligned, 'y')
    plt.title("FLX (red) , EXT (blue) PREDICTION & RST (yellow) \n on FLEXION DATA ")
plt.show()

print(f'PASS/FAIL: {PASS}/{FAIL}')
print(f'ACCURACY: {100*(PASS/COUNT):.2f}%')



#
#   MATCH FILTERING TO CLASSIFY A FILE/MODELING LIKE REAL-TIME
#

L = 1 # LENGTH OF ARM IN CM


# SPECIFY START/END ANGLES
buffer = np.pi/2
start = 0 + buffer
end = -np.pi/2 + buffer
step = -.5

# 
# 
# SET THE TRAJECTORY FOR THE ARM
#
#

traj = []

test_data = pd.read_csv(test_file_realtime, delimiter='\t')
emg_data_raw = test_data[test_data.columns[1]]
alpha = 0.1
expected = 0
actual = 0

# 
# USE EMA TO SMOOTH SIGNAL BEFORE PREDICTION
#

emg_data = []
for pt in emg_data_raw:
    actual = alpha * pt + (1 - alpha) * actual
    emg_data += [actual]

plt.plot(emg_data_raw)
plt.plot(emg_data)
plt.legend(["EMG DATA", "EMG DATA WITH EMA"])
plt.show()

# 
# 
# DYNAMIC WINDOWING 
# 
# predictions made when drop is detected

prev_i = 0 # for comparison
gap = 1 # how much of a decrease between two idx's
idx = 0 # index for iteration
backtrack = 10 # how much to go back once window starts
count_features = 0


while((idx+window_size)<len(emg_data)):
    if (gap + emg_data[idx]) < prev_i:
        # print(f'WINDOW START: {idx}')
        window = emg_data[idx:idx+window_size]
        
        flx_aligned, ext_aligned = align_signal(window) # ALIGN AS YOU CONVOLVE
        out_flx_aligned = convolve(flx_aligned, FLEX_FILTER, mode = 'full') # CONVOLVE FLX ALIGNED W/ FLX FILTER & EXT ALIGNED W/ EXT FILTER
        out_ext_aligned = convolve(ext_aligned, EXT_FILTER, mode = 'full')
        out_rst_aligned = convolve(ext_aligned, RST_FILTER, mode = 'full')



        #
        #       NEED TO UPDATE WITH ABOVE METHOD
        #
        MAX_FLX = np.max(out_flx_aligned)
        MAX_EXT = np.max(out_ext_aligned)
        MAX_RST = np.max(out_rst_aligned)

        PRED = np.max([MAX_FLX, MAX_EXT, MAX_RST])

        print(f'{MAX_FLX:.2e}, {MAX_EXT:.2e}, {MAX_RST:.2e}')

        if PRED <= POOR_PREDICTION_THRESHOLD:
            PRED = MAX_RST
            

        if PRED == MAX_FLX:
            print(f'XXXX: PREDICT FLX {np.max(out_flx_aligned):.2e}')
            title = "PREDICT FLEXION"
        elif PRED == MAX_EXT:
            print(f'XXXX: PREDICT EXT {np.max(out_flx_aligned):.2e}')
            title = "PREDICT EXTENSION"
        elif PRED == MAX_RST: # REST CASE
            print(f'XXXX: PREDICT RST {np.max(out_rst_aligned):.2e}')
            title = "PREDICT REST"

        plt.plot(flx_aligned)
        plt.plot(ext_aligned)
        plt.legend(["FLEX", "EXTEND"])
        plt.title(title)
        plt.show()

        # SAVE PREVIOUS DATA PNT FOR FINDING GAP
        prev_i = emg_data[idx]
        idx = idx+window_size
        count_features += 1 # feature counted


    else:
        prev_i = emg_data[idx]
        idx+=1

# plt.show()

print(f'NUMBER OF FEATURES COUNTED {count_features}')

curr_pos = []

prev_classification = rest
fromhere = start
tohere = end
atstep = step 




# #
# #
# #   ANIMATION WORKFLOW
# #

# traj += [-np.pi for i in range(0,10)] # DISTINGUISHABLE STARTING PT
# for prog,elem in enumerate(prediction):
#     # if (prog % 10 == 0): # PROGRESS
#         # print(f'{prog}/{len(prediction)}')
#     classification = elem[0]
#     if (classification == flexion) and (prev_classification != flexion):
#         # curr_pos = (add_step * np.pi/180) # cos/sin needs radians
#         fromhere = start
#         tohere = end
#         atstep = step
#         prev_classification = classification
#         print(f"{prog*100} FLEXION")
#     elif (classification == extension) and (prev_classification != extension):
#         # curr_pos = -(add_step * np.pi/180)
#         fromhere = end
#         tohere = start
#         atstep = -step
#         prev_classification = classification
#         print(f"{prog*100} EXTENSION")
#     else: 
#         curr_pos = [tohere for i in range(0,5)]
#         traj += curr_pos
#         print(f"{prog*100} STAYING")
#         continue

#     curr_pos = [i for i in np.arange(fromhere,tohere,atstep)]
#     traj += curr_pos
    

# # SET UP THE ANIMATION OBJECTS
# fig = plt.figure(figsize=(3, 3),dpi=80)
# ax = plt.axes(xlim=(-1, 2), ylim=(-1, 2)) 
# line, = ax.plot([], [], lw=3, color='black') 
# circle = plt.Circle((0, 1), 0.1, color='r') 
# ax.add_patch(circle)
# plt.grid('on')

# def animate(i):
#     theta = traj[i*1]

#     endx = L*np.sin(theta)
#     endy = L*np.cos(theta)

#     line.set_xdata(np.array([0,endx]))
#     line.set_ydata(np.array([0,endy]))
#     ax.set_title(f'Torque: {(.3*np.cos(theta)*50):.2f} N*m')

#     circle.center = (endx, endy)

#     return line,

# # SAVE ANIMATION
# anim = FuncAnimation(fig, animate, frames= len(traj), interval=70, blit=True) 
# anim.save('moveArm.gif', writer='imagemagick')
# # plt.show()
