import pandas as pd
import os

def generate_summary():
    # Đọc file CSV từ thư mục result
    file_path = "result/"
    dfs = []
    
    # Dictionary để lưu kết quả cho mỗi dataset
    dataset_results = {}
    
    for file in os.listdir(file_path):
        if file.endswith('.csv'):
            df = pd.read_csv(file_path + file)
            dataset = df['Dataset'].iloc[0]
            
            # Thêm vào dictionary
            if dataset not in dataset_results:
                dataset_results[dataset] = []
            dataset_results[dataset].append(df)
    
    # Tạo summary cho mỗi dataset
    summary_rows = []
    
    obj_compare = {
        '1.txt': 0,
        '2.txt': 2046,
        '3.txt': 0,
        '4.txt': 1878,
        '5.txt': 1664,
        '6.txt': 1170,
        '7.txt': 66,
        '8.txt': 0,
        '9.txt': 2520,
        '10.txt': 44
    }

    for dataset, results in dataset_results.items():
        # Gộp tất cả kết quả của dataset
        df_combined = pd.concat(results)
        
        # Tính các thống kê
        best_solution = df_combined['Distance'].min()
        worst_solution = df_combined['Distance'].max()
        avg_solution = df_combined['Distance'].mean()
        std_solution = df_combined['Distance'].std()
        avg_time = df_combined['Execution Time (s)'].mean()
        
        # Lấy path của best solution
        best_path = df_combined.loc[df_combined['Distance'].idxmin()]['Path']
        
        # Tính Gap
        obj_cmp = obj_compare[dataset]
        gap = ((best_solution - obj_cmp) / obj_cmp * 100) if obj_cmp != 0 else 0
        
        summary_rows.append({
            'Dataset': dataset,
            'Best': best_solution,
            'Worst': worst_solution,
            'Average': round(avg_solution, 2),
            'Std Dev': round(std_solution, 2),
            'Avg Time (s)': round(avg_time, 2),
            'Best Path': best_path,
            'Obj_Cmp': obj_cmp,
            'Gap (%)': round(gap, 2)
        })

    # Tạo DataFrame từ summary
    summary_df = pd.DataFrame(summary_rows)
    
    # Sắp xếp theo tên dataset
    summary_df = summary_df.sort_values('Dataset')
    
    # Ghi vào Excel
    with pd.ExcelWriter('summary_report.xlsx') as writer:
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Format Summary sheet
        worksheet = writer.sheets['Summary']
        worksheet.column_dimensions['A'].width = 15  # Dataset
        worksheet.column_dimensions['B'].width = 12  # Best
        worksheet.column_dimensions['C'].width = 12  # Worst
        worksheet.column_dimensions['D'].width = 12  # Average
        worksheet.column_dimensions['E'].width = 12  # Std Dev
        worksheet.column_dimensions['F'].width = 15  # Avg Time
        worksheet.column_dimensions['G'].width = 50  # Best Path
        worksheet.column_dimensions['H'].width = 12  # Obj_Cmp
        worksheet.column_dimensions['I'].width = 12  # Gap

if __name__ == "__main__":
    generate_summary()