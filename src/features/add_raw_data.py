from .win_rate import add_winrate_gap, add_winrate_last_10_to_csv
from .elo_calculation import add_elo_to_csv
from .calculate_surface_elo import add_surface_elo_to_csv
from .head2head import add_h2h_to_csv
from .days_rest import add_days_rest_to_csv

def add_raw_data_to_csv(df):
    df = add_elo_to_csv(df)
    df = add_surface_elo_to_csv(df)
    df = add_winrate_last_10_to_csv(df)
    df = add_winrate_gap(df)
    df = add_h2h_to_csv(df)
    df = add_days_rest_to_csv(df)
    
    return df