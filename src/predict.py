from pathlib import Path

import pandas as pd

from simulate import run_entire_tournament
from train import training


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "combined.csv"

ao2026_r1_ordered_full_names = [
    ["Carlos Alcaraz", "Adam Walton"],
    ["Yannick Hanfmann", "Zachary Svajda"],
    ["Michael Zheng", "Sebastian Korda"],
    ["Tristan Schoolkate", "Corentin Moutet"],
    ["Tommy Paul", "Aleksandar Kovacevic"],
    ["Thiago Agustin Tirante", "Aleksandar Vukic"],
    ["Nicolai Budkov Kjaer", "Reilly Opelka"],
    ["Filip Misolic", "Alejandro Davidovich Fokina"],

    ["Alexander Bublik", "Jenson Brooksby"],
    ["Camilo Ugo Carabelli", "Marton Fucsovics"],
    ["Miomir Kecmanovic", "Tomas Martin Etcheverry"],
    ["Arthur Fery", "Flavio Cobolli"],
    ["Frances Tiafoe", "Jason Kubler"],
    ["Patrick Kypson", "Francisco Comesana"],
    ["Mariano Navone", "Hamad Medjedovic"],
    ["Mackenzie McDonald", "Alex de Minaur"],

    ["Alexander Zverev", "Gabriel Diallo"],
    ["Alexei Popyrin", "Alexandre Muller"],
    ["Emilio Nava", "Kyrian Jacquet"],
    ["Benjamin Bonzi", "Cameron Norrie"],
    ["Francisco Cerundolo", "Zhizhen Zhang"],
    ["Liam Draxl", "Damir Dzumhur"],
    ["Alexander Blockx", "Jaime Faria"],
    ["Matteo Arnaldi", "Andrey Rublev"],

    ["Daniil Medvedev", "Jesper de Jong"],
    ["Quentin Halys", "Alejandro Tabilo"],
    ["Kamil Majchrzak", "Jacob Fearnley"],
    ["Fabian Marozsan", "Arthur Rinderknech"],
    ["Learner Tien", "Marcos Giron"],
    ["Elias Ymer", "Alexander Shevchenko"],
    ["Juan Manuel Cerundolo", "Jordan Thompson"],
    ["Nuno Borges", "Felix Auger-Aliassime"],

    ["Lorenzo Musetti", "Raphael Collignon"],
    ["Lorenzo Sonego", "Carlos Taberner"],
    ["Grigor Dimitrov", "Tomas Machac"],
    ["Shintaro Mochizuki", "Stefanos Tsitsipas"],
    ["Jiri Lehecka", "Arthur Gea"],
    ["Laslo Djere", "Stan Wawrinka"],
    ["Vit Kopriva", "Jan-Lennard Struff"],
    ["Valentin Royer", "Taylor Fritz"],

    ["Jakub Mensik", "Pablo Carreno Busta"],
    ["Rei Sakamoto", "Rafael Jodar"],
    ["Hubert Hurkacz", "Zizou Bergs"],
    ["Ethan Quinn", "Tallon Griekspoor"],
    ["Brandon Nakashima", "Botic van de Zandschulp"],
    ["Juncheng Shang", "Roberto Bautista Agut"],
    ["Terence Atmane", "Francesco Maestrelli"],
    ["Pedro Martinez", "Novak Djokovic"],

    ["Ben Shelton", "Ugo Humbert"],
    ["Dane Sweeny", "Gael Monfils"],
    ["Adrian Mannarino", "Rinky Hijikata"],
    ["Martin Damm", "Valentin Vacherot"],
    ["Denis Shapovalov", "Bu Yunchaokete"],
    ["Daniel Altmaier", "Marin Cilic"],
    ["Jaume Munar", "Dalibor Svrcina"],
    ["Mattia Bellucci", "Casper Ruud"],

    ["Karen Khachanov", "Alex Michelsen"],
    ["Christopher O'Connell", "Nishesh Basavareddy"],
    ["Giovanni Mpetshi Perricard", "Sebastian Baez"],
    ["Cristian Garin", "Luciano Darderi"],
    ["Joao Fonseca", "Ethan Spizzirri"],
    ["Luca Nardi", "Yibing Wu"],
    ["James Duckworth", "Dino Prizmic"],
    ["Hugo Gaston", "Jannik Sinner"]
]

def main():
    df = pd.read_csv(DATA_PATH)
    bracket = ao2026_r1_ordered_full_names
    model, scaler, features = training(df)
    run_entire_tournament(
        bracket,
        model,
        scaler,
        df,
        features,
        n=10000,
        debug=True,
        debug_runs=1,
    )


if __name__ == "__main__":
    main()
