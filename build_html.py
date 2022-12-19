import os

BASE = '''
<html>
<head>
<style>
img   {width: 100px; height: 100px;}
table    {margin: auto;}
</style>
</head>
<body>
<table>
'''

TAIL = '''
</table>
</body>
</html>
'''

folders = ['samples_demega', 'samples_demini', 'samples_sd1-1',  'samples_sd1-2',  'samples_sd1-4', 'samples_cv2', 'samples_sd2', 'samples_dalle2']

HUMAN = ['']

ANIMAL = ['']

TECH = ['']

for folder in folders:
    if folder == 'samples_dalle2':
        num = 10
    else:
        num = 12

    middle = ""
    middle_human = ""
    middle_animal = ""
    middle_tech = ""

    prompts_base = open("freq_lists_translated.csv", "r").readlines()
    index = prompts_base[0].strip().split(",")
    for line_no, line in enumerate(prompts_base[1:]):
        this_line = ""
        this_line += '<tr style="background-color: black; color: white;"><td style="background-color: white;"></td>'
        line = line.strip().split(",")
        for idx in range(len(index)):
            # build a prompt based on the above templates from the 
            lang = index[idx]
            word = line[idx]
            this_line += f'<td style="text-align: center;">{lang}<br>{word}</td>'
        this_line += "</tr>\n<tr>\n"
        this_line += f'<td style="border-right: 5pt solid rgb(150,0,0); color: rgb(150,0,0); font-size: 20pt; background-color: rgb(255,240,240);"><div style="transform:rotate(-90deg); margin: 0px; padding: 0px;"><b>{line[0]}</b></div></td>'
        # the images
        for idx in range(len(index)):
            this_line += "<td>"
            # build a prompt based on the above templates from the 
            word = index[idx]
            for i in range(10):
                fname = f"{line_no}-{index[idx]}-{line[0]}-{i}.png"
                this_line += f'<img src="{fname}"><br>\n'
            this_line += "</td>\n"
        this_line += "</tr>\n"
        middle += this_line
        if line[0] in HUMAN:
            middle_human += this_line
        if line[0] in ANIMAL:
            middle_animal += this_line
        if line[0] in TECH:
            middle_tech += this_line

    with open(f"samples_translated/{folder}/index.html","w") as f:
        f.write(BASE+middle+TAIL)