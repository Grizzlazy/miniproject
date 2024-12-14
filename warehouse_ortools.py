import ortools.sat.python.cp_model as cp_model

def read_input_from_console():
    N, M = map(int, input().split())
    
    Q = [list(map(int, input().split())) for _ in range(N)]
    
    d = [list(map(int, input().split())) for _ in range(M + 1)]
    
    q = list(map(int, input().split()))
    
    return N, M, Q, d, q

N, M, Q, d, q = read_input_from_console()

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

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    visited = [i for i in range(1, M + 1) 
              if any(solver.Value(x[i, j]) == 1 
                    for j in range(M + 1) 
                    if i != j and (i, j) in x)]
    
    print(len(visited))
    
    route = []
    current = 0
    while len(route) < len(visited):
        next_point = next(j for j in range(1, M + 1) 
                         if (current, j) in x and solver.Value(x[current, j]) == 1)
        route.append(next_point)
        current = next_point
    
    print(' '.join(map(str, route)))