BASE = '''
<html>
<head>
<style>
img   {width: 90px; height: 90px;}
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

prompt_options = [
    'a photograph of $$$',
    'an image of $$$',
    'a photo of $$$',
    'a picture of $$$',
    'a picture of a $$$',
    'a picture of the $$$',
    'a picture of my $$$',
    'a picture of an $$$'
]


middle = ""
prompts_base = open("frequencylist/freq_lists_gold.csv", "r").readlines()
for line_no, line in enumerate(prompts_base[1:]):
    line = line.strip().split(",")
    middle += f'<tr style=" color: rgb(150,0,0); font-size: 20pt; background-color: rgb(255,240,240); text-align: center;"><td></td><td style="border-bottom: 5pt solid rgb(150,0,0);">{line[0]}</td></tr>\n'
    for idx in range(len(prompt_options)):
        prompt = prompt_options[idx].replace("$$$", line[0])
        middle += f'<tr><td style="background-color: black; color: white;"><b>{prompt}</b></td>'
        middle += "<td>"
        for i in range(9):
            fname = f"{line_no}-{idx}-{line[0]}-{i}.png"
            middle += f'<img src="{fname}">'
        middle += "</td>\n"
    middle += "</tr>\n"

with open("samples_test_idx/index.html","w") as f:
    f.write(BASE+middle+TAIL)