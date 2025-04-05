#INTEREST RATE SHOCK STRESS TEST CODE

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Load and clean data
file_path = r"C:\Users\zivoj\Documents\JPM_ERM_Analysis\JPMfinal.csv"
df = pd.read_csv(file_path)

#Convert all numeric columns to float (in billions), except Net Yield (percentage)
for col in df.columns[1:]:
    if col != "Net yield":
        df[col] = df[col].replace({",": ""}, regex=True).astype(float) / 1e9
    else:
        df[col] = df[col].str.replace("%", "").astype(float)  # Remove % and convert to float

#Define shock factors
shock_factors = {
    "Net Interest Income": 0.85,  # -15% mean
    "Net yield": 0.90,            # -10% mean
    "CET1 Capital": 0.95          # -5% mean
}

#Simulation parameters
n_simulations = 10000
n_years = 5
np.random.seed(42)

#Time axes
years_hist = df["Year"].values
years_proj = np.arange(2025, 2030)

#Containers
baseline_medians = {}
stress_medians = {}

#Run simulations for each metric
for metric, shock in shock_factors.items():
    historical = df[metric].values
    mean = np.mean(historical)
    std = np.std(historical)

    #Baseline simulation
    sims_baseline = np.random.normal(loc=mean, scale=std, size=(n_simulations, n_years))
    sims_baseline = np.maximum(sims_baseline, 0)
    baseline_medians[metric] = np.median(sims_baseline, axis=0)

    #Stress simulation
    shocked_mean = mean * shock
    sims_stress = np.random.normal(loc=shocked_mean, scale=std, size=(n_simulations, n_years))
    sims_stress = np.maximum(sims_stress, 0)
    stress_medians[metric] = np.median(sims_stress, axis=0)

#Plot results
for metric in shock_factors:
    hist = df[metric].values
    baseline = baseline_medians[metric]
    stress = stress_medians[metric]

    plt.figure(figsize=(10, 5))
    plt.plot([2024] + list(years_proj), [hist[-1]] + list(baseline),
         linestyle="--", color="blue", linewidth=2, marker='o', label="Baseline Projection")

    plt.plot([2024] + list(years_proj), [hist[-1]] + list(stress),
         linestyle="--", color="red", linewidth=2, marker='o', label="Interest Rate Shock")

    plt.plot(years_hist, hist, color="black", linewidth=2.5, marker='o', label="Historical")

    plt.axvline(x=2024, linestyle="--", color="gray")
    plt.title(f"{metric} – Baseline vs Interest Rate Shock (2020–2029)")
    plt.xlabel("Year")
    plt.xticks(np.arange(2020, 2030, 1))  # Show every year from 2020 to 2029
    plt.ylabel("Value (in Billions USD)" if metric != "Net yield" else "Net Yield (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("C:/Users/zivoj/Downloads/plots/{}_interest_rate_shock.png".format(metric.replace(" ", "_")), dpi=300)
    plt.show()

    #Create DataFrame for Quantified Output
    years = np.arange(2025, 2030)
    df_summary = pd.DataFrame({
        "Year": years,
        "Baseline": np.round(baseline, 2),
        "Stress": np.round(stress, 2),
        "Δ Amount": np.round(stress - baseline, 2),
        "Δ %": np.round((stress - baseline) / baseline * 100, 2)
    })

    # Print Table
    print(f"\n Quantified Impact of Interest Rate Shock – {metric}")
    print(df_summary.to_string(index=False))