# Transit Deserts Project: Comprehensive Analysis & Recommendations

## Executive Summary

This document provides:
1. **Detailed analysis** of each notebook with all assumptions, intricacies, and intuition behind every decision
2. **Recommendations** for next steps to create a simple, presentable end project

---

## Part 1: Detailed Notebook-by-Notebook Analysis

### Notebook 00: Setup

**Purpose**: Environment verification and folder structure initialization

**Key Decisions & Assumptions**:
- **Working Directory**: Uses absolute path resolution (`Path().resolve()`) to ensure consistent file paths across different execution contexts. This prevents path-related errors when notebooks are run from different locations.
- **Folder Structure**: Creates `data_raw/` and `outputs/` directories if they don't exist. This assumes a clean separation between input data (raw, unprocessed) and output data (processed, analysis-ready).
- **Why This Matters**: The project follows a linear workflow where each notebook depends on outputs from previous notebooks. Having a consistent folder structure ensures data flows correctly between notebooks.

**Intuition**: This is a "sanity check" notebook - it verifies the environment is set up correctly before any real work begins. It's simple but critical for catching configuration issues early.

---

### Notebook 01: Data Ingestion

**Purpose**: Download, load, and clean all source data (GTFS, Census, LEHD, OSM)

#### Step-by-Step Analysis:

**1. GTFS Data Loading**
- **Decision**: Uses `gtfs_kit` library to parse GTFS zip files
- **Assumption**: GTFS files are in standard format (GTFS spec v2.0+)
- **Intuition**: GTFS is a standardized format, so using a library handles edge cases (timezone conversions, calendar exceptions, etc.) better than manual parsing
- **Why Separate Bus and Rail**: LA Metro provides separate GTFS feeds for bus and rail. Combining them allows for multimodal routing (walk → bus → rail → walk)
- **Key Data Extracted**:
  - `stops.txt`: Physical locations of transit stops
  - `routes.txt`: Transit lines (bus routes, rail lines)
  - `trips.txt`: Individual service trips
  - `stop_times.txt`: Schedule information (when buses/trains arrive at stops)
  - `shapes.txt`: Geographic paths of routes

**2. Census Data Download**
- **Decision**: Uses Census API (not manual download)
- **Assumption**: API key is valid and rate limits won't be exceeded
- **Intuition**: API is more reliable than manual downloads and ensures we get the latest data
- **Variables Selected**:
  - `B01003_001E` (Total Population): Needed to calculate per-capita accessibility
  - `B19013_001E` (Median Household Income): Key demographic for equity analysis
  - `B25046_001E` (Vehicles Available): Proxy for car ownership (inverse of transit need)
  - `B08126_001E` (Transit Commute by Poverty): Direct measure of transit usage
  - `B08301_001E` (Commute Mode Split): Overall transportation patterns
- **Geographic Scope**: Los Angeles County (State FIPS: 06, County FIPS: 037)
- **Why 5-Year ACS**: More reliable estimates for small geographic areas (tracts) than 1-year estimates

**3. LEHD (LODES) Jobs Data**
- **Decision**: Downloads Workplace Area Characteristics (WAC) file
- **Assumption**: Jobs are distributed uniformly within census tracts (we use tract centroids as job locations)
- **Intuition**: LEHD provides job counts by census tract, which is the finest geographic resolution available. Using tract centroids is a reasonable approximation for accessibility calculations.
- **Why This Matters**: We need to know WHERE jobs are located to calculate "jobs reachable within X minutes"
- **Data Format**: CSV with GEOID (census tract identifier) and job counts by sector

**4. Census Tract Shapefiles**
- **Decision**: Downloads TIGER/Line shapefiles from Census Bureau
- **Assumption**: Tract boundaries are stable (they change every 10 years with the decennial census)
- **Intuition**: Shapefiles provide the geographic boundaries needed to map results and calculate spatial relationships
- **Why 2025 Tracts**: Using the most recent tract boundaries ensures alignment with current ACS data

**5. OSMnx Walking Network**
- **Decision**: Downloads OpenStreetMap road network for walking paths
- **Assumption**: OSM data is reasonably complete and accurate for LA County
- **Intuition**: Transit accessibility requires walking to/from stops. OSM provides pedestrian-accessible paths (sidewalks, crosswalks, etc.)
- **Bounding Box**: Uses LA County extent to download only relevant network data
- **Why Not Use GTFS Walking Times**: GTFS doesn't include walking paths between stops and destinations - we need the full road network

**6. Data Cleaning & Merging**
- **Decision**: Merges ACS, LEHD, and tract shapefiles on GEOID
- **Assumption**: GEOID format is consistent across all sources (11-digit: SSCCCTTTTTT where SS=state, CCC=county, TTTTTT=tract)
- **Intuition**: GEOID is the standard identifier for census tracts, so it's the natural join key
- **Missing Data Handling**: 
  - Census uses `-666666666` as a missing data code (suppressed for privacy)
  - Replaces with `np.nan` to distinguish from real zeros
  - This is critical: treating suppressed data as zero would bias results

**7. Output Files**
- **Decision**: Saves merged data as both GeoJSON (for mapping) and Parquet (for efficient storage)
- **Intuition**: 
  - GeoJSON: Human-readable, works with mapping tools
  - Parquet: Efficient binary format, preserves data types, faster to load
- **Why Both**: Different tools need different formats

**Key Outputs**:
- `la_tracts_with_acs_jobs.geojson`: Tracts with demographics and job counts
- `metro_stops_all.geojson`: All transit stops (bus + rail)
- `jobs_by_tract_la.csv`: Job counts by tract

---

### Notebook 02: Network and Travel Times

**Purpose**: Build multimodal transportation network and compute travel times from origins (tract centroids) to destinations (job locations)

#### Step-by-Step Analysis:

**1. Network Construction Strategy**
- **Decision**: Builds separate networks for walking and transit, then combines them
- **Intuition**: Walking and transit have different properties:
  - Walking: Continuous network, can go anywhere (subject to road network)
  - Transit: Discrete network, only along routes at scheduled times
- **Why Not Build Combined Network First**: Separating allows us to:
  - Handle walking and transit differently (walking is always available, transit has schedules)
  - Debug issues more easily
  - Reuse walking network for multiple transit scenarios

**2. Walking Network (OSMnx)**
- **Decision**: Downloads road network, filters for walkable edges
- **Assumption**: All roads in OSM are walkable (in reality, some highways aren't, but OSMnx handles this)
- **Walking Speed**: Typically assumes 3-4 mph (1.3-1.8 m/s). This is a standard assumption in transportation planning.
- **Why Project to UTM**: 
  - Geographic coordinates (lat/lon) don't preserve distance
  - UTM Zone 11N (EPSG:32611) is appropriate for LA County
  - NetworkX shortest path algorithms need accurate distances
- **Network Simplification**: OSMnx can simplify the network (remove nodes with only 2 connections) to reduce computation time

**3. Transit Network (GTFS)**
- **Decision**: Converts GTFS schedule data into a time-expanded network
- **Intuition**: GTFS is schedule-based, but routing needs a graph structure
- **Time-Expanded Network**: Creates nodes for each (stop, time) pair. This allows routing that respects schedules.
- **Example**: If a bus arrives at Stop A at 8:00 AM and leaves at 8:02 AM, we create:
  - Node: (Stop A, 8:00) - arrival
  - Node: (Stop A, 8:02) - departure
  - Edge: (Stop A, 8:00) → (Stop A, 8:02) with weight = 2 minutes (wait time)
- **Transfer Handling**: 
  - Identifies transfer points (stops where multiple routes meet)
  - Adds transfer edges with transfer time (typically 2-5 minutes)
  - This is critical: without transfers, you can't switch from bus to rail

**4. Multimodal Network Combination**
- **Decision**: Connects walking network to transit network at transit stops
- **Intuition**: To use transit, you must:
  1. Walk from origin to nearest transit stop
  2. Take transit
  3. Walk from transit stop to destination
- **Connection Strategy**:
  - For each transit stop, find nearest node in walking network
  - Add bidirectional edges between stop and walking network node
  - Edge weight = walking time (distance / walking speed)
- **Why Bidirectional**: You can walk TO a stop (to board) and FROM a stop (after alighting)

**5. Origin-Destination Pairs**
- **Decision**: Uses tract centroids as origins, job tract centroids as destinations
- **Assumption**: 
  - People live/work at tract centroids (obviously not true, but reasonable approximation)
  - All jobs in a tract are at the centroid (same approximation)
- **Intuition**: 
  - Using actual addresses would be more accurate but computationally expensive
  - Tract centroids are a standard approach in accessibility studies
  - For large-scale analysis, the approximation error is acceptable
- **Why Not Use Actual Addresses**: 
  - Privacy: Individual addresses aren't publicly available
  - Computation: Would require millions of origin-destination pairs
  - Data availability: We only have job counts by tract, not exact locations

**6. Travel Time Calculation**
- **Decision**: Uses shortest path algorithm (Dijkstra's) on multimodal network
- **Assumption**: People take the fastest route (minimize travel time)
- **Intuition**: This is a standard assumption in transportation planning - "rational choice" model
- **Time-Dependent Routing**: 
  - GTFS includes schedules, so travel time depends on departure time
  - Common approach: Use a "representative" time (e.g., 8:00 AM weekday)
  - Alternative: Calculate for multiple times and average (more accurate but slower)
- **Why Not Use Real-Time Data**: 
  - Real-time data is ephemeral (changes constantly)
  - We want to measure "typical" accessibility, not moment-in-time
  - Real-time APIs are rate-limited and unreliable

**7. Sampling Strategy**
- **Decision**: Computes travel times for a sample of origin-destination pairs
- **Intuition**: Full O-D matrix would be:
  - ~2,500 origins × ~2,500 destinations = 6.25 million pairs
  - Computationally expensive (hours/days)
- **Sampling Approach**: 
  - Random sample of origins
  - For each origin, calculate to all destinations (or sample destinations)
  - This gives a representative sample while keeping computation manageable
- **Why This Works**: 
  - We're interested in average/typical accessibility, not exact values for every tract
  - Statistical sampling is valid if sample is large enough
  - Can always compute full matrix later if needed

**8. Output Format**
- **Decision**: Saves as both CSV (human-readable) and Parquet (efficient)
- **Data Structure**: 
  - Columns: `origin_id`, `destination_id`, `travel_time_minutes`
  - This is a "long format" - one row per O-D pair
  - Alternative "wide format" (matrix) is more compact but harder to work with

**Key Outputs**:
- `origins_tract_centroids.geojson`: Origin points
- `destinations_job_tracts.geojson`: Destination points
- `travel_times_sample.parquet`: Travel time matrix

**Critical Assumptions Summary**:
1. People take fastest route (Dijkstra's algorithm)
2. Walking speed is constant (doesn't account for hills, weather, etc.)
3. Transit schedules are reliable (no delays)
4. Tract centroids represent actual locations
5. Representative time (8 AM) represents typical accessibility
6. Sample is representative of full population

---

### Notebook 03: Accessibility Metrics

**Purpose**: Calculate accessibility indices to identify transit deserts

#### Step-by-Step Analysis:

**1. Accessibility Definition**
- **Decision**: Uses "cumulative opportunity" measure: count of jobs reachable within time threshold
- **Intuition**: This is the simplest and most interpretable accessibility measure
- **Alternative Measures**:
  - **Gravity model**: Weights jobs by travel time (closer jobs count more)
  - **2SFCA (Two-Step Floating Catchment Area)**: Accounts for competition (how many people can reach the same jobs)
  - **Time-weighted**: Jobs at 5 minutes count more than jobs at 25 minutes
- **Why Cumulative Opportunity**: 
  - Easy to understand: "How many jobs can I reach in 30 minutes?"
  - Standard in transit planning literature
  - Doesn't require parameter tuning (gravity model needs decay parameter)

**2. Time Thresholds**
- **Decision**: Calculates for 15, 30, 45, and 60 minutes
- **Intuition**: 
  - 15 min: Short trips (local access)
  - 30 min: Standard commute (most common)
  - 45 min: Longer commute (acceptable for many)
  - 60 min: Maximum acceptable (beyond this is very poor access)
- **Why Multiple Thresholds**: Different people have different time budgets. Showing multiple thresholds provides a more complete picture.

**3. Job Counting**
- **Decision**: For each origin, counts destinations with `travel_time <= threshold`
- **Assumption**: All jobs in a destination tract are reachable if travel time is below threshold
- **Intuition**: This is a binary measure - either a job is reachable or not. More sophisticated measures would weight by travel time.
- **Why Not Weight by Travel Time**: 
  - Simpler to interpret
  - Avoids parameter selection (how much to weight?)
  - Standard in literature

**4. Per-Capita Normalization**
- **Decision**: Divides jobs reachable by population, multiplies by 1,000
- **Intuition**: 
  - Raw job counts favor large tracts (more people = more jobs reachable)
  - Per-capita makes tracts comparable regardless of size
  - Multiplying by 1,000 gives "jobs per 1,000 residents" (easier to interpret than decimals)
- **Formula**: `accessibility = (jobs_reachable / population) × 1,000`
- **Why This Matters**: A tract with 10,000 people and 1 million jobs reachable has the same accessibility as a tract with 1,000 people and 100,000 jobs reachable. This is fair.

**5. Zero/Small Population Handling**
- **Decision**: Replaces zero population with NaN, then fills with 0 accessibility
- **Intuition**: 
  - Can't divide by zero
  - Tracts with zero population (commercial/industrial) don't have residents, so accessibility is undefined
  - Setting to 0 is reasonable (no residents = no accessibility for residents)
- **Small Population Threshold**: Replaces populations < 10 with NaN
- **Why**: Very small populations can create extreme values (1 person, 1 million jobs = 1 billion jobs/1k residents). This is a data quality issue, not a real pattern.

**6. Infinite Value Handling**
- **Decision**: Replaces `np.inf` and `-np.inf` with NaN, then fills with 0
- **Intuition**: Infinite values come from division by very small numbers (numerical precision issues)
- **Why Fill with 0**: If accessibility is infinite, it's likely a data error. Setting to 0 is conservative (assumes poor access).

**7. Outlier Capping**
- **Decision**: Caps extreme values at 99th percentile for visualization
- **Intuition**: 
  - Extreme outliers (e.g., 1 million jobs/1k residents) are likely data errors or special cases (e.g., downtown tracts with very few residents)
  - Capping prevents outliers from dominating visualizations
  - 99th percentile preserves most of the data while removing extreme values
- **Why Not Remove Outliers**: They might be real (downtown tracts). Capping preserves them but limits their visual impact.

**8. Transit Desert Identification**
- **Decision**: Defines transit deserts as tracts with:
  - Low accessibility (bottom quartile)
  - High need (low income OR high population density)
- **Intuition**: 
  - Low accessibility alone isn't enough - a wealthy suburb with poor transit might not be a "desert" (residents have cars)
  - High need = people who likely need transit (low income = can't afford cars, high density = many people affected)
- **Why Quartiles**: 
  - Relative measure (not absolute threshold)
  - Adapts to the distribution of the data
  - Standard approach in equity analysis

**9. Visualization Strategy**
- **Decision**: Creates multiple visualizations:
  - Histograms: Distribution of accessibility
  - Choropleth maps: Spatial patterns
  - Box plots: Comparison of transit deserts vs non-deserts
  - Interactive maps: For exploration
- **Intuition**: Different visualizations reveal different patterns:
  - Histograms: Overall distribution
  - Maps: Geographic clustering
  - Box plots: Statistical differences
  - Interactive: Allows exploration

**10. Data Cleaning for Visualization**
- **Decision**: Creates separate "clean" versions of data for each visualization
- **Intuition**: 
  - Different visualizations need different data treatments
  - Histograms: Can show full distribution (including outliers)
  - Maps: Need capped values for color scale
  - Statistical tests: Need clean data (no infinities)
- **Why Not One Clean Dataset**: Flexibility - we can experiment with different cleaning strategies

**Key Outputs**:
- `accessibility_metrics.csv`: Accessibility scores by tract
- `accessibility_metrics.geojson`: For mapping
- `tracts_with_accessibility.geojson`: Full dataset with accessibility

**Critical Assumptions Summary**:
1. All jobs in a tract are at the centroid
2. Binary reachability (within threshold = reachable, outside = not)
3. Representative travel time (8 AM) represents typical accessibility
4. Per-capita normalization is appropriate
5. Transit deserts = low access + high need
6. Quartiles are appropriate thresholds

---

### Notebook 04: Spatial Analysis

**Purpose**: Analyze spatial patterns in transit accessibility

#### Step-by-Step Analysis:

**1. Spatial Autocorrelation Concept**
- **Decision**: Uses Moran's I to measure spatial clustering
- **Intuition**: 
  - Spatial autocorrelation = "nearby things are similar"
  - If transit accessibility is spatially autocorrelated, it means:
    - Well-connected areas cluster together
    - Poorly-connected areas cluster together
  - This is important for policy: if problems cluster, you can target interventions geographically
- **Why This Matters**: 
  - If accessibility is random (no spatial autocorrelation), interventions should be scattered
  - If accessibility clusters, interventions should target clusters

**2. Spatial Weights Matrix**
- **Decision**: Uses Queen contiguity (tracts that share a border or corner)
- **Intuition**: 
  - Queen = more neighbors (includes corner touches)
  - Rook = fewer neighbors (only edge touches)
  - Queen is more appropriate for irregular shapes (census tracts)
- **Why Contiguity (Not Distance)**: 
  - Contiguity captures "immediate neighbors" (most relevant for spillover effects)
  - Distance-based weights would include far-away tracts (less relevant)
  - Contiguity is standard in spatial econometrics
- **Row Standardization**: Transforms weights so each tract's neighbors sum to 1
  - This makes the spatial lag a "weighted average" of neighbors
  - Easier to interpret

**3. Island Handling**
- **Decision**: Identifies and excludes "islands" (tracts with no neighbors)
- **Intuition**: 
  - Islands can't have spatial autocorrelation (no neighbors to correlate with)
  - Including them would break the spatial weights matrix
  - Common in geographic data (water bodies, isolated tracts)
- **Why Rebuild Weights Matrix**: After removing islands, need to rebuild to ensure consistency

**4. Global Moran's I**
- **Decision**: Calculates single statistic for entire study area
- **Intuition**: 
  - I > 0: Positive autocorrelation (similar values cluster)
  - I < 0: Negative autocorrelation (dissimilar values cluster)
  - I ≈ 0: No spatial pattern (random)
- **Interpretation**: 
  - If I is significantly positive, well-connected areas cluster together
  - This suggests geographic factors (proximity to downtown, transit infrastructure) drive accessibility

**5. Local Moran's I (LISA)**
- **Decision**: Calculates local statistics for each tract
- **Intuition**: 
  - Global Moran's I gives overall pattern
  - LISA identifies WHERE clustering occurs
  - Four types of clusters:
    - **High-High**: High accessibility, surrounded by high accessibility (well-connected cluster)
    - **Low-Low**: Low accessibility, surrounded by low accessibility (transit desert cluster)
    - **High-Low**: High accessibility, surrounded by low (outlier - well-connected island)
    - **Low-High**: Low accessibility, surrounded by high (outlier - transit desert island)
- **Why This Matters**: 
  - Identifies specific geographic clusters for intervention
  - High-High clusters: Study what works, replicate
  - Low-Low clusters: Priority areas for improvement

**6. P-Value Handling**
- **Decision**: Uses simulated p-values (`p_sim`) for significance testing
- **Intuition**: 
  - LISA p-values test: "Is this cluster significantly different from random?"
  - Simulation-based p-values are more robust than analytical (especially for small samples)
  - Standard approach in spatial statistics
- **Significance Threshold**: p < 0.05 (standard)
- **Why Relaxed Threshold for Visualization**: If no clusters are significant, map would be all grey. Relaxing threshold (or showing all clusters) makes patterns visible.

**7. Spatial Regression Models**
- **Decision**: Compares OLS, Spatial Lag, and Spatial Error models
- **Intuition**: 
  - **OLS**: Assumes independence (no spatial effects)
  - **Spatial Lag**: Accessibility depends on neighbor accessibility (spillover effects)
  - **Spatial Error**: Errors are spatially correlated (unmeasured factors cluster)
- **Why Multiple Models**: 
  - Tests if spatial effects matter
  - If spatial lag is significant, neighbor accessibility affects local accessibility
  - If spatial error is significant, unmeasured factors (e.g., historical development) cluster spatially

**8. Feature Selection for Regression**
- **Decision**: Uses income, population density, distance to downtown, job density
- **Intuition**: 
  - These are the most theoretically relevant factors
  - Too many features can cause multicollinearity
  - Focus on interpretable, policy-relevant factors
- **Why Not All Features**: 
  - Some features are redundant (pop_total vs pop_density)
  - Interaction terms can be hard to interpret
  - Spatial lags would create circularity (accessibility predicting accessibility)

**9. Model Comparison**
- **Decision**: Compares R², AIC, and coefficient significance
- **Intuition**: 
  - R²: How much variation is explained
  - AIC: Model fit penalized for complexity (lower is better)
  - Coefficients: Direction and magnitude of effects
- **Why R² Might Be Low**: 
  - Accessibility is complex (many unmeasured factors)
  - Spatial regression often has lower R² than ML models (but is more interpretable)
  - Low R² doesn't mean model is useless - coefficients are still meaningful

**10. Visualization of Spatial Patterns**
- **Decision**: Creates maps showing LISA clusters and regression residuals
- **Intuition**: 
  - Maps reveal geographic patterns that statistics miss
  - Residual maps show where model fails (areas with high/low accessibility not explained by model)
  - These areas might need special attention

**Key Outputs**:
- `spatial_autocorrelation_results.csv`: Moran's I statistics
- `tracts_lisa_clusters.geojson`: LISA cluster assignments
- `spatial_regression_results.csv`: Regression coefficients

**Critical Assumptions Summary**:
1. Queen contiguity captures relevant spatial relationships
2. Islands should be excluded from analysis
3. Simulated p-values are appropriate for significance testing
4. Spatial effects are linear (spatial lag model)
5. Selected features capture main drivers of accessibility

---

### Notebook 05: ML Advanced Analysis

**Purpose**: Apply machine learning to predict accessibility and identify key factors

#### Step-by-Step Analysis:

**1. Why ML After Spatial Analysis?**
- **Decision**: Uses ML to complement (not replace) spatial analysis
- **Intuition**: 
  - Spatial analysis: Identifies WHERE problems are (geographic clusters)
  - ML analysis: Identifies WHAT drives problems (feature importance)
  - Together: Target interventions to specific areas based on key factors
- **Why Not Start with ML**: 
  - Spatial analysis provides theoretical foundation
  - ML can overfit without understanding the problem
  - Spatial analysis is more interpretable

**2. Feature Engineering Strategy**
- **Decision**: Creates comprehensive feature set:
  - Basic demographics (income, population, jobs)
  - Densities (population density, job density)
  - Interaction terms (income × population, etc.)
  - Spatial lags (neighbor averages)
  - Geographic features (coordinates, distance to downtown)
- **Intuition**: 
  - More features = more information
  - But risk of overfitting
  - Interaction terms capture non-linear relationships
  - Spatial lags capture neighborhood effects
  - Geographic features capture unmeasured factors (proximity to freeways, historical development)

**3. Log Transform Removal**
- **Decision**: Removed log-transformed features (log_pop, log_dist, etc.)
- **Intuition**: 
  - Log transforms help with skewed data in linear models
  - Tree-based models (Random Forest, Gradient Boosting) don't need log transforms (they handle non-linearity automatically)
  - Including both original and log features can add noise without benefit
- **Why This Matters**: Simpler model = easier to interpret, less risk of overfitting

**4. Spatial Lag Features**
- **Decision**: Includes spatial lags for key variables
- **Intuition**: 
  - Neighbor characteristics affect local accessibility (spillover effects)
  - Example: A tract surrounded by high-income tracts might have better transit (transit agencies prioritize wealthy areas)
- **Why Not Include Accessibility Lag**: 
  - Would create circularity (accessibility predicting accessibility)
  - But including demographic lags is valid (neighbor demographics affect local accessibility)

**5. Interaction Terms**
- **Decision**: Creates income × population, income × jobs, population × jobs
- **Intuition**: 
  - Relationships might be non-linear
  - Example: High density + high income might have different accessibility than high density + low income
  - Interaction terms capture these effects
- **Why Scaled (Divided by 1e6, 1e9)**: 
  - Prevents numerical overflow
  - Makes coefficients more interpretable
  - Standard practice

**6. Geographic Coordinates**
- **Decision**: Includes x_coord and y_coord as features
- **Intuition**: 
  - Captures unmeasured geographic factors:
    - Proximity to freeways
    - Historical development patterns
    - Natural barriers (mountains, rivers)
    - Distance from coast
  - Even after controlling for distance to downtown, location matters
- **Why This Works**: 
  - ML models can learn complex geographic patterns
  - Coordinates act as "catch-all" for geographic factors

**7. Distance to Downtown**
- **Decision**: Calculates Euclidean distance to downtown LA
- **Intuition**: 
  - Downtown is the transit hub (most routes converge there)
  - Distance to downtown is a strong predictor of accessibility
  - This is a key geographic factor
- **Why Euclidean (Not Network Distance)**: 
  - Simpler to calculate
  - Network distance would be more accurate but computationally expensive
  - Euclidean is a good proxy

**8. Random Forest Model**
- **Decision**: Uses Random Forest Regressor
- **Intuition**: 
  - Handles non-linear relationships automatically
  - Provides feature importance (interpretable)
  - Robust to outliers
  - Doesn't require feature scaling
- **Hyperparameters**:
  - `n_estimators=100`: Number of trees (more = better but slower)
  - `max_depth=10`: Limits tree depth (prevents overfitting)
  - `random_state=42`: Reproducibility

**9. Feature Importance Interpretation**
- **Decision**: Uses mean decrease in impurity (Gini importance)
- **Intuition**: 
  - Measures how much each feature reduces prediction error
  - Higher importance = feature is more useful for prediction
- **Why This Matters**: 
  - Identifies which factors matter most
  - Guides policy interventions (focus on high-importance features)
- **Limitation**: 
  - Importance is relative (sums to 1)
  - Correlated features share importance (can't distinguish)
  - Doesn't show direction (positive or negative effect)

**10. Gradient Boosting**
- **Decision**: Uses Gradient Boosting (sklearn, optionally XGBoost/LightGBM)
- **Intuition**: 
  - Often better performance than Random Forest
  - Sequential learning (each tree corrects previous errors)
  - Can capture complex patterns
- **Why Multiple Implementations**: 
  - XGBoost/LightGBM are faster and sometimes more accurate
  - But not always available, so sklearn is fallback

**11. Clustering Analysis**
- **Decision**: Uses K-means clustering on all features
- **Intuition**: 
  - Groups similar tracts (not just by accessibility, but by all characteristics)
  - Reveals "types" of tracts (e.g., wealthy suburbs, dense urban core, etc.)
- **Why Cluster on Features (Not Just Accessibility)**: 
  - Accessibility alone might miss important patterns
  - Clustering on features reveals demographic/geographic types
  - These types might need different intervention strategies

**12. Elbow Method (2nd Derivative)**
- **Decision**: Uses 2nd derivative to find optimal number of clusters
- **Intuition**: 
  - Elbow method finds where adding more clusters doesn't help much
  - 2nd derivative finds maximum curvature (where the "elbow" is)
  - More objective than visual inspection
- **Why This Matters**: 
  - Too few clusters: Miss important distinctions
  - Too many clusters: Over-segmentation, hard to interpret

**13. PCA Analysis**
- **Decision**: Performs Principal Component Analysis
- **Intuition**: 
  - Reduces dimensionality (many features → few components)
  - Components capture main patterns in data
  - Helps understand "core dimensions" of the problem
- **Why This Matters**: 
  - If few components explain most variance, problem is simpler than it appears
  - Components might be interpretable (e.g., "urban vs suburban")

**14. Ensemble Methods**
- **Decision**: Combines multiple models (simple average, weighted average)
- **Intuition**: 
  - Different models capture different patterns
  - Combining them can improve predictions
  - Reduces risk of overfitting to one model
- **Why Weighted Average**: 
  - Better models should have more weight
  - Weight by R² (how well model fits)

**15. Model Comparison with Spatial Regression**
- **Decision**: Compares ML models to spatial regression from Notebook 04
- **Intuition**: 
  - ML models often have higher R² (better fit)
  - But spatial regression is more interpretable (coefficients have meaning)
  - Both have value:
    - ML: Better predictions, feature importance
    - Spatial regression: Interpretable coefficients, spatial effects

**Key Outputs**:
- `rf_feature_importance.png`: Feature importance plot
- `clustering_results.png`: Cluster maps
- `pca_analysis.png`: PCA visualization
- `ml_model_comparison.csv`: Model performance comparison

**Critical Assumptions Summary**:
1. All features are relevant (no feature selection)
2. Tree-based models don't need feature scaling
3. Spatial lags capture neighborhood effects
4. Interaction terms capture non-linear relationships
5. Geographic coordinates capture unmeasured factors
6. Clustering on all features reveals meaningful groups

---

### Notebook 08: EDA Feature Analysis

**Purpose**: Comprehensive exploratory data analysis of feature relationships

#### Step-by-Step Analysis:

**1. Correlation Analysis**
- **Decision**: Calculates Pearson correlation for all feature pairs
- **Intuition**: 
  - Correlation measures linear relationships
  - High correlation with accessibility = important feature
  - High correlation between features = multicollinearity (redundancy)
- **Why Pearson (Not Spearman)**: 
  - Pearson assumes linear relationships
  - Spearman is rank-based (non-parametric)
  - For EDA, Pearson is standard
  - Can use Spearman if relationships are non-linear

**2. Correlation Heatmaps**
- **Decision**: Creates full correlation matrix and focused heatmap (top features)
- **Intuition**: 
  - Full matrix: Shows all relationships (can be overwhelming)
  - Focused: Highlights most important relationships
  - Color coding: Red = positive, Blue = negative
- **Why Upper Triangle Mask**: 
  - Correlation matrix is symmetric (r(A,B) = r(B,A))
  - Showing both halves is redundant
  - Masking makes visualization cleaner

**3. Scatter Plots with Trend Lines**
- **Decision**: Creates scatter plots for key features vs accessibility with linear fit
- **Intuition**: 
  - Scatter plots show actual data points (not just summary statistics)
  - Reveals outliers, non-linear patterns, heteroscedasticity
  - Trend line shows overall relationship
- **Why Linear Fit**: 
  - Simple, interpretable
  - Can see if relationship is approximately linear
  - If non-linear, might need transformations

**4. Well-Connected vs Poorly-Connected Comparison**
- **Decision**: Defines as top 25% vs bottom 25% of accessibility
- **Intuition**: 
  - Quartiles are standard thresholds
  - 25% gives enough samples for statistical tests
  - Relative measure (adapts to data distribution)
- **Why Not Absolute Thresholds**: 
  - Absolute thresholds (e.g., 100k jobs/1k) might not be meaningful
  - Relative thresholds adapt to local context

**5. Statistical Tests (Mann-Whitney U)**
- **Decision**: Uses non-parametric test (Mann-Whitney U) instead of t-test
- **Intuition**: 
  - t-test assumes normal distribution
  - Accessibility data is likely skewed (not normal)
  - Mann-Whitney U is rank-based (doesn't assume normality)
  - More robust to outliers
- **Why This Matters**: 
  - Ensures statistical tests are valid
  - p-values are meaningful

**6. Box Plots**
- **Decision**: Creates box plots comparing well-connected vs poorly-connected
- **Intuition**: 
  - Box plots show distribution (not just mean)
  - Reveals:
    - Median (more robust than mean)
    - Quartiles (spread)
    - Outliers
  - More informative than bar charts

**7. Spatial Maps**
- **Decision**: Creates maps showing well-connected vs poorly-connected areas
- **Intuition**: 
  - Reveals geographic patterns
  - Clustering? Random distribution? Concentrated in specific regions?
- **Why This Matters**: 
  - If problems cluster, can target interventions geographically
  - If random, need scattered interventions

**8. Interaction Effects**
- **Decision**: Creates scatter plots colored by accessibility
- **Intuition**: 
  - Shows how two features combine to affect accessibility
  - Example: Income vs Population Density, colored by accessibility
  - Reveals if relationships depend on other factors
- **Why This Matters**: 
  - Might reveal that high density + high income = good access, but high density + low income = poor access
  - Suggests need for interaction terms in models

**9. Spatial Lag Analysis**
- **Decision**: Analyzes correlation between base features and their spatial lags
- **Intuition**: 
  - High correlation = strong spatial autocorrelation
  - If income and income_lag are highly correlated, income clusters spatially
  - This validates use of spatial lags in models
- **Why This Matters**: 
  - If spatial lags aren't correlated with base features, they're not adding information
  - If highly correlated, might cause multicollinearity

**10. Key Insights Summary**
- **Decision**: Creates automated summary of findings
- **Intuition**: 
  - Synthesizes all analyses into actionable insights
  - Highlights most important findings
  - Provides recommendations

**Key Outputs**:
- `feature_summary_statistics.csv`: Summary stats
- `accessibility_correlations.csv`: Correlations with accessibility
- `correlation_matrix_heatmap.png`: Full correlation matrix
- `well_vs_poorly_connected_comparison.csv`: Statistical comparison
- `connection_status_map.png`: Geographic patterns

**Critical Assumptions Summary**:
1. Pearson correlation captures relevant relationships
2. Quartiles are appropriate thresholds
3. Non-parametric tests are appropriate
4. Spatial lags are valid features
5. Interaction effects are important

---

## Part 2: Recommendations for Next Steps

### Current State Assessment

**Strengths**:
- Comprehensive data pipeline (ingestion → analysis → ML)
- Multiple analytical approaches (spatial, ML, EDA)
- Rich feature set
- Good visualizations
- Well-documented code

**Gaps for Presentation**:
1. **Narrative/Story**: Missing clear story arc (problem → analysis → solution)
2. **Executive Summary**: No high-level summary for non-technical audience
3. **Policy Recommendations**: Findings are scattered, not synthesized into actionable recommendations
4. **Final Deliverable**: No single, polished output (report, dashboard, presentation)

### Recommended Next Steps

#### Option 1: Executive Report (Recommended for Simple, Presentable Project)

**Create a single, polished report** that tells the story:

1. **Create `09_final_report.ipynb`**:
   - **Section 1: Executive Summary** (1-2 pages)
     - What is a transit desert?
     - Key findings (3-5 bullet points)
     - Main recommendations
   
   - **Section 2: Methodology** (2-3 pages)
     - Data sources
     - Analysis approach (high-level, non-technical)
     - Key assumptions
   
   - **Section 3: Findings** (5-7 pages)
     - Where are transit deserts? (map)
     - What drives accessibility? (feature importance)
     - How do well-connected areas differ? (comparison)
     - Spatial patterns (clustering)
   
   - **Section 4: Recommendations** (2-3 pages)
     - Priority areas for intervention
     - Specific recommendations (routes, stops, frequency)
     - Expected impact
   
   - **Section 5: Technical Appendix** (optional)
     - Detailed methodology
     - Model specifications
     - Data sources

2. **Output Format**:
   - Export notebook to HTML or PDF
   - Or use `jupyter-book` to create a polished book
   - Include key visualizations (maps, charts)
   - Keep it under 20 pages total

3. **Key Visualizations to Include**:
   - Map of transit deserts (from Notebook 03)
   - Map of well-connected vs poorly-connected (from Notebook 08)
   - Feature importance chart (from Notebook 05)
   - Comparison table (well vs poorly connected)
   - LISA cluster map (from Notebook 04)

#### Option 2: Interactive Dashboard

**Create a Streamlit or Plotly Dash dashboard**:

1. **Features**:
   - Interactive map (click tract to see details)
   - Filters (by income, accessibility, etc.)
   - Key statistics
   - Comparison tool (compare two tracts)

2. **Implementation**:
   - Use `streamlit` (simpler) or `plotly dash` (more customizable)
   - Load pre-computed results from `outputs/`
   - Keep it simple (3-4 pages/sections)

3. **Deploy**:
   - Streamlit Cloud (free)
   - Or export as standalone HTML

#### Option 3: Presentation Slides

**Create a 10-15 slide presentation**:

1. **Structure**:
   - Slide 1: Title + problem statement
   - Slides 2-3: Methodology (high-level)
   - Slides 4-8: Key findings (one finding per slide)
   - Slides 9-10: Recommendations
   - Slide 11: Next steps / limitations

2. **Tools**:
   - Use `reveal.js` in Jupyter
   - Or export to PowerPoint/Google Slides
   - Keep slides visual (more images, less text)

### Specific Recommendations

#### 1. Synthesize Findings into Clear Recommendations

**Create a new notebook or section that**:
- Identifies top 10 priority tracts for intervention
- Provides specific recommendations (e.g., "Add bus route on Main St. between A and B")
- Estimates potential impact (e.g., "Would improve accessibility by X% for Y people")
- Considers cost/benefit (rough estimates)

**How to do this**:
- Use ML model to predict: "If we improve feature X, how much does accessibility increase?"
- Identify tracts that are:
  - Poorly connected (bottom quartile)
  - High need (low income OR high density)
  - High potential (close to existing transit, or high population)
- Rank by some combination of need × potential

#### 2. Create a "Key Findings" Summary

**Extract the most important findings from all notebooks**:

1. **From Notebook 03 (Accessibility)**:
   - X% of tracts are transit deserts
   - Average accessibility: X jobs/1k residents
   - Top/bottom quartile thresholds

2. **From Notebook 04 (Spatial Analysis)**:
   - Global Moran's I: X (significant clustering)
   - X Low-Low clusters identified (priority areas)
   - Spatial regression: Distance to downtown is key factor

3. **From Notebook 05 (ML)**:
   - Top 3 features driving accessibility: [list]
   - ML model R²: X (explains X% of variation)
   - X clusters identified (different types of tracts)

4. **From Notebook 08 (EDA)**:
   - Well-connected areas are X% closer to downtown
   - Key differences: [list top 3]

#### 3. Simplify Technical Content

**For presentation, focus on**:
- **What** you found (not how you found it)
- **Why** it matters (policy implications)
- **What** to do about it (recommendations)

**Move technical details to appendix**:
- Model specifications
- Statistical tests
- Data processing steps

#### 4. Create a "Project Overview" Document

**A 1-page summary that**:
- States the problem
- Describes the approach (1-2 sentences)
- Lists key findings (3-5 bullets)
- Provides main recommendation

**This is your "elevator pitch"** - something you can share quickly.

#### 5. Clean Up Outputs

**Organize `outputs/` folder**:
- Create subfolders: `maps/`, `charts/`, `tables/`, `data/`
- Keep only final, polished outputs
- Remove intermediate files
- Add a README explaining what each output is

### Recommended Final Structure

```
transit-deserts/
├── README.md (project overview)
├── notebooks/
│   ├── 00-08 (existing notebooks)
│   └── 09_final_report.ipynb (NEW - executive report)
├── outputs/
│   ├── final_report.html (exported report)
│   ├── maps/ (key maps)
│   ├── charts/ (key charts)
│   └── data/ (final datasets)
└── PROJECT_ANALYSIS_AND_RECOMMENDATIONS.md (this document)
```

### Next Immediate Steps

1. **Create `09_final_report.ipynb`** with:
   - Executive summary
   - Key findings synthesis
   - Clear recommendations
   - Key visualizations

2. **Test the report**:
   - Can a non-technical person understand it?
   - Are recommendations clear and actionable?
   - Is it visually appealing?

3. **Get feedback**:
   - Share with someone unfamiliar with the project
   - Revise based on feedback

4. **Final polish**:
   - Fix any remaining issues
   - Ensure all visualizations are high-quality
   - Check all numbers are correct

---

## Part 3: Critical Assumptions & Limitations Summary

### Data Assumptions

1. **Tract Centroids**: People/jobs are at tract centroids (not true, but standard approximation)
2. **GTFS Schedules**: Schedules represent typical service (ignores delays, cancellations)
3. **Walking Network**: OSM data is complete and accurate
4. **Representative Time**: 8 AM weekday represents typical accessibility
5. **Job Distribution**: Jobs are uniformly distributed within tracts

### Methodological Assumptions

1. **Shortest Path**: People take fastest route (rational choice model)
2. **Binary Reachability**: Job is either reachable or not (no distance decay)
3. **Per-Capita Normalization**: Appropriate for comparing tracts
4. **Spatial Weights**: Queen contiguity captures relevant spatial relationships
5. **ML Features**: All features are relevant (no feature selection)

### Limitations

1. **Sample Size**: Travel times computed for sample, not full O-D matrix
2. **Time-Dependent**: Single time point (8 AM) doesn't capture temporal variation
3. **Mode Choice**: Doesn't account for mode choice (assumes transit is used if available)
4. **Demand**: Doesn't account for transit demand (crowding, reliability)
5. **Cost**: Doesn't consider transit fares or travel costs

### What This Means

- **Results are approximate**: Good for identifying patterns, not exact values
- **Relative comparisons are valid**: Comparing tracts is more reliable than absolute values
- **Policy guidance is valid**: Recommendations are sound even with limitations
- **Further refinement possible**: Can address limitations in future work

---

## Conclusion

This project provides a comprehensive analysis of transit accessibility in Los Angeles County. The multi-notebook approach ensures reproducibility and allows for iterative refinement. The key to making it presentable is **synthesis** - pulling together findings into a clear, actionable narrative.

**Recommended path forward**: Create `09_final_report.ipynb` that synthesizes all findings into a clear, presentable report with actionable recommendations. This will transform the technical analysis into a policy-relevant document.

