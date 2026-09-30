// dijkstra.cpp - Shortest Path in Weighted Graphs using Priority Queue
#include <iostream>
#include <vector>
#include <queue>
#include <climits>

using namespace std;

typedef pair<int, int> pii; // {distance, node}

// Computes shortest path from single source vertex using Dijkstra's algorithm
// Time Complexity: O((V + E) log V) with binary heap priority queue
vector<int> dijkstra(int n, int src, const vector<vector<pii>>& adj) {
    vector<int> dist(n, INT_MAX);
    priority_queue<pii, vector<pii>, greater<pii>> pq;

    dist[src] = 0;
    pq.push({0, src});

    while (!pq.empty()) {
        int d = pq.top().first;
        int u = pq.top().second;
        pq.pop();

        if (d > dist[u]) continue;

        for (auto& edge : adj[u]) {
            int v = edge.first;
            int weight = edge.second;

            // Relaxation step for shortest path
            if (dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}

int main() {
    int n = 5;
    vector<vector<pii>> adj(n);
    adj[0].push_back({1, 4});
    adj[0].push_back({2, 1});
    adj[2].push_back({1, 2});
    adj[1].push_back({3, 1});
    adj[2].push_back({3, 5});

    vector<int> dist = dijkstra(n, 0, adj);
    cout << "Shortest distances from source 0:" << endl;
    for (int i = 0; i < n; ++i) {
        cout << "Node " << i << ": " << dist[i] << endl;
    }
    return 0;
}
