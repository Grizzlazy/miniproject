from ortools.linear_solver import pywraplp
from input import read_input_from_file
import os
import csv
import time

def solve_warehouse(file_name):
    file_path = "data/" + file_name
    N, M, Q, d, q = read_input_from_file(file_path)
    
    # Tạo solver ILP
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return

    # Biến quyết định x[i,j] = 1 nếu đi từ i đến j
    x = {}
    for i in range(M + 1):
        for j in range(M + 1):
            if i != j:
                x[i, j] = solver.IntVar(0, 1, f'x_{i}_{j}')

    # Biến phụ u[i] cho ràng buộc MTZ
    u = {}
    for i in range(1, M + 1):
        u[i] = solver.IntVar(1, M, f'u_{i}')

    # Biến y[k] cho số lượng sản phẩm k thu được
    y = {}
    for i in range(N):
        max_possible = min(sum(Q[i]), max(q) * M)
        y[i] = solver.IntVar(q[i], max_possible, f'y_{i}')

    # Ràng buộc xuất phát từ depot
    solver.Add(solver.Sum([x[0, j] for j in range(1, M + 1)]) == 1)
    
    # Ràng buộc quay về depot
    solver.Add(solver.Sum([x[i, 0] for i in range(1, M + 1)]) == 1)

    # Ràng buộc luồng
    for i in range(1, M + 1):
        solver.Add(
            solver.Sum([x[i, j] for j in range(M + 1) if j != i]) ==
            solver.Sum([x[j, i] for j in range(M + 1) if j != i])
        )
        # Mỗi điểm chỉ được đến một lần
        solver.Add(solver.Sum([x[j, i] for j in range(M + 1) if j != i]) == 1)

    # Ràng buộc MTZ cho sub-tour elimination
    big_M = M + 1
    for i in range(1, M + 1):
        for j in range(1, M + 1):
            if i != j:
                solver.Add(u[j] >= u[i] + 1 - big_M * (1 - x[i, j]))

    # Ràng buộc sản phẩm
    for k in range(N):
        solver.Add(
            y[k] == solver.Sum([x[i, j] * Q[k][i-1] 
                              for i in range(1, M + 1) 
                              for j in range(M + 1) if i != j])
        )
        solver.Add(y[k] >= q[k])

    # Hàm mục tiêu: Minimize tổng khoảng cách
    objective = solver.Sum([x[i, j] * d[i][j] 
                          for i in range(M + 1) 
                          for j in range(M + 1) if i != j])
    solver.Minimize(objective)

    # Giải
    start_time = time.time()
    status = solver.Solve()
    execution_time = time.time() - start_time

    # Xử lý kết quả
    result_file = file_name + ".csv"
    file_exists = os.path.isfile(result_file)

    with open(result_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Dataset', 'Status', 'Distance', 'Path Length', 'Path', 'Execution Time (s)'])

        if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
            # Xây dựng đường đi
            route = []
            current = 0
            while True:
                next_point = None
                for j in range(1, M + 1):
                    if x[current, j].solution_value() > 0.5:  # Check for 1 with tolerance
                        next_point = j
                        break
                if next_point is None or len(route) >= M:
                    break
                route.append(next_point)
                current = next_point

            status_str = "OPTIMAL" if status == pywraplp.Solver.OPTIMAL else "FEASIBLE"
            writer.writerow([
                file_name,
                status_str,
                objective.solution_value(),
                len(route),
                ' '.join(map(str, route)),
                execution_time
            ])
            
            print(f"Status: {status_str}")
            print(f"Distance: {objective.solution_value()}")
            print(f"Path length: {len(route)}")
            print(f"Path: {' '.join(map(str, route))}")
        else:
            status_str = {
                pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
                pywraplp.Solver.MODEL_INVALID: "INVALID",
                pywraplp.Solver.UNKNOWN: "UNKNOWN"
            }.get(status, "UNKNOWN")
            writer.writerow([file_name, status_str, -1, 0, "No path found", execution_time])
            print(f"Status: {status_str}")
        
        print(f"Execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    file_name = str(os.getenv('dataset', '1.txt'))
    solve_warehouse(file_name)