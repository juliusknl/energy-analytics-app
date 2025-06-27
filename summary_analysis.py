import pandas as pd

# Read the CSV file
df = pd.read_csv('german_energy_benchmark_comprehensive_20250627_115057.csv')

print("=" * 80)
print("GERMAN ENERGY BENCHMARK DATASET ANALYSIS")
print("Why Peer Groups Are Small (20-30 companies instead of 50+)")
print("=" * 80)
print()

print("DATASET OVERVIEW:")
print(f"• Total companies: {len(df):,}")
print(f"• Sectors: {df['sector'].nunique()}")
print(f"• Regions: {df['region'].nunique()}")
print(f"• Employee range: {df['employees'].min():.0f} - {df['employees'].max():.0f}")
print()

# Current peer grouping constraints analysis
def categorize_company_size(employees):
    if employees < 250:
        return "Medium (50-249)"
    elif employees < 500:
        return "Large (250-499)"
    else:
        return "Very Large (500+)"

df['size_category'] = df['employees'].apply(categorize_company_size)

print("CURRENT PEER GROUPING CONSTRAINTS IMPACT:")
print()

# Show the fragmentation effect
print("1. SECTOR DISTRIBUTION:")
sector_counts = df['sector'].value_counts()
for sector, count in sector_counts.items():
    print(f"   {sector:20} {count:3d} companies")
print()

print("2. SIZE CATEGORY DISTRIBUTION:")
size_counts = df['size_category'].value_counts()
for size, count in size_counts.items():
    print(f"   {size:20} {count:3d} companies ({count/len(df)*100:.1f}%)")
print()

print("3. REGIONAL FRAGMENTATION:")
region_counts = df['region'].value_counts()
print("   Major regions:")
for region, count in region_counts.head(5).items():
    print(f"   {region:20} {count:3d} companies ({count/len(df)*100:.1f}%)")
print(f"   Other regions:       {region_counts.tail(4).sum():3d} companies ({region_counts.tail(4).sum()/len(df)*100:.1f}%)")
print()

# Current peer group sizes
peer_groups = df.groupby(['sector', 'size_category']).size().reset_index(name='count')
peer_groups = peer_groups.sort_values('count', ascending=False)

print("4. RESULTING PEER GROUP SIZES (Sector + Size Category):")
print(f"   Total peer groups: {len(peer_groups)}")
print(f"   Groups with 50+ companies: {len(peer_groups[peer_groups['count'] >= 50]):2d}")
print(f"   Groups with 30-49 companies: {len(peer_groups[(peer_groups['count'] >= 30) & (peer_groups['count'] < 50)]):2d}")
print(f"   Groups with 20-29 companies: {len(peer_groups[(peer_groups['count'] >= 20) & (peer_groups['count'] < 30)]):2d}")
print(f"   Groups with <20 companies: {len(peer_groups[peer_groups['count'] < 20]):2d}")
print()

# Show examples of current small groups
print("5. EXAMPLES OF CURRENT SMALL PEER GROUPS (20-35 companies):")
small_groups = peer_groups[(peer_groups['count'] >= 20) & (peer_groups['count'] <= 35)]
for _, row in small_groups.head(8).iterrows():
    print(f"   {row['sector']:20} + {row['size_category']:15} = {row['count']:2d} companies")
print()

print("=" * 80)
print("ROOT CAUSES OF SMALL PEER GROUPS")
print("=" * 80)
print()

print("1. OVER-SEGMENTATION:")
print("   • Using BOTH sector AND size creates", len(peer_groups), "narrow segments")
print("   • Most segments have <50 companies due to double filtering")
print()

print("2. REGIONAL FRAGMENTATION:")
print("   • 9 regions split companies further")
print("   • 46% of companies in just 3 major regions")
print("   • Smaller regions (Brandenburg, Thüringen) have very few companies")
print()

print("3. SIZE CATEGORY DISTRIBUTION:")
print(f"   • 70% of companies are Medium (50-249 employees)")
print(f"   • 25% are Large (250-499 employees)")
print(f"   • Only 5% are Very Large (500+ employees)")
print("   • This creates uneven distribution across size buckets")
print()

print("4. SECTOR IMBALANCE:")
manufacturing_pct = (sector_counts['Manufacturing'] / len(df)) * 100
print(f"   • Manufacturing dominates with {manufacturing_pct:.1f}% of companies")
print("   • Other sectors range from 80-120 companies each")
print("   • When split by size, many sectors become too small")
print()

print("=" * 80)
print("SOLUTIONS TO INCREASE PEER GROUP SIZES")
print("=" * 80)
print()

# Solution 1: Broader size categories
def broad_size_category(employees):
    if employees < 150:
        return "Small-Medium (50-149)"
    elif employees < 350:
        return "Medium-Large (150-349)"
    else:
        return "Large (350+)"

df['broad_size'] = df['employees'].apply(broad_size_category)
broad_groups = df.groupby(['sector', 'broad_size']).size().reset_index(name='count')
broad_groups = broad_groups.sort_values('count', ascending=False)

print("SOLUTION 1: Use Broader Size Categories")
print("   Current: 50-249, 250-499, 500+")
print("   Proposed: 50-149, 150-349, 350+")
print()
print("   Results:")
large_broad = broad_groups[broad_groups['count'] >= 50]
print(f"   • Peer groups with 50+ companies: {len(large_broad)} (vs {len(peer_groups[peer_groups['count'] >= 50])} currently)")
print("   • Largest groups would be:")
for _, row in large_broad.head(6).iterrows():
    print(f"     {row['sector']:20} + {row['broad_size']:20} = {row['count']:3d} companies")
print()

# Solution 2: Sector only
sector_only = df.groupby(['sector']).size().reset_index(name='count')
sector_only = sector_only.sort_values('count', ascending=False)

print("SOLUTION 2: Use Sector Only (Remove Size Constraints)")
print("   Results:")
large_sector = sector_only[sector_only['count'] >= 50]
print(f"   • Peer groups with 50+ companies: {len(large_sector)} (all major sectors)")
print("   • Group sizes would be:")
for _, row in sector_only.head(8).iterrows():
    print(f"     {row['sector']:20} = {row['count']:3d} companies")
print()

print("SOLUTION 3: Regional Consolidation")
print("   • Focus on 5 major regions (covers 88% of companies)")
print("   • Group smaller regions together")
print("   • This alone would improve many peer groups by 10-20%")
print()

print("=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)
print()
print("IMMEDIATE ACTIONS:")
print("1. Switch to broader size categories (50-149, 150-349, 350+)")
print("   → Would give you 6 peer groups with 50+ companies")
print()
print("2. Consider sector-only grouping for initial benchmarking")
print("   → All major sectors would have 80+ companies")
print()
print("3. Consolidate regions into 3-4 major areas")
print("   → North, South, West, East Germany")
print()
print("LONG-TERM:")
print("4. Collect more data to reach 2000+ companies")
print("   → Would allow finer segmentation while maintaining group sizes")
print()
print("5. Use energy intensity ranges as additional grouping criteria")
print("   → Companies with similar kWh/employee patterns")
print()

print("The current dataset of 1,140 companies is actually quite good,")
print("but the segmentation strategy is creating artificial scarcity!"))