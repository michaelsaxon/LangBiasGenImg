import click
import babelnet as bn
from babelnet.language import Language
from babelnet.pos import POS
from babelnet.data.source import BabelSenseSource
import json
from collections import defaultdict


VALID_SOURCES = [
    BabelSenseSource.WN,
    BabelSenseSource.OMWN,
    BabelSenseSource.IWN,
    BabelSenseSource.WNTR,
    BabelSenseSource.OMWN_ID,
    BabelSenseSource.OMWN_ZH,
    BabelSenseSource.OMWN_JA,
    BabelSenseSource.MCR_CA,
    BabelSenseSource.MCR_ES,
    BabelSenseSource.OMWN_KO,
    BabelSenseSource.MCR_PT,
    BabelSenseSource.OMWN_GAE,
    BabelSenseSource.OMWN_CWN,
    BabelSenseSource.WN2020,
    BabelSenseSource.OEWN
]


LANGS = {
    'en' : Language.EN,
    'es' : Language.ES,
    'de' : Language.DE,
    'zh' : Language.ZH,
    'ja' : Language.JA,
    'kr' : Language.KR,
    'he' : Language.HE,
    'id' : Language.ID
}


# lang code in, language frequency list out, each frequency list is keyed by words, 
def get_freq_list(lang):
    print(f"Loading language json {lang}...")
    with open(f"{lang}_2k.json", "r") as f:
        return json.loads(f.read())


def get_word_or_synsets(word, to_langs, from_lang):
    # first, test if this word has a wikipedia page title
    synset = bn.get_synset(bn.resources.WikipediaID(word, LANGS[from_lang], POS.NOUN))
    if synset is None:
        candidate_synsets = bn.get_synsets(
            word, 
            from_langs=[LANGS[from_lang]], 
            to_langs=[LANGS[to_lang] for to_lang in to_langs], 
            sources=VALID_SOURCES
        )
        # this produces a list of synsets for the word, will include garbage senses, use heuristics to pick
        # heuristic 1: is the name in one of the titles
        names = [str(word_synset).split("__")[1].split("#")[0].lower() for word_synset in candidate_synsets]
        if word.lower() in names:
            synset = candidate_synsets[names.index(word)]
        else:
            return candidate_synsets
    return synset

def get_aligned_row(synset, test_languages, freq_lists_dict):
    candidates = defaultdict(dict)
    quality = 0
    for elem in synset:
        word = str(elem).split(":")[-1]
        lang = str(elem.language).lower()
        if word in freq_lists_dict[lang]:
            candidates[lang][word] = freq_lists_dict[lang][word]
    for lang in test_languages:
        if candidates.get(lang, False) is False:
            return None, None
        quality += max(candidates[lang].values())
        candidates[lang] = max(candidates[lang], key=candidates[lang].get)
    return candidates, quality

def aligned_row_to_csv(source_name, aligned_row, test_languages):
    return ",".join([source_name] + list(map(lambda lang: aligned_row[lang], test_languages))) + "\n"

@click.command()
@click.option('--main_lang', default='en')
@click.option('--output_file', default='freq_lists.csv')
def main(main_lang, output_file):
    freq_lists_dict = {}
    languages = list(LANGS.keys())
    for lang in languages:
        freq_lists_dict[lang] = get_freq_list(lang)
    # we will save the final list as a csv
    test_languages = [lang for lang in languages if lang != main_lang]

    csv_rows = [",".join([main_lang] + test_languages) + "\n"]
    for word in freq_lists_dict[main_lang].keys():
        print(word)
        synset_or_list = get_word_or_synsets(word, test_languages, main_lang)
        if synset_or_list is None:
            # can't get anything for this word
            continue
        if type(synset_or_list) is list:
            # we need to determine which is the best
            best_quality = 0
            for synset in synset_or_list:
                aligned_row, quality = get_aligned_row(synset, test_languages, freq_lists_dict)
                if aligned_row is None:
                    continue
                if quality >= best_quality:
                    row = aligned_row
                    best_quality = quality
            if best_quality == 0:
                continue
        else:
            # it's a single synset. let's parse and get the crosslingual words
            aligned_row, _ = get_aligned_row(synset_or_list, test_languages, freq_lists_dict)
            if aligned_row is None:
                continue
            row = aligned_row
        # row should only ever be an aligned row
        csv_row = aligned_row_to_csv(word, row, test_languages)
        print(csv_row)
        csv_rows.append(csv_row)

    with open(output_file) as f:
        f.writelines(csv_rows)


if __name__ == "__main__":
    main()