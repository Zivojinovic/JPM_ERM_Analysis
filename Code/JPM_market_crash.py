#MARKET CRASH STRESS TEST CODE
market_crash_shocks = {
    "Equity": 0.75,         # –25%
    "Total Capital": 0.70,  # –30%
    "CET1 Capital": 0.90    # –10%
}

n_simulations = 10000
n_years = 5
np.random.seed(42)

years_hist = df["Year"].values
years_proj = np.arange(2025, 2030)

#Containers
baseline_medians_mc = {}
stress_medians_mc = {}

for metric, shock in market_crash_shocks.items():
    historical = df[metric].values
    mean = np.mean(historical)
    std = np.std(historical)

    #Baseline simulation
    sims_base = np.random.normal(loc=mean, scale=std, size=(n_simulations, n_years))
    sims_base = np.maximum(sims_base, 0)
    baseline_medians_mc[metric] = np.median(sims_base, axis=0)

    #Stress simulation
    sims_stress = np.random.normal(loc=mean * shock, scale=std, size=(n_simulations, n_years))
    sims_stress = np.maximum(sims_stress, 0)
    stress_medians_mc[metric] = np.median(sims_stress, axis=0)

    #Plot
    plt.figure(figsize=(10, 5))
    plt.plot(years_hist, historical, color="black", linewidth=2.5, marker='o', label="Historical")
    plt.plot([2024] + list(years_proj), [historical[-1]] + list(baseline_medians_mc[metric]),
             linestyle="--", color="blue", linewidth=2, marker='o', label="Baseline Projection")
    plt.plot([2024] + list(years_proj), [historical[-1]] + list(stress_medians_mc[metric]),
             linestyle="--", color="red", linewidth=2, marker='o', label="Market Crash Shock")

    plt.axvline(x=2024, linestyle="--", color="gray")
    plt.xticks(np.arange(2020, 2030, 1))
    plt.title(f"{metric} – Baseline vs Market Crash (2020–2029)")
    plt.xlabel("Year")
    plt.ylabel("Value (in Billions USD)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("C:/Users/zivoj/Downloads/plots/{}_market_crash_shock.png".format(metric.replace(" ", "_")), dpi=300)
    plt.show()

    #Quantified table
    years = np.arange(2025, 2030)
    baseline = baseline_medians_mc[metric]
    stress = stress_medians_mc[metric]

    df_summary = pd.DataFrame({
        "Year": years,
        "Baseline": np.round(baseline, 2),
        "Stress": np.round(stress, 2),
        "Δ Amount": np.round(stress - baseline, 2),
        "Δ %": np.round((stress - baseline) / baseline * 100, 2)
    })

    print(f"\n Quantified Impact of Market Crash Shock – {metric}")
    print(df_summary.to_string(index=False))
