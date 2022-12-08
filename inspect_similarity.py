import click
from PIL import Image
from transformers import CLIPProcessor, CLIPVisionModel
from collections import defaultdict
import torch.nn.functional as F

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

"samples-11-30-7_5-flg1/0-en-dog-0.png"

def get_image_embeddings(processor, model, fnames):
    images = [Image.open(fname, "r") for fname in fnames]
    inputs = processor(images=images, return_tensors="pt")
    inputs.to(model.device)
    outputs = model(**inputs)
    return outputs.pooler_output.squeeze()

def avg_cos_sim(vec_list_1, vec_list_2):
    # this is O(n^2) lmao
    sims_sum = 0
    sims_num = vec_list_1.shape[0] * vec_list_2.shape[0]
    for i in range(vec_list_2.shape[0]):
        sims_sum += float(F.cosine_similarity(vec_list_1, vec_list_2[i].unsqueeze(0)).sum())
    return sims_sum / sims_num

def compare_by_lang(results_dict, main_lang = "en", similarity_func = avg_cos_sim):
    langs = results_dict.keys()
    # evaluate pairwise similarity
    output_dict = {}
    for lang in langs:
        output_dict[lang] = similarity_func(results_dict[main_lang], results_dict[lang])
    return output_dict

@click.command()
@click.option('--analysis_dir', default='samples_sd2')
@click.option('--num_samples', default=12)
def main(analysis_dir, num_samples):
    device = "cuda"
    model = CLIPVisionModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.to(device)
    
    prompts_base = open("frequencylist/freq_lists_gold.csv", "r").readlines()
    out_lines = [prompts_base[0]]

    index = prompts_base[0].strip().split(",")
    for line_no, line in enumerate(prompts_base[1:]):
        results_dict = defaultdict(list)
        line = line.strip().split(",")
        for idx in range(len(index)):
            # build a prompt based on the above templates from the 
            fnames = [f"{analysis_dir}/{line_no}-{index[idx]}-{line[0]}-{i}.png" for i in range(num_samples)]
            image_embedding = get_image_embeddings(processor, model, fnames)
            results_dict[index[idx]] = image_embedding
        language_similarities = compare_by_lang(results_dict)
        print(line[0] + " " + str(language_similarities))
        out_lines.append(",".join([str(language_similarities[index]) for index in index]) + "\n")
    
    with open(f"{analysis_dir}/results.csv", "w") as f:
        f.writelines(out_lines)


if __name__ == "__main__":
    main()