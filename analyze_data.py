"""
Survey Data Analysis Script
Analyzes umfrage.csv and outputs results.csv and assessment.txt
"""

import pandas as pd
import numpy as np
from scipy import stats


def load_data(filepath: str) -> pd.DataFrame:
    """Load the survey data from CSV with § separator."""
    df = pd.read_csv(filepath, sep='§', encoding='utf-8', engine='python')
    return df


def compute_statistics(df: pd.DataFrame) -> dict:
    """
    Compute mean and median for key columns, grouped by Item Type.
    Returns a dictionary with all statistics.
    """
    results = {}
    
    for item_type in ['Stimulus', 'Distraktor']:
        subset = df[df['Item Type'] == item_type]
        prefix = item_type.lower()
        
        # Emotional column
        results[f'{prefix}_emotional_mean'] = subset['Emotional'].mean()
        results[f'{prefix}_emotional_median'] = subset['Emotional'].median()
        
        # Pos / Neg column
        results[f'{prefix}_pos_neg_mean'] = subset['Pos / Neg'].mean()
        results[f'{prefix}_pos_neg_median'] = subset['Pos / Neg'].median()
        
        # Suitability Age (Age Answer where Age Question Type == 'suitability')
        suitability = subset[subset['Age Question Type'] == 'suitability']['Age Answer']
        results[f'{prefix}_suitability_age_mean'] = suitability.mean()
        results[f'{prefix}_suitability_age_median'] = suitability.median()
        
        # Recommended Age (Age Answer where Age Question Type == 'age_recommendation')
        recommended = subset[subset['Age Question Type'] == 'age_recommendation']['Age Answer']
        results[f'{prefix}_recommended_age_mean'] = recommended.mean()
        results[f'{prefix}_recommended_age_median'] = recommended.median()
    
    return results


def compute_correlations(df: pd.DataFrame) -> dict:
    """
    Compute Pearson correlations between Pos/Neg, Emotional, and Age columns.
    - emotional_vs_pos_neg: computed on ALL data
    - Age correlations: computed separately for suitability and age_recommendation question types
    """
    correlations = {}
    
    # Emotional vs Pos/Neg - computed on ALL data
    if len(df) > 2:
        corr, _ = stats.pearsonr(df['Emotional'], df['Pos / Neg'])
        correlations['emotional_vs_pos_neg'] = corr
    
    # Suitability age correlations
    suitability_data = df[df['Age Question Type'] == 'suitability']
    if len(suitability_data) > 2:
        corr, _ = stats.pearsonr(suitability_data['Emotional'], suitability_data['Age Answer'])
        correlations['emotional_vs_age_suitability'] = corr
        
        corr, _ = stats.pearsonr(suitability_data['Pos / Neg'], suitability_data['Age Answer'])
        correlations['pos_neg_vs_age_suitability'] = corr
    
    # Recommended age correlations
    recommended_data = df[df['Age Question Type'] == 'age_recommendation']
    if len(recommended_data) > 2:
        corr, _ = stats.pearsonr(recommended_data['Emotional'], recommended_data['Age Answer'])
        correlations['emotional_vs_age_recommended'] = corr
        
        corr, _ = stats.pearsonr(recommended_data['Pos / Neg'], recommended_data['Age Answer'])
        correlations['pos_neg_vs_age_recommended'] = corr
    
    return correlations


def write_results(statistics: dict, correlations: dict, filepath: str):
    """Write all computed values to a CSV file."""
    # Combine all results
    all_results = {**statistics, **correlations}
    
    # Create DataFrame with metric names and values
    results_df = pd.DataFrame([
        {'Metric': k, 'Value': v} for k, v in all_results.items()
    ])
    
    results_df.to_csv(filepath, index=False)
    print(f"Results written to {filepath}")


def assess_data(df: pd.DataFrame, filepath: str):
    """Assess data completeness and write findings to a text file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("DATA QUALITY ASSESSMENT\n")
        f.write("=" * 50 + "\n\n")
        
        # Basic info
        f.write(f"Total rows: {len(df)}\n")
        f.write(f"Total columns: {len(df.columns)}\n\n")
        
        # Unique participants
        unique_participants = df['Participant ID'].nunique()
        f.write(f"Unique participants: {unique_participants}\n\n")
        
        # Item type distribution
        f.write("Item Type distribution:\n")
        for item_type, count in df['Item Type'].value_counts().items():
            f.write(f"  - {item_type}: {count} rows\n")
        f.write("\n")
        
        # Age Question Type distribution
        f.write("Age Question Type distribution:\n")
        for q_type, count in df['Age Question Type'].value_counts().items():
            f.write(f"  - {q_type}: {count} rows\n")
        f.write("\n")
        
        # Missing values
        f.write("Missing values per column:\n")
        missing = df.isnull().sum()
        has_missing = False
        for col, count in missing.items():
            if count > 0:
                f.write(f"  - {col}: {count} missing\n")
                has_missing = True
        if not has_missing:
            f.write("  No missing values found.\n")
        f.write("\n")
        
        # Duplicate rows
        duplicates = df.duplicated().sum()
        f.write(f"Duplicate rows: {duplicates}\n")
        if duplicates > 0:
            f.write("  WARNING: There are duplicate rows in the dataset.\n")
            # Show which rows are duplicated
            dup_rows = df[df.duplicated(keep=False)]
            f.write(f"  Rows involved in duplication: {len(dup_rows)}\n")
        f.write("\n")
        
        # Check for zero/null answers (potential invalid responses)
        zero_emotional = (df['Emotional'] == 0).sum()
        zero_pos_neg = (df['Pos / Neg'] == 0).sum()
        zero_age = (df['Age Answer'] == 0).sum()
        
        if zero_emotional > 0 or zero_pos_neg > 0 or zero_age > 0:
            f.write("Potential invalid responses (zero values):\n")
            if zero_emotional > 0:
                f.write(f"  - Emotional = 0: {zero_emotional} rows\n")
            if zero_pos_neg > 0:
                f.write(f"  - Pos / Neg = 0: {zero_pos_neg} rows\n")
            if zero_age > 0:
                f.write(f"  - Age Answer = 0: {zero_age} rows\n")
            f.write("\n")
        
        # Summary
        f.write("=" * 50 + "\n")
        f.write("SUMMARY:\n")
        if duplicates == 0 and not has_missing:
            f.write("The data appears to be complete with no missing values.\n")
        else:
            f.write("The data has some quality issues that may need attention.\n")
        
        if duplicates > 0:
            f.write(f"- {duplicates} duplicate rows should be reviewed.\n")
    
    print(f"Assessment written to {filepath}")


def main():
    # File paths (relative to project root)
    input_file = '../data/input/umfrage.csv'
    results_file = '../data/output/results.csv'
    assessment_file = '../data/output/assessment.txt'
    
    # Load data
    print("Loading data...")
    df = load_data(input_file)
    print(f"Loaded {len(df)} rows")
    
    # Compute statistics
    print("Computing statistics...")
    statistics = compute_statistics(df)
    
    # Compute correlations
    print("Computing correlations...")
    correlations = compute_correlations(df)
    
    # Write results
    print("Writing results...")
    write_results(statistics, correlations, results_file)
    
    # Assess data
    print("Assessing data quality...")
    assess_data(df, assessment_file)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
