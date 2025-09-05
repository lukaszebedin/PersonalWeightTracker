import pandas as pd
from datetime import datetime
import argparse

def process_csv(input_file: str, output_file: str) -> None:
    """
    Process CSV file by adding additional columns and reformatting the date.
    Skips lines without Raw values.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save the output CSV file
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Drop rows where Raw is NaN
        df = df.dropna(subset=['Raw'])

        # Convert date string to datetime
        df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')

        # Convert Raw column to float, replacing comma with dot
        df['Raw'] = df['Raw'].str.replace(',', '.').astype(float)

        # Create new columns
        df['day_of_week'] = df['date'].dt.day_name()  # Get full day name
        df['month'] = df['date'].dt.strftime('%B')  # Get full month name
        df['weight_diff'] = df['Raw'].diff()  # Calculate difference with previous row

        # Reorder columns and format date
        df['date'] = df['date'].dt.strftime('%Y-%m-%d 00:00:00')

        # Rename 'Raw' column to 'weight'
        df = df.rename(columns={'Raw': 'weight'})

        # Arrange columns in desired order
        df = df[['date', 'weight', 'day_of_week', 'weight_diff', 'month']]

        # Write to new CSV file
        df.to_csv(output_file, index=False)
        print(f"Successfully processed {input_file} and saved results to {output_file}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    """
    Parse command line arguments and call the process_csv function.
    """
    parser = argparse.ArgumentParser(description='Process CSV file to add additional columns and reformat date.')
    parser.add_argument('input_file', type=str, help='Path to the input CSV file')
    parser.add_argument('output_file', type=str, help='Path to save the output CSV file')
    
    args = parser.parse_args()
    
    process_csv(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
