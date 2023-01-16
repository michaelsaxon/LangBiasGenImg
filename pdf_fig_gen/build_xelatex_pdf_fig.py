import click
from PIL import Image

# all args should be in str
def textcoords(text, x, y):
    return f"\\node[inner sep=0pt, text=white] (base) at ({x},{y})" + "{\\Large \\textbf{" + text + "} }; \n"

def imgcoords(imgurl, x, y, width="1in"):
    return f"\\node[inner sep=0pt] at ({x},{y})" + "{\\includegraphics[width=" + width + "]{" + imgurl + "} };\n"


def generate_title(words_line, start_point_x=0.5, y_point=0.3, spacing=1):
    outstr = ""
    assert len(words_line) == 7
    for i, word in enumerate(words_line):
        x = start_point_x + spacing * i
        if i == 5:
            # hard code this is hebrew
            word = "\\begin{hebrew}" + word + "\\end{hebrew}"
        outstr += textcoords(word, str(x) + "in", str(y_point))
    return outstr


def generate_title_wordlist(word_list, start_point_x=0.5, y_point=0.3, spacing=1):
    outstr = ""
    assert len(word_list) == 7
    for i, word in enumerate(word_list):
        x = start_point_x + spacing * i
        outstr += textcoords(word, str(x) + "in", str(y_point))
    return outstr


def generate_images_vert(fname_base, start_point_y, x_point, spacing=1, fidx_start=0, col_len=3):
    outstr = ""
    for i in range(col_len):
        x = str(x_point) + "in"
        # fname format will be "154-es-sky-#.png"
        fname = fname_base.replace("#", str(int(fidx_start + i)))
        img = Image.open(fname)
        savefname = "tmp/" + fname.split("/")[-2] + "_" + fname.split("/")[-1]
        img = img.resize((100,100),Image.ANTIALIAS)
        img.save(savefname)
        y = str(start_point_y - spacing * i) + "in"
        outstr += imgcoords(savefname, x, y)
    return outstr




@click.command()
@click.option('--meta_folder_dir', default="/Users/mssaxon/samples_translated")
@click.option('--folder_1', default = "samples_demega")
@click.option('--folder_2', default = "samples_sd2")
@click.option('--folder_3', default = "samples_dalle2")
@click.option('--folder_4', default = "altdiffusion")
@click.option('--word_1', default = "dog")
@click.option('--word_2', default = "airplane")
@click.option('--word_3', default = "face")
def main_three(meta_folder_dir, folder_1, folder_2, folder_3, folder_4, word_1, word_2, word_3):
    prompts_base = open("/Users/mssaxon/freq_lists_translated.csv", "r").readlines()

    index = list(map(lambda x: x.split(",")[0], prompts_base))

    word_line_1 = index.index(word_1)
    word_line_2 = index.index(word_2)
    word_line_3 = index.index(word_3)


    source_base = open("base_3part.tex", "r").read()

    left_captions = generate_title(prompts_base[word_line_1].strip().split(","))
    mid_captions = generate_title(prompts_base[word_line_2].strip().split(","), 7.7)
    right_captions = generate_title(prompts_base[word_line_3].strip().split(","), 14.9)


    left_imgs = ""
    right_imgs = ""
    middle_imgs = ""
    left_x_start = 0.5
    mid_x_start = 7.7
    right_x_start = 14.9
    for y_idx, folder in enumerate([folder_1, folder_2, folder_3, folder_4]):
        # hard coded for now, number of languages
        y_start = -0.5 - y_idx * 3
        for x_idx, lang in enumerate(prompts_base[0].strip().split(",")):
            fname_base_left = meta_folder_dir + "/" + folder + f"/{word_line_1-1}-{lang}-{word_1}-#.png"
            left_imgs += generate_images_vert(fname_base_left, y_start, x_idx + left_x_start)
            fname_base_mid = meta_folder_dir + "/" + folder + f"/{word_line_2-1}-{lang}-{word_2}-#.png"
            middle_imgs += generate_images_vert(fname_base_mid, y_start, x_idx + mid_x_start)
            fname_base_right = meta_folder_dir + "/" + folder + f"/{word_line_3-1}-{lang}-{word_3}-#.png"
            right_imgs += generate_images_vert(fname_base_right, y_start, x_idx + right_x_start, fidx_start=3)



    source_base = source_base.replace("LEFTCAPTIONS", left_captions).replace("RIGHTCAPTIONS", right_captions).replace("LEFTIMAGES", left_imgs).replace("RIGHTIMAGES", right_imgs).replace("MIDDLECAPTIONS", mid_captions).replace("MIDDLEIMAGES", middle_imgs)

    with open("output.tex", "w") as f:
        f.write(source_base)

    print("Finished generating target text. Run `xelatex output.tex` to generate pdf")


# the code to gen figure 1
@click.command()
@click.option('--meta_folder_dir', default="/Users/mssaxon/samples_translated")
@click.option('--folder_1', default = "samples_demega")
@click.option('--folder_2', default = "samples_sd1-4")
@click.option('--folder_3', default = "samples_sd2")
@click.option('--folder_4', default = "samples_dalle2")
@click.option('--word_1', default = "dog")
@click.option('--word_2', default = "airplane")
@click.option('--single_half', is_flag = True)
def main_multi_model(meta_folder_dir, folder_1, folder_2, folder_3, folder_4, word_1, word_2, single_half):

    prompts_base = open("/Users/mssaxon/freq_lists_translated.csv", "r").readlines()

    index = list(map(lambda x: x.split(",")[0], prompts_base))

    word_line_1 = index.index(word_1)
    word_line_2 = index.index(word_2)

    if not single_half:
        source_base = open("base_twohalf.tex", "r").read()
    else:
        source_base = open("base_onehalf.tex", "r").read()

    left_captions = generate_title(prompts_base[word_line_1].strip().split(","))
    right_captions = generate_title(prompts_base[word_line_2].strip().split(","), 7.7)

    left_imgs = ""
    right_imgs = ""
    left_x_start = 0.5
    right_x_start = 7.7
    for y_idx, folder in enumerate([folder_1, folder_2, folder_3, folder_4]):
        # hard coded for now, number of languages
        y_start = -0.5 - y_idx * 3
        for x_idx, lang in enumerate(prompts_base[0].strip().split(",")):
            fname_base_left = meta_folder_dir + "/" + folder + f"/{word_line_1-1}-{lang}-{word_1}-#.png"
            left_imgs += generate_images_vert(fname_base_left, y_start, x_idx + left_x_start)
            fname_base_right = meta_folder_dir + "/" + folder + f"/{word_line_2-1}-{lang}-{word_2}-#.png"
            right_imgs += generate_images_vert(fname_base_right, y_start, x_idx + right_x_start)


    source_base = source_base.replace("LEFTCAPTIONS", left_captions).replace("RIGHTCAPTIONS", right_captions).replace("LEFTIMAGES", left_imgs).replace("RIGHTIMAGES", right_imgs)

    with open("output.tex", "w") as f:
        f.write(source_base)

    print("Finished generating target text. Run `xelatex output.tex` to generate pdf")


"""
SD2/JP
good: snow, keyboard, clock, watch, weapon, bird, bicycle
bad: captain, teacher, judge, mother, mama, dad, soldier

DE2/ID
good: cloud, cd, sky, keyboard, movie, moon, apple
bad: men, husband, male, dragon, mama, thigh, milk
"""
# hardcoded I'm sorry god
def gen_best_worst(meta_folder_dir = "/Users/mssaxon/samples_translated", model='samples_sd2', language='ja', words=["snow", "bicycle", "clock", "bird", "captain", "teacher", "judge"]):
    prompts_base = open("/Users/mssaxon/freq_lists_translated.csv", "r").readlines()

    index = list(map(lambda x: x.split(",")[0], prompts_base))

    langs = prompts_base[0].strip().split(",")

    # should be 7
    word_lines = [index.index(word) for word in words]
    words_translated = [prompts_base[word_line].strip().split(",")[langs.index(language)] for word_line in word_lines]

    source_base = open("base_onehalf.tex", "r").read()

    for i, wt in enumerate(words_translated):
        source_base = source_base.replace(f"LANG{i+1}", f"{language.upper()}: {wt}")
    #source_base = source_base.replace(".25in,0.75)", ".9in,0.75)")

    left_captions = generate_title_wordlist(words)

    left_imgs = ""
    right_imgs = ""
    left_x_start = 0.5
    right_x_start = 7.7
    for y_idx in range(1):
        # hard coded for now, number of languages
        y_start = -0.5 - y_idx * 3
        for x_idx, word in enumerate(words):
            fname_base_left = meta_folder_dir + "/" + model + f"/{word_lines[x_idx]-1}-{language}-{word}-#.png"
            left_imgs += generate_images_vert(fname_base_left, y_start, x_idx + left_x_start, col_len=4)


    source_base = source_base.replace("LEFTCAPTIONS", left_captions).replace("RIGHTCAPTIONS", "").replace("LEFTIMAGES", left_imgs).replace("RIGHTIMAGES", "")

    with open("output.tex", "w") as f:
        f.write(source_base)

    print("Finished generating target text. Run `xelatex output.tex` to generate pdf")



if __name__ == "__main__":
    main_three()