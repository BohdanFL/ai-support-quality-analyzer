from typing import Dict, List, Any
import argparse
import json
from pathlib import Path
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

class SupportChatAggregator:
    """Aggregate and process support chat data for analytics"""
    
    def __init__(self, chats_path: str, results_path: str):
        """
        Initialize with paths to data files
        
        Args:
            chats_path: Path to generated_chats.json
            results_path: Path to analysis_results.json
        """
        self.chats_path = Path(chats_path)
        self.results_path = Path(results_path)
        self.chats_data = None
        self.results_data = None
        self.df = None
        
    def load_data(self) -> None:
        """Load JSON data files"""
        print("Loading data files...")
        
        with open(self.chats_path, 'r', encoding='utf-8') as f:
            self.chats_data = json.load(f)
            
        with open(self.results_path, 'r', encoding='utf-8') as f:
            self.results_data = json.load(f)
            
        print(f"Loaded {len(self.chats_data)} chats and {len(self.results_data)} analysis results")
        
    def create_dataframe(self) -> pd.DataFrame:
        """Create unified DataFrame from chats and results"""
        
        records = []
        
        for i, result_item in enumerate(self.results_data):
            # Get the analysis data (nested under "analysis" -> "result")
            analysis_wrapper = result_item.get('analysis', {})
            analysis = analysis_wrapper.get('result', {})
            original_chat = result_item.get('original_chat', {})
            
            # Basic chat info
            record = {
                'chat_id': result_item.get('chat_id', i),
                'scenario': original_chat.get('scenario', 'unknown'),
                'scenario_type': original_chat.get('type', 'unknown'),
                'message_count': len(original_chat.get('messages', [])),
                
                # Analysis results
                'intent': analysis.get('intent', 'unknown'),
                'satisfaction': analysis.get('satisfaction', 'unknown'),
                'quality_score': analysis.get('quality_score', 0),
                'rationale': analysis.get('thought_process', ''),
                
                # Process agent mistakes
                'has_mistakes': False,
                'mistake_count': 0,
            }
            
            # Handle agent mistakes
            mistakes = analysis.get('agent_mistakes', ['none'])
            if mistakes and mistakes != ['none']:
                record['has_mistakes'] = True
                record['mistake_count'] = len(mistakes)
                
                # Create boolean columns for each mistake type
                for mistake in ['ignored_question', 'incorrect_info', 'rude_tone', 
                               'no_resolution', 'unnecessary_escalation']:
                    record[f'mistake_{mistake}'] = mistake in mistakes
            else:
                record['has_mistakes'] = False
                record['mistake_count'] = 0
                for mistake in ['ignored_question', 'incorrect_info', 'rude_tone', 
                               'no_resolution', 'unnecessary_escalation']:
                    record[f'mistake_{mistake}'] = False
            
            records.append(record)
        
        self.df = pd.DataFrame(records)
        return self.df
    
    def calculate_kpis(self) -> Dict[str, Any]:
        """Calculate high-level business metrics"""
        
        if self.df is None:
            raise ValueError("DataFrame not created. Run create_dataframe() first.")
        
        kpis = {}
        
        # 1. Average Quality Score (AQS)
        kpis['avg_quality_score'] = round(self.df['quality_score'].mean(), 2)
        kpis['quality_score_std'] = round(self.df['quality_score'].std(), 2)
        
        # 2. Customer Satisfaction Score (CSAT)
        satisfaction_counts = self.df['satisfaction'].value_counts(normalize=True)
        kpis['satisfaction_distribution'] = {
            'satisfied': round(satisfaction_counts.get('satisfied', 0) * 100, 1),
            'neutral': round(satisfaction_counts.get('neutral', 0) * 100, 1),
            'unsatisfied': round(satisfaction_counts.get('unsatisfied', 0) * 100, 1)
        }
        
        # 3. Mistake Rate
        kpis['mistake_rate'] = round(
            (self.df['has_mistakes'].sum() / len(self.df)) * 100, 1
        )
        kpis['avg_mistakes_per_chat'] = round(self.df['mistake_count'].mean(), 2)
        
        # 4. Hidden Dissatisfaction Rate
        # Customers who are "satisfied" but still have unresolved issues
        hidden_dissat = self.df[
            (self.df['satisfaction'] == 'satisfied') & 
            (self.df['mistake_no_resolution'] == True)
        ]
        kpis['hidden_dissatisfaction_rate'] = round(
            (len(hidden_dissat) / len(self.df)) * 100, 1
        )
        
        return kpis
    
    def create_intent_quality_matrix(self) -> pd.DataFrame:
        """Create intent vs quality score matrix"""
        
        intent_stats = self.df.groupby('intent').agg({
            'quality_score': ['mean', 'std', 'count'],
            'has_mistakes': 'mean',
            'mistake_count': 'mean'
        }).round(2)
        
        intent_stats.columns = ['avg_quality', 'std_quality', 'chat_count', 
                               'mistake_rate', 'avg_mistakes']
        intent_stats['mistake_rate'] = (intent_stats['mistake_rate'] * 100).round(1)
        
        return intent_stats.sort_values('avg_quality', ascending=False)
    
    def create_mistake_pareto(self) -> pd.DataFrame:
        """Create Pareto analysis of mistakes"""
        
        mistake_cols = ['mistake_ignored_question', 'mistake_incorrect_info', 
                       'mistake_rude_tone', 'mistake_no_resolution', 
                       'mistake_unnecessary_escalation']
        
        mistake_counts = self.df[mistake_cols].sum().sort_values(ascending=False)
        mistake_df = pd.DataFrame({
            'mistake_type': mistake_counts.index.str.replace('mistake_', ''),
            'count': mistake_counts.values,
            'percentage': (mistake_counts.values / mistake_counts.sum() * 100).round(1)
        })
        
        # Calculate cumulative percentage for Pareto
        mistake_df['cumulative_percentage'] = mistake_df['percentage'].cumsum().round(1)
        
        return mistake_df
    
    def save_to_csv(self, output_path: str = 'support_analytics.csv'):
        """Save aggregated data to CSV"""
        if self.df is not None:
            self.df.to_csv(output_path, index=False)
            print(f"Data saved to {output_path}")
    
    def run_complete_analysis(self):
        """Run complete analysis pipeline"""
        
        print("=" * 50)
        print("SUPPORT CHAT ANALYTICS - COMPLETE ANALYSIS")
        print("=" * 50)
        
        # Load and process data
        self.load_data()
        self.create_dataframe()
        
        # Calculate KPIs
        kpis = self.calculate_kpis()
        print("\n🔹 HIGH-LEVEL KPIs")
        print("-" * 30)
        print(f"Average Quality Score (AQS): {kpis['avg_quality_score']}/5.0")
        print(f"Quality Score Std Dev: ±{kpis['quality_score_std']}")
        print(f"\nCustomer Satisfaction (CSAT):")
        print(f"  😊 Satisfied: {kpis['satisfaction_distribution']['satisfied']}%")
        print(f"  😐 Neutral: {kpis['satisfaction_distribution']['neutral']}%")
        print(f"  ☹️ Unsatisfied: {kpis['satisfaction_distribution']['unsatisfied']}%")
        print(f"\nMistake Rate: {kpis['mistake_rate']}% of chats")
        print(f"Hidden Dissatisfaction: {kpis['hidden_dissatisfaction_rate']}%")
        
        # Intent vs Quality Matrix
        print("\n🔹 INTENT VS QUALITY MATRIX")
        print("-" * 30)
        if not self.df.empty:
            intent_matrix = self.create_intent_quality_matrix()
            print(intent_matrix.to_string())
        else:
            print("No data available")
        
        # Pareto Analysis
        print("\n🔹 PARETO ANALYSIS - MISTAKE DISTRIBUTION")
        print("-" * 30)
        if not self.df.empty:
            mistake_pareto = self.create_mistake_pareto()
            print(mistake_pareto.to_string(index=False))
        else:
            print("No mistakes data available")
        
        # Business Insights
        print("\n🔹 BUSINESS INSIGHTS")
        print("-" * 30)
        
        if not self.df.empty:
            # Find weakest intent
            intent_matrix = self.create_intent_quality_matrix()
            weakest_intent = intent_matrix.iloc[-1]
            print(f"⚠️  Lowest quality intent: {weakest_intent.name} "
                  f"(avg score: {weakest_intent['avg_quality']}/5.0)")
            
            # Pareto insight
            mistake_pareto = self.create_mistake_pareto()
            if len(mistake_pareto) >= 2:
                top_mistakes = mistake_pareto.head(2)
                if top_mistakes['cumulative_percentage'].iloc[1] >= 70:
                    print(f"📊 Pareto principle applies: Top 2 mistakes account for "
                          f"{top_mistakes['cumulative_percentage'].iloc[1]}% of all issues")
                    print(f"   Focus on: {', '.join(top_mistakes['mistake_type'].tolist())}")
        else:
            print("No data available for insights")
        
        return self.df, kpis


def main():
    parser = argparse.ArgumentParser(description="Aggregate and process support chat data for analytics")
    parser.add_argument("--chats", type=str, default="data\examples\groq_dataset_260.json", help="Path to generated chats JSON")
    parser.add_argument("--results", type=str, default="data\examples\groq_analysis_130.json", help="Path to analysis results JSON")
    parser.add_argument("--output", type=str, default="analytics/support_analytics.csv", help="Output CSV path")
    
    args = parser.parse_args()
    
    if not Path(args.chats).exists():
        print(f"Error: Chats file {args.chats} not found.")
        return
    if not Path(args.results).exists():
        print(f"Error: Results file {args.results} not found.")
        return

    # Initialize aggregator
    aggregator = SupportChatAggregator(
        chats_path=args.chats,
        results_path=args.results
    )
    
    # Run analysis
    df, kpis = aggregator.run_complete_analysis()
    
    # Save processed data
    aggregator.save_to_csv(args.output)
    
    # Show sample of the data
    print("\n📊 Sample of processed data:")
    if df is not None and not df.empty:
        print(df[['chat_id', 'intent', 'satisfaction', 'quality_score', 'has_mistakes']].head())

if __name__ == "__main__":
    main()