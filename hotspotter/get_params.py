''' Written 4/12/2018 by Ross Hartley
    This program checks the log .csv file and returns the parameters for AC, AQ, and mcl_cluster
'''

# Helper function to turn csv values into numbers
def strClean(input):
    output = input
    i = 0
    # Iterate through each item in input and cast it as a float, removing brackets and such
    for str in input:
        output[i] = float(str[1:(len(str)-1)])
        i = i + 1
    return output

def get_params(csv_filepath):
    import csv
    import os

    # Store path to log file
    log_path = os.path.join(csv_filepath, "hs_log.csv")
    # Make variables for parameters
    ac_params = []
    aq_params = []
    cl_params = []
    with open(log_path, 'r') as hs_log:
        # Get data from log file
        reader = csv.reader(hs_log)
        data = list(reader)
        row_count = len(data)
        lastrow = row_count - 1
        # Store AC data in ac_params
        ac_params = data[lastrow][0:2]
        # ac_params = strClean(ac_params)
        # Store AQ data in aq_params
        aq_params = data[lastrow][2:7]
        # aq_params = strClean(aq_params)
        # Store Clustering data in cl_params
        cl_params = data[lastrow][7:11]
        # cl_params = strClean(cl_params)
        # Store status of AC, AQ, and CL
        ac_stat = data[lastrow][14:15]
        aq_stat = data[lastrow][15:16]
        cl_stat = data[lastrow][16:17]

    return ac_params, aq_params, cl_params, ac_stat, aq_stat, cl_stat
