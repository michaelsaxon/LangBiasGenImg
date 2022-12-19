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

#folders = ['samples_demega', 'samples_demini', 'samples_sd1-1',  'samples_sd1-2',  'samples_sd1-4', 'samples_cv2', 'samples_sd2']

folders = ['samples_dalle2']

middle = ""
prompts_base = open("freq_lists_translated.csv", "r").readlines()
index = prompts_base[0].strip().split(",")
for line_no, line in enumerate(prompts_base[1:]):
    middle += '<tr style="background-color: black; color: white;"><td style="background-color: white;"></td>'
    line = line.strip().split(",")
    for idx in range(len(index)):
        # build a prompt based on the above templates from the 
        lang = index[idx]
        word = line[idx]
        middle += f'<td style="text-align: center;">{lang}<br>{word}</td>'
    middle += "</tr>\n<tr>\n"
    middle += f'<td style="border-right: 5pt solid rgb(150,0,0); color: rgb(150,0,0); font-size: 20pt; background-color: rgb(255,240,240);"><div style="transform:rotate(-90deg); margin: 0px; padding: 0px;"><b>{line[0]}</b></div></td>'
    # the images
    for idx in range(len(index)):
        middle += "<td>"
        # build a prompt based on the above templates from the 
        word = index[idx]
        for i in range(10):
            fname = f"{line_no}-{index[idx]}-{line[0]}-{i}.png"
            middle += f'<img src="{fname}"><br>\n'
        middle += "</td>\n"
    middle += "</tr>\n"

with open("samples_translated/samples_dalle2/index.html","w") as f:
    f.write(BASE+middle+TAIL)