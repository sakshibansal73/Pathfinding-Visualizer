# Pathfinding Visualizer

An interactive grid-based pathfinding visualizer built in Python. Draw walls, place a
start/end point, and watch **BFS**, **DFS**, **Dijkstra**, and **A\*** search the grid
in real time.

![status](https://img.shields.io/badge/status-complete-brightgreen)
![python](https://img.shields.io/badge/python-3.8%2B-blue)

## Why this project

Most pathfinding demos hardcode one algorithm. This one is built so that **adding a new
algorithm requires zero changes to the GUI or grid code** — it's a clean demonstration
of the **Strategy design pattern**:

```python
class PathfindingAlgorithm(ABC):
    @abstractmethod
    def search(self, grid: Grid):
        ...
```

`BFS`, `DFS`, `Dijkstra`, and `AStar` all implement this interface. The GUI only ever
calls `algorithm.search(grid)` — it has no idea which concrete algorithm it's running.
That's polymorphism doing real work, not just a textbook example.

## Run it

No dependencies beyond the Python standard library (`tkinter` ships with Python).

```bash
python pathfinding_visualizer.py
```

## Controls

| Action              | How                                   |
|---------------------|----------------------------------------|
| Place start cell    | Click **Set Start**, then click a cell |
| Place end cell      | Click **Set End**, then click a cell   |
| Draw walls          | **Draw Walls** mode, left-click/drag   |
| Erase a wall        | Right-click on a wall cell             |
| Choose algorithm    | Dropdown menu                          |
| Run search          | **Run** button                         |
| Reset search only   | **Clear Path** (keeps walls)           |
| Reset everything    | **Clear All**                          |

## Algorithms implemented

| Algorithm | Data structure used     | Shortest path guaranteed? | Notes                                  |
|-----------|--------------------------|----------------------------|------------------------------------------|
| BFS       | Queue (`collections.deque`) | Yes (unweighted grid)   | Explores in rings outward from start     |
| DFS       | Stack                    | No                          | Explores deeply before backtracking      |
| Dijkstra  | Min-heap (`heapq`)       | Yes                          | Generalizes to weighted graphs           |
| A\*       | Min-heap + heuristic     | Yes (admissible heuristic)  | Manhattan distance heuristic; converges faster than Dijkstra |

## Architecture

```
Node        -> a single grid cell (row, col, state)
Grid        -> 2D array of Nodes; owns neighbor logic & boundary checks
Algorithm   -> abstract base class; each concrete algorithm returns
               (visited_order, path) so the GUI can animate any of them identically
VisualizerApp -> Tkinter GUI; only depends on the Grid/Algorithm abstractions
```

This separation means the core logic (`Node`, `Grid`, algorithms) has **no dependency
on Tkinter at all** — it could be tested headlessly or swapped to a web frontend
without touching the algorithm code.

## Talking points for interviews

- **Why a min-heap for Dijkstra/A\* instead of scanning for the minimum each time?**
  Reduces the "get next node" operation from O(V) to O(log V), which matters at scale.
- **Why does A\* converge faster than Dijkstra here?**
  The Manhattan-distance heuristic is admissible (never overestimates), so A\* prioritizes
  nodes that are closer to the goal instead of exploring uniformly in all directions.
- **What would you change for a production version?**
  Swap the 4-directional grid for a general graph (adjacency list), add weighted edges,
  and extract the algorithms into a package with unit tests per algorithm using a
  fixed small grid with a known shortest path.

## Possible extensions (if you have more time before submitting)

- Add diagonal movement (8-directional) and compare path lengths.
- Add maze-generation (e.g., randomized DFS) to auto-generate walls.
- Add a "weighted terrain" mode where some cells cost more to traverse (shows off Dijkstra vs. BFS more clearly, since they'd diverge).
- Write unit tests for each algorithm against a fixed grid with a known answer.
