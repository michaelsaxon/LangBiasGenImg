import click
from PIL import Image
import os
from tqdm import tqdm
import shutil

@click.command()
@click.option('--file')
@click.option('--out_dim', default=75)
def main(file, out_dim):
    if ".png" in file:
        img = Image.open(file)
        img = img.resize((out_dim,out_dim),Image.ANTIALIAS)
        img.save(file)


if __name__ == "__main__":
    main()