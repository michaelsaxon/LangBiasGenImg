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

PROMPTS = """a photograph of a dog
a photograph of a big dog
a photograph of a big dog in a field
a photograph of a big dog playing frisbee in a field
a photograph of a big dog chasing a ball in a field
a photograph of a big dog chasing a squirrel
un foto de un perro
un foto de un perro grande
un foto de un perro en el campo
un foto de un perro grande en el campo
un foto de un perro grande jugando en el campo
un foto de un perro grande jugando con una pelota en el campo
un foto de un perro grande persiguiendo a una ardilla
犬の写真
大犬の写真
大きい犬の写真
大きな犬の写真
大型犬の写真
野原で遊ぶ大きな犬の写真
フィールドでフリスビーをしている大きな犬の写真
リスを追いかける犬の写真
a photograph of a dog made of fire
a photograph of a big dog made of fire
a photograph of a big dog made of fire standing on the moon
a photograph of a big dog made of fire standing on the moon eating a pizza
un foto de un perro hecho de fuego
un foto de un perro hecho de fuego pisando la luna
un foto de un perro hecho de fuego en la luna
un foto de un perro hecho de fuego comiendo pizza en la luna
火でできた犬の写真
火でできた大型犬の写真
月に立っている火でできた犬の写真
月に立っていてピザを食べる火でできた犬の写真"""


def gen_middle_self():
    middle = ""
    for line_no, line in enumerate(PROMPTS.split("\n")):
        middle += f'<tr style="background-color: black; color: white;"><td>{line.strip()}</td></tr>\n<tr>\n<td>\n'
        # the images
        for i in range(12):
            fname = f"{line_no}-{i}.png"
            middle += f'<img src="{fname}">'
        middle += "\n</td>\n"
        middle += "</tr>\n"
    return middle

def gen_middle_all():
    middle = ""
    for line_no, line in enumerate(PROMPTS.split("\n")):
        middle += f'<tr style="background-color: black; color: white; text-align: center;"><td style="background-color: white;"></td><td>{line.strip()}</td></tr>\n'
        for folder in ['demega', 'demini', 'sd1-4',  'sd2']:
            middle += f'<tr>\n<td style="border-right: 1pt solid rgb(150,0,0); color: rgb(150,0,0); background-color: rgb(255,240,240);">{folder}</td>\n<td>\n'
            # the images
            for i in range(12):
                fname = f"simple_{folder}/{line_no}-{i}.png"
                middle += f'<img src="{fname}">'
            middle += "\n</td>\n"
            middle += "</tr>\n"
    return middle

with open("simples/index.html","w") as f:
    f.write(BASE+gen_middle_all()+TAIL)