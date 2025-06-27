import pandas as pd
import numpy as np
import json
import glob
from datetime import datetime

class GermanEnergyBenchmarker:
    def __init__(self, data_file=None):
        """Initialize with the latest benchmark dataset"""
        if data_file is None:
            # Find the most recent data file
            csv_files = glob.glob('german_energy_benchmark_comprehensive_*.csv')
            if not csv_files:
                raise FileNotFoundError("No benchmark data found. Run fetch_real_data.py first!")
            data_file = max(csv_files)  # Most recent file
        
        print(f"📊 Loading benchmark data from: {data_file}")
        self.df = pd.read_csv(data_file)
        print(f"✅ Loaded {len(self.df)} German companies")
        
        # Load metadata if available
        json_files = glob.glob('german_energy_metadata_*.json')
        if json_files:
            metadata_file = max(json_files)
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
            print(f"📋 Loaded metadata from: {metadata_file}")
        else:
            self.metadata = {}
    
    def benchmark_company(self, company_profile):
        """
        Benchmark a company against German peers
        
        company_profile = {
            'sector': 'Manufacturing',
            'region': 'Bayern', 
            'employees': 150,
            'annual_kwh': 2000000,
            'cost_per_kwh': 0.15
        }
        """
        print(f"\n🔍 Benchmarking {company_profile['sector']} company...")
        print(f"📍 Location: {company_profile['region']}")
        print(f"👥 Employees: {company_profile['employees']}")
        print(f"⚡ Annual consumption: {company_profile['annual_kwh']:,} kWh")
        print(f"💰 Energy cost: €{company_profile['cost_per_kwh']:.3f}/kWh")
        
        # Find peer companies
        peers = self._find_peers(company_profile)
        print(f"🏢 Found {len(peers)} peer companies")
        
        # Calculate user metrics
        user_kwh_per_employee = company_profile['annual_kwh'] / company_profile['employees']
        user_annual_cost = company_profile['annual_kwh'] * company_profile['cost_per_kwh']
        
        # Calculate benchmarks
        benchmarks = self._calculate_benchmarks(company_profile, peers, user_kwh_per_employee)
        
        # Generate insights
        insights = self._generate_insights(company_profile, benchmarks, user_kwh_per_employee)
        
        return {
            'company_profile': company_profile,
            'peer_group_size': len(peers),
            'benchmarks': benchmarks,
            'insights': insights,
            'user_metrics': {
                'kwh_per_employee': user_kwh_per_employee,
                'annual_cost_eur': user_annual_cost,
                'cost_per_kwh': company_profile['cost_per_kwh']
            }
        }
    
    def _find_peers(self, profile):
        """Find similar companies for benchmarking"""
        df = self.df
        
        # Primary criteria: same sector + similar size
        sector_match = df['sector'] == profile['sector']
        size_match = (
            (df['employees'] >= profile['employees'] * 0.7) & 
            (df['employees'] <= profile['employees'] * 1.3)
        )
        
        peers = df[sector_match & size_match]
        
        # Expand criteria if too few peers
        if len(peers) < 5:
            print("⚠️ Few size matches, expanding to sector only...")
            peers = df[sector_match]
        
        if len(peers) < 5:
            print("⚠️ Few sector matches, using all companies...")
            peers = df
        
        return peers
    
    def _calculate_benchmarks(self, profile, peers, user_kwh_per_employee):
        """Calculate detailed benchmark metrics"""
        
        # Percentile rankings
        efficiency_percentile = (peers['kwh_per_employee'] > user_kwh_per_employee).mean() * 100
        cost_percentile = (peers['cost_per_kwh'] < profile['cost_per_kwh']).mean() * 100
        
        # Peer statistics
        peer_stats = {
            'kwh_per_employee_median': peers['kwh_per_employee'].median(),
            'kwh_per_employee_q25': peers['kwh_per_employee'].quantile(0.25),
            'kwh_per_employee_q75': peers['kwh_per_employee'].quantile(0.75),
            'cost_per_kwh_median': peers['cost_per_kwh'].median(),
            'cost_per_kwh_q25': peers['cost_per_kwh'].quantile(0.25),
            'cost_per_kwh_q75': peers['cost_per_kwh'].quantile(0.75),
        }
        
        # Performance vs peers
        efficiency_vs_median = ((user_kwh_per_employee / peer_stats['kwh_per_employee_median']) - 1) * 100
        cost_vs_median = ((profile['cost_per_kwh'] / peer_stats['cost_per_kwh_median']) - 1) * 100
        
        # Savings potential
        efficiency_gap = user_kwh_per_employee - peer_stats['kwh_per_employee_q25']
        if efficiency_gap > 0:
            efficiency_savings_kwh = efficiency_gap * profile['employees']
            efficiency_savings_eur = efficiency_savings_kwh * profile['cost_per_kwh']
        else:
            efficiency_savings_kwh = 0
            efficiency_savings_eur = 0
        
        cost_gap = profile['cost_per_kwh'] - peer_stats['cost_per_kwh_median']
        if cost_gap > 0:
            cost_savings_eur = profile['annual_kwh'] * cost_gap
        else:
            cost_savings_eur = 0
        
        # German national context
        if self.metadata and 'energy_statistics' in self.metadata:
            national_avg = self.metadata['energy_statistics'].get('manufacturing_kwh_per_employee', 26897)
            vs_national = ((user_kwh_per_employee / national_avg) - 1) * 100
        else:
            vs_national = None
        
        return {
            'efficiency_percentile': efficiency_percentile,
            'cost_percentile': cost_percentile,
            'efficiency_vs_median_pct': efficiency_vs_median,
            'cost_vs_median_pct': cost_vs_median,
            'vs_national_pct': vs_national,
            'peer_stats': peer_stats,
            'savings_potential': {
                'efficiency_kwh': efficiency_savings_kwh,
                'efficiency_eur': efficiency_savings_eur,
                'cost_eur': cost_savings_eur,
                'total_eur': efficiency_savings_eur + cost_savings_eur
            }
        }
    
    def _generate_insights(self, profile, benchmarks, user_kwh_per_employee):
        """Generate actionable insights"""
        insights = []
        
        # Efficiency insights
        if benchmarks['efficiency_percentile'] < 50:
            priority = 'HIGH' if benchmarks['efficiency_percentile'] < 25 else 'MEDIUM'
            insights.append({
                'type': 'EFFICIENCY_OPPORTUNITY',
                'priority': priority,
                'title': 'Energy Efficiency Improvement Opportunity',
                'message': f"You rank {benchmarks['efficiency_percentile']:.0f}th percentile among peer companies",
                'details': f"Top 25% use {benchmarks['peer_stats']['kwh_per_employee_q25']:,.0f} kWh/employee vs your {user_kwh_per_employee:,.0f}",
                'action': f"Potential annual savings: €{benchmarks['savings_potential']['efficiency_eur']:,.0f}",
                'recommendations': [
                    "Conduct energy audit to identify efficiency opportunities",
                    "Consider LED lighting upgrades and smart controls",
                    "Evaluate HVAC optimization and building automation",
                    "Implement ISO 50001 energy management system"
                ]
            })
        else:
            insights.append({
                'type': 'EFFICIENCY_STRENGTH',
                'priority': 'POSITIVE',
                'title': 'Strong Energy Efficiency Performance',
                'message': f"You rank {benchmarks['efficiency_percentile']:.0f}th percentile - above average!",
                'details': f"You use {abs(benchmarks['efficiency_vs_median_pct']):.1f}% less energy per employee than peer median",
                'action': "Consider sharing best practices or offering consulting services",
                'recommendations': [
                    "Document your energy management practices",
                    "Apply for energy efficiency awards/recognition",
                    "Share best practices with industry associations",
                    "Consider additional renewable energy investments"
                ]
            })
        
        # Cost insights
        if benchmarks['cost_percentile'] > 60:
            priority = 'HIGH' if benchmarks['cost_percentile'] > 80 else 'MEDIUM'
            insights.append({
                'type': 'COST_OPPORTUNITY', 
                'priority': priority,
                'title': 'Energy Cost Reduction Opportunity',
                'message': f"You pay more than {benchmarks['cost_percentile']:.0f}% of peer companies",
                'details': f"Your €{profile['cost_per_kwh']:.3f}/kWh vs peer median €{benchmarks['peer_stats']['cost_per_kwh_median']:.3f}/kWh",
                'action': f"Potential annual savings: €{benchmarks['savings_potential']['cost_eur']:,.0f}",
                'recommendations': [
                    "Review energy procurement strategy and contracts",
                    "Consider switching to renewable energy tariffs",
                    "Evaluate demand response program participation",
                    "Negotiate better rates with current supplier"
                ]
            })
        
        # Total savings potential
        total_savings = benchmarks['savings_potential']['total_eur']
        if total_savings > 20000:
            insights.append({
                'type': 'TOTAL_OPPORTUNITY',
                'priority': 'HIGH',
                'title': 'Significant Cost Optimization Potential',
                'message': f"Combined optimization potential: €{total_savings:,.0f} annually",
                'details': "Based on achieving top-quartile performance in your sector",
                'action': "ROI payback typically under 2-3 years for most efficiency measures",
                'recommendations': [
                    "Develop comprehensive energy strategy",
                    "Consider financing options for efficiency investments",
                    "Engage energy management consultant",
                    "Set measurable efficiency targets and KPIs"
                ]
            })
        
        # German context
        if benchmarks['vs_national_pct'] and benchmarks['vs_national_pct'] > 15:
            insights.append({
                'type': 'NATIONAL_CONTEXT',
                'priority': 'MEDIUM',
                'title': 'Above German Industrial Average',
                'message': f"You use {benchmarks['vs_national_pct']:.1f}% more energy than German industrial average",
                'details': "Consider systematic energy management approach",
                'action': "ISO 50001 certification could provide structured improvement framework",
                'recommendations': [
                    "Benchmark against German best practices",
                    "Participate in energy efficiency networks",
                    "Apply for government efficiency funding programs",
                    "Connect with German energy agencies for support"
                ]
            })
        
        return insights
    
    def print_benchmark_report(self, result):
        """Print a comprehensive benchmark report"""
        print("\n" + "="*60)
        print("🇩🇪 GERMAN ENERGY BENCHMARKING REPORT")
        print("="*60)
        
        profile = result['company_profile']
        benchmarks = result['benchmarks']
        insights = result['insights']
        
        # Company overview
        print(f"\n🏭 COMPANY PROFILE")
        print(f"Sector: {profile['sector']}")
        print(f"Region: {profile['region']}")
        print(f"Employees: {profile['employees']}")
        print(f"Annual consumption: {profile['annual_kwh']:,} kWh")
        print(f"Energy intensity: {result['user_metrics']['kwh_per_employee']:,.0f} kWh/employee")
        print(f"Energy cost: €{profile['cost_per_kwh']:.3f}/kWh")
        print(f"Annual energy cost: €{result['user_metrics']['annual_cost_eur']:,.0f}")
        
        # Benchmark results
        print(f"\n📊 BENCHMARK RESULTS")
        print(f"Peer group: {result['peer_group_size']} similar German companies")
        print(f"Energy efficiency ranking: {benchmarks['efficiency_percentile']:.0f}th percentile")
        print(f"Cost performance ranking: {benchmarks['cost_percentile']:.0f}th percentile")
        print(f"vs Peer median efficiency: {benchmarks['efficiency_vs_median_pct']:+.1f}%")
        print(f"vs Peer median cost: {benchmarks['cost_vs_median_pct']:+.1f}%")
        
        if benchmarks['vs_national_pct']:
            print(f"vs German national average: {benchmarks['vs_national_pct']:+.1f}%")
        
        # Savings potential
        savings = benchmarks['savings_potential']
        if savings['total_eur'] > 0:
            print(f"\n💰 SAVINGS POTENTIAL")
            if savings['efficiency_eur'] > 0:
                print(f"Efficiency improvements: €{savings['efficiency_eur']:,.0f}/year")
            if savings['cost_eur'] > 0:
                print(f"Cost optimization: €{savings['cost_eur']:,.0f}/year")
            print(f"TOTAL POTENTIAL: €{savings['total_eur']:,.0f}/year")
        
        # Key insights
        print(f"\n🎯 KEY INSIGHTS & RECOMMENDATIONS")
        for i, insight in enumerate(insights, 1):
            print(f"\n{i}. {insight['title']} [{insight['priority']}]")
            print(f"   {insight['message']}")
            print(f"   {insight['details']}")
            print(f"   → {insight['action']}")
            
            if 'recommendations' in insight:
                print("   Recommendations:")
                for rec in insight['recommendations'][:3]:  # Top 3 recommendations
                    print(f"   • {rec}")
        
        print("\n" + "="*60)
        print("✅ Benchmark analysis complete!")
        print("📊 Data source: Real German industrial energy statistics")
        print("🗓️ Generated:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

def run_example_benchmark():
    """Run an example benchmark analysis"""
    print("🚀 Running example German energy benchmark...")
    
    # Initialize benchmarker
    benchmarker = GermanEnergyBenchmarker()
    
    # Example company profile
    example_company = {
        'sector': 'Food Production',
        'region': 'Bayern',    
        'employees': 50,
        'annual_kwh': 726_935,      # 35,000 kWh/employee - inefficient but not terrible
        'cost_per_kwh': 0.1378         # Good negotiated rate
    }
    
    # Run benchmark
    result = benchmarker.benchmark_company(example_company)
    
    # Print report
    benchmarker.print_benchmark_report(result)
    
    return result

if __name__ == "__main__":
    # Run example
    result = run_example_benchmark()