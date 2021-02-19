import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        num_cells = len(self.cells)
        if self.count == num_cells:
            return self.cells

        else:
            return None


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells

        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # The function should mark the cell as one of the moves made in the game.
        self.moves_made.add(cell)

        # The function should mark the cell as a safe cell, updating any sentences that contain the cell as well.
        self.mark_safe(cell)

        for sentence in self.knowledge.copy():
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

        # The function should add a new sentence to the AI’s knowledge base, based on the value of cell and count, to
        # indicate that count of the cell’s neighbors are mines. Be sure to only include cells whose state is still undetermined in the sentence.
        nearby_cells = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                new_cell = (i, j)

                if new_cell == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    if new_cell not in self.moves_made:
                        nearby_cells.add(new_cell)

        if len(nearby_cells) != 0:
            new_sentence = Sentence(nearby_cells, count)
            if new_sentence not in self.knowledge:
                self.knowledge.append(new_sentence)

        # If, based on any of the sentences in self.knowledge, new cells can be marked as safe or as mines, then the function should do so.
        for sentence in self.knowledge.copy():
            mines = sentence.known_mines()
            if mines != None:
                for mine in mines.copy():
                    self.mark_mine(mine)

            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

            else:
                safes = sentence.known_safes()
                if safes != None:
                    for safe in safes.copy():
                        self.mark_safe(safe)

        # Remove any empty sentences
        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

        # If, based on any of the sentences in self.knowledge, new sentences can be inferred (using the subset method
        # described in the Background), then those sentences should be added to the knowledge base as well.
        knowledge_copy = copy.deepcopy(self.knowledge)
        for i in range(len(knowledge_copy) - 1):
            for j in range(i + 1, len(knowledge_copy)):
                sentence1 = knowledge_copy[i]
                sentence2 = knowledge_copy[j]

                # In case duplicate is made somehow by removing cells
                if sentence1 == sentence2:
                    self.knowledge.remove(sentence1)

                elif sentence1.cells.issubset(sentence2.cells):
                    new_cells = sentence2.cells.difference(sentence1.cells)
                    new_count = sentence2.count - sentence1.count
                    new_sentence = Sentence(new_cells, new_count)
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)

                elif sentence2.cells.issubset(sentence1.cells):
                    new_cells = sentence1.cells.difference(sentence2.cells)
                    new_count = sentence1.count - sentence2.count
                    new_sentence = Sentence(new_cells, new_count)
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)

        # Remove any empty sentences
        for sentence in self.knowledge.copy():
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        if len(self.safes) == 0:
            return None

        else:
            for move in self.safes:
                if move not in self.moves_made:
                    return move


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        if len(self.moves_made) == self.height * self.width:
            return None

        if len(self.moves_made) + len(self.mines) == self.height * self.width:
            return None

        while True:
            i = random.randint(0, self.height - 1)
            j = random.randint(0, self.width - 1)
            move = (i,j)
            if move not in self.moves_made and move not in self.mines:
                return move