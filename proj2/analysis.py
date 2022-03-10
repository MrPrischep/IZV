#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os

# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

""" Ukol 1:
načíst soubor nehod, který byl vytvořen z vašich dat. Neznámé integerové hodnoty byly mapovány na -1.

Úkoly:
- vytvořte sloupec date, který bude ve formátu data (berte v potaz pouze datum, tj sloupec p2a)
- vhodné sloupce zmenšete pomocí kategorických datových typů. Měli byste se dostat po 0.5 GB. Neměňte však na kategorický typ region (špatně by se vám pracovalo s figure-level funkcemi)
- implementujte funkci, která vypíše kompletní (hlubkou) velikost všech sloupců v DataFrame v paměti:
orig_size=X MB
new_size=X MB

Poznámka: zobrazujte na 1 desetinné místo (.1f) a počítejte, že 1 MB = 1e6 B. 
"""

def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    df = pd.read_pickle(filename)
    origSize = df.memory_usage(deep=True).sum() /1048576
    df['p2a'] = df['p2a'].astype('datetime64')
    df.rename(columns={'p2a': 'date'}, inplace=True)

    category = ['p36', 'weekday(p2a)', 'p6', 'p7', 'p8', 'p9', 'p11',
                'p12', 'p13a', 'p13b', 'p13c', 'p15', 'p16', 'p17', 
                'p19', 'p20', 'p22', 'p23', 'p24', 'p27', 'p28', 'p34', 
                'p35', 'p39', 'p44', 'p45a', 'p47', 'p48a', 'p49', 'p50a',
                'p50b', 'p51', 'p52', 'p53', 'p55a', 'p57', 'p5a', 
                'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 't']

    df[category] = df[category].astype('category')
    if verbose:
        newSize = df.memory_usage(deep=True).sum() /1048576
        print("orig_size={:.1f} MB".format(origSize))
        print("new_size={:.1f} MB".format(newSize))
    return df

# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic

def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    df.reset_index(inplace=True)
    title = ['žádná z uvedených', 'Dvoupruhová', 'Třípruhová', 'čtyřpruhová', 'vícepruhová', 'rychlostní komunikace']
    regions = ["JHM", "MSK", "OLK", "ZLK"]
    df['Pocet'] = pd.to_numeric(df['p21'])
    df.set_index('region', inplace=True)
    data = df.loc[regions, ['p21', 'Pocet']]
    data = (data.groupby(['region', 'p21'])['Pocet'].agg('count')).reset_index()
    grouped = data.groupby('p21')    
    dataframes = [grouped.get_group(x) for x in grouped.groups] #list of DataFrames
    
    for x in grouped.groups:
        dataframes[x].set_index('region', inplace=True)
    dataframes[3] = dataframes[3] + dataframes[4]
    del dataframes[4]

    for x in grouped.groups:
        dataframes[x] = dataframes[x].reset_index()
        if x == 5:
            break;

    fig, axes = plt.subplots(2, 3, figsize=(12, 10))
    count = 0

    for i in range(2):
        for j in range(3):
            sns.barplot(ax=axes[i, j], x='region', y='Pocet', data=dataframes[count])
            axes[i, j].set(ylabel='', xlabel='Kraj')
            axes[i, j].set_title(title[count])
            count = count + 1
        axes[i, 0].set(ylabel='Počet nehod')

    plt.tight_layout()

    if fig_location:
        (dirname, filename) = os.path.split(fig_location)
		#create folder if doesnt exist
        if dirname:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        plt.savefig(fig_location)

    if show_figure == True:
        plt.show()

# Ukol3: zavinění zvěří
def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    df.reset_index(inplace=True)
    regions = ["JHM", "MSK", "OLK", "ZLK"]
    df.set_index('region', inplace=True)
    df = df[df.p58 == 5]
    data = df.loc[regions, ['p58', 'p10', 'date']]
    data['p10'] = data['p10'].astype(str)
    data.p10 = data.p10.str.replace('0', 'jiné')
    data.p10 = data.p10.str.replace('1', 'řidičem')
    data.p10 = data.p10.str.replace('2', 'řidičem')
    data.p10 = data.p10.str.replace('3', 'jiné')
    data.p10 = data.p10.str.replace('4', 'zvěří')
    data.p10 = data.p10.str.replace('5', 'jiné')
    data = data.reset_index()
    data = data[(data['date'] < '2021-01-01')]
    data.date = data.date.dt.month
    data = (data.groupby(['region', 'p10', 'date'])['p58'].agg('count').reset_index())

    sns.set_theme(style="ticks")
    sns.set_style("darkgrid")
    g = sns.catplot(x="date", y='p58', col="region", col_wrap=2,
                    hue='p10', data=data, legend=False, col_order=regions, 
                    kind="bar", height=4.2, aspect=1, saturation=1)
    g.set(yscale="log").set_titles("{col_name}", fontweight="bold", color='#404040', size=15)
    g.set_axis_labels("Měsíc", "Počet nehod", fontweight="bold", color='#404040')
    plt.legend(loc='upper right', title='Zavineni')
    plt.tight_layout()

    if fig_location:
        (dirname, filename) = os.path.split(fig_location)
		#create folder if doesnt exist
        if dirname:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        plt.savefig(fig_location)

    if show_figure == True:
        plt.show()

# Ukol 4: Povětrnostní podmínky
def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    df.reset_index(inplace=True)
    regions = ["JHM", "MSK", "OLK", "ZLK"]
    df.set_index('region', inplace=True)
    df['pocet'] = pd.to_numeric(df['p18'])
    df = df[df.p18 != 0]
    data = df.loc[regions, ['p18', 'date', 'pocet']].reset_index()
    data['p18'] = data['p18'].astype(str)
    data = data[(data['date'] < '2021-01-01')]
    data.p18 = data.p18.str.replace('1', 'neztížené')
    data.p18 = data.p18.str.replace('2', 'mlha')
    data.p18 = data.p18.str.replace('3', 'na počátku deště')
    data.p18 = data.p18.str.replace('4', 'déšť')
    data.p18 = data.p18.str.replace('5', 'sněžení')
    data.p18 = data.p18.str.replace('6', 'náledí')
    data.p18 = data.p18.str.replace('7', 'nárazový vítr')
    
    data['pocet'] = data['pocet'].astype(str)
    data.pocet = data.pocet.str.replace('2', '1')
    data.pocet = data.pocet.str.replace('3', '1')
    data.pocet = data.pocet.str.replace('4', '1')
    data.pocet = data.pocet.str.replace('5', '1')
    data.pocet = data.pocet.str.replace('6', '1')
    data.pocet = data.pocet.str.replace('7', '1')
    data['pocet'] = data['pocet'].astype(int)

    table = pd.pivot_table(data=data, index=['region', 'date'], columns='p18', values='pocet',aggfunc=np.sum)
    table = table.reset_index().set_index('date')
    table = table.groupby(['region']).resample("M").sum()
    table = table.stack().reset_index()
    table.rename(columns={0: 'Počet nehod', 'p18': 'Podminky'}, inplace=True)

    sns.set_style("darkgrid")
    g = sns.relplot(x='date', y='Počet nehod', col='region', col_wrap=2,
                    hue='Podminky', data=table,
                    col_order=regions,
                    height=4.2, aspect=1, kind='line')
    g.set_titles("{col_name}", fontweight="bold", color='#404040', size=15)
    g.set_axis_labels("", "Počet nehod", fontweight="bold", color='#404040')
    plt.tight_layout()
    leg = g._legend
    leg.set_bbox_to_anchor([0.99, 0.37])
    plt.setp(leg.get_title(), fontsize=15, color='#404040', fontweight="bold")

    if fig_location:
        (dirname, filename) = os.path.split(fig_location)
		#create folder if doesnt exist
        if dirname:
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        plt.savefig(fig_location)

    if show_figure == True:
        plt.show()

if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz") # tento soubor si stahnete sami, při testování pro hodnocení bude existovat
    plot_roadtype(df, fig_location="01_roadtype.png", show_figure=True)
    #plot_animals(df, "02_animals.png", True)
    #plot_conditions(df, "03_conditions.png", True)
