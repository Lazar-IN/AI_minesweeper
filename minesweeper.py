import itertools
import random

#implementacija igre MINOLOVAC
class Minesweeper():
    def __init__(self, height=8, width=8, mines=8):
        #inicijalizacija sirine,visine i br mina
        self.height = height
        self.width = width
        self.mines = set()
        #inicijalizacija prazne table
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)
        #nasumicno dodavanje mina
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True
        self.mines_found = set()
        
    #stmpana reprezentacija
    def print(self):
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")
        
    #da li je polje mina
    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        count = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1
        return count
    
    #pobeda ako su sve mine pronadjene(flegovane)
    def won(self):
        return self.mines_found == self.mines

#broj mina i njihove pozocije na tabli
#pomocna f-ja za AI
class Sentence():
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    #vraca skup poznatih mina
    def known_mines(self):
        if len(self.cells) == self.count:
            return self.cells
        return None

    #vraca skup poznatih sigurnih polja
    def known_safes(self):
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        newCells = set()
        for item in self.cells:
            if item != cell:
                newCells.add(item)
            else:
                self.count -= 1
        self.cells = newCells

    def mark_safe(self, cell):
        newCells = set()
        for item in self.cells:
            if item != cell:
                newCells.add(item)
        self.cells = newCells
        

#implementacija AI
class MinesweeperAI():
    def __init__(self, height=8, width=8):

        #inicijalizacija visine i sirine table
        self.height = height
        self.width = width

        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        #lista polja sa poznatom okolinom(skup)
        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    #dodavanje polja sa poznatom okolinom u listu(skup)
    def add_knowledge(self, cell, count):
        
        self.mark_safe(cell)
        self.moves_made.add(cell)

        neighbors, count = self.get_cell_neighbors(cell, count)
        sentence = Sentence(neighbors, count)
        self.knowledge.append(sentence)

        new_inferences = []
        for s in self.knowledge:
            if s == sentence:
                continue
            elif s.cells.issuperset(sentence.cells):
                setDiff = s.cells-sentence.cells
                #sigurna polja
                if s.count == sentence.count:
                    for safeFound in setDiff:
                        self.mark_safe(safeFound)
                #mine
                elif len(setDiff) == s.count - sentence.count:
                    for mineFound in setDiff:
                        self.mark_mine(mineFound)
                else:
                    new_inferences.append(
                        Sentence(setDiff, s.count - sentence.count)
                    )
            elif sentence.cells.issuperset(s.cells):
                setDiff = sentence.cells-s.cells
                #poznata sigurna polja
                if s.count == sentence.count:
                    for safeFound in setDiff:
                        self.mark_safe(safeFound)
                #poznata polja mine
                elif len(setDiff) == sentence.count - s.count:
                    for mineFound in setDiff:
                        self.mark_mine(mineFound)
                #poznati zakljucak(znanje)
                else:
                    new_inferences.append(
                        Sentence(setDiff, sentence.count - s.count)
                    )
        self.knowledge.extend(new_inferences)
        self.remove_dups()
        self.remove_sures()

    def make_safe_move(self):
        safeCells = self.safes - self.moves_made
        if not safeCells:
            return None
        #print(f"Pool: {safeCells}")
        move = safeCells.pop()
        return move
    #za pocetak igre
    def make_random_move(self):
        all_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                if (i,j) not in self.mines and (i,j) not in self.moves_made:
                    all_moves.add((i,j))
        if len(all_moves) == 0:
            return None
        move = random.choice(tuple(all_moves))
        return move
               
    def get_cell_neighbors(self, cell, count):
        i, j = cell
        neighbors = []
        for row in range(i-1, i+2):
            for col in range(j-1, j+2):
                if (row >= 0 and row < self.height) \
                and (col >= 0 and col < self.width) \
                and (row, col) != cell \
                and (row, col) not in self.safes \
                and (row, col) not in self.mines:
                    neighbors.append((row, col))
                if (row, col) in self.mines:
                    count -= 1
        return neighbors, count

    def remove_dups(self):
        unique_knowledge = []
        for s in self.knowledge:
            if s not in unique_knowledge:
                unique_knowledge.append(s)
        self.knowledge = unique_knowledge

    def remove_sures(self):
        final_knowledge = []
        for s in self.knowledge:
            final_knowledge.append(s)
            if s.known_mines():
                for mineFound in s.known_mines():
                    self.mark_mine(mineFound)
                final_knowledge.pop(-1)
            elif s.known_safes():
                for safeFound in s.known_safes():
                    self.mark_safe(safeFound)
                final_knowledge.pop(-1)
        self.knowledge = final_knowledge
