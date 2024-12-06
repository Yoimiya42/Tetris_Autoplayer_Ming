from board import Direction, Rotation, Action
from random import Random
import time

# v1.0

class Player:
    def choose_action(self, board):
        raise NotImplementedError

class MingPlayer(Player):
    
    previous_score = 0
    # NOTE: The weights are based on the paper (Modified slightly by me)
    # https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
    weighted_stack_height= - 0.510066
    weighted_holes = - 0.35663
    weighted_bumpiness = - 0.184483
    weighted_lines_cleared = 0.760066

    def __init__ (self, seed = None):
        self.random = Random(seed)
        return
        
    

#  Heuristic 1 :  Stack Height
    def _generate_heights_list(self,board):
        heights_list = []
        for x in range(board.width):
            for y in range(board.height):
                if (x,y) in board.cells:
                    heights_list.append(board.height- y)
                    break
                heights_list.append(0)

        return heights_list
    
    def _get_max_height(self, board):
        return max(self._generate_heights_list(board))

    def calculate_stack_height(self, board):
        return sum(self._generate_heights_list(board))

#  Heuristic 2 :  Holes
    def calculate_holes(self, board):
        holes = 0
        for x in range(board.width):
            tip_reached = False
            for y in range(board.height):
                if (x,y) in board.cells:
                    tip_reached = True
                if tip_reached and (x, y) not in board.cells:
                    holes += 1
        return holes

#  Heuristic 3 :  Bumpiness
    def calculate_bumpiness(self, board):
        heights_list = self._generate_heights_list(board)
        bumpiness = 0
        for i in range(len(heights_list)-1):
            bumpiness += abs(heights_list[i] - heights_list[i+1])

        return bumpiness

#  Heuristic 4 :  Lines Cleared
    def calculate_lines_cleared(self, board):
  
        current_score = board.score
        diff_score = current_score - self.previous_score

        lines_cleared =0 

        if diff_score >= 1600:
            lines_cleared = 4
            return 100
        
        elif diff_score >= 400:
            lines_cleared = 3
        elif diff_score >= 100:
            lines_cleared = 2
        elif diff_score >= 25:
            lines_cleared = 1

        return lines_cleared

#  Evaluation Function
    def evaluation(self, board):

        stack_height = self.calculate_stack_height(board)
        holes = self.calculate_holes(board)
        bumpiness = self.calculate_bumpiness(board)
        lines_cleared = self.calculate_lines_cleared(board)



        
        evaluation_score = (  self.weighted_stack_height *  stack_height 
                            + self.weighted_holes *         holes 
                            + self.weighted_bumpiness *     bumpiness 
                            + self.weighted_lines_cleared * lines_cleared)
        
        return evaluation_score
    

# Action Functions

    def rotation(self, board, times):
        if times == 1 :
            board.rotate(Rotation.Clockwise)
            return [Rotation.Clockwise]
        if times == 2 :
            board.rotate(Rotation.Clockwise)
            board.rotate(Rotation.Clockwise)
            return [Rotation.Clockwise, Rotation.Clockwise]
        if times == 3 :
            board.rotate(Rotation.Anticlockwise)
            return [Rotation.Anticlockwise]

        
    def translation(self, board, dest_x):
        start_x = board.falling.left
        has_landed = False
        if dest_x > start_x:
            while has_landed == False and dest_x > board.falling.left:
                has_landed = board.move(Direction.Right)
            return [Direction.Right for _ in range(dest_x - start_x)]
        
        elif dest_x < start_x:
            while has_landed == False and dest_x < board.falling.left:
                has_landed = board.move(Direction.Left)
            return [Direction.Left for _ in range(start_x - dest_x)] 
        
        return [None]      
            

# Core Function
    def choose_action(self, board):
         
        self.previous_score = board.score
        previous_holes = self.calculate_holes(board)

        min_height = min(self._generate_heights_list(board))
        max_height = max(self._generate_heights_list(board))
        diff_height = max_height - min_height
        
        best_score = -99999
        best_actions = []

        if board.falling is None:
            return Direction.Down
        
        elif board.falling is not None: 


           
            
            
            for rot1 in range(4):
                if rot1 > 0:
                    rotation_board1 = board.clone()
                    rotation_list1 = self.rotation(rotation_board1, rot1)

                for trans1 in range(1,board.width):
                    translation_board1 = rotation_board1.clone()
                    translation_list1 = self.translation(translation_board1, trans1)
    
                    translation_board1.move(Direction.Drop)
                    actions_list1 = rotation_list1 + translation_list1 + [Direction.Drop]

                    if translation_board1.falling is None:
                        return Direction.Down
                    
                    for rot2 in range(4):
                        rotation_board2 = translation_board1.clone()
                        rotation_list2 = self.rotation(rotation_board2, rot2)
                        for trans2 in range(1,board.width):
                            translation_board2 = rotation_board2.clone()
                            translation_list2 = self.translation(translation_board2, trans2)

                            if translation_board2.falling is None:
                                return Direction.Down

                            translation_board2.move(Direction.Drop)
                            actions_list2 = rotation_list2 + translation_list2 + [Direction.Drop]

                            final_board = translation_board2

                            score = self.evaluation(final_board)

                            if score > best_score:
                                best_score = score
                                best_actions = actions_list1

            height = self._generate_heights_list(final_board)
            if max(height) > 15:
                if board.bombs_remaining > 0:
                    best_actions.append(Action.Bomb)
                elif board.discards_remaining > 0:
                    return Action.Discard
                
            best_actions.append(Direction.Drop)

                        
            return best_actions


SelectedPlayer = MingPlayer
