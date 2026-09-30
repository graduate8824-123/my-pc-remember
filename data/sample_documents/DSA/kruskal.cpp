// kruskal.cpp - Minimum Spanning Tree using Disjoint Set Union (DSU)
#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

// Disjoint Set Union (DSU) with Path Compression and Union by Rank
struct DSU {
    vector<int> parent;
    vector<int> rank;

    DSU(int n) {
        parent.resize(n);
        rank.assign(n, 0);
        for (int i = 0; i < n; ++i) parent[i] = i;
    }

    int find(int i) {
        if (parent[i] == i)
            return i;
        return parent[i] = find(parent[i]); // Path compression
    }

    bool unite(int i, int j) {
        int root_i = find(i);
        int root_j = find(j);
        if (root_i == root_j) return false;

        if (rank[root_i] < rank[root_j]) {
            parent[root_i] = root_j;
        } else if (rank[root_i] > rank[root_j]) {
            parent[root_j] = root_i;
        } else {
            parent[root_j] = root_i;
            rank[root_i]++;
        }
        return true;
    }
};

struct Edge {
    int u, v, weight;
    bool operator<(const Edge& other) const {
        return weight < other.weight;
    }
};

// Kruskal's Algorithm for Minimum Spanning Tree (MST)
int kruskalMST(int n, vector<Edge>& edges) {
    sort(edges.begin(), edges.end());
    DSU dsu(n);
    int mst_weight = 0;
    int edges_count = 0;

    for (const auto& edge : edges) {
        if (dsu.unite(edge.u, edge.v)) {
            mst_weight += edge.weight;
            edges_count++;
            if (edges_count == n - 1) break;
        }
    }
    return mst_weight;
}

int main() {
    int n = 4;
    vector<Edge> edges = {
        {0, 1, 10},
        {0, 2, 6},
        {0, 3, 5},
        {1, 3, 15},
        {2, 3, 4}
    };
    cout << "Weight of Minimum Spanning Tree: " << kruskalMST(n, edges) << endl;
    return 0;
}
