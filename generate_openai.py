import click
from typing import Callable, List, Optional, Union
import os
import openai
import urllib.request
from tqdm import tqdm
import time
import math

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
@click.option('--n_predictions', default=10)
@click.option('--split_batch', default=1)
@click.option('--input_csv', default="freq_lists_translated.csv")
@click.option('--start_line', default=1)
def main(output_dir, n_predictions, split_batch, input_csv, start_line):
    assert n_predictions % split_batch == 0
    os.makedirs(output_dir, exist_ok=True)

    prompts_base = open(f"frequencylist/{input_csv}", "r").readlines()
    index = prompts_base[0].strip().split(",")
    for line_idx in tqdm(range(start_line, len(prompts_base))):
        line = prompts_base[line_idx]
        line_no = line_idx - 1
        line = line.strip().split(",")
        for idx in range(len(index)):
            # build a prompt based on the above templates from the 
            start_time = time.time()
            prompt = LANG_PROMPT_BITS[index[idx]].replace("$$$", line[idx])
            print(f"generating {index[idx]}:{line[0]}, '{line[idx]}'")
            for j in range(split_batch):
                try:
                    response = openai.Image.create(
                        prompt=prompt,
                        n=int(n_predictions / split_batch),
                        size="256x256"
                    )
                    for i in range(int(n_predictions / split_batch)):
                        fname = f"{line_no}-{index[idx]}-{line[0]}-{i+j*int(n_predictions / split_batch)}.png"
                        print(f"retrieving and saving image {fname}...")
                        urllib.request.urlretrieve(response['data'][i]['url'], f"{output_dir}/{fname}")
                    # dumbass rate limit to DALLE API
                except Exception as e:
                    fname = f"{line_no}-{index[idx]}-{line[0]}-failure.log"
                    print(f"Exception for request with prompt {prompt}")
                    with open(f"{output_dir}/{fname}", "w") as f:
                        f.write(str(e))
                remaining_time = math.ceil(60 - (time.time() - start_time))
                print(f"Sleeping {remaining_time} s to not make OpenAI's api mad at me...")
                time.sleep(remaining_time)


if __name__ == "__main__":
    main()