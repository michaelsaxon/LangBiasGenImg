#import plotly.express as px
import pandas as pd
#pd.options.plotting.backend = "plotly"
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
from collections import defaultdict

from plot_util import bivariate

def r2(x, y):
    return stats.pearsonr(x, y)[0] ** 2


# 'samples_cv2',

modelnames = ['samples_demega', 'samples_demini', 'samples_sd1-1',  'samples_sd1-2',  'samples_sd1-4', 'samples_sd2', 'samples_cv2', 'samples_dalle2', 'altdiffusion']

#results_en/zh.csv
#results_self.csv
#results_specific.csv


def label_map(key):
    return key



def merge_set(dict_of_dfs):
    dfs = []
    for key in dict_of_dfs.keys():
        df = dict_of_dfs[key]
        df = df.replace('---',-1)
        s = df.select_dtypes(include='object').columns
        s = [ss for ss in s if ss != "concept"]
        df[s] = df[s].astype("float")
        df = df.assign(model=key)   
        dfs.append(df)
    df = pd.concat(dfs)
    return df

def load_csv_add_concepts(fname, concepts_axis):
    df = pd.read_csv(fname)
    df['concept'] = concepts_axis
    return df


def load_all_csvs(folder = "/Users/mssaxon/results", merge=True):
    results_cross = {}
    results_self = {}
    results_spec = {}
    results_langdiv = {}
    concepts = pd.read_csv("/Users/mssaxon/freq_lists_translated.csv")["en"]
    for modelname in modelnames:
        results_self[modelname] = load_csv_add_concepts(f"{folder}/{modelname}_results_self.csv", concepts)
        results_spec[modelname] = load_csv_add_concepts(f"{folder}/{modelname}_results_specific.csv", concepts)
        results_langdiv[modelname] = pd.read_csv(f"{folder}/{modelname}_language_diversity.csv")
        if "cv2" in modelname:
            lang = "zh"
        else:
            lang = "en"
        results_cross[modelname] = load_csv_add_concepts(f"{folder}/{modelname}_results_{lang}.csv", concepts)
    if merge:
        return merge_set(results_cross), merge_set(results_self), merge_set(results_spec), merge_set(results_langdiv)
    return results_cross, results_self, results_spec, results_langdiv



languages = ["en", "es", "de", "zh", "ja", "he", "id"]


results_cross, results_self, results_spec, results_langdiv = load_all_csvs()

heights = []
bins = []

"""
fig, ax = plt.subplots()

for i, language in enumerate(languages):
    this_heights, this_bins = np.histogram(df[language], bins=50, range=(0,1))
    heights.append(this_heights)
    bins.append(this_bins)
    ax.bar(this_bins[:-1], this_heights)

fig.show()
"""



#rcm = results_cross.melt().rename(columns={"value":"rcm", "variable" : "language"})
#rcs = results_self.melt().rename(columns={"value":"rcs", "variable" : "language"})

#df = rcm.join(rcs["rcs"])

#sns.histplot(df, x='rcm', y="rcs", hue='variable', multiple='layer', element="poly")

#print(results_cross["en"])


def hists_by_language(df, ylim = 120, value_name = "Value", title = "", fname = "default.pdf"):
    print(len(list(df.index)))

    fig, axs = plt.subplots(7,1)

    colors = ["blue", "green", "black", "gold", "red", "lightblue", "purple"]
    fontcolors = ["white", "white", "white", "black", "white", "black", "white"]

    for i, language in enumerate(languages):
        #sns.histplot(df, x="rcs", hue='language', multiple='layer', element="poly")
        axs[i].set(ylim=(0,ylim), xlim=(0,1), yticklabels=[])
        if i != len(languages) - 1:
            axs[i].set(xticklabels=[], xlabel = None, ylabel=None)
        sns.histplot(df[language], element="step", ax = axs[i], bins=50, binrange=(0,1), color=colors[i])
        axs[i].set(xlabel='',ylabel='')
        axs[i].text(0.05, ylim/2, language.upper(), fontsize=10, weight='bold', color=fontcolors[i],
            bbox={'facecolor': colors[i], 'alpha': 0.5, 'pad': 5}, fontname="monospace")
    fig.supxlabel(value_name)
    fig.supylabel("Language")
    if title != "":
        top = 0.917
        fig.suptitle(title + " Histograms")
    else:
        top = 0.962
    fig.subplots_adjust(left=0.086, top=top, right=0.933)
    #plt.show() 
    plt.savefig(f"/Users/mssaxon/cococrola_plots/{fname}")
    plt.clf()


def filter_out_of_range(df, ax1, ax2, low = 0, up = 1):
    df = df[df[ax1] >= low]
    df = df[df[ax2] >= low] 
    df = df[df[ax1] <= up]
    df = df[df[ax2] <= up]
    return df


def scatter_two_ax(df, ax1 = "ja", ax2 = "zh"):
    fig, axs = plt.subplots(1,1)
    #axs.set(ylim=(0,1), xlim=(0,1))
    r = r2(df[ax1], df[ax2])
    g = sns.scatterplot(df, x=ax1, y=ax2, ax=axs)
    plt.show()


def list_sorted_words(df, ax, ascending=False, n=20):
    df = df.sort_values(ax, ascending = ascending)
    return df["concept"][0:n]

# [results_cross["model"] == "samples_sd2"]


def average_key(df, column):
    rules = {}
    for language in languages:
        rules[language] = "mean"
    other_keys = [key for key in df.keys() if key != column and key not in language]
    for key in other_keys:
        rules[key] = lambda x: x.sample(1)
    df = df.groupby(column).agg(rules)
    df[column] = df.index
    return df


def model_filter(df, models):
    return df[df["model"] == models]

def model_neg_filter(df, models):
    return df[df["model"] != models]


#print(results_cross)
#print(list_sorted_words(average_key(results_cross, "concept"), "ja"))
#print(list_sorted_words(model_filter(results_cross, "samples_sd1-1"), "ja", ascending = True))

#scatter_two_ax(model_filter(results_cross, "samples_sd1-1"))

"""hists_by_language(model_filter(results_cross, 'samples_demini'), 50, "Correctness (EN-lang Cross-Consistency)", "DALL-E Mini", fname="hist_cov_demini.pdf")
hists_by_language(model_filter(results_cross, 'samples_sd2'), 50, "Correctness (EN-lang Cross-Consistency)", "Stable Diffusion 2", fname="hist_cov_sd2.pdf")
hists_by_language(model_filter(results_cross, 'samples_dalle2'), 50, "Correctness (EN-lang Cross-Consistency)", "DALL-E 2", fname="hist_cov_de2.pdf")
hists_by_language(model_filter(results_cross, 'samples_cv2'), 50, "Correctness (ZH-lang Cross-Consistency)", "CogView2", fname="hist_cov_cv2.pdf")
hists_by_language(model_neg_filter(results_spec, 'lmao'), 120, "Inverse Distinctiveness", "All Models", fname="hist_spec_all.pdf")
"""

hists_by_language(model_filter(results_cross, 'altdiffusion'), 50, "Correctness (EN-lang Cross-Consistency)", "AltDiffusion", fname="hist_cov_altdiff.pdf")
hists_by_language(model_filter(results_cross, 'samples_demini'), 50, "Correctness (EN-lang Cross-Consistency)", "DALL-E Mini", fname="hist_cov_demini.pdf")
hists_by_language(model_filter(results_cross, 'samples_sd2'), 50, "Correctness (EN-lang Cross-Consistency)", "Stable Diffusion 2", fname="hist_cov_sd2.pdf")
hists_by_language(model_filter(results_cross, 'samples_dalle2'), 50, "Correctness (EN-lang Cross-Consistency)", "DALL-E 2", fname="hist_cov_de2.pdf")
hists_by_language(model_filter(results_cross, 'samples_cv2'), 50, "Correctness (ZH-lang Cross-Consistency)", "CogView2", fname="hist_cov_cv2.pdf")



def bivariate_wrapped(df, lang1, lang2, var_template = "$\\bf{###}$-EN Cross. Consistency", title="", filt=""):
    df = filter_out_of_range(df, lang1, lang2)
    bivariate(df[lang1], df[lang2], xscale=(0,1), yscale=(0,1), xlabel=var_template.replace("###",lang1.upper()), ylabel=var_template.replace("###",lang2.upper()), title=title, fname=f"{lang1}_{lang2}{filt}.pdf")

#bivariate_wrapped(results_cross, "en", "he")

#bivariate_wrapped(results_cross, "ja", "zh")

"""
bivariate_wrapped(model_neg_filter(results_cross, "samples_cv2"), "es", "ja")
bivariate_wrapped(model_neg_filter(results_cross, "samples_cv2"), "es", "de")
bivariate_wrapped(model_neg_filter(results_cross, "samples_cv2"), "es", "id")
bivariate_wrapped(model_neg_filter(results_cross, "samples_cv2"), "zh", "ja")
bivariate_wrapped(model_neg_filter(results_cross, "samples_cv2"), "en", "he")

bivariate_wrapped(model_filter(results_cross, "samples_cv2"), "es", "ja", filt="zhtrain")
bivariate_wrapped(model_filter(results_cross, "samples_cv2"), "es", "de", filt="zhtrain")
bivariate_wrapped(model_filter(results_cross, "samples_cv2"), "es", "id", filt="zhtrain")
bivariate_wrapped(model_filter(results_cross, "samples_cv2"), "zh", "ja", filt="zhtrain")
bivariate_wrapped(model_filter(results_cross, "samples_cv2"), "en", "he", filt="zhtrain")

"""

"""
top_words = defaultdict(lambda: 0)
for language in languages:
    for model in ['samples_demega', 'samples_demini', 'samples_sd1-1',  'samples_sd1-2',  'samples_sd1-4', 'samples_sd2', 'samples_dalle2']:
        top_word_this = list_sorted_words(model_filter(results_cross, model), language, n = 20)
        for word in top_word_this:
            top_words[word] += 1
df = pd.DataFrame.from_dict({'word' : [key for key in top_words.keys()], 'count' : [top_words[key] for key in top_words.keys()]}).sort_values(by="count", ascending=False)

sns.barplot(df[df["count"] > 10], x="word", y="count")
plt.tick_params(rotation=60)
plt.title("Most well-covered concepts relative to English across Languages")
plt.xlabel("")
plt.ylabel("Num. occurences")
plt.show()
"""
#plt.plot(fig)
#plt.show()



#print(list_sorted_words(average_key(results_cross, "concept"), "ja", n=5))


#print(list_sorted_words(model_filter(results_cross, "samples_sd1-4"), "zh", n=7))
#print(list_sorted_words(model_filter(results_cross, "samples_sd1-4"), "en", n=90))

