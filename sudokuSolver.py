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

# ----------------- Input/output functions ----------------

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

# ----------------- Data functions -------------------
# Establish comparison set:
solvedSet = set(range(1,10))

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
		possible = solvedSet.difference(solvedCells)
		possibleOptions.append(possible)
	return possibleOptions

def insertKnown(unsolved,index,known):
	# Insert solved number into cell, does not enter if incorrect
	rows, cols, boxs = getSets(unsolved)
	if (known not in rows[whatRow(index)]) and (known not in cols[whatCol(index)]) and (known not in boxs[whatBox(index)]):
		unsolved[whatRow(index)][whatCol(index)] = known
		return unsolved		
	else:
		print str(known)+" cannot go in row "+str(whatRow(index))+", column "+str(whatCol(index))
		return unsolved


# ---------- Strategies used ------------------

def eliminatePairs(unknowns,options,unsolved):
	# Finds cells in same row, col, or box with matching option pairs and eliminates
	# those entries from the other cells in that row, col, or box.

	# Determine option pairs in puzzle
	pairs = []
	for index, unknown in enumerate(unknowns):
		if len(options[index]) == 2:
			if options.count(options[index])>1:
				pairs.append([whatRow(unknown),whatCol(unknown),options[index]])

	# Need to find hidden pairs!!!! 
	# Example:
	# 	R C B Options
	# 	-------------
	# 	0 3 1 set([1, 4, 9])
	# 	0 4 1 set([1, 4, 9])
	# 	2 5 1 set([1, 9])
	# Output: [0,3,set([1,4])], [0,3,set([1,4])]
	
	# Eliminate the options found in pairs from other cells in row, col, box
	for pairNumber, pair in enumerate(pairs):
		for comPairIndex in range(pairNumber+1, len(pairs)):
			# If the pairs match:
			if pair[2] == pairs[comPairIndex][2]:
				# Check if they are the same row/col/box:
				for test in whatRowColOrBox:
					# If they are in the same row/col/box:
					if test(pair) == test(pairs[comPairIndex]):
						# Eliminate those options from the options 
						# in the other cells in that row/col/box:
						for index, unknown in enumerate(unknowns):
							# If the pairs are in the same row/col/box 
							# and its not the same cell
							if (test(unknown) == test(pair)) and (pair[2] != options[index]):
								options[index] = options[index] - pair[2]
	return unknowns, options, unsolved

def checkOnlyOptions(unknowns,options,rows,cols,boxs):
	# Checks if there is a cell in a row, column or box that has an unique option 
	# for that whole row, column, box
	
	groups = [rows,cols,boxs]	
	# Algorithm for rows:
	groupNumber = 0	
	instance = [0,0]
	for group, groupTest in groups:
		while (groupNumber < len(group)):
			# Check options in the row
			row = list(solvedSet - groups[groupNumber])
			optionNumber = 0
			while (optionNumber < len(group)):	
				occurs = 0
				cellNumber = 0
				while ((cellNumber < len(unknowns)) and (occurs < 2)):
					if whatRowColOrBox[groupTest](unknowns[cellNumber]) == groupNumber:
						if group[optionNumber] in options[cellNumber]:		
							instance = [cellNumber, group[optionNumber]]
							occurs += 1
					cellNumber += 1
				if occurs == 1: # It's a unique option, store it in the option matrix
					options[instance[0]] = set([instance[1]])
				optionNumber += 1
			groupNumber += 1	
#
#
#	while (rowNumber < len(rows)):
#		# Check options in the row
#		row = list(solvedSet - rows[rowNumber])
#		optionNumber = 0
#		while (optionNumber < len(row)):	
#			occurs = 0
#			cellNumber = 0
#			while ((cellNumber < len(unknowns)) and (occurs < 2)):
#				if whatRow(unknowns[cellNumber]) == rowNumber:
#					if row[optionNumber] in options[cellNumber]:		
#						instance = [cellNumber, row[optionNumber]]
#						occurs += 1
#				cellNumber += 1
#			if occurs == 1: # It's a unique option, store it in the option matrix
#				options[instance[0]] = set([instance[1]])
#			optionNumber += 1
#		rowNumber += 1	
#	
#	# Algorithm for cols:
#	colNumber = 0	
#	instance = [0,0]
#	while (colNumber < len(cols)):
#		# Check options in the col
#		col = list(solvedSet - cols[colNumber])
#		optionNumber = 0
#		while (optionNumber < len(col)):	
#			occurs = 0
#			cellNumber = 0
#			while ((cellNumber < len(unknowns)) and (occurs < 2)):
#				if whatCol(unknowns[cellNumber]) == colNumber:
#					if col[optionNumber] in options[cellNumber]:		
#						instance = [cellNumber, col[optionNumber]]
#						occurs += 1
#				cellNumber += 1
#			if occurs == 1: # It's a unique option, store it in the option matrix
#				options[instance[0]] = set([instance[1]])
#			optionNumber += 1
#		colNumber += 1	
#
#	# Algorithm for boxs:
#	boxNumber = 0	
#	instance = [0,0]
#	while (boxNumber < len(boxs)):
#		# Check options in the box
#		box = list(solvedSet - boxs[boxNumber])
#		optionNumber = 0
#		while (optionNumber < len(box)):	
#			occurs = 0
#			cellNumber = 0
#			while ((cellNumber < len(unknowns)) and (occurs < 2)):
#				if whatBox(unknowns[cellNumber]) == boxNumber:
#					if box[optionNumber] in options[cellNumber]:		
#						instance = [cellNumber, box[optionNumber]]
#						occurs += 1
#				cellNumber += 1
#			if occurs == 1: # It's a unique option, store it in the option matrix
#				options[instance[0]] = set([instance[1]])
#			optionNumber += 1
#		boxNumber += 1
		
	return unknowns,options

# ---------------- Main implementation of strategies -------------------
def inputOptions(unknowns,options,unsolved):
	# Determines cells with only one option for cell by applying strategies and
	# escapes after not reducing unknown cells whether its solved or not
	unsuccessfulPasses = 0
	trialNumber = 0
	numUnknowns = len(unknowns)
	solved = False
	while (numUnknowns != 0) and (unsuccessfulPasses < 4):
		# Locate unknowns 
		unknowns = findZeros(unsolved)

		# Get sets of options for each row, col, box
		rows, cols, boxs = getSets(unsolved)
	
		# Get cell options
		options = getOptions(rows, cols, boxs, unknowns)
		
		# Eliminate pairs
		unknowns, options, unsolved = eliminatePairs(unknowns,options,unsolved)
		
		# Check for only options
		unknowns, options = checkOnlyOptions(unknowns,options,rows,cols,boxs)
		
		# Insert the option if there's only one!
		squaresFilled = 0
		for cellNumber, cell in enumerate(unknowns):
			if len(options[cellNumber]) == 1:
				squaresFilled += 1
				unsolved = insertKnown(unsolved,[cell[0],cell[1]],options[cellNumber].pop())
		
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
		
	if numUnknowns != 0:
		printCellOptions(unknowns,options)
	else:
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
	
			
		
	
	

