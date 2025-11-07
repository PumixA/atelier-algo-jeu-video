from __future__ import annotations
from typing import List, Tuple, Dict, Optional
import heapq
import math

Coord = Tuple[int, int]  # (row, col)

def neighbors(grid: List[List[Optional[int]]], cell: Coord) -> List[Coord]:
    (r, c) = cell
    cand = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
    out: List[Coord] = []
    for nr, nc in cand:
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] is not None:
            out.append((nr, nc))
    return out

def reconstruct_path(parents, start, goal):
    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        if cur not in parents: 
            return []
        cur = parents[cur]
    path.append(start)
    path.reverse()
    return path


def dijkstra(grid: List[List[Optional[int]]], start: Coord, goal: Coord) -> Tuple[float, List[Coord], int]:
    dist: Dict[Coord, float] = {start: 0.0}
    parents: Dict[Coord, Coord] = {}
    explored = 0
    pq: List[Tuple[float, Coord]] = [(0.0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        explored += 1
        if u == goal:
            return d, reconstruct_path(parents, start, goal), explored
        if d > dist.get(u, math.inf):
            continue
        for v in neighbors(grid, u):
            cost = grid[v[0]][v[1]]
            assert cost is not None
            nd = d + float(cost)
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                parents[v] = u
                heapq.heappush(pq, (nd, v))
    return math.inf, [], explored

def manhattan(a: Coord, b: Coord) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid: List[List[Optional[int]]], start: Coord, goal: Coord) -> Tuple[float, List[Coord], int]:
    g: Dict[Coord, float] = {start: 0.0}
    parents: Dict[Coord, Coord] = {}
    explored = 0
    pq: List[Tuple[float, Coord]] = [(manhattan(start, goal), start)]

    while pq:
        f, u = heapq.heappop(pq)
        explored += 1
        if u == goal:
            return g[u], reconstruct_path(parents, start, goal), explored
        for v in neighbors(grid, u):
            cost = grid[v[0]][v[1]]
            assert cost is not None
            tentative = g[u] + float(cost)
            if tentative < g.get(v, math.inf):
                g[v] = tentative
                parents[v] = u
                score = tentative + manhattan(v, goal)
                heapq.heappush(pq, (score, v))
    return math.inf, [], explored


# ---- DSU for cycles (guild merges) ----

Edge = Tuple[int, int]

class DisjointSet:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1
        return True

def detect_cycle_with_dsu(edges: List[Edge], n: int) -> bool:
    dsu = DisjointSet(n)
    for (u, v) in edges:
        if not dsu.union(u, v):
            return True
    return False


if __name__ == "__main__":
    grid = [[1,1,1],[1,2,1],[1,1,1]]
    start, goal = (0,0), (2,2)
    dist, path, explored = astar(grid, start, goal)
    print("dist:", dist, "path:", path, "explored:", explored)