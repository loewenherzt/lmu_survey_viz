"""
Data Quality Assessment Script
Finds and reports duplicate rows and data issues with detailed information.
"""

import pandas as pd


def load_data(filepath: str) -> pd.DataFrame:
    """Load the survey data from CSV with § separator."""
    df = pd.read_csv(filepath, sep='§', encoding='utf-8', engine='python')
    return df


def find_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Find duplicate rows and return detailed information.
    Returns a DataFrame with all duplicate rows including their row numbers.
    """
    # Add row number (1-indexed to match CSV line numbers, +1 for header)
    df_with_rows = df.copy()
    df_with_rows['CSV Row Number'] = range(2, len(df) + 2)  # Line 1 is header
    
    # Find duplicates (keep all occurrences)
    duplicates = df_with_rows[df_with_rows.duplicated(subset=df.columns.tolist(), keep=False)]
    
    return duplicates


def find_zero_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Find rows with zero values in numeric columns (potential invalid responses).
    """
    df_with_rows = df.copy()
    df_with_rows['CSV Row Number'] = range(2, len(df) + 2)
    
    zero_mask = (df['Emotional'] == 0) | (df['Pos / Neg'] == 0) | (df['Age Answer'] == 0)
    zero_rows = df_with_rows[zero_mask]
    
    return zero_rows


def check_participant_completeness(df: pd.DataFrame) -> dict:
    """
    Check if every participant has answered all questions.
    Questions are identified by their Page Ref.
    Returns a dict with missing info per participant.
    """
    # Get all unique questions (by Page Ref)
    all_questions = set(df['Page Ref'].unique())
    
    # Get all unique participants
    all_participants = df['Participant ID'].unique()
    
    # Check each participant
    missing = {}
    for participant in all_participants:
        participant_answers = set(df[df['Participant ID'] == participant]['Page Ref'].unique())
        missing_questions = all_questions - participant_answers
        if missing_questions:
            missing[participant] = sorted(missing_questions)
    
    return {
        'all_questions': sorted(all_questions),
        'total_questions': len(all_questions),
        'total_participants': len(all_participants),
        'missing_by_participant': missing,
        'complete_participants': len(all_participants) - len(missing)
    }


def main():
    input_file = '../data/input/umfrage.csv'
    output_file = '../data/output/data_issues.txt'
    
    print("Loading data...")
    df = load_data(input_file)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("DETAILED DATA ISSUES REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        # ==================== DUPLICATES ====================
        f.write("DUPLICATE ROWS\n")
        f.write("-" * 70 + "\n\n")
        
        duplicates = find_duplicates(df)
        
        if len(duplicates) == 0:
            f.write("No duplicate rows found.\n\n")
        else:
            f.write(f"Found {len(duplicates)} rows involved in duplication:\n\n")
            
            # Group duplicates to show which rows are duplicates of each other
            dup_groups = duplicates.groupby(list(df.columns))
            
            group_num = 1
            for _, group in dup_groups:
                if len(group) > 1:
                    f.write(f"Duplicate Group {group_num}:\n")
                    for _, row in group.iterrows():
                        f.write(f"  - CSV Row: {row['CSV Row Number']}, ")
                        f.write(f"Participant ID: {row['Participant ID']}, ")
                        f.write(f"Timestamp: {row['Timestamp']}\n")
                        f.write(f"    Text: {row['Text'][:60]}...\n")
                    f.write("\n")
                    group_num += 1
        
        # ==================== ZERO VALUES ====================
        f.write("\nROWS WITH ZERO VALUES (POTENTIAL INVALID RESPONSES)\n")
        f.write("-" * 70 + "\n\n")
        
        zero_rows = find_zero_values(df)
        
        if len(zero_rows) == 0:
            f.write("No rows with zero values found.\n\n")
        else:
            f.write(f"Found {len(zero_rows)} rows with zero values:\n\n")
            
            for _, row in zero_rows.iterrows():
                f.write(f"CSV Row: {row['CSV Row Number']}\n")
                f.write(f"  Participant ID: {row['Participant ID']}\n")
                f.write(f"  Timestamp: {row['Timestamp']}\n")
                f.write(f"  Item Type: {row['Item Type']}\n")
                f.write(f"  Emotional: {row['Emotional']}, Pos/Neg: {row['Pos / Neg']}, Age Answer: {row['Age Answer']}\n")
                f.write(f"  Text: {row['Text'][:60]}...\n")
                f.write("\n")
        
        # ==================== PARTICIPANT COMPLETENESS ====================
        f.write("\nPARTICIPANT QUESTION COMPLETENESS\n")
        f.write("-" * 70 + "\n\n")
        
        completeness = check_participant_completeness(df)
        
        f.write(f"Total unique questions (by Page Ref): {completeness['total_questions']}\n")
        f.write(f"Total participants: {completeness['total_participants']}\n")
        f.write(f"Participants with all questions: {completeness['complete_participants']}\n")
        f.write(f"Participants missing questions: {len(completeness['missing_by_participant'])}\n\n")
        
        if completeness['missing_by_participant']:
            f.write("Participants with missing questions:\n\n")
            for participant, missing_qs in completeness['missing_by_participant'].items():
                f.write(f"Participant: {participant}\n")
                f.write(f"  Missing {len(missing_qs)} question(s):\n")
                for q in missing_qs:
                    f.write(f"    - {q}\n")
                f.write("\n")
        else:
            f.write("All participants have answered all questions.\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("END OF REPORT\n")
    
    print(f"Report written to {output_file}")
    
    # Also print summary to console
    print(f"\nSummary:")
    print(f"  - Duplicate rows: {len(duplicates)}")
    print(f"  - Rows with zero values: {len(zero_rows)}")
    print(f"  - Participants missing questions: {len(completeness['missing_by_participant'])}")


if __name__ == '__main__':
    main()
