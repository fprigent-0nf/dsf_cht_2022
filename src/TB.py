# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 20:57:53 2022

@author: fprigent-0nf

><(((°>
"""

################################################################################

import pandas as pd
import geopandas as gpd
import os

path_csv1 = '../data/csv/releves_chataignier_IdF_DSF_2022_TB3.csv'
# path_csv2 = '../data/csv/releves_chataignier_IdF_DSF_2022_VLM_RT_TB.csv'

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

       epicollect:

    'uuid', 'DATE', 'REC_SUP2', 'REC_LIGN', 'G', 'MORTAL01', 'MRAMIF01',
           'MORTAL02', 'MRAMIF02', 'MORTAL03', 'MRAMIF03', 'MORTAL04', 'MRAMIF04',
           'MORTAL05', 'MRAMIF05', 'MORTAL06', 'MRAMIF06', 'MORTAL07', 'MRAMIF07',
           'MORTAL08', 'MRAMIF08', 'MORTAL09', 'MRAMIF09', 'MORTAL10', 'MRAMIF10',
           'MORTAL11', 'MRAMIF11', 'MORTAL12', 'MRAMIF12', 'MORTAL13', 'MRAMIF13',
           'MORTAL14', 'MRAMIF14', 'MORTAL15', 'MRAMIF15', 'MORTAL16', 'MRAMIF16',
           'MORTAL17', 'MRAMIF17', 'MORTAL18', 'MRAMIF18', 'MORTAL19', 'MRAMIF19',
           'MORTAL20', 'MRAMIF20', 'R_MAX', 'DIST_MAX', 'REMARQUE', 'NOTATEUR',
           'geometry', 'filename'],
       '''


csv1 = pd.read_csv(path_csv1, delimiter=';', header=2, encoding="ISO-8859-1")
# csv2 = pd.read_csv(path_csv2, delimiter=';', header=2, encoding="ISO-8859-1")

csv1['filename'] = os.path.basename(path_csv1)
# csv2['filename'] = os.path.basename(path_csv2)
# dcsv['geometry'] = dcsv.geometry.apply(wkt.loads)
# ddcsv=gpd.GeoDataFrame(dcsv, geometry='geometry', crs=2154)

# csv = pd.concat([csv1, csv2])
csv = csv1.copy()

csv['lib_codeinsee'].fillna('dsf', inplace=True)
# csv.loc[csv.code_placette.dtype != 'int64', 'placette'] = csv.code_placette

cols = ['code_placette', 'x93', 'y93', 'lib_codeinsee', 'observation', 'date_obs',
        'codeco1', 'G___PLAC', 'DMAXA___PLAC', 'REMARQUES___PLAC',
        'RECOUV_SUP___PLAC', 'RECOUV_INF___PLAC', 'lib_PEUP_RUIN___PLAC',
        'filename']

d2=pd.pivot_table(csv, index=cols, values=['MORBRA2___ARBRE','PERRAM2___ARBRE'],
           columns=['arbre'])

d2.columns = [f"{x[0]}{int(x[1]):0>2}"
              .replace('MORBRA2___ARBRE','MORTAL')
              .replace('PERRAM2___ARBRE','MRAMIF')
              for x in d2.columns]
d2.reset_index(inplace=True)

row = [177, 652120, 6837020, 'SAINTE-GENEVIEVE-DES-BOIS',
 67874, '29/06/2022', '78S01', 33, 10,
 "Peuplement ruiné. Coupe sanitaire et nombreux arbres E et F mais sur une zone restreinte centrée sur les coordonnées enregistrées. Le centre de la placette est 14 mètres plus au sud qu'en 2020. Peuplement très dépérissant autour.",
 3, 3, 'OUI', 'releves_chataignier_IdF_DSF_2022_TB3.csv',
 5,5,5,5,5,5,5,5,5,5,
 5,5,5,5,5,5,5,5,5,5,
 5,5,5,5,5,5,5,5,5,5,
 5,5,5,5,5,5,5,5,5,5]
# df.loc[len(df)] = list
d2.loc[len(d2)] = row

gdf = gpd.GeoDataFrame(d2, geometry=gpd.points_from_xy(d2.x93,
                                                       d2.y93,
                                                       crs='epsg:2154'))
gdf.rename(columns = {'code_placette': 'NUM_PLAC',
                      'lib_codeinsee': 'NMASSIF',
                      'observation':'uuid',
                      'date_obs':'DATE',
                      'codeco1': 'NOTATEUR',
                      'G___PLAC': 'G',
                      'DMAXA___PLAC': 'DIST_MAX',
                      'REMARQUES___PLAC': 'REMARQUE',
                      'RECOUV_SUP___PLAC': 'REC_SUP2',
                      'RECOUV_INF___PLAC': 'REC_LIGN',
                      'lib_PEUP_RUIN___PLAC': 'ETAT_SAN'
                     }, inplace = True)
gdf.drop(['x93', 'y93'], axis='columns', inplace=True)
gdf['R_MAX'] = 20
gdf['NOTATEUR'] = 'dsf_' + gdf['NOTATEUR']



