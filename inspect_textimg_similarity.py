import click
from PIL import Image, ImageFile
from transformers import CLIPProcessor, CLIPModel
from collections import defaultdict
import torch.nn.functional as F
import random
import os

ImageFile.LOAD_TRUNCATED_IMAGES = True

# if image exists, open it. Else, generate 50x50 black
def open_image_if_exists(fname):
    if os.path.isfile(fname):
        return Image.open(fname, "r")
    else:
        return Image.new('RGB', (50, 50), (0, 0, 0))

def get_concept_images_sim(processor, model, concept, fnames):
    images = [open_image_if_exists(fname) for fname in fnames]
    inputs = processor(text=[concept], images=images, return_tensors="pt")
    inputs.to(model.device)
    outputs = model(**inputs)
    probs = outputs.logits_per_image
    #print(probs)
    return probs.mean().squeeze()


@click.command()
@click.option('--analysis_dir', default='samples_sd2')
@click.option('--num_samples', default=12)
@click.option('--fingerprint_selection_count', default=100)
@click.option('--main_language', default="en")
def main(analysis_dir, num_samples, fingerprint_selection_count, main_language):
    device = "cuda"
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.to(device)
    
    prompts_base = open("frequencylist/freq_lists_translated.csv", "r").readlines()
    index = prompts_base[0].strip().split(",")

    out_lines_main_sim = [prompts_base[0]]
    
    for line_no, line in enumerate(prompts_base[1:]):
        results_dict = defaultdict(list)
        line = line.strip().split(",")
        scores = []
        
        word = line[index.index(main_language)]

        # collect this languages embeddings
        for language in range(len(index)):
            # build a prompt based on the above templates from the 
            fnames = [f"{analysis_dir}/{line_no}-{index[language]}-{line[0]}-{i}.png" for i in range(num_samples)]
            images_score = get_concept_images_sim(processor, model, word, fnames)
            scores.append(images_score)
        
        '''
        # zero out if there's an error log for each word
        for language in index:
            if os.path.isfile(f"{analysis_dir}/{line_no}-{language}-{line[0]}-failure.log"):
                language_similarities[language] = "---"
                self_sims[language] = "---"
                inverse_specificity[language] = "---"
        '''

        print(word)

        outstr = ",".join([str(val.detach().cpu().numpy()) for val in scores]) + "\n"

        print(outstr)


        out_lines_main_sim.append(outstr)
        
        
    with open(f"{analysis_dir}/word_results_{main_language}.csv", "w") as f:
        f.writelines(out_lines_main_sim)



if __name__ == "__main__":
    main()