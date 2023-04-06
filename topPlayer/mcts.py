"""
mcts.py

Implements the MCTS methods and simulation
- use UCT to choose the best actions
- expand the chosen parent node to get the childrens

Implements TreeNode Class contains nodes to expand

Written by the Yingyue Cao, Xinran Li and Lingrui Zhou, based on CMPUT455 sample codes
"""
from board_base import opponent, BLACK, WHITE, GO_COLOR, GO_POINT, NO_POINT, coord_to_point
from board import GoBoard
from gain_weight import weight_map
from board_util import GoBoardUtil
from gtp_connection import point_to_coord, format_point

import numpy as np
from typing import Dict, Tuple
import random
import signal

weight_map = weight_map()

def uct(child_wins: int, child_visits: int, parent_visits: int, exploration: float) -> float:
    return child_wins / child_visits + exploration * np.sqrt(np.log(parent_visits) / child_visits)

class TreeNode:
    """
    A node in the MCTS tree
    """

    def __init__(self, color: GO_COLOR) -> None:
        self.move: GO_POINT = NO_POINT
        self.color: GO_COLOR = color
        self.n_visits: int = 0
        self.n_opp_wins: int = 0
        self.parent: 'TreeNode' = self
        self.children: Dict[TreeNode] = {}
        self.expanded: bool = False
    
    def set_parent(self, parent: 'TreeNode') -> None:
        self.parent: 'TreeNode' = parent

    def expand(self, board: GoBoard, color: GO_COLOR) -> None:
        """
        Expands tree by creating new children.
        """
        opp_color = opponent(board.current_player)
        moves = board.get_empty_points()
        for move in moves:
            if board.is_legal(move, color):
                node = TreeNode(opp_color)
                node.move = move
                node.set_parent(self)
                self.children[move] = node

        self.expanded = True
    
    def select_in_tree(self, exploration: float) -> Tuple[GO_POINT, 'TreeNode']:
        """
        Select the child to be expand in the tree using UCT.
        """
        _child = None
        _uct_val = -1
        for move, child in self.children.items():
            if child.n_visits == 0:
                return child.move, child
            uct_val = uct(child.n_opp_wins, child.n_visits, self.n_visits, exploration)
            if uct_val > _uct_val:
                _uct_val = uct_val
                _child = child
        return _child.move, _child
    
    def select_best_child(self) -> Tuple[GO_POINT, 'TreeNode']:
        '''
        return the best child for the current step
        '''
        _n_visits = -1
        best_child = None
        for move, child in self.children.items():
            if child.n_visits > _n_visits:
                _n_visits = child.n_visits
                best_child = child
        return best_child.move, best_child
    
    def update(self, winner: GO_COLOR) -> None:
        self.n_opp_wins += self.color != winner
        self.n_visits += 1
        if not self.is_root():
            self.parent.update(winner)
    
    def is_leaf(self) -> bool:
        """
        Check if leaf node
        """
        return len(self.children) == 0
    
    def is_root(self) -> bool:
        """
        Check if root node
        """
        return self.parent == self
    

class MCTS:

    def __init__(self) -> None:
        self.root: 'TreeNode' = TreeNode(BLACK)
        self.root.set_parent(self.root)
        self.toplay: GO_COLOR = BLACK

        signal.signal(signal.SIGALRM, self.handler)
    
    def search(self, board: GoBoard, color: GO_COLOR) -> None:
        """
        search until the leaf node is met. Update the result of the game as the rewards
        """
        node = self.root
        # This will be True only once for the root
        if not node.expanded:
            node.expand(board, color)
        while not node.is_leaf():
            move, next_node = node.select_in_tree(self.exploration)
            board.play_move(move, color)
            color = opponent(color)
            node = next_node
        if not node.expanded:
            node.expand(board, color)
        
        assert board.current_player == color
        winner = self.pattern_simulation(board)
        node.update(winner)
    
    def pattern_simulation(self, board):
        """
        use the pattern simulation methods. Expand the nodes with the highest weight first.
        """
        while len(GoBoardUtil.generate_legal_moves(board, board.current_player)) > 0:
            
            color = board.current_player
            move = self.pattern_generate_move(board, color)
            board.play_move(move, color)

        if board.current_player == BLACK:
            return WHITE
        elif board.current_player == WHITE:
            return BLACK

    def pattern_generate_move(self, board, color):
        """
        generate move according to the weight
        """
        emptyPoints = board.get_empty_points()
        moves = []
        for p in emptyPoints:
            if board.is_legal(p, color):
                moves.append(p)
        range_list = self.pattern_prob_range(moves,board)
        number = random.random()

        for i in range(len(range_list)):
            if number < range_list[i] :
                return moves[i]

    def pattern_prob_range(self, moves, board):
        """
        generate the probability to choose a neighbots according to its weight in weighted map
        """
        prob_range = []
        score_list = []
        weight_sum = 0
        for move in moves:

            neighbors = []

            neighbors.append(board.board[move + board.NS - 1])
            neighbors.append(board.board[move + board.NS])
            neighbors.append(board.board[move + board.NS + 1])
            neighbors.append(board.board[move - 1])
            neighbors.append(board.board[move + 1])
            neighbors.append(board.board[move - board.NS - 1])
            neighbors.append(board.board[move - board.NS])
            neighbors.append(board.board[move - board.NS + 1])

            
            count = 0
            for i in range(len(neighbors)):
                count += neighbors[i] * pow(4, i)
            score_list.append(weight_map.weight_map[count])
            weight_sum += weight_map.weight_map[count]

        probability = []
        for i in range(len(moves)):
            probability.append(score_list[i] / weight_sum)

        bound = 0
        for p in probability:
            bound = bound + p
            prob_range.append(bound)
        return prob_range
    
    def get_move(
        self,
        board: GoBoard,
        color: GO_COLOR,
        limit: int,
        num_simulation: int,
        exploration: float
    ) -> GO_POINT:
        """
        Runs all playouts sequentially and returns the most visited move.
        This step is limited to run at most 30 sec
        """
        if self.toplay != color:
            self.toplay = color
            self.root = TreeNode(color)

        self.limit = limit
        self.exploration = exploration

        if not self.root.expanded:
            self.root.expand(board, color)

        count = num_simulation*len(self.root.children)
        try:
            signal.alarm(29)
            while count > 0:
                cboard = board.copy()
                self.search(cboard, color)
                count = count - 1
            signal.alarm(0)
        except Exception as e:
            pass

        # choose a move that has the most visit
        best_move, best_child = self.root.select_best_child()
        return best_move
    
    def update_with_move(self, last_move: GO_POINT) -> None:
        """
        update the tree with the move chosen
        """
        if last_move in self.root.children:
            self.root = self.root.children[last_move]
        else:
            self.root = TreeNode(opponent(self.toplay))
        self.root.parent = self.root
        self.toplay = opponent(self.toplay)

    def handler(self, signum, fram):
        raise TimeoutError("Time out!")
    
