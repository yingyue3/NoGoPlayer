"""
nogo4.py

Implements the basic NoGo player. 
- initialize board for the game
- initial the NoGo player
- initial the connection to the GTP comment

Written by the Yingyue Cao, Xinran Li and Lingrui Zhou, based on CMPUT455 sample codes
"""
from gtp_connection import GtpConnection
from board_base import DEFAULT_SIZE, GO_POINT, GO_COLOR
from board import GoBoard
from board_util import GoBoardUtil
from engine import GoEngine
from math import sqrt
from mcts import MCTS, TreeNode
from typing import List, Tuple
from gain_weight import weight_map

# gain the original weight map
weight_map = weight_map()

def count_at_depth(node: TreeNode, depth: int, nodesAtDepth: List[int]) -> None:
    """
    check the depth of all the nodes
    """
    if not node.expanded:
        return
    nodesAtDepth[depth] += 1
    for _, child in node.children.items():
        count_at_depth(child, depth + 1, nodesAtDepth)

class NoGo:
    def __init__(        
        self,
        num_simulation,
        limit = 100,
        exploration: float = sqrt(2)):
        """
        NoGo player that selects moves from the MCTS and simulation.
        Does not use the fill-eye filter.
        Passes only if there is no other legal move.

        Parameters
        ----------
        num_simulation: number of times the simulation runs
        """
        GoEngine.__init__(self, "topPlayer", 1.0)
        self.MCTS = MCTS()
        self.exploration = exploration
        self.num_simulation = num_simulation
        self.limit = limit

    def reset(self) -> None:
        """
        reset the MCTS
        """
        self.MCTS = MCTS()

    def update(self, move: GO_POINT) -> None:
        """
        update the player's with the root MCTS took and the move took
        """
        self.parent = self.MCTS.root
        self.MCTS.update_with_move(move)

    def get_move(self, board: GoBoard, color: GO_COLOR) -> GO_POINT:
        """
        get move using MCTS and simulation
        """
        move = self.MCTS.get_move(
            board,
            color,
            limit=self.limit,
            num_simulation=self.num_simulation,
            exploration=self.exploration
        )
        self.update(move)
        return move

    def get_node_depth(self, root: TreeNode) -> List[int]:
        """
        restriced the search depth to 100 in order to decrease the running time
        """
        MAX_DEPTH = 100
        nodesAtDepth = [0] * MAX_DEPTH
        count_at_depth(root, 0, nodesAtDepth)
        return nodesAtDepth

    def get_random_best_move(self, board: GoBoard, color: GO_COLOR):
        """
        if the simulation time exceed, get the random move from the neighbors according to
        the weight maps
        """
        legal_moves = GoBoardUtil.generate_legal_moves(board, color)
        weights = []
        for move in legal_moves:
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
            weights.append(weight_map.weight_map[count])
        if len(legal_moves) == 0:
            return None
        index = weights.index(max(weights))
        return legal_moves[index]





def run() -> None:
    """
    start the gtp connection and wait for commands.
    """
    board: GoBoard = GoBoard(DEFAULT_SIZE)
    con: GtpConnection = GtpConnection(NoGo(500), board)
    con.start_connection()


if __name__ == "__main__":
    run()
