import os

from arxiv_plots import *

from collections import defaultdict

BASE = '''
<html>
<head>
<style>
img   {width: 100px; height: 100px;}
table    {margin: auto;}
</style>
</head>
<body>

  <header style="border-top:2px solid black; border-bottom: 1px dotted #676767; position:fixed; height: 60px; overflow:hidden; top:0; right: 0; width:100%; background-color:white;">
    <!--div class="menucontainer" -->
    <div>
    <h2 style="margin-left: 20pt; margin-top:6pt;float:left;color:black;">
            <a style="color:FD2925; text-weight: 800;" href="../../index.html">[CoCo-CroLa Project Home]</a> /
            <a style="color:darkblue; text-weight: 800; font-style: italic;" href="../index.html">v0.1 Demo</a> /
            <a style="color:cD0905; text-weight: 400;" href="index.html">###NAME###</a></h2>
  </div>
  </header>

  <div style="height:65px;">&nbsp;</div> 

<table>
'''

TAIL = '''
</table>
</body>
</html>
'''

folders = ['samples_demega', 'samples_demini', 'samples_sd1-1',  'samples_sd1-2',  'samples_sd1-4', 'samples_cv2', 'samples_sd2', 'samples_dalle2']

results_cross, results_self, results_spec, results_langdiv = load_all_csvs(merge=False)


fname_map = {'samples_demega' : "DALL-E Mega Sorted by ###LANG Correctness", 
            'samples_demini' : "DALL-E Mini Sorted by ###LANG Correctness", 
            'samples_sd1-1' : "StableDiffusion 1.1 Sorted by ###LANG Correctness", 
            'samples_sd1-2' : "StableDiffusion 1.2 Sorted by ###LANG Correctness", 
            'samples_sd1-4' : "StableDiffusion 1.4 Sorted by ###LANG Correctness", 
            'samples_cv2' : "CogView2 Sorted by ###LANG Correctness", 
            'samples_sd2' : "StableDiffusion 2 Sorted by ###LANG Correctness", 
            'samples_dalle2' : "DALL-E 2 Sorted by ###LANG Correctness"
}

for folder in folders:
    df = results_cross[folder]


    if folder == 'samples_dalle2':
        num = 10
    else:
        num = 12

    default_index_lang  = "en"
    if folder == 'samples_cv2':
        default_index_lang = "zh"


    prompts_base = open("/Users/mssaxon/freq_lists_translated.csv", "r").readlines()
    index = prompts_base[0].strip().split(",")

    for lang in index:
        df = df[df[lang] != '---']


    middles = defaultdict(lambda : "")

    for page_sort_language in index:

        middle = ""

        # sorting by this column. Color its cell dark red. link to others in the 
        # we are drawing this page
        coords_order = list(df.sort_values(page_sort_language, ascending = False).index + 1)
        if folder == "samples_cv2":
            print(page_sort_language)
            print(coords_order)

        for line_no in coords_order:
            line = prompts_base[line_no]
            line_no = line_no - 1
            this_line = ""
            this_line += '<tr style="background-color: black; color: white;"><td style="background-color: white;"></td>'
            line = line.strip().split(",")
            for idx in range(len(index)):
                # build a prompt based on the above templates from the 
                lang = index[idx]
                word = line[idx]
                if lang == default_index_lang:
                    url = "index.html"
                else: 
                    url = f"sort_{lang}.html"
                if lang == page_sort_language:
                    this_line += f'<td style="text-align: center; background-color: darkred;">{lang}<br>{word}</td>'
                else:
                    this_line += f'<td style="text-align: center;"><a style="color: white;" href="{url}">{lang}<br>{word}</td>'
            this_line += "</tr>\n<tr>\n"
            this_line += f'<td style="border-right: 5pt solid rgb(150,0,0); color: rgb(150,0,0); font-size: 20pt; background-color: rgb(255,240,240);"><div style="transform:rotate(-90deg); margin: 0px; padding: 0px;"><b>{line[0]}</b></div></td>'
            # the images
            for idx in range(len(index)):
                lang = index[idx]
                if lang == default_index_lang:
                    url = "index.html"
                else: 
                    url = f"sort_{lang}.html"
                this_line += "<td>"
                # build a prompt based on the above templates from the 
                word = index[idx]
                for i in range(10):
                    fname = f"{line_no}-{index[idx]}-{line[0]}-{i}.png"
                    if lang != page_sort_language:
                        this_line += f'<a href="{url}">'
                    this_line += f'<img src="{fname}">'
                    if lang != page_sort_language:
                        this_line += "</a>"
                    this_line += '<br>\n'
                this_line += "</td>\n"
            this_line += "</tr>\n"
            middle += this_line

        if page_sort_language == default_index_lang:
            pname = "index.html"
        else:
            pname = f"sort_{page_sort_language}.html"
        with open(f"/Users/mssaxon/samples_translated_downsampled/{folder}/{pname}","w") as f:
            f.write(BASE.replace("###NAME###",fname_map[folder].replace("###LANG", page_sort_language.upper()))+middle+TAIL)