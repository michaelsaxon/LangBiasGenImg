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

def main(meta_folder_dir="/Users/mssaxon/samples_translated", 
    folder_1 = "samples_demega", 
    folder_2 = "samples_sd1-4", 
    folder_3 = "samples_sd2", 
    folder_4 = "samples_dalle2", 
    word_1 = "dog", 
    word_2 = "airplane"):

    prompts_base = open("/Users/mssaxon/freq_lists_translated.csv", "r").readlines()

    index = list(map(lambda x: x.split(",")[0], prompts_base))

    word_line_1 = index.index(word_1)
    word_line_2 = index.index(word_2)

    source_base = open("base.tex", "r").read()

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


if __name__ == "__main__":
    main()