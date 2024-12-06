from board import Direction, Rotation, Action, Shape
from random import Random
import time


class Player:
    def choose_action(self, board):
        raise NotImplementedError

class MingPlayer(Player):
    def __init__(self):
        self.best_actions = []

    previous_score = 0
    previous_height = 24
    previous_holes = 0
    # weighted for each heuristic
    weighted_height= - 0.510066
    weighted_holes = - 0.955 #- 0.954915
    weighted_bumpiness = - 0.184483
    weighted_lines_cleared = 1.5 #0.760066

    bottom_holes_penalty = 0

    initLine = 0
    
    counter_block = 1

    lines_cleared = 0
    
    discord_counter = 0
#_______________________________________________________________________________#
    #  Heuristic 1 :  Height Increase

    def _generate_height_lists(self,board):
        height_lists = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for y in reversed(range(board.height)):
            for x in range(10):
                if (x,y) in board.cells:
                    height = 24 - y
                    height_lists[x] = height
        return height_lists
    
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
        
    def _get_max_height(self, board):
        return max(self._generate_height_lists(board))
        
    # Heuristic 2 :  Holes

    def _generate_holes_lists(self, board):
        holes_lists = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for x in range(board.width):
            tip_reached = False
            for y in range(board.height):
                if (x,y) in board.cells:
                    tip_reached = True
                if tip_reached and (x, y) not in board.cells:
                    holes_lists [x] += 1 
                    # if y >= board.height - 4:
                    #     holes_lists [x] += (y - (board.height - 4) + 1)

        return holes_lists 
    
    def calculate_total_holes(self, board):
        return sum(self._generate_holes_lists(board))
    
    # Heuristic 3 :  Wells
    def calculate_wells(self,board):
        holes = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        height_list = self._generate_height_lists(board)
        for x in range(10):
            for y in range(24 - height_list[x],24):
                if (x,y) not in board.cells:
                    holes[x] += 1
        max_holes = max(holes)
        return max_holes
    
    
    # Heuristic 4 :  Bumpiness
    def calculate_bumpiness(self, board):
        height_list = self._generate_height_lists(board)
        bumpiness = 0
        
        for i in range(len(height_list) - 1):
            bumpiness += abs(height_list[i] - height_list[i+1]) 
            #abs(height_list[i] - height_list[i+1])
        return bumpiness

    #  Heuristic 5 :  Lines Cleared
    def calculate_lines_cleared(self, board):
  
        current_score = board.score
        diff_score = current_score - self.previous_score

        self.lines_cleared =0 

        if diff_score >= 1600:
            self.lines_cleared = 4
            return 100 #100
        
        elif diff_score >= 400:
            self.lines_cleared = 3
        elif diff_score >= 100:
            self.lines_cleared = 2
        elif diff_score >= 25:
            self.lines_cleared = 1

        return self.lines_cleared * self.weighted_lines_cleared
    
    # Heuristic 6 
                               
    
######################################### Evaluation Function #############################################
    def evaluation(self, board):

        height_increase = self.calculate_height_increase(board)
        bumpiness = self.calculate_bumpiness(board)
        holes = self.calculate_total_holes(board)
        wells = self.calculate_wells(board)
        lines_cleared = self.calculate_lines_cleared(board)
        

        evaluation_score = (height_increase * self.weighted_height 
                            + holes * self.weighted_holes
                            # + self.bottom_holes_penalty * self.weighted_holes
                            + wells * self.weighted_holes * 2.0
                            + bumpiness * self.weighted_bumpiness 
                            + lines_cleared)
        
        
        return evaluation_score
#_________________________________________________________________________________________________________#
   # Action Selection
    def _rotate_and_record(self, board, rotations, actions_list):
        for _ in range(rotations):
            if board.falling is not None and board.falling.shape != Shape.O:
                board.rotate(Rotation.Anticlockwise)
                actions_list.append(Rotation.Anticlockwise)

    def _move_and_record(self, board, target_x, actions_list):
        has_landed = False
        start_x = board.falling.left if board.falling is not None else None

        while start_x is not None and start_x > target_x and not has_landed:
            board.move(Direction.Left)
            actions_list.append(Direction.Left)
            start_x = board.falling.left if board.falling is not None else None
            if start_x is None:
                has_landed = True
                break

        while start_x is not None and start_x < target_x and not has_landed:
            board.move(Direction.Right)
            actions_list.append(Direction.Right)
            start_x = board.falling.left if board.falling is not None else None
            if start_x is None:
                has_landed = True
                break

        return has_landed


  
        
#_______________________________________________________________________________#
    def choose_action(self, board):

        self.counter_block += 1
        print(self.counter_block)

        best_actions = []

        final_score = 0
        best_score = -999999
        self.previous_score = board.score

        self.previous_holes = self.calculate_total_holes(board)
        best_holes = 0
        # self.bottom_holes_penalty = 0

        max_height = max(self._generate_height_lists(board))
        first_height = self._generate_height_lists(board)[0]
        diff_height = max_height - first_height
        self.prevHeight = max_height


        if max_height > 18 and board.bombs_remaining > 0:
            return Action.Bomb
        
        if board.falling.shape != Shape.I and self.counter_block > 150:
            self.discord_counter += 1
        else:
            self.discord_counter = 0
        print("discord_counter:", self.discord_counter)

        if self.discord_counter > 10 and board.discards_remaining > 0 and max_height > 16 and self.counter_block > 150:
            self.discord_counter -= 1
            return [Action.Discard]  
        # if self.discord_counter > 6 and board.discards_remaining > 0 and max_height > 14 and self.counter_block > 300:
        #     self.discord_counter -= 1
        #     return [Action.Discard]

        ###### 1st block ######
        if max_height < 8 and diff_height < 6:
            start = 1 
        else:
            start = 0 

        for trans1 in range(start, 10):
            for rot1 in range(0, 4):
                demo1_board = board.clone()
                actions_list1 = []
                has_landed1 = False

                if rot1 > 0:
                    self._rotate_and_record(demo1_board, rot1, actions_list1)

                if demo1_board.falling is not None:
                    has_landed1 = self._move_and_record(demo1_board, trans1, actions_list1)

                    if not has_landed1:
                        demo1_board.move(Direction.Drop)
                        actions_list1.append(Direction.Drop)
                        has_landed1 = True

                    score1 = self.evaluation(demo1_board)

                ###### 2nd block ######
                if has_landed1:
                    for trans2 in range(10):
                        for rot2 in range(4):
                            demo2_board = demo1_board.clone()
                            has_landed2 = False

                            if rot2 > 0:
                                self._rotate_and_record(demo2_board, rot2, [])

                            if demo2_board.falling is not None:
                                has_landed2 = self._move_and_record(demo2_board, trans2, [])

                                if not has_landed2:
                                    demo2_board.move(Direction.Drop)

                                score2 = self.evaluation(demo2_board)
                                final_score = score2

                            if final_score > best_score:
                                best_score = final_score
                                best_actions = actions_list1
                                best_holes = self.calculate_total_holes(demo2_board)
                                best_board = demo2_board

        if self._get_max_height(best_board) > 16 and self.lines_cleared <= 1 and board.bombs_remaining > 0:
            return Action.Bomb
        
        if best_holes - self.previous_holes > 0 and board.discards_remaining > 0 :
            return Action.Discard

        print("Best score: ", best_score)
        print("Best actions: ", best_actions)
        return best_actions

SelectedPlayer = MingPlayer