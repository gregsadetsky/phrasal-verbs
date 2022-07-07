import matplotlib
import csv
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import subprocess
from pathlib import Path

CURR_DIR = Path(__file__).parent.resolve()
DATA_PATH = CURR_DIR / 'data.csv'
PNG_PATH_OUT = CURR_DIR / 'output.png'

all_rows = []
with open(DATA_PATH) as f:
  for row in csv.DictReader(f):
    v, p = row['match'].split()
    # our sketchy way of splitting/joining array elements on bigquery
    # means that we have some stray '_' elements in the data. skip them
    if v == '_' or p == '_':
      continue
    all_rows.append({
      'pre': v,
      'suff': p,
      'count': int(row['c'])
    })

df = pd.DataFrame(all_rows)

# taken from
# https://github.com/colinmorris/pejorative-compounds/blob/master/heatmap.py
df = df.pivot('pre', 'suff', 'count')
df.fillna(0, inplace=True)

# per reddit request
# df.to_csv(CURR_DIR / 'data-pivoted.csv', float_format='%.0f', na_rep=0)

# these words did not seem verby-enough to my personal taste.
# this is an editorial choice that I moderately stand behind.
df.drop(labels=['piece', 'pay', 'sort', 'even', 'amount', 'chance', 'front', 'happen', 'line', 'man', 'name', 'number', 'part', 'plan', 'point', 'post', 'power', 'reason', 'result', 'shit', 'stuff', 'team', 'time', 'well', 'while',], axis=0, inplace=True)
df.drop(labels=['aside', 'along', 'among', 'aback', 'open', 'together', 'it', 'to', 'past', 'round', 'above', 'across', 'forward', 'way'], axis=1, inplace=True)

# selects a small subset of all verbs
# a different interesting subset happens when using .mean instead
df = df[df.max(axis=1) > 10500000]

# reset index, otherwise indices appear in descending alpha order
df = df.iloc[::-1]

FONT_SIZE = 8

fig = plt.figure(figsize=(6, 5))
ax = fig.add_subplot(1, 1, 1)

plt.text(x=0.5, y=0.94, s="Phrasal Verbs on Reddit", fontsize=16, ha="center", transform=fig.transFigure)
plt.text(x=0.1, y=0.875, s="""
Frequency of phrasal verbs (e.g., "find out", "get over") in Reddit comments, 2005-2019. Viz by /u/gregsadetsky, version 0.2
Made using the public dataset on BigQuery. List of phrasal verbs from Wiktionary
Thanks to /u/halfeatenscone for the inspiring "Rude Compounds" and to J. for the data processing help
""".strip(), fontsize=5, ha="left", transform=fig.transFigure)
plt.subplots_adjust(top=0.75)

plot = plt.pcolor(df, norm=colors.LogNorm(clip=True))
# make it square, thanks to seaborn for the tip
ax.set_aspect("equal")


# based on feedback from reddit users and a suggestion by /u/halfeatenscone
for i in range(1, df.shape[1]):
  ax.axvline(i, color='white', lw=0.8)
for i in range(1, df.shape[0]):
  ax.axhline(i, color='white', lw=0.8)


# from https://stackoverflow.com/a/7039989
mkfunc = lambda x, pos: '%1.0fM' % (x * 1e-6) if x >= 1e6 else '%1.0fK' % (x * 1e-3) if x >= 1e3 else '%1.0f' % x
mkformatter = matplotlib.ticker.FuncFormatter(mkfunc)

cbar = fig.colorbar(plot, location='bottom', format=mkformatter, shrink=0.31, pad=0.04)
cbar.set_label('# of mentions', size=7)
cbar.ax.tick_params(labelsize=6)


plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns, rotation=90, ha='center')

plt.tick_params(axis="x", bottom=False, pad=0, labelsize=FONT_SIZE, labeltop=True, labelbottom=False)
plt.tick_params(axis="y", left=False, pad=0, labelsize=FONT_SIZE)

plt.tight_layout()


# plt.show()

plt.savefig(PNG_PATH_OUT, dpi=200)
subprocess.run(['open', PNG_PATH_OUT])
