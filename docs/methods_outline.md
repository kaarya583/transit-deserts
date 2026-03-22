# Methods Outline: Transit Corridor Optimization

## 1. Data Sources

### 1.1 Transit Network
- **GTFS**: LA Metro bus and rail schedules
- **OSM**: OpenStreetMap walking network
- **Format**: Stops as GeoDataFrames, routes as polylines

### 1.2 Employment Data
- **LEHD/LODES**: Workplace Area Characteristics (WAC)
- **Aggregation**: Jobs per census tract
- **Assumption**: Jobs located at tract centroids

### 1.3 Population & Demographics
- **Census ACS**: Population, income, car ownership
- **Tract-level**: All variables at census tract resolution
- **Weight vector**: w_i = f(population, income, need) for optimization

## 2. Accessibility Metric (Frozen Definition)

### 2.1 Cumulative Opportunity Measure

\[
A_i = \sum_j J_j \cdot \mathbf{1}(T_{ij} \leq \tau)
\]

Where:
- \(A_i\) = accessibility for tract \(i\)
- \(J_j\) = jobs in tract \(j\)
- \(T_{ij}\) = travel time from tract \(i\) to tract \(j\)
- \(\tau\) = time threshold (30 or 45 minutes)
- \(\mathbf{1}(\cdot)\) = indicator function (binary cutoff)

### 2.2 Per-Capita Normalization

\[
A_i^{per-capita} = \frac{A_i}{P_i} \times 1000
\]

Where \(P_i\) = population in tract \(i\)

**Units**: Jobs per 1,000 residents

### 2.3 Key Properties
- **Binary reachability**: No distance decay within threshold
- **Additive**: Jobs are counted, not weighted
- **Interpretable**: Direct count of opportunities

## 3. Counterfactual Design

### 3.1 Synthetic Corridor Definition

Each corridor \(\ell\) has:
- **Geometry**: Polyline (start → end)
- **Stop spacing**: Distance between stops (e.g., 400m)
- **Speed**: Average transit speed (e.g., 20 km/h)
- **Headway**: Service frequency (not used in accessibility, but documented)

### 3.2 Network Augmentation

For each corridor:
1. Generate synthetic stops along polyline
2. Connect stops to walking network
3. Update travel time matrix
4. Compute counterfactual accessibility \(A_i^{cf}(\ell)\)

### 3.3 Impact Measurement

\[
\Delta A_i(\ell) = A_i^{cf}(\ell) - A_i^{baseline}
\]

**Output**: Matrix of tract × corridor accessibility gains

## 4. Optimization

### 4.1 Objective Function

\[
\text{Score}(\ell) = \sum_i w_i \cdot \Delta A_i(\ell)
\]

Where:
- \(w_i\) = weight for tract \(i\) (population × need indicator)
- \(\Delta A_i(\ell)\) = accessibility gain from corridor \(\ell\)

### 4.2 Weight Definition

\[
w_i = P_i \cdot \text{need}_i
\]

Where \(\text{need}_i\) could be:
- Inverse income (low income = high need)
- Binary desert indicator
- Population density

### 4.3 Ranking

1. Compute scores for all corridors
2. Rank by Score(ℓ)
3. Compare weighted vs unweighted rankings
4. Select top-k corridors

## 5. Demand Estimation (Upper Bound)

### 5.1 Demand Proxy

\[
D_i(\ell) = P_i \cdot \frac{\Delta A_i(\ell)}{A_i^{baseline} + \epsilon}
\]

Where:
- \(D_i(\ell)\) = additional demand from tract \(i\) for corridor \(\ell\)
- \(\epsilon\) = small constant to avoid division by zero
- **Interpretation**: Proportional to accessibility gain, scaled by baseline

### 5.2 Aggregation

\[
D(\ell) = \sum_i D_i(\ell)
\]

**Units**: Additional trips per day (upper bound)

### 5.3 Limitations

- **Upper bound only**: Assumes all accessibility gains translate to usage
- **No mode choice**: Doesn't account for existing transit or car usage
- **No behavioral response**: Fixed population and job locations

## 6. Equity Analysis

### 6.1 Distributional Effects

- **By income decile**: Compute gains for each income group
- **By desert status**: Compare gains in transit deserts vs well-connected areas
- **Lorenz curves**: Distribution of gains across population

### 6.2 Metrics

- **Gini coefficient**: Inequality in accessibility gains
- **Mean vs median**: Skewness of distribution
- **Bottom quartile gains**: Focus on most disadvantaged

## 7. Sensitivity Analysis

### 7.1 Parameters to Vary

1. **Time threshold**: τ = 30 vs 45 minutes
2. **Stop spacing**: 200m vs 400m vs 800m
3. **Weight definition**: Different need indicators
4. **Corridor generation**: Different candidate sets

### 7.2 Robustness Checks

- **Ranking stability**: Do top corridors change?
- **Score magnitudes**: How sensitive are scores?
- **Demand estimates**: How do they vary?

## 8. Limitations

### 8.1 Data Limitations
- Tract centroids approximate locations (systematic bias)
- Single time point (8 AM weekday)
- Schedule-based routing (no delays)

### 8.2 Methodological Limitations
- Binary reachability (no distance decay)
- Fixed job locations (no relocation)
- Upper-bound demand (not actual ridership)
- Synthetic corridors (not constrained by existing infrastructure)

### 8.3 Scope Limitations
- No land-use feedback
- No operational constraints
- No political feasibility
- No cost-benefit analysis

## 9. Validation & Sanity Checks

### 9.1 Baseline Validation
- Accessibility distribution matches literature
- Transit deserts align with known areas
- Travel times are reasonable

### 9.2 Counterfactual Validation
- Gains are non-negative (or explainable if negative)
- Corridor impacts are spatially coherent
- No computational errors

### 9.3 Optimization Validation
- Scores are interpretable
- Rankings are stable
- Top corridors are plausible

### 9.4 Demand Validation
- Estimates are reasonable (compare to existing ridership)
- Upper bounds are clearly labeled
- Sensitivity analysis shows robustness

