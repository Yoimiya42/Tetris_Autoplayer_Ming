from board import Direction, Rotation, Action
from random import Random
import time

# v2.0

class Player:
    def choose_action(self, board):
        raise NotImplementedError

class MingPlayer(Player):
    
    previous_score = 0
    previous_height = 0
    # NOTE: The weights are based on the paper (Modified slightly by me)
    # https://codemyroad.wordpress.com/2013/04/14/tetris-ai-the-near-perfect-player/
    weighted_height= - 0.510066
    weighted_holes = - 0.954915
    weighted_bumpiness = - 0.184483
    weighted_lines_cleared = 1.5 #0.760066

    counter_block = 1

    def __init__ (self, seed = None):
        self.random = Random(seed)
        
        
    

#  Heuristic 1 :  Stack Height
    def _generate_heights_list(self, board):
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
    
    def calculate_height_increase(self, board):
        min_block_row = 24
        for (x, y) in board.cells:
            if y < min_block_row:
                min_block_row = y

        height_increase = (24 - min_block_row) - self.previous_height
        if height_increase >0 :
            return height_increase 
        else:
            return 0

#  Heuristic 2 :  Holes
    def _generate_holes_lists(self, board):
        holes_lists = [0] * board.width
        for x in range(board.width):
            tip_reached = False
            for y in range(board.height):
                if (x,y) in board.cells:
                    tip_reached = True
                if tip_reached and (x, y) not in board.cells:
                    holes_lists [x] += 1 
        return holes_lists
    
    def calculate_total_holes(self, board):
        return sum(self._generate_holes_lists(board))
    
    def calculate_wells(self, board):
        return max(self._generate_holes_lists(board))
    
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

        return lines_cleared * self.weighted_lines_cleared    

#  Evaluation Function
    def evaluation(self, board):

        stack_height = self.calculate_stack_height(board)
        max_height = self._get_max_height(board)
        height_increase = self.calculate_height_increase(board)
        holes = self.calculate_total_holes(board)
        bumpiness = self.calculate_bumpiness(board)
        score_lines_cleared = self.calculate_lines_cleared(board)
        wells = self.calculate_wells(board)

        
        evaluation_score = (  #self.weighted_stack_height *  stack_height 
                              self.weighted_height   *      height_increase
                            + self.weighted_holes*          holes 
                            + self.weighted_holes * wells * 1.5
                            + self.weighted_bumpiness *     bumpiness
                            + score_lines_cleared)
                            
        
        return evaluation_score
    

# Action Functions

    def rotation(self, board, times):

        if (board.falling is not None) and (board.falling.shape != "Shape.O"):
            if times == 1:
                return [Rotation.Clockwise]
            elif times == 2:   
                return [Rotation.Clockwise, Rotation.Clockwise]
            elif times == 3:
                return [Rotation.Anticlockwise]
            

    def translation(self, board, dest_x):
        landed = False
        trans_list = []
        
        start_x = board.falling.left

        while start_x < dest_x:
            board.move(Direction.Right)
            trans_list.append(Direction.Right)
            if board.falling is not None:
                start_x = board.falling.left
            else:
                landed = True
                break

        while start_x > dest_x:
            board.move(Direction.Left)
            trans_list.append(Direction.Left)
            if board.falling is not None:
                start_x = board.falling.left
            else:
                landed = True
                break            
        
        return landed, trans_list

# Core Function
    
    def choose_action(self, board):
        self.counter_block +=1 
        print("block:", self.counter_block)
        self.previous_score = board.score
        print("current score:", self.previous_score)
        # previous_holes = self.calculate_holes(board)

        min_height = min(self._generate_heights_list(board))
        max_height = max(self._generate_heights_list(board))
        diff_height = max_height - min_height
        
        best_score = -99999
        best_actions = []
        self.previous_height = self._get_max_height(board)

        start_column = 0
        if diff_height != 4 and max_height <6:
            start_column = 1
        else:
            start_column = 0
            
        if board.bombs_remaining > 0 and max_height > 18:
            return [Action.Bomb]

        for trans1 in range(start_column,board.width):
            for rot1 in range(4):
                demo1_board = board.clone()
                actions_list1 = []
                has_landed1 = False
                
                if rot1 > 0:
                    # actions_list1.extend(self.rotation(demo1_board, rot1))
                    for _ in range(0, rot1):
                        if demo1_board.falling is not None: 
                            demo1_board.rotate(Rotation.Anticlockwise)
                            actions_list1.append(Rotation.Anticlockwise)
                if demo1_board.falling is not None:
                    start_x = demo1_board.falling.left

                    while start_x < trans1 and has_landed1 == False:
                        demo1_board.move(Direction.Right)
                        actions_list1.append(Direction.Right)
                        if demo1_board.falling is not None:
                            start_x = demo1_board.falling.left
                        else:
                            has_landed1 = True
                            break

                    while start_x > trans1 and has_landed1 == False:
                        demo1_board.move(Direction.Left)
                        actions_list1.append(Direction.Left)    
                        if demo1_board.falling is not None:
                            start_x = demo1_board.falling.left
                        else:
                            has_landed1 = True
                            break         
                
                    if not has_landed1:
                        demo1_board.move(Direction.Drop)
                        actions_list1.append(Direction.Drop)
                        has_landed1 = True

                    score1 = self.evaluation(demo1_board)
##############################################################################
                if has_landed1 :
                    for trans2 in range(board.width):
                        for rot2 in range(4):
                
                            demo2_board = demo1_board.clone()
                            actions_list2 = []
                            has_landed2 = False

                            if rot2 > 0:
                                # actions_list2.extend(self.rotation(demo2_board, rot2))
                                for _ in range(0, rot1):
                                    if demo2_board.falling is not None: 
                                        demo2_board.rotate(Rotation.Anticlockwise)
                                        actions_list2.append(Rotation.Anticlockwise)
                            if demo2_board.falling is not None:
                                start_x = demo2_board.falling.left

                                while start_x < trans2 and has_landed2 == False:
                                    demo2_board.move(Direction.Right)
                                    actions_list1.append(Direction.Right)
                                    if demo2_board.falling is not None:
                                        start_x = demo2_board.falling.left
                                    else:
                                        has_landed2 = True
                                        break

                                while start_x > trans2 and has_landed2 == False:
                                    demo2_board.move(Direction.Left)
                                    actions_list1.append(Direction.Left)    
                                    if demo2_board.falling is not None:
                                        start_x = demo2_board.falling.left
                                    else:
                                        has_landed2 = True
                                        break         
                
                                if not has_landed2:
                                    demo2_board.move(Direction.Drop)
                                    actions_list2.append(Direction.Drop)

                                score2 = self.evaluation(demo2_board)
                                final_score = score2
                            
                            if final_score > best_score:
                                best_score = final_score
                                best_actions = actions_list1
                                best_board = demo2_board
    

                            height = self._generate_heights_list(best_board)
                            if max(height) > 18 and board.bombs_remaining > 0:
                                    # best_actions.append(Action.Bomb)
                                    return [Action.Bomb]
        
        return best_actions


SelectedPlayer = MingPlayer



#  self.previous_score = board.score
#         previous_holes = self.calculate_holes(board)

#         min_height = min(self._generate_heights_list(board))
#         max_height = max(self._generate_heights_list(board))
#         diff_height = max_height - min_height
        
#         best_score = -99999
#         best_actions = []
        

#         for trans1 in range(0, board.width):
#             for rot1 in range(4):
#                 demo1_board = board.clone()
#                 actions_list1 = []
#                 has_landed1 = False
                
#                 if rot1 > 0:
#                     actions_list1.extend(self.rotation(demo1_board, rot1))
#                 if board.falling is not None:
#                     has_landed1 , trans_list1 = self.translation(demo1_board, trans1)
#                     actions_list1.extend(trans_list1)
                
#                     if not has_landed1:
#                         demo1_board.move(Direction.Drop)
#                         actions_list1.append(Direction.Drop)
#                         has_landed1 = True

#                     score1 = self.evaluation(demo1_board)
# ##############################################################################
#                 if has_landed1 :
#                     for rot2 in range(4):
#                         for trans2 in range(board.width):
#                             demo2_board = demo1_board.clone()
#                             actions_list2 = []
#                             has_landed2 = False

#                             if rot2 > 0:
#                                 actions_list2.extend(self.rotation(demo2_board, rot2))
#                             if board.falling is not None:
#                                 has_landed2, trans_list2 = self.translation(demo2_board, trans2)
#                                 actions_list2.extend(trans_list2)

#                                 if not has_landed2:
#                                     demo2_board.move(Direction.Drop)
#                                     actions_list2.append(Direction.Drop)

#                                 score2 = self.evaluation(demo2_board)
#                                 final_score = score2
                            
#                             if final_score > best_score:
#                                 best_score = final_score
#                                 best_actions = actions_list1
#                                 best_board = demo2_board
    

#                             height = self._generate_heights_list(best_board)
#                             if max(height) > 15 and board.bombs_remaining > 0:
#                                     best_actions.append(Action.Bomb)
        
#         return best_actions
