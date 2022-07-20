# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 21:14:22 2022

@author: fprigent-ONF
"""

import dsf_cht_2022 as d
import markdown


table1 = d.ddl.reset_index().iloc[:,1:].to_markdown(index=False)


head = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <title>dsf_cht2022_report</title>
    <style type="text/css">
        html {
            line-height: 1.5;
            font-family: Georgia, serif;
            font-size: 20px;
            color: #1a1a1a;
            background-color: #fdfdfd;
            }

        h1 {
            color: navy;
            #margin-left: 20px;
            text-align: center;
            }
        
        table, th, td {
            border: none;
            border-bottom: 1px solid #C8C8C8;
            border-collapse: collapse;
            text-align:left;
            padding: 10px;
            margin-bottom: 40px;
            font-size: 0.9em;
            }
    </style>
</head>

<body>
'''
tail = """
</body>
</html>
"""

md_text = f'''
# DSF_CHT 2022

*{d.date}   fprigent-ONF*

### {len(d.dsf)} placettes retenues ({len(d.dsf[d.dsf.NMASSIF=="DSF"])} placettes epicollect)
### {len(d.arbres)} arbres notés
    
## Localisation des relevés
<img src="./img/g_localisation.png" alt="Localisation">

{table1}

## classes d’amplitude 20%
![alt g_20_EF](./img/g_20_EF.png "g_20_EF") ![alt g_20_DEF](./img/g_20_DEF.png "g_20_DEF")

## classes d’amplitude 25%
![alt g_25_EF](./img/g_25_EF.png "g_25_EF") ![alt g_25_DEF](./img/g_25_DEF.png "g_25_DEF")


## Etat sanitaire des placettes
### Codification état sanitaire DSF
|Code|Libellé                             |Définition                          |
|:---|:-----------------------------------|:-----------------------------------|
|0   |Peuplement sain ou peu dépérissant  |Moins de 20% d’arbres dépérissants  |
|1   |Peuplement dépérissant              |Entre 20% et 50% d’arbres dépérissants|
|2   |Peuplement très dépérissant         |Entre 50% et 75% d’arbres dépérissants|
|3   |Peuplement mort ou ruiné            |Plus de 75% d’arbres dépérissants   |
|C   |Coupe rase                          |                                    |

![alt g_etat_san_par_class](./img/g_etat_san_par_class.png "g_etat_san_par_class")


## Notation DEPERIS
![alt tableau_DEPERIS](./img/tableau_DEPERIS.png "tableau_DEPERIS")

![alt g_mb_mr](./img/g_mb_mr.png "g_mb_mr")


## Surface terrière
![alt g_g](./img/g_g.png "g_g")


## Rayon de représentativité
![alt g_rmax](./img/g_rmax.png "g_rmax")


## Distance du 20e arbre
![alt g_dmax20](./img/g_dmax20.png "g_dmax20")


## visibilité houppiers
![alt g_visi](./img/g_visi.png "g_visi")


## Nombre de placettes par notateurs
{d.nb_plac_par_notateur.to_markdown(index=False)}


## Nombre de placettes par massifs
{d.nb_plac_par_massif.to_markdown(index=False)}




'''
html = head + markdown.markdown(md_text, extensions=['tables']) + tail
#
report_html = "../report/dsf_cht2022_report.html"
report_md = "../report/README.md"
with open(report_html, "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
    output_file.write(html)
with open(report_md, "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
    output_file.write(md_text)
