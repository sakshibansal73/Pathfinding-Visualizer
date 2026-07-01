"""
Pathfinding Visualizer
=======================
A grid-based pathfinding visualizer demonstrating:
  - Object-Oriented Design (abstract base class + polymorphism / Strategy pattern)
  - Core Data Structures & Algorithms (BFS, DFS, Dijkstra, A*)
  - Priority Queues, Queues, Stacks, Graph traversal
  - A simple GUI built with Tkinter (no external dependencies required)

Run with:  python pathfinding_visualizer.py

Controls:
  - Left click: place a wall
  - Right click: erase a wall
  - "Set Start" / "Set End" buttons then click a cell to place them
  - Choose an algorithm from the dropdown and click "Run"
  - "Clear Path" resets visited/path cells but keeps walls
  - "Clear All" resets everything
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from collections import deque
import heapq
import math


# ----------------------------------------------------------------------
# Domain model
# ----------------------------------------------------------------------

class CellState:
    EMPTY = "empty"
    WALL = "wall"
    START = "start"
    END = "end"
    VISITED = "visited"
    FRONTIER = "frontier"
    PATH = "path"


class Node:
    """Represents a single cell in the grid graph."""

    __slots__ = ("row", "col", "state")

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.state = CellState.EMPTY

    def __repr__(self):
        return f"Node({self.row},{self.col},{self.state})"

    def __lt__(self, other):
        # Needed for heapq tie-breaking when priorities are equal
        return (self.row, self.col) < (other.row, other.col)


class Grid:
    """A 2D grid of Nodes acting as an implicit graph.

    Encapsulates neighbor logic so algorithms don't need to know
    about grid boundaries or wall-checking directly.
    """

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.nodes = [[Node(r, c) for c in range(cols)] for r in range(rows)]
        self.start = None
        self.end = None

    def get(self, row: int, col: int) -> Node:
        return self.nodes[row][col]

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def neighbors(self, node: Node):
        """Returns walkable (non-wall) 4-directional neighbors."""
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        result = []
        for dr, dc in deltas:
            nr, nc = node.row + dr, node.col + dc
            if self.in_bounds(nr, nc):
                neighbor = self.nodes[nr][nc]
                if neighbor.state != CellState.WALL:
                    result.append(neighbor)
        return result

    def reset_search_state(self):
        """Clears visited/frontier/path markings but keeps walls & start/end."""
        for row in self.nodes:
            for node in row:
                if node.state in (CellState.VISITED, CellState.FRONTIER, CellState.PATH):
                    node.state = CellState.EMPTY

    def clear_all(self):
        for row in self.nodes:
            for node in row:
                node.state = CellState.EMPTY
        self.start = None
        self.end = None


# ----------------------------------------------------------------------
# Algorithms (Strategy pattern via abstract base class)
# ----------------------------------------------------------------------

class PathfindingAlgorithm(ABC):
    """Abstract base for all pathfinding strategies.

    Subclasses implement `search`, which must return:
        (visited_in_order: list[Node], path: list[Node] | None)
    This lets the GUI animate the search process the same way
    regardless of which concrete algorithm is used (polymorphism).
    """

    name = "Base Algorithm"

    @abstractmethod
    def search(self, grid: Grid):
        raise NotImplementedError

    @staticmethod
    def reconstruct_path(came_from: dict, end: Node):
        path = []
        current = end
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path


class BFS(PathfindingAlgorithm):
    """Breadth-First Search — guarantees shortest path on unweighted grids."""

    name = "BFS (Breadth-First Search)"

    def search(self, grid: Grid):
        start, end = grid.start, grid.end
        visited_order = []
        came_from = {}
        visited = {start}
        queue = deque([start])

        while queue:
            current = queue.popleft()
            visited_order.append(current)
            if current is end:
                return visited_order, self.reconstruct_path(came_from, end)

            for neighbor in grid.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return visited_order, None


class DFS(PathfindingAlgorithm):
    """Depth-First Search — explores deeply first; does NOT guarantee shortest path."""

    name = "DFS (Depth-First Search)"

    def search(self, grid: Grid):
        start, end = grid.start, grid.end
        visited_order = []
        came_from = {}
        visited = {start}
        stack = [start]

        while stack:
            current = stack.pop()
            if current in visited_order:
                continue
            visited_order.append(current)
            if current is end:
                return visited_order, self.reconstruct_path(came_from, end)

            for neighbor in grid.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    stack.append(neighbor)

        return visited_order, None


class Dijkstra(PathfindingAlgorithm):
    """Dijkstra's Algorithm — shortest path with uniform edge weights (=1 here),
    implemented with a min-heap priority queue to show general weighted-graph handling.
    """

    name = "Dijkstra"

    def search(self, grid: Grid):
        start, end = grid.start, grid.end
        visited_order = []
        came_from = {}
        dist = {start: 0}
        visited = set()

        # heap entries: (distance, insertion_order, node) — insertion_order avoids
        # comparing Node objects directly when distances tie.
        counter = 0
        heap = [(0, counter, start)]

        while heap:
            current_dist, _, current = heapq.heappop(heap)
            if current in visited:
                continue
            visited.add(current)
            visited_order.append(current)

            if current is end:
                return visited_order, self.reconstruct_path(came_from, end)

            for neighbor in grid.neighbors(current):
                new_dist = current_dist + 1
                if new_dist < dist.get(neighbor, math.inf):
                    dist[neighbor] = new_dist
                    came_from[neighbor] = current
                    counter += 1
                    heapq.heappush(heap, (new_dist, counter, neighbor))

        return visited_order, None


class AStar(PathfindingAlgorithm):
    """A* Search — Dijkstra + Manhattan-distance heuristic for faster convergence."""

    name = "A* (A-Star)"

    @staticmethod
    def heuristic(a: Node, b: Node) -> int:
        return abs(a.row - b.row) + abs(a.col - b.col)

    def search(self, grid: Grid):
        start, end = grid.start, grid.end
        visited_order = []
        came_from = {}
        g_score = {start: 0}
        visited = set()

        counter = 0
        heap = [(self.heuristic(start, end), counter, start)]

        while heap:
            _, _, current = heapq.heappop(heap)
            if current in visited:
                continue
            visited.add(current)
            visited_order.append(current)

            if current is end:
                return visited_order, self.reconstruct_path(came_from, end)

            for neighbor in grid.neighbors(current):
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, math.inf):
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, end)
                    came_from[neighbor] = current
                    counter += 1
                    heapq.heappush(heap, (f_score, counter, neighbor))

        return visited_order, None


ALGORITHMS = {
    "BFS": BFS(),
    "DFS": DFS(),
    "Dijkstra": Dijkstra(),
    "A*": AStar(),
}


# ----------------------------------------------------------------------
# GUI Layer (Tkinter) — depends only on the Grid/Algorithm abstractions above
# ----------------------------------------------------------------------

CELL_SIZE = 24
ROWS, COLS = 22, 32

COLORS = {
    CellState.EMPTY: "#1e1e2e",
    CellState.WALL: "#45475a",
    CellState.START: "#a6e3a1",
    CellState.END: "#f38ba8",
    CellState.VISITED: "#313244",
    CellState.FRONTIER: "#89b4fa",
    CellState.PATH: "#f9e2af",
}


class VisualizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Pathfinding Visualizer — BFS / DFS / Dijkstra / A*")
        self.root.configure(bg="#11111b")

        self.grid = Grid(ROWS, COLS)
        self.mode = "wall"  # "wall" | "start" | "end"
        self.is_running = False

        self._build_controls()
        self._build_canvas()
        self.draw()

    # ---- UI construction -------------------------------------------------

    def _build_controls(self):
        bar = tk.Frame(self.root, bg="#11111b", pady=8)
        bar.pack(side=tk.TOP, fill=tk.X)

        style = {"bg": "#313244", "fg": "#cdd6f4", "activebackground": "#45475a",
                 "activeforeground": "#ffffff", "relief": tk.FLAT, "padx": 10, "pady": 5}

        tk.Button(bar, text="Set Start", command=lambda: self.set_mode("start"), **style).pack(side=tk.LEFT, padx=4)
        tk.Button(bar, text="Set End", command=lambda: self.set_mode("end"), **style).pack(side=tk.LEFT, padx=4)
        tk.Button(bar, text="Draw Walls", command=lambda: self.set_mode("wall"), **style).pack(side=tk.LEFT, padx=4)

        self.algo_var = tk.StringVar(value="A*")
        algo_menu = ttk.Combobox(bar, textvariable=self.algo_var, values=list(ALGORITHMS.keys()),
                                  state="readonly", width=10)
        algo_menu.pack(side=tk.LEFT, padx=10)

        tk.Button(bar, text="Run", command=self.run_algorithm, bg="#a6e3a1", fg="#11111b",
                  relief=tk.FLAT, padx=12, pady=5, activebackground="#94e2d5").pack(side=tk.LEFT, padx=4)
        tk.Button(bar, text="Clear Path", command=self.clear_path, **style).pack(side=tk.LEFT, padx=4)
        tk.Button(bar, text="Clear All", command=self.clear_all, **style).pack(side=tk.LEFT, padx=4)

        self.status = tk.Label(bar, text="Click 'Set Start', then 'Set End', then draw walls, then Run.",
                                bg="#11111b", fg="#a6adc8")
        self.status.pack(side=tk.LEFT, padx=16)

    def _build_canvas(self):
        self.canvas = tk.Canvas(self.root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE,
                                 bg=COLORS[CellState.EMPTY], highlightthickness=0)
        self.canvas.pack(side=tk.TOP, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_right_click)

    # ---- Interaction handlers ---------------------------------------------

    def set_mode(self, mode: str):
        self.mode = mode
        self.status.config(text=f"Mode: {mode}. Click a cell on the grid.")

    def _cell_from_event(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if self.grid.in_bounds(row, col):
            return self.grid.get(row, col)
        return None

    def on_left_click(self, event):
        if self.is_running:
            return
        node = self._cell_from_event(event)
        if node is None:
            return

        if self.mode == "start":
            if self.grid.start:
                self.grid.start.state = CellState.EMPTY
            node.state = CellState.START
            self.grid.start = node
        elif self.mode == "end":
            if self.grid.end:
                self.grid.end.state = CellState.EMPTY
            node.state = CellState.END
            self.grid.end = node
        else:  # wall mode
            if node.state == CellState.EMPTY:
                node.state = CellState.WALL

        self.draw()

    def on_left_drag(self, event):
        if self.is_running or self.mode != "wall":
            return
        node = self._cell_from_event(event)
        if node and node.state == CellState.EMPTY:
            node.state = CellState.WALL
            self.draw()

    def on_right_click(self, event):
        if self.is_running:
            return
        node = self._cell_from_event(event)
        if node and node.state == CellState.WALL:
            node.state = CellState.EMPTY
            self.draw()

    # ---- Algorithm execution & animation ----------------------------------

    def run_algorithm(self):
        if self.is_running:
            return
        if not self.grid.start or not self.grid.end:
            self.status.config(text="Please set both a Start and an End cell first.")
            return

        self.clear_path()
        algo = ALGORITHMS[self.algo_var.get()]
        self.status.config(text=f"Running {algo.name}...")
        visited_order, path = algo.search(self.grid)
        self.is_running = True
        self._animate(visited_order, path, index=0)

    def _animate(self, visited_order, path, index):
        if index < len(visited_order):
            node = visited_order[index]
            if node.state not in (CellState.START, CellState.END):
                node.state = CellState.VISITED
            self.draw()
            self.root.after(6, lambda: self._animate(visited_order, path, index + 1))
        else:
            if path:
                self._animate_path(path, 0)
            else:
                self.status.config(text="No path found — the end is unreachable.")
                self.is_running = False

    def _animate_path(self, path, index):
        if index < len(path):
            node = path[index]
            if node.state not in (CellState.START, CellState.END):
                node.state = CellState.PATH
            self.draw()
            self.root.after(12, lambda: self._animate_path(path, index + 1))
        else:
            self.status.config(text=f"Path found! Length: {len(path)} steps.")
            self.is_running = False

    # ---- Reset ---------------------------------------------------------

    def clear_path(self):
        self.grid.reset_search_state()
        self.draw()

    def clear_all(self):
        self.grid.clear_all()
        self.is_running = False
        self.status.config(text="Grid cleared. Set a Start and End cell.")
        self.draw()

    # ---- Rendering -------------------------------------------------------

    def draw(self):
        self.canvas.delete("all")
        for row in self.grid.nodes:
            for node in row:
                x0, y0 = node.col * CELL_SIZE, node.row * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=COLORS[node.state],
                                              outline="#11111b")


def main():
    root = tk.Tk()
    VisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
