#!/usr/bin/env python

import os, sys, string, math
from operator import itemgetter
from optparse import OptionParser
from csv import reader as csvReader
from csv import writer as csvWriter

def main():
	usage = "usage: %prog -f file"
	parser = OptionParser(usage)
	parser.add_option("-f","--file", dest="file", 
			help="sudoku puzzle csv file")
	(options, args) = parser.parse_args()

	# Ensure file given
	if (options.file is None):
		parser.error("No file given!")
	# Check if csv
	if not (options.file.endswith('.csv')):	
		parser.error("Must be csv file!")
	# Ensure file exists
	if (os.path.exists(os.getcwd()+options.file)):
		parser.error("File not found in current directory!")	
	
	print '\nI will solve the sudoku in file '+options.file+' asap!\n'
	
	sudokuPuzzle = csvToList(options.file)
	
	# Ensure its a standard puzzle
	if not (len(sudokuPuzzle)==9):
		parser.error("Its not a standard 9x9 puzzle!")
	
	return options.file, sudokuPuzzle

# -------------------------------------------------------------
# ------------------- INPUT/OUTPUT FUNCTIONS ------------------
# -------------------------------------------------------------

def csvToList(csvFile):
	# Converts csv file of integers to nested list of integers
	integerList = []
	with open(csvFile,'rb') as openFile:
		reader = csvReader(openFile)
		for line in reader:
			integerList.append([int (i) for i in line])
	return integerList

def listToCSV(integerList,filename):
	# Converts nested list of integers to csv file of integers
	with open(filename,'wb') as csvfile:
		writer = csvWriter(csvfile,delimiter=',')
		for row in integerList:
			writer.writerow(row)
	return filename

def printPuzzle(puzzle):
	# Prints puzzle in readable format
	rowNumber = 0
	for row in puzzle:
		cellNumber = 0
		rowToPrint = '|'
		for cell in row:
			if cell == 0: 
	       			rowToPrint += '  '
			else: rowToPrint += str(cell) + ' '
			cellNumber += 1
		       	if cellNumber%3 == 0: rowToPrint += '|'
		if rowNumber%3 == 0:
       			print '-'*21
		rowNumber += 1
		print rowToPrint
	print '-'*21+'\n'

	# Check number of zeros (unknowns)
	emptySquares = sum(row.count(0) for row in puzzle)
	if not emptySquares == 0:
		if emptySquares == 1:
			print 'There is '+str(emptySquares)+' empty square!\n'
		else:
			print 'There are '+str(emptySquares)+' empty squares!\n'
	return

def printCellOptions(unknowns,options):
	# Prints unknown cell options
	unknowns.sort(key=lambda x: x[0])

	previous = 0
	print 'R C B Options\n-------------'
	for index,unknown in enumerate(unknowns):
		unknowns[index].append(options[index])
		if whatRow(unknown) != previous: print ''
		print whatRow(unknown),whatCol(unknown),whatBox(unknown),unknown[2]
		previous = unknown[0]
	
	previous = 0
	print '\nR C B Options\n-------------'
	unknowns.sort(key=lambda x: x[1])	
	for unknown in unknowns:
		if whatCol(unknown) != previous: print ''
		print whatRow(unknown),whatCol(unknown),whatBox(unknown),unknown[2]
		previous = unknown[1]

	previous = 0
	print '\nR C B Options\n-------------'
	unknowns.sort(key=lambda x: whatBox(x))
	for unknown in unknowns:
		if whatBox(unknown) != previous: print ''
		print whatRow(unknown),whatCol(unknown),whatBox(unknown),unknown[2]
		previous = whatBox(unknown)
		
	unknowns.sort(key=lambda x: x[0])
	return True

def printPuzzleAndOptions(puzzle,unknowns,options):
	unknowns.sort(key=lambda x: x[0])
	columns = [0]*9
	for index,option in enumerate(options):
		if len(option) > columns[unknowns[index][1]]:
			columns[unknowns[index][1]] = len(option)
	rowNumber = 0
	unknown = 0
	for row in puzzle:
		colNumber = 0
		rowToPrint = '|'
		for cell in row:
			if cell == 0: 
				spacing = ' '*((3*(columns[colNumber]))-(3*len(options[unknown]))+1)
	       			rowToPrint += str(list(options[unknown]))+spacing
				unknown += 1
			else: 
				spacing = (3*columns[colNumber])
				rowToPrint += ' '*int((math.floor(spacing/2)))+str(cell)+' '*int(spacing-(math.floor(spacing/2)))
			colNumber += 1
		       	if colNumber%3 == 0: 
				rowToPrint += '|'
		if rowNumber%3 == 0:
       			print '-'*(13+sum(columns)*3)
		rowNumber += 1
		print rowToPrint
       	print '-'*(13+sum(columns)*3)+'\n'

# -------------------------------------------------------------
# --------------------- DATA FUNCTIONS ------------------------
# -------------------------------------------------------------

# Establish comparison set:
SOLVEDSET = set(range(1,10))

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

# Function dictionary to simplify checking rows, cols, and boxs
whatRowColOrBox = [lambda x: whatRow(x),lambda x: whatCol(x), lambda x: whatBox(x)]

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

	return rowSets,colSets,boxSets

def getOptions(rowSets,colSets,boxSets,unknowns):
	# Determines options for unknown cells by set differences

	# Find out what can go in an unknown cell w/ set difference:
	possibleOptions = []
	for cell in unknowns:
		solvedCells = (rowSets[whatRow(cell)].union(colSets[whatCol(cell)])).union(boxSets[whatBox(cell)])
				# Check if same row:
		possible = SOLVEDSET.difference(solvedCells)
		possibleOptions.append(possible)
	return possibleOptions

def insertKnown(unsolved,index,known):
	# Insert solved number into cell, does not enter if incorrect
	rows, cols, boxs = getSets(unsolved)
	if (	known not in rows[whatRow(index)] and 
		known not in cols[whatCol(index)] and 
		known not in boxs[whatBox(index)]):
		# Insert the number!
		unsolved[whatRow(index)][whatCol(index)] = known
		return False,unsolved		
	else:
		print str(known)+" cannot go in row "+str(whatRow(index))+", column "+str(whatCol(index))
		print "\nI MADE A MISTAKE.\n"
		return True,unsolved

# -------------------------------------------------------------
# -------------------- STRATEGY FUNCTIONS ---------------------
# -------------------------------------------------------------
def findSiblings(unknowns,options,number):
	# Determine cells with identical options in same row/col/box in puzzle
	# (Referred to as siblings)
	siblings = []
	for index, unknown in enumerate(unknowns):
		if len(options[index]) == number:
			if options.count(options[index])>1:
				siblings.append([whatRow(unknown),whatCol(unknown),options[index]])
	return siblings

newArray = object()

def checkSiblings(sibling,siblings,functionCall = 0,allSiblings = newArray,familyGroups = newArray):
	# Recursive function to find siblings sharing groups
	functionCall +=1
	index = siblings.index(sibling)+1
	while index < (len(siblings)):
		if sibling[2] == siblings[index][2]:
			sharedGroups = sameGroup(sibling,siblings[index])
			if familyGroups is newArray:
				familyGroups = sameGroup(sibling,siblings[index])
			if any([familyGroups[i] and sharedGroups[i] for i in range(0,3)]):
				familyGroups = [familyGroups[i] and sharedGroups[i] for i in range(0,3)]
				if allSiblings is newArray:
					allSiblings = [sibling,siblings[index]]
				else:
					if siblings[index] not in allSiblings:
						allSiblings.append(siblings[index])
				if functionCall < (len(sibling[2])-1):
					allSiblings = checkSiblings(siblings[index],siblings,
									functionCall,allSiblings,familyGroups)
			else:
				familyGroups = newArray
		index += 1
	if allSiblings is newArray: allSiblings = []
	else: 
		if len(allSiblings) != len(sibling[2]): allSiblings = []
	return allSiblings

def eliminateSiblings(unknowns,options,unsolved):
	# Finds cells in same row, col, or box with matching option twins and eliminates
	# those entries from the other cells in that row, col, or box.
	families = []
	for numOfSiblings in range(1,4):
		siblingGroups = findSiblings(unknowns,options,numOfSiblings)
		for siblings in siblingGroups:
			family = checkSiblings(siblings,siblingGroups)
			if type(family) == list and len(family)== numOfSiblings:
				for test in whatRowColOrBox:
					allTested = [test(sibling) for sibling in family]
					if allTested[1:] == allTested[:-1]:
						for index,unknown in enumerate(unknowns):
							if (test(unknown) == test(family[0]) and family[0][2] != options[index]):
									options[index] = options[index] - family[0][2]
	return unknowns, options, unsolved

def checkOnlyOptions(unknowns,options,rows,cols,boxs):
	# Checks if there is a cell in a row, col or box that has an unique option 
	# for that whole row, col, box
	allGroups = [rows,cols,boxs]
	for groupTest, groups in enumerate(allGroups):
		groupNumber = 0	
		instance = [0,0]
		while (groupNumber < len(groups)):
			# Find the possible options for each group:
			group = list(SOLVEDSET - groups[groupNumber])
			optionNumber = 0
			# Go through each option to see if its found in only one cell
			while (optionNumber < len(group)):	
				occurs = 0
				cellNumber = 0
				# Check how many times it occurs in each cell of the group, 
				# but stop checking if it happens more than once
				while ((cellNumber < len(unknowns)) and (occurs < 2)):
					# If the cell is in the group:
					if whatRowColOrBox[groupTest](unknowns[cellNumber]) == groupNumber:
						# If the option is in the cell:
						if group[optionNumber] in options[cellNumber]:		
							# Then it occurred and remember it!
							instance = [cellNumber, group[optionNumber]]
							occurs += 1
					cellNumber += 1
				if occurs == 1: # It's a unique option, store it in the option matrix
					options[instance[0]] = set([instance[1]])
				optionNumber += 1
			groupNumber += 1	
	return unknowns,options

# ---------------- Main implementation of strategies -------------------
def inputOptions(unknowns,options,unsolved):
	# Determines cells with only one option for cell by applying strategies and
	# escapes after not reducing unknown cells whether its solved or not
	unsuccessfulPasses = 0
	trialNumber = 0
	numUnknowns = len(unknowns)
	solved = False
	while (numUnknowns != 0) and (unsuccessfulPasses < 2):
		# Locate unknowns 
		unknowns = findZeros(unsolved)

		# Get sets of options for each row, col, box
		rows, cols, boxs = getSets(unsolved)
	
		# Get cell options
		options = getOptions(rows, cols, boxs, unknowns)
		
		# Eliminate pairs
		unknowns, options, unsolved = eliminateSiblings(unknowns,options,unsolved)
		
		# Check for only options
		unknowns, options = checkOnlyOptions(unknowns,options,rows,cols,boxs)
		
		# Insert the option if there's only one!
		squaresFilled = 0
		for cellNumber, cell in enumerate(unknowns):
			if len(options[cellNumber]) == 1:
				squaresFilled += 1
				mistake, unsolved = insertKnown(unsolved,[cell[0],cell[1]],options[cellNumber].pop())
		
		# Break routine after two non-reductions of cell options
		if numUnknowns == len(unknowns):
			unsuccessfulPasses +=1 
			print 'Unsuccessful Pass! (Number '+str(unsuccessfulPasses)+')\n'
		else:
			unsuccessfulPasses = 0
	
		if len(options) != squaresFilled and len(unknowns) != 0:
			if trialNumber == 1:
				print 'After '+str(trialNumber)+' pass, the puzzle is:'
			else:
				print 'After '+str(trialNumber)+' passes, the puzzle is:'
			printPuzzle(unsolved)
	
		numUnknowns = len(unknowns)
		trialNumber += 1
		
	if numUnknowns == 0:
		solved = True

	return unsolved, unknowns, options, solved
	
	
if __name__ == "__main__":
	filename, unSolved  = main()
	printPuzzle(unSolved)
	
	# Locate unknowns 
	unKnowns = findZeros(unSolved)
	
	# Get sets of options for each row, col, box
	optionRows, optionCols, optionBoxs = getSets(unSolved)
	
	# Get cell options
	cellOptions = getOptions(optionRows, optionCols, optionBoxs, unKnowns)
	
	# Check for unknown cells
	unSolved, unKnowns, cellOptions, solved  = inputOptions(unKnowns,cellOptions,unSolved)

	if solved:	
		printPuzzle(unSolved)
		print 'The puzzle is solved!\n'
		print listToCSV(unSolved,os.path.splitext(filename)[0]+'_solved.csv\n')
	else:
		print '\nI have failed you.\n'
		printPuzzle(unSolved)
		printPuzzleAndOptions(unSolved,unKnowns,cellOptions)
