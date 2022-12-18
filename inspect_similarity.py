import click
from PIL import Image
from transformers import CLIPProcessor, CLIPVisionModel
from collections import defaultdict
import torch.nn.functional as F
import random

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

# query cross-consistency
def compare_by_lang(results_dict, main_lang = "en", similarity_func = avg_cos_sim):
    langs = results_dict.keys()
    # evaluate pairwise similarity
    output_dict = {}
    for lang in langs:
        output_dict[lang] = similarity_func(results_dict[main_lang], results_dict[lang])
    return output_dict

# query self-sim by lang
def lang_self_sim(results_dict, similarity_func = avg_cos_sim):
    langs = results_dict.keys()
    # evaluate pairwise similarity
    output_dict = {}
    for lang in langs:
        output_dict[lang] = similarity_func(results_dict[lang], results_dict[lang])
    return output_dict

# results dict is a language-indexed dictionary of the gpu-placed word matrices
# the fingerprint dict is identical in structure but not tied to a word.

# produce a language-level index by precomputing the n=0 image for every word, language pair
def precompute_fingerprint_matrix(processor, model, prompts_base, selection_count, number_spec_range = 12):
    fingerprints = {}
    index = prompts_base[0].strip().split(",")
    if selection_count >= len(prompts_base) - 1 or selection_count == -1:
        use_lines = prompts_base[1:]
    else:
        use_lines = random.sample(prompts_base[1:], selection_count)
    # extract a fingerprint for each language
    for idx in range(len(index)):
        fnames = []
        for line_no, line in enumerate(use_lines):
            line = line.strip().split(",")
            # sample a number in the correct range
            img_idx = random.randrange(number_spec_range)
            fnames.append(f"{analysis_dir}/{line_no}-{index[idx]}-{line[0]}-{img_idx}.png")
        fingerprints[index[idx]] = get_image_embeddings(processor, model, fnames).cpu()
    return fingerprints


@click.command()
@click.option('--analysis_dir', default='samples_sd2')
@click.option('--num_samples', default=12)
@click.option('--fingerprint_selection_count', default=100)
def main(analysis_dir, num_samples, fingerprint_selection_count):
    device = "cuda"
    model = CLIPVisionModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model.to(device)
    
    prompts_base = open("frequencylist/freq_lists_translated.csv", "r").readlines()
    index = prompts_base[0].strip().split(",")

    out_lines_en = [prompts_base[0]]
    out_lines_self_sim = [prompts_base[0]]

    # collect the fingerprints for each language in this model
    fingerprints = precompute_fingerprint_matrix(processor, model, prompts_base, fingerprint_selection_count)
    # language fingerprint self-similarity (negative diversity)
    for lang in index:
        cuda_avg_cos_sim = lambda x,y: avg_cos_sim(x.to(device), y.to(device))
        self_sim = lang_self_sim(fingerprints, similarity_func= cuda_avg_cos_sim)
        print(f"DIVERSITY {lang}: {self_sim}")
    
    assert False

    for line_no, line in enumerate(prompts_base[1:]):
        results_dict = defaultdict(list)
        line = line.strip().split(",")
        for idx in range(len(index)):
            # build a prompt based on the above templates from the 
            fnames = [f"{analysis_dir}/{line_no}-{index[idx]}-{line[0]}-{i}.png" for i in range(num_samples)]
            image_embedding = get_image_embeddings(processor, model, fnames)
            results_dict[index[idx]] = image_embedding
        language_similarities = compare_by_lang(results_dict)
        self_sims = lang_self_sim(results_dict)
        print(line[0] + " " + str(language_similarities))
        out_lines_en.append(",".join([str(language_similarities[index]) for index in index]) + "\n")
        out_lines_self_sim.append(",".join([str(self_sims[index]) for index in index]) + "\n")
    
    with open(f"{analysis_dir}/results_en.csv", "w") as f:
        f.writelines(out_lines_en)

    with open(f"{analysis_dir}/results_self.csv", "w") as f:
        f.writelines(out_lines_self_sim)


if __name__ == "__main__":
    main()