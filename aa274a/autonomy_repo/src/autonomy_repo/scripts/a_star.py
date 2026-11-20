"""Copied from HW1"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from asl_tb3_lib.grids import StochOccupancyGrid2D

def plot_line_segments(segments, **kwargs):
    plt.plot([x for tup in [(p1[0], p2[0], None) for (p1, p2) in segments] for x in tup],
             [y for tup in [(p1[1], p2[1], None) for (p1, p2) in segments] for y in tup], **kwargs)

class AStar(object):
    """Represents a motion planning problem to be solved using A*"""

    def __init__(self, statespace_lo, statespace_hi, x_init, x_goal, occupancy: StochOccupancyGrid2D, resolution=1,
                 heuristic="l2", heuristic_weight=1.0):
        self.statespace_lo = statespace_lo         # state space lower bound (e.g., [-5, -5])
        self.statespace_hi = statespace_hi         # state space upper bound (e.g., [5, 5])
        self.occupancy = occupancy                 # occupancy grid (a StochOccupancyGrid2D object)
        self.resolution = resolution               # resolution of the discretization of state space (cell/m)
        self.heuristic_type = heuristic            # norm used by the heuristic: "l1", "l2", or "linf"
        self.heuristic_weight = heuristic_weight   # weight w >= 1 on the heuristic (w > 1 gives weighted A*)
        self.x_offset = x_init                     
        self.x_init = self.snap_to_grid(x_init)    # initial state
        self.x_goal = self.snap_to_grid(x_goal)    # goal state

        self.closed_set = set()    # the set containing the states that have been visited
        self.open_set = set()      # the set containing the states that are candidate for future expansion

        self.est_cost_through = {}  # dictionary of the estimated cost from start to goal passing through state (often called f score)
        self.cost_to_arrive = {}    # dictionary of the cost-to-arrive at state from start (often called g score)
        self.came_from = {}         # dictionary keeping track of each state's parent to reconstruct the path

        self.open_set.add(self.x_init)
        self.cost_to_arrive[self.x_init] = 0
        self.est_cost_through[self.x_init] = self.heuristic(self.x_init)

        self.path = None        # the final path as a list of states

    def is_free(self, x):
        """
        Checks if a give state x is free, meaning it is inside the bounds of the map and
        is not inside any obstacle.
        Inputs:
            x: state tuple
        Output:
            Boolean True/False
        """
        x = np.asarray(x)
        collision_free = self.occupancy.is_free(x)
        
        in_bounds = (
            x[0] >= self.statespace_lo[0] and
            x[1] >= self.statespace_lo[1] and
            x[0] <= self.statespace_hi[0] and
            x[1] <= self.statespace_hi[1]
        )
        
        return collision_free and in_bounds

    def distance(self, x1, x2):
        return np.linalg.norm(np.asarray(x1) - np.asarray(x2))

    def heuristic(self, x):
        """
        Computes the weighted heuristic estimate of the cost-to-go from state x
        to self.x_goal, i.e. w * ||x - x_goal||, where w = self.heuristic_weight
        and the norm is selected by self.heuristic_type:
            "l1":   sum of absolute coordinate differences
            "l2":   Euclidean norm
            "linf": largest absolute coordinate difference
        Input:
            x: state tuple
        Output:
            Float heuristic value
        """
        ########## Code starts here ##########
        if self.heuristic_type not in ["l1", "l2", "linf"]:
            raise ValueError(f"Unrecognized heuristic_type: {self.heuristic_type}")
        
        ord = {"l1": 1, "l2": 2, "linf": np.inf}
        
        return self.heuristic_weight * float(np.linalg.norm(np.asarray(self.x_goal) - np.asarray(x), ord=ord[self.heuristic_type]))
        ########## Code ends here ##########

    def snap_to_grid(self, x):
        """ Returns the closest point on a discrete state grid
        Input:
            x: tuple state
        Output:
            A tuple that represents the closest point to x on the discrete state grid
        """
        return (
            self.resolution * round((x[0] - self.x_offset[0]) / self.resolution) + self.x_offset[0],
            self.resolution * round((x[1] - self.x_offset[1]) / self.resolution) + self.x_offset[1],
        )

    def get_neighbors(self, x):
        """
        Gets the FREE neighbor states of a given state x. Assumes a motion model
        where we can move up, down, left, right, or along the diagonals by an
        amount equal to self.resolution.
        Input:
            x: tuple state
        Ouput:
            List of neighbors that are free, as a list of TUPLES
        """
        neighbors = []
        ########## Code starts here ##########
        
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                if i == 0 and j == 0:
                    continue

                candidate = self.snap_to_grid((x[0] + i*self.resolution, x[1] + j*self.resolution))
                if not self.is_free(candidate):
                    continue
                
                neighbors.append(candidate)
        ########## Code ends here ##########
        return neighbors

    def find_best_est_cost_through(self):
        """
        Gets the state in open_set that has the lowest est_cost_through
        Output: A tuple, the state found in open_set that has the lowest est_cost_through
        """
        return min(self.open_set, key=lambda x: self.est_cost_through[x])

    def reconstruct_path(self):
        """
        Use the came_from map to reconstruct a path from the initial location to
        the goal location
        Output:
            A list of tuples, which is a list of the states that go from start to goal
        """
        path = [self.x_goal]
        current = path[-1]
        while current != self.x_init:
            path.append(self.came_from[current])
            current = path[-1]
        return list(reversed(path))

    def solve(self):
        """
        Solves the planning problem using the A* search algorithm. It places
        the solution as a list of tuples (each representing a state) that go
        from self.x_init to self.x_goal inside the variable self.path
        Input:
            None
        Output:
            Boolean, True if a solution from x_init to x_goal was found
        """
        # Init sets
        self.open_set.clear()
        self.open_set.add(self.snap_to_grid(self.x_init))
        self.closed_set.clear()
    
        # Costs and clearing
        self.cost_to_arrive = {self.x_init: 0}
        self.est_cost_through = {self.x_init: self.heuristic(self.x_init)}
        self.came_from = {}
        self.path = None
        
        while len(self.open_set) > 0:
            x_curr = self.snap_to_grid(self.find_best_est_cost_through())
            if x_curr == self.x_goal:
                self.path = self.reconstruct_path()
                return True
            
            self.open_set.remove(x_curr)
            self.closed_set.add(x_curr)
            

            
            for x_neigh in self.get_neighbors(x_curr):
                if x_neigh in self.closed_set:
                    continue
                
                tentative_cost_to_arrive = self.cost_to_arrive[x_curr] + self.distance(x_curr, x_neigh)
                
                if x_neigh not in self.open_set:
                    self.open_set.add(x_neigh)

                elif tentative_cost_to_arrive > self.cost_to_arrive[x_neigh]:
                    continue
                
                self.came_from[x_neigh] = x_curr
                self.cost_to_arrive[x_neigh] = tentative_cost_to_arrive
                self.est_cost_through[x_neigh] = tentative_cost_to_arrive + self.heuristic(x_neigh)                
                    
        return False

# class DetOccupancyGrid2D(object):
#     """
#     A 2D state space grid with a set of rectangular obstacles. The grid is
#     fully deterministic
#     """
#     def __init__(self, width, height, obstacles):
#         self.width = width
#         self.height = height
#         self.obstacles = obstacles

#     def is_free(self, x):
#         """Verifies that point is not inside any obstacles by some margin"""
#         for obs in self.obstacles:
#             if x[0] >= obs[0][0] - self.width * .01 and \
#                x[0] <= obs[1][0] + self.width * .01 and \
#                x[1] >= obs[0][1] - self.height * .01 and \
#                x[1] <= obs[1][1] + self.height * .01:
#                 return False
#         return True

#     def plot(self, fig_num=0):
#         """Plots the space and its obstacles"""
#         fig = plt.figure(fig_num)
#         ax = fig.add_subplot(111, aspect='equal')
#         for obs in self.obstacles:
#             ax.add_patch(
#             patches.Rectangle(
#             obs[0],
#             obs[1][0]-obs[0][0],
#             obs[1][1]-obs[0][1],))
#         ax.set(xlim=(0,self.width), ylim=(0,self.height))
