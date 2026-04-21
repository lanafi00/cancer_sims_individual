from pathlib import Path
import pandas as pd
from tqdm import tqdm
import argparse
import numpy as np

def parse_data(sim_dir, output_file):
    params_file = sim_dir / "params.csv"
    params_df = pd.read_csv(params_file)
    fraction_extinct = []
    mut_rates = []
    doses = []
    mean_final_cycles = []
    for _, params_df_row in tqdm(params_df.iterrows(), total=len(params_df)):
        mut_rate = params_df_row.base_mut_rate
        dose = params_df_row.dose_drug_1_mono 
        param_id = int(params_df_row.param_id)
        #fitness_cost = params_df_row.fitness_cost
        rep_final_Ns = []
        rep_final_cycles = []
        replicate_files = list(sim_dir.glob(f"log_{param_id}_*.csv"))
        for rep_file in replicate_files:
            file_df = pd.read_csv(rep_file)
            file_df.fillna(0, inplace=True)
            final_N = file_df.iloc[-1].N
            final_cycle = file_df.iloc[-1].cycle
            rep_final_Ns.append(final_N)
            rep_final_cycles.append(final_cycle)
        fraction_extinct.append(np.mean([N == 0 for N in rep_final_Ns]))
        mean_final_cycles.append(np.mean(rep_final_cycles))
        mut_rates.append(mut_rate)
        doses.append(dose)
        #second_strike_lags.append(second_strike_lag)

    results_df = pd.DataFrame({
        "base_mut_rate": mut_rates,
        "dose_drug_1_mono": doses,
        "fraction_extinct": fraction_extinct
    })
    results_df = results_df.sort_values(by=["base_mut_rate", "dose_drug_1_mono"])
    results_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    argpaser = argparse.ArgumentParser()
    argpaser.add_argument("--sims_dir", type=str, help="Path to the directory containing the simulation output files", required=True)
    argpaser.add_argument("--output", type=str, help="Path to the outputfile", required=True)

    args = argpaser.parse_args()
    sims_dir = Path(args.sims_dir)
    output_file = Path(args.output)
    parse_data(Path(args.sims_dir), Path(args.output))  # this line was missing