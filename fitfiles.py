# -*- coding: utf-8 -*-
"""
Created on Sat May 20 17:53:38 2017

@author: Ron
"""

import pandas as pd

import os
import xml.etree.ElementTree as ET
import datetime as dt

os.chdir(r'C:\ProgramData\Garmin\GarminConnect\Forerunner 410-3853586166\FitnessHistory')

def tcx_to_df(tcx):
    try:
        tree = ET.parse(tcx)
        root_x = tree.getroot()
        tps =  root_x.findall('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint')
    except:
        print("{0} skipped".format(tcx))
    
    df_dict={'dist':[], 'elev':[], 'ts':[]}
    if len(tps)>0:
        for tp in tps:
            d=tp.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters')
            e=tp.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}AltitudeMeters')
            t=tp.find('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time')
            if ((type(e)==type(root_x))&(type(e)==type(d))):
                df_dict['dist'].append(d.text)
                df_dict['elev'].append(e.text)
                df_dict['ts'].append(t.text)
    return(pd.DataFrame(df_dict).astype({'dist':float, 'elev':float, 'ts':'datetime64[ns]'}))

def TSS(d, NGP,FTP):
    #add 3% penalty per 1% incline, reduce by 45% of 3% for downhill -- Davies
    return ((d*NGP*(NGP/FTP))/(FTP*3600))*100

def change(df):
    '''takes difference between row above and row below'''
    #ftp is about 4.624 mps
    
    try:
        print(df.sample().T)
        new_df = df.apply(lambda x:x.shift(-1)-x)
        new_df['ts'] = new_df['ts'].dt.seconds
        if len(new_df)>10:
            f_df = new_df.rolling(window=4).mean()
        else:
            f_df = new_df
        f_df.dropna(inplace=True)
        f_df['pace'] = f_df['dist']/f_df['ts']
        f_df['grade'] = f_df['elev']/f_df['dist']
        f_df['NGP'] = f_df.apply(lambda x: x.pace*(1+.033*x.grade*100) if x.grade>0
                              else x.pace*(1+.03*.45*x.grade*100), axis=1)
        f_df['stress'] = f_df.apply(lambda x: TSS(x.ts,x.pace,4.624), axis=1)
    except:
        f_df=pd.DataFrame({'stress':[0]})
    return f_df



f1 = r"C:\ProgramData\Garmin\GarminConnect\Forerunner 410-3853586166\FitnessHistory\2018-05-18-162740.TCX"
f_dates = [f[:10] for f in os.listdir(os.getcwd())]
df = pd.DataFrame(data={'date':f_dates, 'runs':os.listdir(os.getcwd())})
df['stress'] = df['runs'].apply(lambda x:change(tcx_to_df(x))['stress'].sum() if len(tcx_to_df(x))>0 else 0)
df['date'] = pd.to_datetime(df['date'])
g_df =df.groupby('date')['stress'].sum().reset_index()
#three_day_list = [f for f in os.listdir(os.getcwd()) if 
#                  dt.date.fromtimestamp(os.path.getctime(f)) > 
#                  (dt.date.today()-dt.timedelta(days=3))]
#
#list_14 = [f for f in os.listdir(os.getcwd()) if 
#                  dt.date.fromtimestamp(os.path.getctime(f)) > 
#                  (dt.date.today()-dt.timedelta(days=14))]
#
#
#list_42 = [f for f in os.listdir(os.getcwd()) if 
#                  dt.date.fromtimestamp(os.path.getctime(f)) > 
#                  (dt.date.today()-dt.timedelta(days=42))]
#
#
#stress_3_day = [change(tcx_to_df(x))['stress'].sum() for x in three_day_list]
#stress_3 = sum(stress_3_day)/3
#
#stress_14_day = [change(tcx_to_df(x))['stress'].sum() for x in list_14]
#stress_14 = sum(stress_14_day)/14
#
#stress_42_day = [change(tcx_to_df(x))['stress'].sum() for x in list_42]
#stress_42 = sum(stress_42_day)/42
#
#print(stress_3, stress_14, stress_42)
#
