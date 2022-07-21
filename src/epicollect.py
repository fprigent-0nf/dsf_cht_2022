# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 18:36:14 2022

@author: fprigent-0nf
"""

import pandas as pd
import geopandas as gpd
import requests
from io import StringIO


project_slug = 'dsf-chataignier-ile-de-france-et-oise'
map_index = 1
filter_by = 'created_at' #or uploaded_at
filter_from = '2022-06-01'
_format = 'csv'

url = f"https://five.epicollect.net/api/export/entries/{project_slug}?"
url += f"map_index={map_index}&format={_format}&headers=true"
url += f"&filter_by={filter_by}&filter_from={filter_from}"

print('loading epicollect')
download = requests.get(url)
text=StringIO(download.content.decode('utf-8'))
df = pd.read_csv(text)

# placette Nan df.ec5_uuid=="1332a1fd-a583-48a0-94e9-ec30aea79b7b"
df.loc[df.ec5_uuid=="1332a1fd-a583-48a0-94e9-ec30aea79b7b",'arbre_01':'MR_20'] = 5

print(f"    {len(df)} placettes")

''' géorelevé: dsf_cht_2022

       'uuid', 'ObjetId', 'Descriptif', 'DATE', 'NOTATEUR', 'NMASSIF',
       'NUM_PLAC', 'ETAT_SAN', 'G', 'REC_SUP2', 'REC_LIGN', 'DIST_MAX',
       'R_MAX', 'Coupe2020', 'REMARQUE',
       'MORTAL01', 'MRAMIF01', 'VISIH_01', 'MORTAL02', 'MRAMIF02', 'VISIH_02',
       'MORTAL03', 'MRAMIF03', 'VISIH_03', 'MORTAL04', 'MRAMIF04', 'VISIH_04',
       'MORTAL05', 'MRAMIF05', 'VISIH_05', 'MORTAL06', 'MRAMIF06', 'VISIH_06',
       'MORTAL07', 'MRAMIF07', 'VISIH_07', 'MORTAL08', 'MRAMIF08', 'VISIH_08',
       'MORTAL09', 'MRAMIF09', 'VISIH_09', 'MORTAL10', 'MRAMIF10', 'VISIH_10',
       'MORTAL11', 'MRAMIF11', 'VISIH_11', 'MORTAL12', 'MRAMIF12', 'VISIH_12',
       'MORTAL13', 'MRAMIF13', 'VISIH_13', 'MORTAL14', 'MRAMIF14', 'VISIH_14',
       'MORTAL15', 'MRAMIF15', 'VISIH_15', 'MORTAL16', 'MRAMIF16', 'VISIH_16',
       'MORTAL17', 'MRAMIF17', 'VISIH_17', 'MORTAL18', 'MRAMIF18', 'VISIH_18',
       'MORTAL19', 'MRAMIF19', 'VISIH_19', 'MORTAL20', 'MRAMIF20', 'VISIH_20',
       'geometry', 'CCOD_FRT', 'CCOD_UG','CCOD_PRF',
       'A', 'B', 'C', 'D', 'E', 'F', 'prop_EF', 'prop_DEF', 'etat_sanit'


    epicollect: dsf-chataignier-ile-de-france-et-oise

       'ec5_uuid', 'created_at', 'uploaded_at', 'title', 'date',
       '2_Coupes_effectues_d', 'type_obs_1', 'obs_1', 'obs_onf_1',
       'lat_coord_gps', 'long_coord_gps', 'accuracy_coord_gps',
       'UTM_Northing_coord_gps', 'UTM_Easting_coord_gps', 'UTM_Zone_coord_gps',
       'RECOUV_SUP', 'RECOUV_INF', 'G', 'PEUP_RUIN', '14_Visibilit_des_hou',
       'arbre_01', 'MB_01', 'MR_01', 'arbre_02', 'MB_02', 'MR_02',
       'arbre_03', 'MB_03', 'MR_03', 'arbre_04', 'MB_04', 'MR_04',
       'arbre_05', 'MB_05', 'MR_05', 'arbre_06', 'MB_06', 'MR_06',
       'arbre_07', 'MB_07', 'MR_07', 'arbre_08', 'MB_08', 'MR_08',
       'arbre_9', 'MB_09', 'MR_09', 'arbre_10', 'MB_10', 'MR_10',
       'arbre_11', 'MB_11', 'MR_11', 'arbre_12', 'MB_12', 'MR_12',
       'arbre_13', 'MB_13', 'MR_13', 'arbre_14', 'MB_14', 'MR_14',
       'arbre_15', 'MB_15', 'MR_15', 'arbre_16', 'MB_16', 'MR_16',
       'arbre_17', 'MB_17', 'MR_17', 'arbre_18', 'MB_18', 'MR_18',
       'arbre_19', 'MB_19', 'MR_19', 'arbre_20', 'MB_20', 'MR_20',
       'RAYON_PLACETTE', 'DMAXA', 'REMARQUES'
'''

################################################################################

df['date'] = df['date'].str.replace('/','-')
df['NOTATEUR'] = df.apply(lambda x: f"{x['type_obs_1']}_{x['obs_1']}_{x['obs_onf_1']}".replace('_nan',''),axis=1)
df.rename({'arbre_9': 'arbre_09'}, inplace=True, axis=1)

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.long_coord_gps,
                                                       df.lat_coord_gps,
                                                       crs='epsg:4326'))
gdf.to_crs(epsg=2154, inplace=True)
gdf.rename(columns = {'ec5_uuid':'uuid',
                     'date':'DATE',
                     'RECOUV_SUP': 'REC_SUP2',
                     'RECOUV_INF': 'REC_LIGN',
                     'RAYON_PLACETTE': 'R_MAX',
                     'DMAXA': 'DIST_MAX',
                     'REMARQUES': 'REMARQUE'
                     }, inplace = True)
gdf.columns = gdf.columns.str.replace('MB_','MORTAL').str.replace('MR_','MRAMIF')

cols = ['created_at',
        'uploaded_at',
        '2_Coupes_effectues_d',
        'title',
        'type_obs_1',
        'obs_1',
        'obs_onf_1',
        'lat_coord_gps',
        'long_coord_gps',
        'accuracy_coord_gps',
        'UTM_Northing_coord_gps',
        'UTM_Easting_coord_gps',
        'UTM_Zone_coord_gps',
        'PEUP_RUIN',
        '14_Visibilit_des_hou']
gdf.drop(cols, axis='columns', inplace=True)

for c in gdf.columns:
    if 'arbre_' in c:
        gdf.drop(c, axis='columns', inplace=True)

gdf['filename'] = 'epicollect'
