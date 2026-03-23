# Methods

**Area:** Los Angeles County census tracts.

**Accessibility:** Nearest GTFS stop to tract centroid; simplified walk–transit–walk time to job tracts; jobs reachable in **≤ 30 min**. **Transit desert** = bottom **20%** of tract accessibility.

**Metro graph:** GTFS rail modes (0–2), edges = track segments + **transfers**. Edge length = great-circle meters. **Conductance** \(c_{ij} = 1/(d_{ij}+1)\). **Weighted Laplacian** \(L = D - A\). **Pseudoinverse** \(L^+\) via NumPy `pinv`.

**Effective resistance** between stations \(a,b\):  
\(R_{\mathrm{eff}}(a,b) = L^+_{aa} + L^+_{bb} - 2L^+_{ab}\).  
Higher \(R_{\mathrm{eff}}\) means the pair is **more weakly connected** on today’s network (fewer parallel paths).

**Station demand:** Within **800 m**, \(\sqrt{\text{pop}\times\text{jobs}}\). Mean tract accessibility near each station is used only for **roughness** \(f^\top L f\) in the summary.

**Corridor impact score (simple):**  
\(\textbf{impact} = \text{demand}_a \times \text{demand}_b \times R_{\mathrm{eff}}(a,b)\).

- **Demand** = activity at both endpoints (product of the two station demand weights).  
- **\(R_{\mathrm{eff}}\)** = graph statistic from the Laplacian (same for every pair).  

Buffer tract stats (mean accessibility, % deserts) are still saved in the CSV for context but **not** multiplied into the score.

**Outputs:** `corridor_priorities.csv`; figures `01`–`07` (including desert overlay + results table for top corridors).

Planning analysis, not engineering design or ridership forecasting.
