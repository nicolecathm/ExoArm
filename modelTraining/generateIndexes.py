import pandas as pd

# PARSE THROUGH MARKER FILE
MARKER_FILE = 'markerData/09:57:34.csv'  # CHANGE EACH TIME, SHOULD NOT WORK O/W
SHEET_NUMBER = 'Sheet3'                  # CHANGE EACH TIME, SHOULD NOT WORK O/W
data_file = '../data/TEST.txt'           # CHANGE EACH TIME, SHOULD NOT WORK O/W
window = 90

# GET MARKER FILE OPENED AND RDY
markers = pd.read_csv(MARKER_FILE, header=None)

# GET DATA FILENAME
excel_file = "../data/filenames-indexes.xlsx"

# curr_sheet = pd.read_excel(excel_file, SHEET_NUMBER)
# data_file = curr_sheet['FILENAMES'][0]

print(f'FILENAME BEING USED ON SHEET {SHEET_NUMBER}: {data_file}')

# READ IN TIMES FROM DATA FILE
data = pd.read_csv(data_file, delimiter='\t', header=None)
# print(data)

# PREPARE MARKER LISTS
flexion_startindexes = []
sustain_startindexes = []
extension_startindexes = []
rest_startindexes = []

flexion = 0
extension = 1
sustain = 2
rest = 3

# COMPARE DATA TIMES AND MARKER TIMES SAVING INDEX FOR EACH MARKER
prev = '0' # in case two markers are same time on accident
index_counter = 0

for j,marker_time in enumerate(markers[1]): # go through each marker time
    if prev == marker_time: # check for overlap, ignore repeat times
        continue
    for i,time in enumerate(data[0]): # compare to data times, saving indexes
        if marker_time == time:
            # print(f'{markers[0][j]} data index: {i}')
            marker = markers[0][j]
            # FLEX
            if marker == flexion:
                flexion_startindexes.append(i)

            # EXTENSION
            if marker == extension:
                extension_startindexes.append(i)

            # SUSTAIN
            if marker == sustain:
                sustain_startindexes.append(i)

            # REST
            if marker == rest:
                rest_startindexes.append(i)

            prev = marker_time
            index_counter += 1
            break

print(f'indexes found: {index_counter}')

# SAVE EACH INDEX TO EXCEL FILE

flex_series = pd.Series(flexion_startindexes, index = [i for i in range(0,len(flexion_startindexes))])
exte_series = pd.Series(extension_startindexes, index = [i for i in range(0,len(extension_startindexes))])
sust_series = pd.Series(sustain_startindexes, index = [i for i in range(0,len(sustain_startindexes))])
rest_series = pd.Series(rest_startindexes, index = [i for i in range(0,len(rest_startindexes))])

d = {"FILENAMES": pd.Series(data_file, index = [0]), "FLEXION": flex_series, "EXTENSION": exte_series, "SUSTAIN": sust_series, "REST": rest_series, "WINDOW": pd.Series([window], index = [0])}
df = pd.DataFrame(data=d, index = [i for i in range(0,index_counter)])
with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a') as writer: 
     df.to_excel(writer, sheet_name=SHEET_NUMBER) 

print("indexes saved to file")