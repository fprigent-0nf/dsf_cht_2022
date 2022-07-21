# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 11:53:27 2022

@author: fprigent-0nf
"""

import glob
import os
import sys
from tqdm import tqdm
import pandas as pd
import geopandas as gpd
from shapely import wkt

import epicollect as epi

survey_path = "../data/shp"
csv_path = "../data/csv"
# write_dir = f"{survey_path}/EXTRACT"
out_path = "../result"
rdf_path = r"C:\Donnees\fp42778\SIG\@ENDO\Referentiel\8520_rdf\rdf_ugs_8520.shp"
placettes_2022_path = "../data/sig/placettes2022.zip"
img_path = "../report/img"


################################################################################
def load_all_zipsurveys_as_geopandas(path):
    files = glob.glob(f"{path}/*shp.zip", recursive=False)
    geoliste = list()
    for f in tqdm(files, ascii=' #', desc='loading files'):
        try:
            gdf = gpd.read_file(f)
            if gdf.crs != 'epsg:2154': #Lambert-93
                gdf.to_crs('EPSG:2154', inplace=True)
            gdf['filename'] = os.path.basename(f)
            geoliste.append(gdf)
        except:
            print("Unexpected error:", sys.exc_info()[0])
    g = gpd.GeoDataFrame(pd.concat(geoliste, ignore_index=True), crs='EPSG:2154')
    return g



################################################################################
################################################################################

dsf0 = load_all_zipsurveys_as_geopandas(survey_path)
epigdf = epi.gdf
#load csv
dcsv = pd.read_csv(csv_path + '/dsf_cht_2022_p173_ronqueux_releve.csv',
              delimiter=';')
dcsv['geometry'] = dcsv.geometry.apply(wkt.loads)
ddcsv=gpd.GeoDataFrame(dcsv, geometry='geometry', crs=2154)

dsf = pd.concat([dsf0, epi.gdf, dcsv], axis=0, ignore_index=True)

l1 = len(dsf)
dsf.drop_duplicates(subset=dsf.columns[dsf.columns!='filename'],
                    keep='last', inplace=True)
print (f"    {l1-len(dsf)} placettes dupliquées")

# epi = get_epicollect.gdf
# e2 = pd.concat([dsf.filter(regex='MORTAL|MRAMIF'), epi.filter(regex='MORTAL|MRAMIF')],
#           ignore_index=True)
# epi.rename(columns = {'team':'team_name', 'points':'points_scored'}, inplace = True)
### Transformation Datas ################################################
replace_class = {
       # Classes MB et MR
       "0 : 0 -> 5 %":    0,
       "1 : 6 -> 25 %":   1,
       "2 : 26 -> 50 %":  2,
       "3 : 51 -> 75 %":  3,
       "4 : 76 -> 95 %":  4,
       "5 : 96 -> 100 %": 5,
       # Classes recouvrement
       "1: 0-5%":    1,
       "2: 5-25%" :  2,
       "3: 25-50%":  3,
       "4: 50-75%":  4,
       "5: 75-100%": 5
       }
replace_nmassif = {
    "BOIS D'ARCY": "BOISARCY",
    "CARNELLE": "CARN",
    "ECHARCON": "ECHA",
    "FAUSSE REPOSE": "F-REPOSE",
    "GIF": "GIFV",
    "GRANDS AVAUX": "GRAV",
    "HAUTILV": "HAUTIL-V",
    "LA CLAYE": "RAMB",
    "LA COUARDE": "RAMB",
    "LA MALMAISON": "MALMAI92",
    "MARLY": "MARLY-VS",
    "RONQUEUX": "RONQ",
    "SAULX": "SACH",
    "ST BENOIT": "SAINT-BE",
    "ST EUTROPE": "SAINTEUT",
    "TAILLES D'HERBELAY": "HERBELAY",
    "VERSAILLES": "VERSAILL",
    }
dsf.replace(replace_class, regex=True, inplace=True)

# suppression coupes rases
dsf = dsf[dsf.Coupe2020 != "RASE"]
# ajout colonnes CCOD_FRT;CCOD_UG;CCOD_PRF jointure spataile sur rdf_ugs_8520
# normalisation colonnes
dsf['NOTATEUR'] = dsf.NOTATEUR.str.lower()
dsf['NMASSIF'] = dsf.NMASSIF.str.upper()
dsf.replace(replace_nmassif, regex=True, inplace=True)
# récupération de la parcelle et ug la plus proche dans le référentiel RDF
rdf = gpd.read_file(rdf_path)
placettes_2022 = gpd.read_file(placettes_2022_path)

dsf = dsf.sjoin_nearest(rdf[['CCOD_FRT','CCOD_UG','CCOD_PRF','geometry']],
                        how='left', max_distance=25)
placettes_2022 = placettes_2022.sjoin_nearest(dsf[['NUM_PLAC','geometry']],
                                              how='left',distance_col='distance',
                                              max_distance=52)
del dsf['index_right']
# insertion colonne uuid hash pour garantie unicitée de ligne
# dsf.insert(0, 'uuid', pd.util.hash_pandas_object(dsf, index=False).apply(hex))
dsf['uuid'] = pd.util.hash_pandas_object(dsf, index=False).apply(hex)
dsf['NMASSIF'].fillna('DSF', inplace=True)
dsf['CCOD_FRT'].fillna('DSF', inplace=True)
dsf['NUM_PLAC'].fillna('000', inplace=True)

# index sur colonnes, ex: dsf[index]
# MORTAL <- grep("MORTAL",colnames(dsf))
MORTAL = dsf.columns[dsf.columns.str.contains('MORTAL')]
# MRAMIF <- grep("MRAMIF",colnames(dsf))
MRAMIF = dsf.columns[dsf.columns.str.contains('MRAMIF')]
# VISI   <- grep("VISIH",colnames(dsf))
VISI = dsf.columns[dsf.columns.str.contains('VISIH')]

# remplacement des notations aberrentes 5_0 par 5_5
# TODO: à améliorer
count_5_0 = 0
for i in range(0, 20):
    for j in range(0, len(dsf)):
        if dsf[MORTAL[i]].iat[j] == 5 and dsf[MRAMIF[i]].iat[j] == 0:
            dsf[MRAMIF[i]].iat[j] = 5
            count_5_0 += 1
#
mortal = dsf[MORTAL]
ramif = dsf[MRAMIF]
visih = dsf[VISI]

#rectification num placettes éronnées
# ECHARCON erreur num_plac 193 -> 194
dsf.loc[dsf.uuid=='0x47b3f749f1766e17', 'NUM_PLAC'] = 194
# placette 133 MISSIONNAIRE -> BOISARCY
dsf.loc[dsf.NUM_PLAC==133, 'NMASSIF'] = "BOISARCY"

### tidy dataframe sur l'ensemble des arbres ttes placettes confondues #########
a = pd.melt(dsf,id_vars=['uuid','NUM_PLAC','NMASSIF'],value_vars=MORTAL.append(MRAMIF).append(VISI))
a['num_arbre'] = a.variable.str.slice(-2)
a.variable = a.variable.str.slice(stop=-2)

arbres = a.pivot(index=['uuid','NUM_PLAC','NMASSIF','num_arbre'], columns='variable', values='value').reset_index()
arbres = arbres.rename(columns={"MORTAL": "MB", "MRAMIF": "MR", "VISIH_": "visi"}, errors="raise")

# casting
arbres[['MB','MR','num_arbre']] = arbres[['MB','MR','num_arbre']].astype('Int64')
# arbres['visi'] = (arbres.visi=='T')
arbres.visi.replace({'T':'non', 'F':'oui'}, inplace=True)

### Fonctions de calcul notation DEPERIS #######################################
### MB: Mortalité branche
### MR: Manque ramifications
def get_note_deperis(mb, mr):
    matrice_deperis = [['A','B','C','D','E','F'],
                       ['B','B','C','D','E','F'],
                       ['C','C','D','D','E','F'],
                       ['D','D','D','E','F','F'],
                       ['E','E','E','F','F','F'],
                       ['F','F','F','F','F','F']]
    return matrice_deperis[mb][mr]

arbres['note'] = arbres.apply(lambda x: get_note_deperis(x.MB, x.MR), axis=1)


# Codification état sanotaire DSF ##############################################
# Code   Libellé                          Définition
# 0   Peuplement sain ou peu dépérissant  Moins de 20% d’arbres dépérissants
# 1   Peuplement dépérissant              Entre 20% et 50% d’arbres dépérissants
# 2   Peuplement très dépérissant         Entre 50% et 75% d’arbres dépérissants
# 3   Peuplement mort ou ruiné            Plus de 75% d’arbres dépérissants
# C   Coupe rase
################################################################################

def get_notes_by_placette(notes_string):
    '''renvoie le nombre de valeurs dans chaque classe A,B,C,D,E,F
    '''
    result = map(lambda x: notes_string.count(x), list("ABCDEF"))
    return pd.Series(result, index=list("ABCDEF"))
def get_codif_etat_sanitaire_placette(prop_deperissant):
    return
# répartition des arbres par placette dans chaque classe de note deperiss
# A B C D E F
p_notes = arbres.groupby(['uuid','NUM_PLAC','NMASSIF'])['note'].sum()
ddl = p_notes.apply(get_notes_by_placette)
ddl.sort_values(['NMASSIF','NUM_PLAC'], inplace=True)
# proportion EF dans chaque placette
ddl['prop_EF'] = (ddl.E + ddl.F)/20
# proportion DEF das chaque placette
ddl['prop_DEF'] = (ddl.D + ddl.E + ddl.F)/20

interv = [0, 0.2, 0.5, 0.75, 1.1]
lab = ["0","1","2","3"]
ddl['etat_sanit'] = pd.to_numeric(pd.cut(ddl.prop_EF, bins=interv, labels=lab,
                              include_lowest=True, right=False))

dsf = dsf.join(ddl, on=['uuid','NUM_PLAC','NMASSIF'])

### Sauvegardes data.frame FINAL ################################################
# from datetime import datetime
# date = datetime.today().strftime('%Y-%m-%d_%H%M')

# file_name = f"{date}_dsf_cht_global_{len(dsf):03}placettes"
repex = {';': ' - ',
         ',': ' - ',
         '\n': '',         
         '\r': '',
         '\r\n': ''
         }
dsf.replace(repex, regex=True, inplace=True)
epigdf.replace(repex, regex=True, inplace=True)
file_name = "dsf_cht_2022_final"
dsf.to_csv(f"{out_path}/{file_name}.csv", sep=',', encoding="latin1")
dsf.to_file(f"{out_path}/{file_name}.shp.zip", driver='ESRI Shapefile')
epigdf.to_csv(f"{out_path}/dsf_2022_epicollect.csv", index=False, sep=',',
              encoding="latin1")

### statistiques ###############################################################

nb_plac_par_massif = dsf[['uuid','NMASSIF']].groupby('NMASSIF').count().reset_index()
nb_plac_par_massif.columns = ['massif','nb. placettes']
nb_plac_par_notateur = dsf[['uuid','NOTATEUR']].groupby('NOTATEUR').count().reset_index()
nb_plac_par_notateur.columns = ['notateur','nb. placettes']
nb_arbres_par_classes = ddl[list('ABCDEF')].sum()
nb_arbres_par_classes.columns = ['classe','nb.arbres']



################################################################################
### PLOTS ######################################################################
################################################################################
import seaborn as sns
sns.set_style("darkgrid")
_dpi = 90
bin_20 = [0, .2, .4, .6, .8, 1]
bin_25 = [0,.25,.5,.75,1]
ddl2 = ddl2 = ddl.melt(ignore_index=False, value_vars=['prop_EF', 'prop_DEF'])
ddl2.reset_index(inplace=True)
### Histogram de répartition des placettes par classe état sanitaire ###########

dsf['etat_sanit'] = dsf['etat_sanit'].astype('category')
dsf['R_MAX'] = dsf['R_MAX'].astype('str').astype('category')
### classes d'amplitude 20% ####################################################
g2_20_EF = sns.displot(ddl2, x='value', stat='count', bins=bin_20, hue='NMASSIF',
                       multiple="stack", col='variable')
g_20_EF = sns.displot(ddl, x='prop_EF', stat='count', bins=bin_20,
                   hue='NMASSIF', multiple="stack")
g_20_EF.set(xticks=bin_20)
g_20_EF.set_xlabels('proportion E,F')
g_20_EF.set_ylabels('nb. placettes')
g_20_EF.savefig(f"{img_path}/g_20_EF.png", dpi=_dpi)
#
g_20_DEF = sns.displot(ddl, x='prop_DEF', stat='count', bins=bin_20,
                   hue='NMASSIF', multiple="stack")
g_20_DEF.set(xticks=bin_20)
g_20_DEF.set_xlabels('proportion D,E,F')
g_20_DEF.set_ylabels('nb. placettes')
g_20_DEF.savefig(f"{img_path}/g_20_DEF.png", dpi=_dpi)
### classes d'amplitude 25% ####################################################
g2_25_EF = sns.displot(ddl2, x='value', stat='count', bins=bin_25, hue='NMASSIF',
                       multiple="stack", col='variable')
g2_25_EF.set(xticks=bin_25)
g2_25_EF.set_xlabels('proportion')
g2_25_EF.set_ylabels('nb. placettes')
g_25_EF = sns.displot(ddl, x='prop_EF', stat='count', bins=bin_25,
                   hue='NMASSIF', multiple="stack")
g_25_EF.set(xticks=bin_25)
g_25_EF.set_xlabels('proportion E,F')
g_25_EF.set_ylabels('nb. placettes')
g_25_EF.savefig(f"{img_path}/g_25_EF.png", dpi=_dpi)
#
g_25_DEF = sns.displot(ddl, x='prop_DEF', stat='count', bins=bin_25,
                   hue='NMASSIF', multiple="stack")
g_25_DEF.set(xticks=bin_25)
g_25_DEF.set_xlabels('proportion D,E,F')
g_25_DEF.set_ylabels('nb. placettes')
g_25_DEF.savefig(f"{img_path}/g_25_DEF.png", dpi=_dpi)

### nb. placettes par classe etat sanitaire ####################################
# sns.catplot(x="etat_sanit", kind="count", hue='NMASSIF', data=dsf, dodge=True)
g_etat_san_par_class = sns.catplot(x="etat_sanit", kind="count", data=dsf)
g_etat_san_par_class.set_xlabels('classe état sanitaire')
g_etat_san_par_class.set_ylabels('nb. placettes')
g_etat_san_par_class.savefig(f"{img_path}/g_etat_san_par_class.png",
                                           dpi=_dpi)


g_g = sns.displot(dsf, x='G', stat='count', bins=list(range(0,60,5)),
                  hue='NMASSIF', multiple='stack')
g_g.set_xlabels('surface terrière m²')
g_g.set_ylabels('nb. placettes')
g_g.savefig(f"{img_path}/g_g.png", dpi=_dpi)

g_rmax = sns.displot(dsf, x='R_MAX', stat='count', hue='NMASSIF',
                     multiple='stack')
g_rmax.set_xlabels('rayon de représentativité placette')
g_rmax.set_ylabels('nb. placettes')
g_rmax.savefig(f"{img_path}/g_rmax.png", dpi=_dpi)

g_dmax20 = sns.displot(dsf, x='DIST_MAX', stat='count', hue='NMASSIF',
                       multiple='stack', bins=list(range(0,60,10)))
g_dmax20.set_xlabels('distance du 20e arbre')
g_dmax20.set_ylabels('nb. placettes')
g_dmax20.savefig(f"{img_path}/g_dmax20.png", dpi=_dpi)

### visi houppier  #############################################################
g_visi = sns.displot(arbres, x='visi', stat='count', hue='NMASSIF',
                     multiple='stack')
g_visi.set_xlabels('visbilité houppier')
g_visi.set_ylabels('nb. arbres')
# g_visi.set_xticklabels(['non visible', 'visible'])
g_visi.savefig(f"{img_path}/g_visi.png", dpi=_dpi)



### matrice mb mr ##############################################################
mb_mr = pd.melt(arbres,id_vars=['MB','MR']).groupby(['MB','MR']).count()
g_mb_mr = sns.relplot(x="MR", y="MB", size="value",
                      sizes=(min(mb_mr.value*1.5),max(mb_mr.value*1.5)), alpha=.7,
                      palette="muted", height=6, color='orange', data=mb_mr)
# g_mb_mr.axes.ravel()[0].invert_yaxis()
g_mb_mr.axes[0][0].invert_yaxis()
g_mb_mr._legend.set_title('nb.arbres')
for lh in g_mb_mr._legend.legendHandles:
    lh.set_alpha(.4)
    lh.set_color('orange')
g_mb_mr.savefig(f"{img_path}/g_mb_mr.png", dpi=_dpi)


# carte de répartition des placettes réalisées #################################
import contextily as cx
dsf_wm = dsf.to_crs(epsg=3857)
# rdf_wm = rdf.to_crs(epsg=3857)
ax = dsf_wm.plot(figsize=(8, 14), alpha=0.9, color='red', markersize=2,
                 edgecolor='red')
# bx = rdf_wm.plot(figsize=(20, 40), alpha=0.5, edgecolor='k')
# dsf_wm.apply(lambda x: ax.annotate(text=x['NUM_PLAC'], xy=x.geometry.coords[0],
#                                    xytext=(3, 3), textcoords="offset points", fontsize=7),
#              axis=1)
ax.set_axis_off()
cx.add_basemap(ax, zoom=11)
ax.get_figure().savefig(f"{img_path}/g_localisation.png", bbox_inches='tight',
                        dpi=_dpi*2.0, orientation='landscape')
