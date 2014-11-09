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
		entryNumber = 0
		rowToPrint = '|'
		for entry in row:
			if entry == 0: 
	       			rowToPrint += '  '
			else: rowToPrint += str(entry) + ' '
			entryNumber += 1
		       	if entryNumber%3 == 0: rowToPrint += '|'
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
	previous = 0
	for index,unknown in enumerate(unknowns):
		if unknown[0] != previous: print ''
		print unknown[0],unknown[1],whatBox(unknown[0],unknown[1]),options[index]
		previous = unknown[0]
	return

def whatBox(rowNum, colNum):
	# Returns box number based on index of row and column
	boxNumber = 3*math.floor(rowNum/3) + math.floor(colNum/3) 
	return int(boxNumber)

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
			boxNumber = whatBox(rowNumber, colNumber)
			boxSets[boxNumber] = boxSets[boxNumber] | {colEntry}

	return rowSets,colSets,boxSets

def getOptions(rowSets,colSets,boxSets,unknowns):
	# Determines options for unknown cells by set differences

	# Establish comparison set:
	solvedRow = set([1,2,3,4,5,6,7,8,9])

	# Find out what can go in an unknown cell w/ set difference:
	possibleOptions = []
	for entry in unknowns:
		row = entry[0]
		col = entry[1]
		solvedCells = (rowSets[row].union(colSets[col])).union(boxSets[whatBox(row,col)])
		possible = solvedRow.difference(solvedCells)
		possibleOptions.append(possible)
	return possibleOptions

def insertKnown(unsolved,index,known):
	# Insert solved number into cell, does not enter if incorrect
	rows, cols, boxs = getSets(unsolved)
	if (known not in rows[index[0]]) and (known not in cols[index[1]]) and (known not in boxs[whatBox(index[0],index[1])]):
		unsolved[index[0]][index[1]] = known
		return unsolved		
	else:
		print str(known)+" cannot go in row "+str(index[0])+", column "+str(index[1])
		return unsolved

def eliminatePairs(unknowns,options,unsolved):
	# Finds cells in same row, col, or box with matching option pairs and eliminates
	# those entries from the other cells in that row, col, or box.

	# Determine option pairs in puzzle
	pairs = []
	for index, unknown in enumerate(unknowns):
		if len(options[index]) == 2:
			if options.count(options[index])>1:
				pairs.append([unknown[0],unknown[1],options[index]])
	
	# Eliminate option pairs from other cells in row, col, box
	for pairNumber, pair in enumerate(pairs):
		for comPairIndex in range(pairNumber+1, len(pairs)):
			if pair[2] == pairs[comPairIndex][2]:
				# Check if same row:
				if pair[0] == pairs[comPairIndex][0]:
				       # Eliminate numbers from other unknown cells in that row:
					for index, unknown in enumerate(unknowns):
						if (unknown[0] == pair[0]) and (pair[2] != options[index]):
							options[index] = options[index] - pair[2]
				# Check if same column:
				if pair[1] == pairs[comPairIndex][1]:
				       # Eliminate numbers from other unknown cells in that column:
					for index, unknown in enumerate(unknowns):
						if (unknown[1] == pair[1]) and (pair[2] != options[index]):
							options[index] = options[index] - pair[2]
				# Check if same box:
				pairBoxNumber = whatBox(pair[0],pair[1])
				if whatBox(pair[0],pair[1]) == whatBox(pairs[comPairIndex][0],pairs[comPairIndex][1]):
					# Eliminate numbers from other unknown cells in that box:
					for index, unknown in enumerate(unknowns):
						boxNumber = whatBox(unknown[0],unknown[1])
						if pairBoxNumber == boxNumber and (pair[2] != options[index]):
							options[index] = options[index] - pair[2]
	return unknowns, options, unsolved

def checkOnlyOptions(unknowns,options):
	# Checks if there is a cell in a row, column or box that has an unique option 
	# for that whole row, column, box
	rowTests = [set()]*9
	colTests = [set()]*9
	boxTests = [set()]*9
	
	# Algorithm for rows:
	unknownIndex = 0
	possibleUnique = 0
	while unknownIndex < (len(unknowns)-1):
		otherUnknownIndex = 0
		while otherUnknownIndex < (len(unknowns)-1):
			rowNumber = unknowns[unknownIndex][0]
			# Compare with the sets in the same row but not itself
			if rowNumber == unknowns[otherUnknownIndex][0] and unknownIndex != otherUnknownIndex:
				# Find difference:
				diff = options[unknownIndex] - options[otherUnknownIndex]
				# Is there only one option?
				if len(diff) == 1:
					if possibleUnique == 0:
						prospective = diff.pop()
						# Has this number been tested before?
						if prospective not in rowTests[unknowns[unknownIndex][0]]:
							# No! Let's try it.
							possibleUnique = prospective
							# Start from the beginning of the row
							otherUnknownIndex = 0
						else:
							# Not unique - we tested it before.
							possibleUnique = 0
					else:	
						# Might not be a unique value:
						if diff.pop() != possibleUnique:
							# Not unique, remember that this number is not unique:
							rowTests[rowNumber] = rowTests[rowNumber] | set([possibleUnique])
							possibleUnique = 0
						
				else:
					if possibleUnique != 0 and possibleUnique in options[otherUnknownIndex]:
						# Not unique, remember that this number is not unique:
						rowTests[rowNumber] = rowTests[rowNumber] | set([possibleUnique])
						possibleUnique = 0
						# Next row (as long as we're not at the end) !
						if unknownIndex<(len(unknowns)-1):unknownIndex += 1
			otherUnknownIndex += 1
		
		# Did the algorithm find a unique number?
		if not possibleUnique == 0:
			# It did!
			options[unknownIndex] = set([possibleUnique])
			
		unknownIndex += 1
	
	# Repeat algorithm for columns
	while unknownIndex < (len(unknowns)-1):
		otherUnknownIndex = 0
		while otherUnknownIndex < (len(unknowns)-1):
			colNumber = unknowns[unknownIndex][1]
			# Compare with the sets in the same col but not itself
			if colNumber == unknowns[otherUnknownIndex][1] and unknownIndex != otherUnknownIndex:
				# Find difference:
				diff = options[unknownIndex] - options[otherUnknownIndex]
				# Is there only one option?
				if len(diff) == 1:
					if possibleUnique == 0:
						prospective = diff.pop()
						# Has this number been tested before?
						if prospective not in colTests[unknowns[unknownIndex][1]]:
							# No! Let's try it.
							possibleUnique = prospective
							# Start from the beginning of the col
							otherUnknownIndex = 0
						else:
							# Not unique - we tested it before.
							possibleUnique = 0
					else:	
						# Might not be a unique value:
						if diff.pop() != possibleUnique:
							# Not unique, remember that this number is not unique:
							colTests[colNumber] = colTests[colNumber] | set([possibleUnique])
							possibleUnique = 0
						
				else:
					if possibleUnique != 0 and possibleUnique in options[otherUnknownIndex]:
						# Not unique, remember that this number is not unique:
						colTests[colNumber] = colTests[colNumber] | set([possibleUnique])
						possibleUnique = 0
						# Next col (as long as we're not at the end) !
						if unknownIndex<(len(unknowns)-1):unknownIndex += 1
			otherUnknownIndex += 1
		# Did the algorithm find a unique number?
		if not possibleUnique == 0:
			# It did!
			options[unknownIndex] = set([possibleUnique])
			
		unknownIndex += 1

	
	# Repeat algorithm for boxes
	while unknownIndex < (len(unknowns)-1):
		boxNumber = whatBox(unknowns[unknownIndex][0],unknowns[unknownIndex][1])
		while otherUnknownIndex < (len(unknowns)-1):
			otherBoxNumber = whatBox(unknowns[otherUnknownIndex][0],unknowns[otherUnknownIndex][1])
			# Compare with the sets in the same box but not itself
			if boxNumber == unknowns[otherUnknownIndex][1] and unknownIndex != otherUnknownIndex:
				# Find difference:
				diff = options[unknownIndex] - options[otherUnknownIndex]
				# Is there only one option?
				if len(diff) == 1:
					if possibleUnique == 0:
						prospective = diff.pop()
						# Has this number been tested before?
						if prospective not in boxTests[unknowns[unknownIndex][1]]:
							# No! Let's try it.
							possibleUnique = prospective
							# Start from the beginning of the box
							otherUnknownIndex = 0
						else:
							# Not unique - we tested it before.
							possibleUnique = 0
					else:	
						# Might not be a unique value:
						if diff.pop() != possibleUnique:
							# Not unique, remember that this number is not unique:
							boxTests[boxNumber] = boxTests[boxNumber] | set([possibleUnique])
							possibleUnique = 0
						
				else:
					if possibleUnique != 0 and possibleUnique in options[otherUnknownIndex]:
						# Not unique, remember that this number is not unique:
						boxTests[boxNumber] = boxTests[boxNumber] | set([possibleUnique])
						possibleUnique = 0
						# Next box (as long as we're not at the end) !
						if unknownIndex<(len(unknowns)-1):unknownIndex += 1
			otherUnknownIndex += 1
		# Did the algorithm find a unique number?
		if not possibleUnique == 0:
			# It did!
			options[unknownIndex] = set([possibleUnique])
			
		unknownIndex += 1

	return unknowns,options

def inputOptions(unknowns,options,unsolved):
	# Determines cells with only one option for cell, escapes after not reducing unknown cells
	# whether its solved or not
	trialNumber = 0
	numUnknowns = len(unknowns)
	solved = False
	while len(unknowns) != 0:
		# Replace eliminated numbers
		for index, entry in enumerate(unknowns):
			if len(options[index]) == 1:
				unsolved = insertKnown(unsolved,[entry[0],entry[1]],options[index].pop())
		# Locate unknowns 
		unknowns = findZeros(unsolved)

		# Break routine after non-reduction of cell options - Change strategy!	
		if numUnknowns == len(unknowns):
			return unsolved, unknowns, options, solved
		else:
			if len(unknowns) != 0:
				if trialNumber == 1:
					print 'After '+str(trialNumber)+' pass, the puzzle is:'
				else:
					print 'After '+str(trialNumber)+' passes, the puzzle is:'
				printPuzzle(unsolved)
		numUnknowns = len(unknowns)
		trialNumber += 1
		
		# Get sets of options for each row, col, box
		rows, cols, boxs = getSets(unsolved)
	
		# Get cell options
		options = getOptions(rows, cols, boxs, unknowns)
		
		# Eliminate pairs
		unknowns, options, unsolved = eliminatePairs(unknowns,options,unsolved)
		
		# Check for only options
		unknowns, options = checkOnlyOptions(unknowns,options)
		
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
		print listToCSV(unSolved,os.path.splitext(filename)[0]+'_solved.csv')
	else:
		print 'I have failed you.\n'
		printPuzzle(unSolved)
		printCellOptions(unKnowns, cellOptions)
			
		
	
	

