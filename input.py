def read_input_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    lines = [line.strip() for line in lines]
    N, M = map(int, lines[0].split())
    
    # Đọc ma trận Q
    Q = []
    for i in range(N):
        Q.append(list(map(int, lines[i + 1].split())))
    
    # Đọc ma trận khoảng cách d
    d = []
    for i in range(M + 1):
        d.append(list(map(int, lines[N + 1 + i].split())))
    
    # Đọc mảng q
    q = list(map(int, lines[N + M + 2].split()))
    
    return N, M, Q, d, q

def read_input_from_console():
    # Đọc N và M
    N, M = map(int, input().split())
    
    lines = []
    lines.append(f"{N} {M}")
    
    # Đọc ma trận Q
    for _ in range(N):
        lines.append(input().strip())
    
    # Đọc ma trận khoảng cách d
    for _ in range(M + 1):
        lines.append(input().strip())
    
    # Đọc mảng q
    lines.append(input().strip())
    
    lines = [line.strip() for line in lines]
    N, M = map(int, lines[0].split())
    
    # Đọc ma trận Q
    Q = []
    for i in range(N):
        Q.append(list(map(int, lines[i + 1].split())))
    
    # Đọc ma trận khoảng cách d
    d = []
    for i in range(M + 1):
        d.append(list(map(int, lines[N + 1 + i].split())))
    
    # Đọc mảng q
    q = list(map(int, lines[N + M + 2].split()))
    
    return N, M, Q, d, q
    