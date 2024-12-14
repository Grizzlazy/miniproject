import numpy as np
import random
import os
from input import read_input_from_file, read_input_from_console

filename = str(os.getenv('dataset', default = "10.txt"))

def is_collection_complete(collected, required):
    return all(collected[i] >= required[i] for i in range(len(required)))

def select_next_shelf(current, visited, pheromone, distances, Q, collected, required, alpha, beta):
    n_shelves = len(distances) - 1
    probabilities = []
    
    for next_shelf in range(1, n_shelves + 1):
        if next_shelf not in visited:
            # Kiểm tra xem kệ này có sản phẩm cần thiết không
            has_needed_products = False
            for i in range(len(required)):
                if collected[i] < required[i] and Q[i][next_shelf-1] > 0:
                    has_needed_products = True
                    break
            
            if has_needed_products:
                # Tính xác suất chọn kệ này
                pheromone_value = pheromone[current][next_shelf]
                distance = distances[current][next_shelf]
                visibility = 1.0 / distance if distance > 0 else 1.0
                
                probability = (pheromone_value ** alpha) * (visibility ** beta)
                probabilities.append((next_shelf, probability))
    
    if not probabilities:
        return None
        
    # Chọn kệ tiếp theo dựa trên xác suất
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
    total = distances[0][path[0]]  # Từ cửa đến kệ đầu tiên
    
    # Giữa các kệ
    for i in range(len(path) - 1):
        total += distances[path[i]][path[i+1]]
        
    # Từ kệ cuối về cửa
    total += distances[path[-1]][0]
    return total

def update_pheromone(pheromone, path, distance):
    pheromone_delta = 1.0 / distance if distance > 0 else 0
    
    # Cập nhật pheromone cho toàn bộ đường đi
    current = 0  # Bắt đầu từ cửa
    for next_pos in path:
        pheromone[current][next_pos] += pheromone_delta
        pheromone[next_pos][current] += pheromone_delta
        current = next_pos
    # Cập nhật đường về cửa
    pheromone[current][0] += pheromone_delta
    pheromone[0][current] += pheromone_delta

def solve_aco(distances, Q, q_required, n_ants=20, n_iterations=100, 
              decay_rate=0.1, alpha=1, beta=2):
    n_shelves = len(distances) - 1
    n_products = len(Q)
    
    # Khởi tạo ma trận pheromone
    pheromone = np.ones((n_shelves + 1, n_shelves + 1))
    
    best_path = None
    best_distance = float('inf')
    
    for iteration in range(n_iterations):
        # Mỗi kiến sẽ tìm một đường đi
        for ant in range(n_ants):
            current_pos = 0  # Bắt đầu từ cửa (điểm 0)
            path = []
            collected = np.zeros(n_products)
            visited = set([0])
            
            # Tìm đường đi cho đến khi thu đủ sản phẩm
            while not is_collection_complete(collected, q_required):
                next_pos = select_next_shelf(
                    current_pos, visited, pheromone, distances,
                    Q, collected, q_required, alpha, beta
                )
                
                if next_pos is None:
                    break
                    
                path.append(next_pos)
                visited.add(next_pos)
                # Cập nhật số lượng sản phẩm đã thu thập
                for i in range(n_products):
                    collected[i] += Q[i][next_pos-1]
                current_pos = next_pos
            
            # Tính tổng khoảng cách
            if path:
                total_distance = calculate_total_distance(path, distances)
                
                # Cập nhật đường đi tốt nhất
                if (is_collection_complete(collected, q_required) and 
                    total_distance < best_distance):
                    best_distance = total_distance
                    best_path = path.copy()
                    
                # Cập nhật pheromone cho đường đi này
                update_pheromone(pheromone, path, total_distance)
        
        # Bay hơi pheromone
        pheromone *= (1 - decay_rate)
        
    return best_path, best_distance

def main():
    # Đọc input
    file = "data/"+filename
    N, M, Q, distances, q_required = read_input_from_file(file)
    
    best_path, best_distance = solve_aco(
        distances=distances,
        Q=Q,
        q_required=q_required,
        n_ants=20,
        n_iterations=100,
        decay_rate=0.1,
        alpha=1,
        beta=2
    )
    
    print(best_distance)
    # In kết quả
    if best_path:
        print(len(best_path))
        print(' '.join(map(str, best_path)))
    else:
        print("Không tìm thấy đường đi thỏa mãn")

if __name__ == "__main__":
    main()