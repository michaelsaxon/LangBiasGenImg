import click
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize

def get_nouns(sentence):
    pos_seq = pos_tag(word_tokenize(sentence.strip().lower())) 
    nouns = []
    for word, pos in pos_seq:
        if pos == "NN":
            nouns.append(word)
    return nouns

def sentence_nouns_in_list(sentence, noun_list, acceptable_num_out = 1):
    num_out = 0
    for noun in get_nouns(sentence):
        if noun not in noun_list:
            num_out += 1
        if num_out > acceptable_num_out:
            return False
    return True
    
langs_list = ['en', 'es', 'de', 'zh', 'ja']

@click.command()
@click.option('--input_csv', '-i', default='freq_lists_translated.csv')
def main(input_csv):
    prompts_base = open(input_csv, "r").readlines()
    lang_idx = {lang : i for i, lang in enumerate(prompts_base[0].strip().split(","))}
    print(lang_idx)
    lang_sentences = {}
    for lang in langs_list:
        lang_sentences[lang] = open(f"test_1kcaptions_{lang}.txt", "r").readlines()
    num_sent = 1000
    out_sents = {lang : [] for lang in prompts_base[0].strip().split(",")}
    # first remove all sents that contain nouns outside the set
    en_nouns = [line[lang_idx["en"]] for line in prompts_base[1:]]
    for i, sentence in enumerate(lang_sentences["en"]):
        if sentence_nouns_in_list(sentence, en_nouns):
            #print(sentence)
            print(i)
            out_sents["en"].append(sentence)
    print(len(out_sents["en"]))


if __name__ == "__main__":
    main()