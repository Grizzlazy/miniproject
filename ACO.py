import numpy as np
import os
import csv
import time
from input import read_input_from_file

filename = str(os.getenv('dataset', default = "10.txt"))
run_number = str(os.getenv('run_number', default = "1"))
def is_collection_complete(collected, required):
    return np.all(collected >= required)

def select_next_shelf(current, visited, pheromone, distances, Q, collected, required):
    n_shelves = len(distances) - 1
    unvisited = list(set(range(1, n_shelves + 1)) - visited)
    
    if not unvisited:
        return None
        
    # Tính toán xác suất một lần cho tất cả các kệ chưa thăm
    probs = np.zeros(len(unvisited))
    for idx, next_shelf in enumerate(unvisited):
        # Kiểm tra nhanh xem kệ có sản phẩm cần thiết không
        if not np.any((collected < required) & (Q[:, next_shelf-1] > 0)):
            continue
            
        visibility = 1.0 / max(distances[current][next_shelf], 1e-10)
        probs[idx] = pheromone[current][next_shelf] * visibility
    
    if np.sum(probs) == 0:
        return None
        
    # Chọn kệ tiếp theo dựa trên xác suất
    probs = probs / np.sum(probs)
    return np.random.choice(unvisited, p=probs)

def solve_aco(distances, Q, q_required, n_ants=20, n_iterations=50):
    n_shelves = len(distances) - 1
    pheromone = np.ones((n_shelves + 1, n_shelves + 1))
    best_path = None
    best_distance = float('inf')
    
    for _ in range(n_iterations):
        for _ in range(n_ants):
            current = 0
            path = []
            collected = np.zeros_like(q_required)
            visited = {0}
            
            while not is_collection_complete(collected, q_required):
                next_pos = select_next_shelf(
                    current, visited, pheromone, distances,
                    Q, collected, q_required
                )
                
                if next_pos is None:
                    break
                    
                path.append(next_pos)
                visited.add(next_pos)
                collected += Q[:, next_pos-1]
                current = next_pos
            
            if path and is_collection_complete(collected, q_required):
                # Tính khoảng cách
                distance = distances[0][path[0]]
                for i in range(len(path)-1):
                    distance += distances[path[i]][path[i+1]]
                distance += distances[path[-1]][0]
                
                # Cập nhật đường đi tốt nhất
                if distance < best_distance:
                    best_distance = distance
                    best_path = path.copy()
                
                # Cập nhật pheromone
                delta = 1.0 / distance
                current = 0
                for next_pos in path:
                    pheromone[current][next_pos] += delta
                    pheromone[next_pos][current] += delta
                    current = next_pos
                pheromone[current][0] += delta
                pheromone[0][current] += delta
        
        # Bay hơi pheromone
        pheromone *= 0.9
        
    return best_path, best_distance

def main():
    file = "data/"+filename
    N, M, Q, distances, q_required = read_input_from_file(file)
    
    start_time = time.time()
    best_path, best_distance = solve_aco(distances, Q, q_required)
    execution_time = time.time() - start_time
    
    # Lưu kết quả
    result_file = filename+run_number+".csv"
    file_exists = os.path.isfile(result_file)
    
    with open(result_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['Dataset', 'Distance', 'Path Length', 'Path', 'Execution Time (s)'])
        path_str = ' '.join(map(str, best_path)) if best_path else "No path found"
        writer.writerow([filename, best_distance, len(best_path) if best_path else 0, 
                        path_str, execution_time])

    print(f"Distance: {best_distance}")
    print(f"Path length: {len(best_path)}")
    print(f"Path: {' '.join(map(str, best_path))}")

if __name__ == "__main__":
    main()