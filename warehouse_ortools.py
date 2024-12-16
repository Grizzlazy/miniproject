import ortools.sat.python.cp_model as cp_model
from input import read_input_from_file
import os
import csv
import time

def solve_warehouse(file_name):
    file_path = "data/" + file_name
    N, M, Q, d, q = read_input_from_file(file_path)
    
    model = cp_model.CpModel()
    
    # Optimize variable creation
    x = {}
    for i in range(M + 1):
        for j in range(M + 1):
            if i != j:
                if i == 0 or j == 0 or i < j:
                    x[i, j] = model.NewBoolVar(f'x_{i}_{j}')
                    if i > 0 and j > 0:
                        x[j, i] = model.NewBoolVar(f'x_{j}_{i}')

    # Tối ưu biến u bằng cách giảm bound
    max_u = min(M, sum(q))
    u = {i: model.NewIntVar(1, max_u, f'u_{i}') for i in range(1, M + 1)}

    # Tối ưu biến y
    y = {}
    for i in range(N):
        max_possible = min(sum(Q[i]), max(q) * M)
        y[i] = model.NewIntVar(q[i], max_possible, f'y_{i}')

    # Tối ưu objective
    max_distance = max(max(row) for row in d)
    obj = model.NewIntVar(0, max_distance * (M + 1), 'obj')
    model.Minimize(obj)

    # Các ràng buộc
    model.Add(sum(x[0, j] for j in range(1, M + 1) if (0, j) in x) == 1)
    model.Add(sum(x[i, 0] for i in range(1, M + 1) if (i, 0) in x) == 1)

    for i in range(1, M + 1):
        outgoing = sum(x[i, j] for j in range(M + 1) if i != j and (i, j) in x)
        incoming = sum(x[j, i] for j in range(M + 1) if i != j and (j, i) in x)
        model.Add(outgoing == incoming)

    for i in range(1, M + 1):
        for j in range(1, M + 1):
            if i != j and (i, j) in x:
                model.Add(u[j] >= u[i] + 1).OnlyEnforceIf(x[i, j])

    # Tối ưu ràng buộc sản phẩm
    for k in range(N):
        product_sum = []
        for i in range(1, M + 1):
            for j in range(M + 1):
                if i != j and (i, j) in x:
                    product_sum.append(x[i, j] * Q[k][i-1])
        model.Add(y[k] == sum(product_sum))
        model.Add(y[k] >= q[k])

    # Tối ưu objective constraint
    distance_sum = []
    for i in range(M + 1):
        for j in range(M + 1):
            if i != j and (i, j) in x:
                distance_sum.append(x[i, j] * d[i][j])
    model.Add(obj == sum(distance_sum))

    # Giải
    start_time = time.time()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 300.0
    status = solver.Solve(model)
    execution_time = time.time() - start_time

    # Xử lý và ghi kết quả
    result_file = file_name + ".csv"
    file_exists = os.path.isfile(result_file)

    with open(result_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Dataset', 'Status', 'Distance', 'Path Length', 'Path', 'Execution Time (s)'])
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            route = []
            current = 0
            while True:
                next_point = None
                for j in range(1, M + 1):
                    if (current, j) in x and solver.Value(x[current, j]) == 1:
                        next_point = j
                        break
                if next_point is None or len(route) >= M:
                    break
                route.append(next_point)
                current = next_point

            status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
            writer.writerow([
                file_name,
                status_str,
                solver.Value(obj),
                len(route),
                ' '.join(map(str, route)),
                execution_time
            ])
            
            print(f"Status: {status_str}")
            print(f"Distance: {solver.Value(obj)}")
            print(f"Path length: {len(route)}")
            print(f"Path: {' '.join(map(str, route))}")
        else:
            status_str = {
                cp_model.INFEASIBLE: "INFEASIBLE",
                cp_model.MODEL_INVALID: "INVALID",
                cp_model.UNKNOWN: "UNKNOWN"
            }.get(status, "UNKNOWN")
            writer.writerow([file_name, status_str, -1, 0, "No path found", execution_time])
            print(f"Status: {status_str}")
        
        print(f"Execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    file_name = str(os.getenv('dataset', '1.txt'))
    solve_warehouse(file_name)