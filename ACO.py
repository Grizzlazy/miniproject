import numpy as np
import random
import os
import csv
import time
from input import read_input_from_file, read_input_from_console

filename = str(os.getenv('dataset', default = "10.txt"))

def is_collection_complete(collected, required):
    return np.all(collected >= required)

def find_needed_shelves(Q, q_required, collected):
    needed_shelves = set()
    for i in range(len(q_required)):
        if collected[i] < q_required[i]:
            for j in range(len(Q[i])):
                if Q[i][j] > 0:
                    needed_shelves.add(j + 1)
    return needed_shelves

def select_next_shelf(current, visited, pheromone, distances, Q, collected, required, alpha, beta):
    # Tìm các kệ có sản phẩm cần thiết
    needed_shelves = find_needed_shelves(Q, required, collected)
    candidates = needed_shelves - visited
    
    if not candidates:
        return None
    
    probabilities = []
    for next_shelf in candidates:
        pheromone_value = pheromone[current][next_shelf]
        distance = distances[current][next_shelf]
        visibility = 1.0 / distance if distance > 0 else 1.0
        probability = (pheromone_value ** alpha) * (visibility ** beta)
        probabilities.append((next_shelf, probability))
    
    if not probabilities:
        return None
    
    total = sum(prob for _, prob in probabilities)
    if total == 0:
        return None
    
    r = random.random() * total
    current_sum = 0
    for shelf, prob in probabilities:
        current_sum += prob
        if current_sum >= r:
            return shelf
    
    return probabilities[-1][0]

def calculate_total_distance(path, distances):
    if not path:
        return float('inf')
    total = distances[0][path[0]]
    total += sum(distances[path[i]][path[i+1]] for i in range(len(path)-1))
    total += distances[path[-1]][0]
    return total

def update_pheromone(pheromone, path, distance, decay_rate):
    pheromone_delta = 1.0 / distance if distance > 0 else 0
    
    current = 0
    for next_pos in path:
        pheromone[current][next_pos] = (1 - decay_rate) * pheromone[current][next_pos] + pheromone_delta
        pheromone[next_pos][current] = pheromone[current][next_pos]
        current = next_pos
    pheromone[current][0] = (1 - decay_rate) * pheromone[current][0] + pheromone_delta
    pheromone[0][current] = pheromone[current][0]

def solve_aco(distances, Q, q_required, decay_rate=0.1, alpha=1, beta=2):
    n_shelves = len(distances) - 1
    n_products = len(Q)
    
    # Điều chỉnh số kiến theo kích thước bài toán
    if n_shelves <= 100:
        n_ants = 20
        n_iterations = 100
    elif n_shelves <= 500:
        n_ants = 30
        n_iterations = 150
    else:
        n_ants = 40
        n_iterations = 200
        
    pheromone = np.ones((n_shelves + 1, n_shelves + 1), dtype=np.float32)
    
    best_path = None
    best_distance = float('inf')
    
    for iteration in range(n_iterations):
        iteration_best_distance = float('inf')
        iteration_best_path = None
        
        for ant in range(n_ants):
            current_pos = 0
            path = []
            collected = np.zeros(n_products, dtype=np.int32)
            visited = {0}
            
            while not is_collection_complete(collected, q_required):
                next_pos = select_next_shelf(
                    current_pos, visited, pheromone, distances,
                    Q, collected, q_required, alpha, beta
                )
                
                if next_pos is None:
                    break
                    
                path.append(next_pos)
                visited.add(next_pos)
                collected += np.array([Q[i][next_pos-1] for i in range(n_products)])
                current_pos = next_pos
            
            if path and is_collection_complete(collected, q_required):
                total_distance = calculate_total_distance(path, distances)
                
                if total_distance < iteration_best_distance:
                    iteration_best_distance = total_distance
                    iteration_best_path = path.copy()
                
                if total_distance < best_distance:
                    best_distance = total_distance
                    best_path = path.copy()
        
        if iteration_best_path:
            update_pheromone(pheromone, iteration_best_path, iteration_best_distance, decay_rate)
        
    return best_path, best_distance

def main():
    file = "data/"+filename
    N, M, Q, distances, q_required = read_input_from_file(file)
    
    start_time = time.time()
    best_path, best_distance = solve_aco(
        distances=distances,
        Q=Q,
        q_required=q_required
    )
    end_time = time.time()
    execution_time = end_time - start_time
    
    result_file = filename+".csv"
    
    with open(result_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Dataset', 'Distance', 'Path Length', 'Path', 'Execution Time (s)'])
        
        path_str = ' '.join(map(str, best_path)) if best_path else "No path found"
        path_length = len(best_path) if best_path else 0
        writer.writerow([filename, best_distance, path_length, path_str, execution_time])

    print(f"Distance: {best_distance}")
    print(f"Path length: {len(best_path)}")
    print(f"Path: {' '.join(map(str, best_path))}")

if __name__ == "__main__":
    main()