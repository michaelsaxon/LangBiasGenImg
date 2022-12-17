import click
import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from typing import Callable, List, Optional, Union
import os
import openai
import urllib.request

openai.api_key = os.getenv("OPENAI_API_KEY")

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

# stabilityai/stable-diffusion-2
@click.command()
@click.option('--output_dir', default='samples_dalle2')
@click.option('--n_predictions', default=12)
@click.option('--split_batch', default=2)
@click.option('--model_id', default="CompVis/stable-diffusion-v1-4")
@click.option('--input_csv', default="freq_lists_translated.csv")
@click.option('--start_line', default=1)
def main(output_dir, n_predictions, split_batch, model_id, input_csv, start_line):
    assert n_predictions % split_batch == 0
    model_id = model_id
    device = "cuda"

    pipe = StableDiffusionPipeline.from_pretrained(model_id, use_auth_token=True)
    pipe = pipe.to(device)

    os.makedirs(output_dir, exist_ok=True)

    prompts_base = open(f"frequencylist/{input_csv}", "r").readlines()
    index = prompts_base[0].strip().split(",")
    for line_idx in range(start_line, len(prompts_base)):
        line = prompts_base[line_idx]
        line_no = line_idx - 1
        line = line.strip().split(",")
        for idx in range(len(index)):
            # build a prompt based on the above templates from the 
            prompt = LANG_PROMPT_BITS[index[idx]].replace("$$$", line[idx])
            print(f"generating {index[idx]}:{line[0]}, '{line[idx]}'")
            for j in range(split_batch):
                response = openai.Image.create(
                    prompt=prompt,
                    n=int(n_predictions / split_batch),
                    size="256x256"
                )
                for i in range(int(n_predictions / split_batch)):
                    fname = f"{line_no}-{index[idx]}-{line[0]}-{i+j*int(n_predictions / split_batch)}.png"
                    print(f"retrieving and saving image {fname}...")
                    urllib.request.urlretrieve(response['data'][i]['url'], f"{output_dir}/{fname}")


if __name__ == "__main__":
    main()