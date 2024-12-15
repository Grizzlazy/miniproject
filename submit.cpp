#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <set>
#include <algorithm>
using namespace std;

// Kiểm tra xem đã thu thập đủ sản phẩm chưa
bool isCollectionComplete(const vector<int>& collected, const vector<int>& required) {
    for(size_t i = 0; i < required.size(); i++) {
        if(collected[i] < required[i]) return false;
    }
    return true;
}

// Chọn kệ tiếp theo
int selectNextShelf(int current, const set<int>& visited, 
                    vector<vector<double>>& pheromone,
                    const vector<vector<int>>& distances,
                    const vector<vector<int>>& Q,
                    const vector<int>& collected,
                    const vector<int>& required,
                    double alpha, double beta) {
    
    int n_shelves = distances.size() - 1;
    vector<pair<int, double>> probabilities;
    
    for(int next_shelf = 1; next_shelf <= n_shelves; next_shelf++) {
        if(visited.find(next_shelf) == visited.end()) {
            // Kiểm tra xem kệ này có sản phẩm cần thiết không
            bool hasNeededProducts = false;
            for(size_t i = 0; i < required.size(); i++) {
                if(collected[i] < required[i] && Q[i][next_shelf-1] > 0) {
                    hasNeededProducts = true;
                    break;
                }
            }
            
            if(hasNeededProducts) {
                double pheromone_value = pheromone[current][next_shelf];
                double distance = distances[current][next_shelf];
                double visibility = distance > 0 ? 1.0 / distance : 1.0;
                
                double probability = pow(pheromone_value, alpha) * pow(visibility, beta);
                probabilities.push_back({next_shelf, probability});
            }
        }
    }
    
    if(probabilities.empty()) return -1;
    
    // Tính tổng xác suất
    double total = 0;
    for(const auto& p : probabilities) {
        total += p.second;
    }
    
    if(total == 0) return -1;
    
    // Chọn ngẫu nhiên dựa trên xác suất
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> dis(0, total);
    double r = dis(gen);
    
    double current_sum = 0;
    for(const auto& p : probabilities) {
        current_sum += p.second;
        if(current_sum >= r) return p.first;
    }
    
    return probabilities.back().first;
}

// Tính tổng khoảng cách
int calculateTotalDistance(const vector<int>& path, const vector<vector<int>>& distances) {
    int total = distances[0][path[0]];
    
    for(size_t i = 0; i < path.size() - 1; i++) {
        total += distances[path[i]][path[i+1]];
    }
    
    total += distances[path.back()][0];
    return total;
}

// Cập nhật pheromone
void updatePheromone(vector<vector<double>>& pheromone, const vector<int>& path, int distance) {
    double pheromone_delta = distance > 0 ? 1.0 / distance : 0;
    
    int current = 0;
    for(int next_pos : path) {
        pheromone[current][next_pos] += pheromone_delta;
        pheromone[next_pos][current] += pheromone_delta;
        current = next_pos;
    }
    pheromone[current][0] += pheromone_delta;
    pheromone[0][current] += pheromone_delta;
}

// Hàm chính giải thuật ACO
pair<vector<int>, int> solveACO(const vector<vector<int>>& distances,
                               const vector<vector<int>>& Q,
                               const vector<int>& q_required,
                               int n_ants = 20,
                               int n_iterations = 100,
                               double decay_rate = 0.1,
                               double alpha = 1,
                               double beta = 2) {
    
    int n_shelves = distances.size() - 1;
    int n_products = Q.size();
    
    // Khởi tạo ma trận pheromone
    vector<vector<double>> pheromone(n_shelves + 1, vector<double>(n_shelves + 1, 1.0));
    
    vector<int> best_path;
    int best_distance = INT_MAX;
    
    for(int iteration = 0; iteration < n_iterations; iteration++) {
        for(int ant = 0; ant < n_ants; ant++) {
            int current_pos = 0;
            vector<int> path;
            vector<int> collected(n_products, 0);
            set<int> visited = {0};
            
            while(!isCollectionComplete(collected, q_required)) {
                int next_pos = selectNextShelf(current_pos, visited, pheromone, distances,
                                            Q, collected, q_required, alpha, beta);
                
                if(next_pos == -1) break;
                
                path.push_back(next_pos);
                visited.insert(next_pos);
                
                for(int i = 0; i < n_products; i++) {
                    collected[i] += Q[i][next_pos-1];
                }
                current_pos = next_pos;
            }
            
            if(!path.empty()) {
                int total_distance = calculateTotalDistance(path, distances);
                
                if(isCollectionComplete(collected, q_required) && total_distance < best_distance) {
                    best_distance = total_distance;
                    best_path = path;
                }
                
                updatePheromone(pheromone, path, total_distance);
            }
        }
        
        // Bay hơi pheromone
        for(auto& row : pheromone) {
            for(double& p : row) {
                p *= (1 - decay_rate);
            }
        }
    }
    
    return {best_path, best_distance};
}

int main() {
    int N, M;
    cin >> N >> M;
    
    // Đọc ma trận Q
    vector<vector<int>> Q(N, vector<int>(M));
    for(int i = 0; i < N; i++) {
        for(int j = 0; j < M; j++) {
            cin >> Q[i][j];
        }
    }
    
    // Đọc ma trận khoảng cách
    vector<vector<int>> distances(M + 1, vector<int>(M + 1));
    for(int i = 0; i <= M; i++) {
        for(int j = 0; j <= M; j++) {
            cin >> distances[i][j];
        }
    }
    
    // Đọc yêu cầu sản phẩm
    vector<int> q_required(N);
    for(int i = 0; i < N; i++) {
        cin >> q_required[i];
    }
    
    auto [best_path, best_distance] = solveACO(distances, Q, q_required);
    
    cout << best_path.size() << endl;
    for(size_t i = 0; i < best_path.size(); i++) {
        cout << best_path[i] << (i < best_path.size()-1 ? " " : "");
    }
    cout << endl;
    
    return 0;
}