import math

# -------------------------------------------------------------
# --------------------- DATA FUNCTIONS ------------------------
# -------------------------------------------------------------

SOLVEDSET = set(range(1,10))
ROWS,COLS,BOXS = 0,1,2
whatRowColOrBox = [lambda cell: whatRow(cell),\
		   lambda cell: whatCol(cell),\
		   lambda cell: whatBox(cell)]


def whatRow(unknown):
	# Returns row number
	return unknown[0]

def whatCol(unknown):
	# Returns col number
	return unknown[1]

def whatBox(unknown):
	# Returns box number based on index of row and column
	boxNumber = 3*math.floor(whatRow(unknown)/3) + math.floor(whatCol(unknown)/3) 
	return int(boxNumber)


def sameGroup(unknown1,unknown2):
	results = []
	for test in whatRowColOrBox:
		results.append(test(unknown1) == test(unknown2))
	return results
		

def findZeros(inputList):
	# Returns list of (row index, col index) of 0's in a nested list
	zeros = []
	for rowNumber,rowEntry in enumerate(inputList):
		for colNumber, colEntry in enumerate(rowEntry):
			# Locate zeros:
			if colEntry == 0:
				zeros.append([rowNumber, colNumber])
	return zeros

def getSets(inputList):
	# Form sets of numbers entered into the rows, colums, and boxes:
	# (possible expand to be able to adjust dimensions?)
	rowSets = [] 
	colSets = [set()]*9
	boxSets = [set()]*9
	for rowNumber,rowEntry in enumerate(inputList):
		# Assemble row set first:
		rowSets.append(set(rowEntry))
		for colNumber, colEntry in enumerate(rowEntry):
			# Enter column set next:	
			colSets[colNumber] = colSets[colNumber] | {colEntry}
			# Lastly determine box set:
			boxNumber = whatBox([rowNumber, colNumber])
			boxSets[boxNumber] = boxSets[boxNumber] | {colEntry}
	sets = [rowSets,colSets,boxSets]
	return sets

def getOptions(sets,unknowns):
	# Determines options for unknown cells by set differences
	possibleOptions = []
	for cell in unknowns:
		solvedCells = sets[ROWS][whatRow(cell)].union(sets[COLS][whatCol(cell)].union(sets[BOXS][whatBox(cell)]))
		possible = SOLVEDSET.difference(solvedCells)
		possibleOptions.append(possible)
	return possibleOptions

def insertKnown(unsolved,index,known):
	# Insert solved number into cell, does not enter if incorrect
	sets = getSets(unsolved)
	if (	known not in sets[ROWS][whatRow(index)] and 
		known not in sets[COLS][whatCol(index)] and 
		known not in sets[BOXS][whatBox(index)]):
		# Insert the number!
		unsolved[whatRow(index)][whatCol(index)] = known
		return False,unsolved		
	else:
		print str(known)+" cannot go in row "+str(whatRow(index))+", column "+str(whatCol(index))
		print "\nI MADE A MISTAKE.\n"
		return True,unsolved


