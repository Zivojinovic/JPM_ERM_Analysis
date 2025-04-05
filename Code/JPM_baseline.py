import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Load and clean the data
file_path = r"C:\Users\zivoj\Documents\JPM_ERM_Analysis\JPMfinal.csv"
df = pd.read_csv(file_path)

#Clean all relevant columns
for col in df.columns[1:]:
    if col != "Net yield":
        df[col] = df[col].replace({",": ""}, regex=True).astype(float) / 1e9  # Convert to billions

#Define metrics and settings
metrics = [
    "Total Assets", "Total Liabilities", "Equity",
    "Loans(Net of Allowance for Loan Losses)", "Deposits", "Net Interest Income",
    "CET1 Capital", "Tier 1 Capital", "Total Capital"
]

n_simulations = 10000
n_years = 5  # 2025–2029
np.random.seed(42)

#Monte Carlo simulation
median_paths = {}
percentile_5 = {}
percentile_25 = {}
percentile_75 = {}
percentile_95 = {}
all_simulations = {}

for metric in metrics:
    historical = df[metric].values
    mean = np.mean(historical)
    std = np.std(historical)

    sims = np.random.normal(loc=mean, scale=std, size=(n_simulations, n_years))
    sims = np.maximum(sims, 0)

    all_simulations[metric] = sims
    median_paths[metric] = np.median(sims, axis=0)
    percentile_5[metric] = np.percentile(sims, 5, axis=0)
    percentile_25[metric] = np.percentile(sims, 25, axis=0)
    percentile_75[metric] = np.percentile(sims, 75, axis=0)
    percentile_95[metric] = np.percentile(sims, 95, axis=0)

#Define years
years_hist = df["Year"].values
years_proj = np.arange(2025, 2030)
full_years = np.concatenate([years_hist, years_proj])

#Display table of median projections
median_table = pd.DataFrame(median_paths, index=[f"Year {year}" for year in years_proj])
print("\nBaseline Monte Carlo Median Projections (in Billions USD):\n")
print(median_table.round(2))

#Plot each metric
for metric in metrics:
    hist_values = df[metric].values
    median_vals = median_paths[metric]
    p5 = percentile_5[metric]
    p25 = percentile_25[metric]
    p75 = percentile_75[metric]
    p95 = percentile_95[metric]

    # Extend projection intervals to start at 2024
    p5_full = np.insert(p5, 0, hist_values[-1])
    p95_full = np.insert(p95, 0, hist_values[-1])
    p25_full = np.insert(p25, 0, hist_values[-1])
    p75_full = np.insert(p75, 0, hist_values[-1])
    future_years_extended = np.insert(years_proj, 0, 2024)

    #Plot
    plt.figure(figsize=(10, 5))
    plt.plot(years_hist, hist_values, color="black", linewidth=2.5,marker="o", label="Historical")
    plt.plot(future_years_extended, [hist_values[-1]] + list(median_vals),
             linestyle="--", color="black", linewidth=2,marker="o", label="Median Projection")
    plt.fill_between(future_years_extended, p5_full, p95_full,
                     color="mistyrose", alpha=0.6, label="5%–95% Projection Interval")
    plt.fill_between(future_years_extended, p25_full, p75_full,
                     color="moccasin", alpha=0.6, label="25%–75% Projection Interval")
    plt.axvline(x=2024, linestyle="--", color="gray")
    plt.title(f"{metric} – Historical and Projected (2020–2029)")
    plt.xlabel("Year")
    plt.xticks(np.arange(2020, 2030, 1))  # Show every year from 2020 to 2029
    plt.ylabel("Value (in Billions USD)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"plots/{metric.replace(' ', '_')}_projection.png", dpi=300)
    plt.show()

    