import ortools.sat.python.cp_model as cp_model
from input import read_input_from_file
import os
import csv
import time

file_name = str(os.getenv('data_set'))
file_path = "data/" + file_name
N, M, Q, d, q = read_input_from_file(file_path)

model = cp_model.CpModel()

x = {}
for i in range(M + 1):
    for j in range(M + 1):
        if i != j:
            if i == 0 or j == 0:
                x[i, j] = model.NewBoolVar(f'x_{i}_{j}')
            elif i < j:
                x[i, j] = model.NewBoolVar(f'x_{i}_{j}')
                x[j, i] = model.NewBoolVar(f'x_{j}_{i}')

u = {i: model.NewIntVar(1, min(M, sum(q)), f'u_{i}') for i in range(1, M + 1)}

y = {}
for i in range(N):
    max_possible = min(sum(Q[i]), max(q) * M) 
    y[i] = model.NewIntVar(q[i], max_possible, f'y_{i}')

max_distance = max(max(row) for row in d)
obj = model.NewIntVar(0, max_distance * (M + 1), 'obj')
model.Minimize(obj)

# Ràng buộc xuất phát và kết thúc
model.Add(sum(x[0, j] for j in range(1, M + 1) if (0, j) in x) == 1)
model.Add(sum(x[i, 0] for i in range(1, M + 1) if (i, 0) in x) == 1)

# Ràng buộc luồng
for i in range(1, M + 1):
    model.Add(
        sum(x[i, j] for j in range(M + 1) if i != j and (i, j) in x) ==
        sum(x[j, i] for j in range(M + 1) if i != j and (j, i) in x)
    )

# Ràng buộc MTZ
for i in range(1, M + 1):
    for j in range(1, M + 1):
        if i != j and (i, j) in x:
            model.Add(u[j] >= u[i] + 1).OnlyEnforceIf(x[i, j])

# Ràng buộc sản phẩm
for k in range(N):
    model.Add(
        y[k] == sum(x[i, j] * Q[k][i-1] 
                   for i in range(1, M + 1) 
                   for j in range(M + 1) 
                   if i != j and (i, j) in x)
    )
    model.Add(y[k] >= q[k])

# Ràng buộc objective
model.Add(
    obj == sum(x[i, j] * d[i][j] 
              for i in range(M + 1) 
              for j in range(M + 1) 
              if i != j and (i, j) in x)
)

# Đo thời gian thực thi
start_time = time.time()

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 3600.0
status = solver.Solve(model)

end_time = time.time()
execution_time = end_time - start_time

# Xử lý kết quả và ghi vào file CSV
result_file = file_name + ".csv"
file_exists = os.path.isfile(result_file)

with open(result_file, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Ghi header nếu file chưa tồn tại
    if not file_exists:
        writer.writerow(['Dataset', 'Status', 'Distance', 'Path Length', 'Path', 'Execution Time (s)'])
    
    # Chuẩn bị dữ liệu để ghi
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        visited = [i for i in range(1, M + 1) 
                  if any(solver.Value(x[i, j]) == 1 
                        for j in range(M + 1) 
                        if i != j and (i, j) in x)]
        
        route = []
        current = 0
        while len(route) < len(visited):
            next_point = next(j for j in range(1, M + 1) 
                            if (current, j) in x and solver.Value(x[current, j]) == 1)
            route.append(next_point)
            current = next_point
        
        status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
        distance = solver.Value(obj)
        path_str = ' '.join(map(str, route))
        path_length = len(route)
        
    else:
        status_str = {
            cp_model.INFEASIBLE: "INFEASIBLE",
            cp_model.MODEL_INVALID: "INVALID",
            cp_model.UNKNOWN: "UNKNOWN"
        }.get(status, "UNKNOWN")
        distance = -1
        path_str = "No path found"
        path_length = 0
    
    # Ghi kết quả
    writer.writerow([file_name, status_str, distance, path_length, path_str, execution_time])

# In kết quả ra console
print(f"Status: {status_str}")
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"Distance: {distance}")
    print(f"Path length: {path_length}")
    print(f"Path: {path_str}")
print(f"Execution time: {execution_time:.2f} seconds")