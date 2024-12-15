import pandas as pd
import os

def generate_summary():
    # Đọc file CSV từ thư mục result
    file_path = "result/"
    dfs = []
    for file in os.listdir(file_path):
        if file.endswith('.csv'):
            df = pd.read_csv(file_path + file)
            dfs.append(df)
    
    # Gộp tất cả dataframes
    if dfs:
        df = pd.concat(dfs, ignore_index=True)
        
        # Add obj_compare values
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
        
        # Add obj_compare column to df
        df['Obj_Compare'] = df['Dataset'].map(obj_compare)
        
        # Calculate Gap percentage
        df['Gap (%)'] = ((df['Distance'] - df['Obj_Compare']) / df['Obj_Compare'] * 100).round(2)

        # Tạo best solutions summary
        best_solutions = df.loc[df.groupby('Dataset')['Distance'].idxmin()][
            ['Dataset', 'Path Length', 'Distance', 'Execution Time (s)', 'Path', 'Obj_Compare', 'Gap (%)']
        ].rename(columns={
            'Distance': 'Solution',
            'Execution Time (s)': 'Time',
            'Obj_Compare': 'Obj_Cmp'
        })

        # Sắp xếp lại các cột theo thứ tự yêu cầu
        best_solutions = best_solutions[['Dataset', 'Path Length', 'Solution', 'Time', 'Path', 'Obj_Cmp', 'Gap (%)']]
        
        # Sắp xếp theo tên dataset
        best_solutions = best_solutions.sort_values('Dataset')
        
        # Ghi vào Excel
        with pd.ExcelWriter('summary_report.xlsx') as writer:
            best_solutions.to_excel(writer, sheet_name='Best Solutions', index=False)
            
            # Format Best Solutions sheet
            worksheet = writer.sheets['Best Solutions']
            worksheet.column_dimensions['A'].width = 15  # Dataset
            worksheet.column_dimensions['B'].width = 12  # Path Length
            worksheet.column_dimensions['C'].width = 12  # Solution
            worksheet.column_dimensions['D'].width = 12  # Time
            worksheet.column_dimensions['E'].width = 50  # Path
            worksheet.column_dimensions['F'].width = 12  # Obj_Cmp
            worksheet.column_dimensions['G'].width = 12  # Gap

if __name__ == "__main__":
    generate_summary()