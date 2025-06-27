import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('german_energy_benchmark_comprehensive_20250627_115057.csv')

print("=== DETAILED PEER GROUP ANALYSIS ===")
print(f"Total companies in dataset: {len(df)}")
print()

# Define different peer grouping strategies and see their effectiveness

# Strategy 1: Sector + Size Category
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

print("STRATEGY 1: Sector + Size Category")
peer_groups_1 = df.groupby(['sector', 'size_category']).size().reset_index(name='count')
peer_groups_1 = peer_groups_1.sort_values('count', ascending=False)

print(f"Total peer groups: {len(peer_groups_1)}")
print(f"Groups with 50+ companies: {len(peer_groups_1[peer_groups_1['count'] >= 50])}")
print(f"Groups with 30-49 companies: {len(peer_groups_1[(peer_groups_1['count'] >= 30) & (peer_groups_1['count'] < 50)])}")
print(f"Groups with 20-29 companies: {len(peer_groups_1[(peer_groups_1['count'] >= 20) & (peer_groups_1['count'] < 30)])}")
print(f"Groups with <20 companies: {len(peer_groups_1[peer_groups_1['count'] < 20])}")
print()

# Strategy 2: Sector + Region (for major regions)
major_regions = ['Nordrhein-Westfalen', 'Bayern', 'Baden-Württemberg', 'Hessen', 'Niedersachsen']
df_major_regions = df[df['region'].isin(major_regions)]

print("STRATEGY 2: Sector + Major Regions Only")
peer_groups_2 = df_major_regions.groupby(['sector', 'region']).size().reset_index(name='count')
peer_groups_2 = peer_groups_2.sort_values('count', ascending=False)

print(f"Total peer groups (major regions only): {len(peer_groups_2)}")
print(f"Companies in major regions: {len(df_major_regions)} out of {len(df)}")
print(f"Groups with 50+ companies: {len(peer_groups_2[peer_groups_2['count'] >= 50])}")
print(f"Groups with 30+ companies: {len(peer_groups_2[peer_groups_2['count'] >= 30])}")
print(f"Groups with 20+ companies: {len(peer_groups_2[peer_groups_2['count'] >= 20])}")
print()

# Strategy 3: Broader size categories
def categorize_company_size_broad(employees):
    if employees < 150:
        return "Small-Medium (50-149)"
    elif employees < 350:
        return "Medium-Large (150-349)"
    else:
        return "Large (350+)"

df['size_category_broad'] = df['employees'].apply(categorize_company_size_broad)

print("STRATEGY 3: Sector + Broader Size Categories")
peer_groups_3 = df.groupby(['sector', 'size_category_broad']).size().reset_index(name='count')
peer_groups_3 = peer_groups_3.sort_values('count', ascending=False)

print(f"Total peer groups: {len(peer_groups_3)}")
print(f"Groups with 50+ companies: {len(peer_groups_3[peer_groups_3['count'] >= 50])}")
print(f"Groups with 30+ companies: {len(peer_groups_3[peer_groups_3['count'] >= 30])}")
print()

print("Top 15 largest peer groups (Sector + Broad Size):")
print(peer_groups_3.head(15).to_string(index=False))
print()

# Strategy 4: Sector only (no size/region constraints)
print("STRATEGY 4: Sector Only (No Size/Region Constraints)")
peer_groups_4 = df.groupby(['sector']).size().reset_index(name='count')
peer_groups_4 = peer_groups_4.sort_values('count', ascending=False)

print("Companies by sector:")
print(peer_groups_4.to_string(index=False))
print()

# Analysis of the constraint impact
print("=== CONSTRAINT IMPACT ANALYSIS ===")
print()

# Regional distribution impact
print("Regional distribution analysis:")
region_impact = df['region'].value_counts()
print("Companies per region:")
for region, count in region_impact.items():
    print(f"  {region}: {count} companies ({count/len(df)*100:.1f}%)")
print()

# Size distribution impact
print("Size distribution analysis:")
size_impact = df['size_category'].value_counts()
print("Companies per size category:")
for size, count in size_impact.items():
    print(f"  {size}: {count} companies ({count/len(df)*100:.1f}%)")
print()

# Specific examples of peer groups that are too small
print("=== EXAMPLES OF SMALL PEER GROUPS ===")
print("Sector + Size combinations with 20-30 companies (typical current peer group size):")
small_groups = peer_groups_1[(peer_groups_1['count'] >= 15) & (peer_groups_1['count'] <= 35)]
print(small_groups.to_string(index=False))
print()

# What if we remove regional constraints and use broader categories?
print("=== RECOMMENDED APPROACH ===")
print("Using broader size categories without regional constraints:")
print("This would give you these peer group sizes:")
recommended = peer_groups_3[peer_groups_3['count'] >= 50]
print(f"Number of peer groups with 50+ companies: {len(recommended)}")
print("These groups are:")
print(recommended.to_string(index=False))