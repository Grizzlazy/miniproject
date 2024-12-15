#PYTHON 
import numpy as np
import random
import os
from array import array


def is_collection_complete(collected, required):
    return np.all(collected >= required)

def select_next_shelf(current, visited, pheromone, distances, Q, collected, required, alpha, beta, needed_products):
    candidates = needed_products - visited
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
    total = distances[0][path[0]]
    total += np.sum([distances[path[i]][path[i+1]] for i in range(len(path)-1)])
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

def find_needed_shelves(Q, q_required):
    needed_shelves = set()
    for i in range(len(q_required)):
        if q_required[i] > 0:
            for j in range(len(Q[i])):
                if Q[i][j] > 0:
                    needed_shelves.add(j + 1)
    return needed_shelves

def solve_aco(distances, Q, q_required, decay_rate=0.1, alpha=1, beta=2):
    n_shelves = len(distances) - 1
    n_products = len(Q)
    
    if n_shelves <= 100:
        n_ants = 20
    elif n_shelves <= 500:
        n_ants = 30
    else:
        n_ants = 40
    
    pheromone = np.ones((n_shelves + 1, n_shelves + 1), dtype=np.float32)
    
    needed_shelves = find_needed_shelves(Q, q_required)
    
    best_path = None
    best_distance = float('inf')
    no_improvement_count = 0
    
    while no_improvement_count < 10:
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
                    Q, collected, q_required, alpha, beta, needed_shelves
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
                    no_improvement_count = 0
        
        if iteration_best_path:
            update_pheromone(pheromone, iteration_best_path, iteration_best_distance, decay_rate)
        
        if iteration_best_distance >= best_distance:
            no_improvement_count += 1
        
    return best_path, best_distance

def input_file():
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

def main():
    N, M, Q, distances, q_required = input_file()
    
    best_path, best_distance = solve_aco(
        distances=distances,
        Q=Q,
        q_required=q_required,
        decay_rate=0.1,
        alpha=1,
        beta=2
    )
    print(len(best_path))
    print(' '.join(map(str, best_path)))

if __name__ == "__main__":
    main()
