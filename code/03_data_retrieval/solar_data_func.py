### Importation of the libraries
import requests
import pandas as pd
from datetime import date, timedelta

### General functions

##calculate mean from a list
def mean(liste):
    return sum(liste)/len(liste)


def daterange(start_date: date, end_date: date):
    days = int((end_date - start_date).days)
    for n in range(days):
        yield start_date + timedelta(n)

###Requesting the data

def req_solar(base_url, date):

    file= f'{date.year}'+f'{date.month:02}'+f'{date.day:02}'+"SGAS.txt"
    url = f"{base_url}/{date.year}/{f'{date.month:02}'}/{file}"
    daily = {"date" : date}
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        return response.text, daily
    else:
        #Return an empty list to avoid breaking the data collection process if missing file.
        return [], daily

### Splitting the response text in different paragraphs
def split_response(text):
    # print(text)
    text_split_temp = text.split("\nA.")[1]
    text_A, text_split_temp = text_split_temp.split("\nB.")
    text_B, text_split_temp = text_split_temp.split("\nC. ") #Added the space to prevent confusion with "UTC."
    text_C, text_split_temp = text_split_temp.split("\nD.")
    text_D, text_split_temp = text_split_temp.split("\nE.")
    text_E, text_F = text_split_temp.split("\nF.")
    return text_A, text_B, text_C, text_D, text_E, text_F

### data collection for the different paragraphs
#Traitement de la section A
def coll_data_A(text_A, daily):
    #hard codding the data limits for later separation.
    indices = [1, 6, 11, 17, 22, 29, 35, 38, 45, 49, 68]
    data = []
    test_A = text_A.splitlines()[1:]
    for line in range(len(test_A)):
        if line == 0:
            #colnames are stored in the first line kept
            col = test_A[line].split()
        else:
            #retrieval of the data based on the previously stored indices
            data.append([test_A[line][indices[i]:indices[i+1]].strip() for i in range(len(indices)-1)])

    events_df = pd.DataFrame(data, columns=col)

    daily.update({'nb_event' : len(events_df)})
    return daily

#Traitement des sections B, C, F
def coll_data_text(text_ini, daily):
    text = text_ini.splitlines()
    if len(text) > 1:
        text = ' '.join(text)
    else:
        text = text[0]
    text_split_temp = text.split(':')
    text_col = text_split_temp[0]
    if len(text_split_temp) < 3:
        text_content = text_split_temp[1]
    else:
        text_content = ' '.join(text_split_temp[1:])
    daily.update({text_col.strip() : text_content.strip()})
    return daily

#Traitement de la section E
def coll_data_E(text_E, daily):
    test_E = text_E.splitlines()
    dailies_E = test_E[1].split() #Line with the base data
    proton_E = test_E[3].split() #Line with the proton data
    K_index_Boulder, K_index_Planetary = test_E[9].split('Planetary')
    K_index_Boulder = K_index_Boulder.split() #.remove('Boulder')
    K_index_Boulder.pop(0)
    K_index_Boulder = [float(x) if x != '?' else 0 for x in K_index_Boulder]
    K_index_Planetary = [float(x) if x != '?' else 0 for x in K_index_Planetary.split()]
    # print(K_index_Boulder)
    daily.update({
        "10cm" : dailies_E[2],
        "SSN" : dailies_E[4],
        "Afr" : dailies_E[6].split('/')[0],
        "Ap" : dailies_E[6].split('/')[1],
        "Xray Bg" : dailies_E[9].lstrip('B'),
        "Proton Fluence (GT1MeV)" : proton_E[3],
        "Proton Fluence (GT10MeV)" : proton_E[7],
        "Electron Fluence (GT2MeV)" : test_E[6].split()[3], #reaching directly for the line containing the electron data
        "K index Boulder" : mean(K_index_Boulder),
        "K index Planetary" : mean(K_index_Planetary)
    })
    return daily

### The complete workflow for a single file, returning a one-line dataframe.
def extract_date(base_url, single_date):
    data, daily = req_solar(base_url, single_date)
    if len(data) >1:
        text_A, text_B, text_C, _, text_E, text_F = split_response(data) #The section D of the text is not used because obsolete
        daily = coll_data_A(text_A, daily)
        daily = coll_data_text(text_B, daily)
        daily = coll_data_text(text_C, daily)
        daily = coll_data_E(text_E, daily)
        daily = coll_data_text(text_F, daily)

        date_df = pd.DataFrame(daily, index=[single_date])
        return date_df

