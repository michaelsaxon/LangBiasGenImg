import click
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline, AltDiffusionPipeline
from typing import Callable, List, Optional, Union
import os

# CUDA_VISIBLE_DEVICES=3 python generate_inspect_utils.py --output_dir samples_translated/altdiffusion --n_predictions 12 --model_id BAAI/AltDiffusion-m9 --split_batch 3

'''
def get_generate():
    prompt = input("Prompt:\n").strip().lower()
    with autocast("cuda"):
        image = pipe(prompt, guidance_scale=7.5, num_images_per_prompt=9).images
    for i, im in enumerate(image):
        print(f"done generating {prompt.replace(' ','')}_{i}.png")
        im.save(f"playground/{prompt.replace(' ','')}_{i}.png")
'''

# some of these are hacks. I believe german and indonesian require some inflections depending on the word
# english, spanish, and german additionally probably need an indefinite article
# unclear if this is the correct colloquial chinese
LANG_PROMPT_BITS = {
    'en' : "a photograph of $$$",
    'es' : "una fotografía de $$$",
    'de' : "ein Foto von $$$",
    'zh' : "$$$照片",
    'ja' : "$$$の写真",
    #'kr' : Language.KR,
    'he' : " צילום של$$$",
    'id' : "foto $$$"
}


prompt_options = {
    'en' : [
        'a photograph of $$$',
        'an image of $$$',
        'a photo of $$$',
        'a picture of $$$',
        'a picture of a $$$',
        'a picture of the $$$',
        'a picture of my $$$',
        'a picture of an $$$'
    ],
    'zh' : [
        "$$$照片",
        "$$$图片",
        "$$$的照片",
        "$$$的图片",
        "一张$$$照片",
        "一张$$$图片",
        "一张$$$的照片",
        "一张$$$的图片"
    ],
    'es' : [
        "un foto de $$$",
        "un foto de un $$$",
        "un foto de una $$$",
        "un foto de el $$$",
        "un foto de la $$$",
        "un foto de mi $$$",
        "un foto de tu $$$",
        "un foto de nuestra $$$"
    ]
}

# BAAI/AltDiffusion-m9
# stabilityai/stable-diffusion-2
@click.command()
@click.option('--output_dir', default='prompt_exps/')
@click.option('--n_predictions', default=9)
@click.option('--split_batch', default=1)
@click.option('--model_id', default="CompVis/stable-diffusion-v1-4")
@click.option('--input_csv', default="freq_lists_translated.csv")
@click.option('--language', default='en')
def main(output_dir, n_predictions, split_batch, model_id, input_csv, language):
    output_dir = output_dir + language
    assert n_predictions % split_batch == 0
    model_id = model_id
    device = "cuda"

    if model_id == "BAAI/AltDiffusion-m9":
        pipe = AltDiffusionPipeline.from_pretrained(model_id, use_auth_token=True)
    else:    
        pipe = StableDiffusionPipeline.from_pretrained(model_id, use_auth_token=True)
    pipe = pipe.to(device)

    os.makedirs(output_dir, exist_ok=True)

    prompts_base = open(f"frequencylist/{input_csv}", "r").readlines()
    index = prompts_base[0].strip().split(",")

    start_line = 0

    for line_idx in range(start_line, len(prompts_base)):
        line = prompts_base[line_idx]
        line_no = line_idx - 1
        line = line.strip().split(",")
        for prompt_template in prompt_options[language]:
            # build a prompt based on the above templates from the 
            word = line[index.index(language)]
            prompt = prompt_template.replace("$$$", word)
            print(f"generating {language}:{line[0]}, '{word}'")
            images = []
            for _ in range(split_batch):
                with autocast("cuda"):
                    images += pipe(prompt, guidance_scale=7.5, num_images_per_prompt=int(n_predictions / split_batch)).images
            for i, im in enumerate(images):
                fname = f"{line_no}-{language}-{line[0]}-{i}.png"
                print(f"saving image {fname}...")
                im.save(f"{output_dir}/{fname}")


if __name__ == "__main__":
    main()