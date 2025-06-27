import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('german_energy_benchmark_comprehensive_20250627_115057.csv')

# Basic dataset info
print("=== DATASET OVERVIEW ===")
print(f"Total number of companies: {len(df)}")
print(f"Number of columns: {len(df.columns)}")
print(f"Column names: {list(df.columns)}")
print()

# Show first few rows structure
print("=== SAMPLE DATA STRUCTURE ===")
print(df.head(3).to_string())
print()

# Distribution by sector
print("=== DISTRIBUTION BY SECTOR ===")
sector_dist = df['sector'].value_counts()
print(sector_dist)
print(f"\nNumber of unique sectors: {df['sector'].nunique()}")
print()

# Distribution by region
print("=== DISTRIBUTION BY REGION ===")
region_dist = df['region'].value_counts()
print(region_dist)
print(f"\nNumber of unique regions: {df['region'].nunique()}")
print()

# Employee size distribution analysis
print("=== EMPLOYEE SIZE DISTRIBUTION ===")
print(f"Employee count statistics:")
print(df['employees'].describe())
print()

# Create employee size categories
def categorize_company_size(employees):
    if employees < 50:
        return "Small (1-49)"
    elif employees < 250:
        return "Medium (50-249)"
    elif employees < 500:
        return "Large (250-499)"
    else:
        return "Very Large (500+)"

df['size_category'] = df['employees'].apply(categorize_company_size)
size_dist = df['size_category'].value_counts()
print("Companies by size category:")
print(size_dist)
print()

# Cross-tabulation of sector and size
print("=== SECTOR x SIZE CROSS-TABULATION ===")
cross_tab = pd.crosstab(df['sector'], df['size_category'])
print(cross_tab)
print()

# Potential peer groups analysis
print("=== PEER GROUP ANALYSIS ===")
print("If peer groups are defined by sector + size category:")
peer_groups = df.groupby(['sector', 'size_category']).size().reset_index(name='count')
peer_groups = peer_groups.sort_values('count', ascending=False)
print("Top 10 largest potential peer groups:")
print(peer_groups.head(10).to_string(index=False))
print()

print("Peer groups with less than 50 companies:")
small_groups = peer_groups[peer_groups['count'] < 50]
print(f"Number of peer groups with <50 companies: {len(small_groups)} out of {len(peer_groups)}")
print()

# Regional analysis within sectors
print("=== REGIONAL DISTRIBUTION WITHIN MANUFACTURING ===")
if 'Manufacturing' in df['sector'].values:
    manu_regions = df[df['sector'] == 'Manufacturing']['region'].value_counts()
    print(manu_regions)
    print()

# Energy consumption patterns
print("=== ENERGY CONSUMPTION PATTERNS ===")
print("kWh per employee statistics by sector:")
kwh_by_sector = df.groupby('sector')['kwh_per_employee'].agg(['count', 'mean', 'median', 'std']).round(2)
print(kwh_by_sector)