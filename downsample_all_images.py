import click
from PIL import Image
import os
from tqdm import tqdm
import shutil

@click.command()
@click.option('--meta_folder_dir', default="/Users/mssaxon/samples_translated")
@click.option('--out_folder_dir', default="/Users/mssaxon/samples_translated_downsampled")
def main(meta_folder_dir, out_folder_dir):
    for folder in os.listdir(meta_folder_dir):
        print(folder)
        os.makedirs(f"{out_folder_dir}/{folder}")
        for file in tqdm(os.listdir(f"{meta_folder_dir}/{folder}")):
            if ".png" in file:
                img = Image.open(f"{meta_folder_dir}/{folder}/{file}")
                img = img.resize((100,100),Image.ANTIALIAS)
                img.save(f"{out_folder_dir}/{folder}/{file}")
            else:
                shutil.copyfile(f"{meta_folder_dir}/{folder}/{file}", f"{out_folder_dir}/{folder}/{file}")


if __name__ == "__main__":
    main()