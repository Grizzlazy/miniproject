import pandas as pd
import os

def generate_summary():
    # Đọc file CSV
    df = pd.read_csv('results.csv')
    
    # Tạo summary
    summary = {
        'Total Datasets': len(df),
        'Average Distance': df['Distance'].mean(),
        'Min Distance': df['Distance'].min(),
        'Max Distance': df['Distance'].max(),
        'Average Path Length': df['Path Length'].mean(),
        'Average Execution Time': df['Execution Time (s)'].mean(),
        'Min Execution Time': df['Execution Time (s)'].min(),
        'Max Execution Time': df['Execution Time (s)'].max()
    }
    
    # Tạo summary theo từng dataset
    dataset_summary = df.groupby('Dataset').agg({
        'Distance': ['mean', 'min', 'max'],
        'Path Length': 'mean',
        'Execution Time (s)': ['mean', 'min', 'max']
    }).round(3)
    
    # Lưu kết quả vào file
    with open('summary_report.txt', 'w') as f:
        f.write("=== OVERALL SUMMARY ===\n\n")
        for key, value in summary.items():
            f.write(f"{key}: {value:.3f}\n")
            
        f.write("\n\n=== DATASET SUMMARY ===\n\n")
        f.write(dataset_summary.to_string())
        
        f.write("\n\n=== BEST SOLUTIONS ===\n\n")
        best_solutions = df.loc[df.groupby('Dataset')['Distance'].idxmin()]
        for _, row in best_solutions.iterrows():
            f.write(f"Dataset: {row['Dataset']}\n")
            f.write(f"Distance: {row['Distance']:.3f}\n")
            f.write(f"Path Length: {row['Path Length']}\n")
            f.write(f"Path: {row['Path']}\n")
            f.write(f"Execution Time: {row['Execution Time (s)']:.3f}s\n")
            f.write("-" * 50 + "\n")

if __name__ == "__main__":
    if not os.path.exists('results.csv'):
        print("Error: results.csv not found!")
    else:
        generate_summary()
        print("Summary generated in summary_report.txt")