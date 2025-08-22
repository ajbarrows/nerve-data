import os
import pandas as pd
from pathlib import Path
from collections import defaultdict


def scan_bids_directory(bids_dir):
    """
    Scan a BIDS directory and return a DataFrame with subject-session combinations
    and imaging modality indicators.
    
    Parameters:
    -----------
    bids_dir : str or Path
        Path to the BIDS directory
    
    Returns:
    --------
    pd.DataFrame
        DataFrame where each row is a subject-session combination and each column
        is a boolean indicator for imaging modalities (anat, dwi, fmap, func, motion, mrs)
    """
    bids_path = Path(bids_dir)
    
    # Define modalities to look for
    modalities = ['anat', 'dwi', 'fmap', 'func', 'motion', 'mrs']
    
    # List to store data
    data = []
    
    # Iterate through subjects
    for subject_dir in bids_path.glob('sub-*'):
        if not subject_dir.is_dir():
            continue
            
        subject_id = subject_dir.name
        
        # Check for session directories
        session_dirs = list(subject_dir.glob('ses-*'))
        
        if session_dirs:
            # Multi-session dataset
            for session_dir in session_dirs:
                if not session_dir.is_dir():
                    continue
                    
                session_id = session_dir.name
                row = {'subject': subject_id, 'session': session_id}
                
                # Check each modality
                for modality in modalities:
                    modality_dir = session_dir / modality
                    row[modality] = modality_dir.exists() and any(modality_dir.iterdir())
                
                data.append(row)
        else:
            # Single-session dataset (no ses- directories)
            row = {'subject': subject_id, 'session': 'ses-01'}  # Default session name
            
            # Check each modality directly under subject
            for modality in modalities:
                modality_dir = subject_dir / modality
                row[modality] = modality_dir.exists() and any(modality_dir.iterdir())
            
            data.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Sort by subject and session
    df = df.sort_values(['subject', 'session']).reset_index(drop=True)

    summary_table = (
        df
        .set_index('subject')
        .melt(id_vars='session')
        .groupby('variable')
        .value_counts()
        .reset_index()
        .query("value")
        .pivot(
            index='session',
            columns='variable',
            values='count'
        )
)
    
    return df, summary_table, df['subject'].nunique()
