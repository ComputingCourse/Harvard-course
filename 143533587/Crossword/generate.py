import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            for word in self.domains[var].copy():
                if len(word) != var.length:
                    self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False
        for word in self.domains[x].copy():
            consistent = False
            for each in self.domains[y]:
                i,j = self.crossword.overlaps[x, y]
                if word[i] == each[j]:
                    consistent = True
            if consistent == False:
                self.domains[x].remove(word)
                revision = True
        return revision


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []
            for word in self.domains:
                for neighbors in self.crossword.neighbors(word):
                    arcs.append((word,neighbors))
        while arcs:
            node = arcs[0]
            x,y = node
            arcs.remove(node)
            if self.revise(x,y):
                for neighbors in self.crossword.neighbors(x):
                    arcs.append((x,neighbors))
                    arcs.append((neighbors,x))
                if not self.domains[x]:
                    return False

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) != len(self.crossword.variables):
            return False
        used =[]
        for each in assignment:#
            if not assignment[each] or assignment[each] in used:
                return False
            else:
                used.append(assignment[each])
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used = []
        for variable in assignment:
            if  not assignment[variable] or assignment in used:
                return False
            if variable.length != len(assignment[variable]):
                return False
            for each in self.crossword.neighbors(variable):
                i,j = self.crossword.overlaps[variable,each]
                try:
                    if assignment[variable][i] != assignment[each][j]:
                        return False
                except KeyError:
                    pass
                except:
                    return False

            used.append(assignment[variable])
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        possibilities = {}
        possibilities2 = {}
        for variable in self.domains[var]:
            num = 0
            for every in self.crossword.neighbors(var):
                if not every in assignment:
                    for each in self.domains[every]:
                        i,j = self.crossword.overlaps[var,every]
                        if variable[i] != each[j]:
                            num +=1
            possibilities[variable] = num
            possibilities2[num] = variable
        sorted_ =sorted(possibilities2)
        sorted2 = []
        for each in sorted_:
            for every in possibilities:
                if possibilities[every] == each:
                    sorted2.append(every)

        return sorted2



    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_var = {}
        unassigned_domain = {}
        for var in self.crossword.variables:
            if var not in assignment:
                unassigned_var[var] = len(self.domains[var])
                unassigned_domain[len(self.domains[var])] = var
        sorted_ =sorted(unassigned_domain)#sort by domain length
        sorted2 = []
        for each in sorted_:
            variables = []
            for every in unassigned_var:
                if unassigned_var[every] == each:
                    variables.append(every)
            if len(variables) == 1:
                sorted2.append(variables[0])
            else:
                neigh = {}
                for every in variables:
                    neigh[len(self.crossword.neighbors(every))] = every
                sorted3 = sorted(neigh)
                sorted2.append(neigh[sorted3[0]])

        return sorted2[0]




    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        domain_values = self.order_domain_values(var, assignment)#idk
        for each in domain_values:
            new_assignment = assignment.copy()
            new_assignment[var] = each
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result:#not none
                    return result
        return None




def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
