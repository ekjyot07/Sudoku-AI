import numpy as np
import itertools
from collections import deque
import sys

class SudokuBoard(object):
    
    def __init__(self, config):
        
        self.config = config
        
        self.variables = [row + str(col) for row in 'ABCDEFGHI' for col in np.arange(1,10)]
        
        self.board = {v : config[i] for i, v in enumerate(self.variables)}

        self.domains = {v: list(range(1, 10)) if config[i] == '0' else [int(config[i])] for i, v in enumerate(self.variables)}
        
        self.constraints = set()
        
        self.generateConstraints()
        
        self.arcs = dict()
        
        self.generateArcs()
        
        self.pruned = {v: list() if config[i] == '0' else [int(config[i])] for i, v in enumerate(self.variables)}
        
    
    #display the sudoku board
    def display(self):

        for i in range(9):

            line = []

            offset = i * 9
            
            if i%3 == 0 and i != 0:
                print(' '.join(['—' for x in range(11)]))
            
            for j in range(9):
                
                if j%3 == 0 and j != 0: 
                    line.append('|')
                
                line.append(str(self.config[offset + j]))
            
            print(' '.join(line))
            
            
    #generating row, column and block constraints
    def generateConstraints(self):
        
        nAryConstraints = list()
        
        #row constraints
        for row in 'ABCDEFGHI':
            nAryConstraints.append([row + str(col) for col in np.arange(1, 10)])
        
        #column constraints
        for col in np.arange(1, 10):
            nAryConstraints.append([row + str(col) for row in 'ABCDEFGHI'])
        
        #block constraints
        for row in ('ABC', 'DEF', 'GHI'):
            for col in ('123', '456', '789'):
                nAryConstraints.append([r + str(c) for r in row for c in col])
        
        #converting n-ary constraints to binary constraints
        for nAryconstraint in nAryConstraints:
            for binaryTuple in itertools.permutations(nAryconstraint, 2):
                if binaryTuple not in self.constraints:
                    self.constraints.add(binaryTuple) 
    
    
    #generate arcs from constraint tuples
    def generateArcs(self):
    
        for variable in self.variables:
            self.arcs[variable] = list()
            
            for constraint in self.constraints:
                if constraint[0] == variable:
                    self.arcs[variable].append(constraint[1])
   


def AC3(board):
    
    queue = deque(board.constraints)
    
    while queue:
        
        Xi, Xj = queue.popleft()
        
        if revise(board, Xi, Xj):
            if len(board.domains[Xi]) == 0:
                return False
            
            for Xk in board.arcs[Xi]:
                if Xk != Xj:
                    queue.append([Xk, Xi])
                    
    return True

                                    
def revise(board, Xi, Xj):
    
    revised = False
    
    for x in board.domains[Xi]:
        if not any([x!=y for y in board.domains[Xj]]):
            board.domains[Xi].remove(x)
            revised = True
    return revised


#Backtacking Search
def BTS(board):
    return Backtrack({}, board)


def Backtrack(assignment, board):
    
    #assignment is {variable, value} pair for all the varialbes (cells) in the sudoku board
    
    if len(assignment) == len(board.variables):
        return assignment
    
    # which variable should be assigned next?
    var = Select_Unassigned_Variable(board, assignment)

    # In what order should its values be tried?
    for val in Order_domain_values(var, board):
        
        if isConsistent(assignment, val, var, board):
            
            assignment[var] = val
            
            ForwardChecking(assignment, val, var, board)
            
            result = Backtrack(assignment, board)
            
            if result:
                return result
        
            #add back pruned items during ForwardChecking and remove assignment
            for (arc, v) in board.pruned[var]:
                board.domains[arc].append(v)

            board.pruned[var] = []

            assignment.pop(var)
    
    return False
            

# Minimum Remaining Values -- Choose the variable with the fewest legal values in its domain
def Select_Unassigned_Variable(board, assignment):
    
    unassignedVariables = []
    
    mrv = None
    minVal = sys.maxsize
    
    for var in board.variables:
        if var not in assignment:
            if len(board.domains[var]) < minVal:
                mrv = var 
                minVal = len(board.domains[var])
    
    return mrv

# Least constraining value -- Given a variable, choose the value that rules out the fewest values in the remaining variables
def Order_domain_values(var, board):
    
    if len(board.domains[var]) == 1:
        return board.domains[var]
    
    constraints = dict()
    
    for val in board.domains[var]:
        count = 0
        
        for arc in board.arcs[var]:
            if val in board.domains[arc]:
                count += 1
                
        constraints[val] = count
        
    return sorted(board.domains[var], key=lambda val: constraints[val])        


#checks if an assignment violates any constraint
def isConsistent(assignment, val, var, board):
    
    isConsistent = True
    
    for assigned_var, assigned_val in assignment.items():
        if assigned_val == val and assigned_var in board.arcs[var]:
            isConsistent = False
    
    return isConsistent
    
    
#Keep track of remaining legal values for the unassigned variables, terminate when any variable has no legal values.
def ForwardChecking(assignment, val, var, board):
    
    unassigned_arcs = {unassigned_var: board.arcs[unassigned_var] for unassigned_var in board.arcs[var] if unassigned_var not in assignment}
    
    for arc, arc_domain in unassigned_arcs.items():
        if val in arc_domain:
            board.domains[arc].pop(val)
            board.pruned[var].append((arc, val))

def getFilledSudokuBoard(assignment, board):
    filled_sudoku_board = []
    
    for var in board.variables:
        filled_sudoku_board.append(str(assignment[var]))

    return ''.join(filled_sudoku_board)

# To check if a sudoku board solved by 
def solved(board):
    
    for var in board.variables:
        if len(board.domains[var]) > 1:
            return False
    
    return True
    
    
   
def main():

    inputConfig = sys.argv[1]

    # inputConfigs = []

    # file = open('sudokus_start.txt', 'r')

    # for x in file:
    #   inputConfigs.append(x) 
    # file.close()


    # for i in inputConfigs:

    #     inputConfig = i

    sudokuBoard = SudokuBoard(inputConfig)

    if AC3(sudokuBoard):

        if solved(sudokuBoard):
            ans = []
            for var in sudokuBoard.variables:
                ans.append(str(sudokuBoard.domains[var][0]))

            answer = ''.join(ans) + ' AC3'

        else:
            assignment = dict()
            assignment = BTS(sudokuBoard) 
            answer = getFilledSudokuBoard(assignment, sudokuBoard) + ' BTS' #might be an issue here


    '''Write output to the file'''

    file = open('output.txt', 'w')
    file.write(answer)
    file.close()

    
if __name__ == '__main__':

    main()
