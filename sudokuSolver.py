#!/usr/bin/env python

import os, sys, string
from operator import itemgetter
from optparse import OptionParser
import io,data,strategy

PUZZLESIZE = 9

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
	
	sudokuPuzzle = io.csvToList(options.file)
	
	# Ensure its a standard puzzle
	if not (len(sudokuPuzzle)==PUZZLESIZE):
		parser.error("Its not a standard "+PUZZLESIZE+"x"+PUZZLESIZE+" puzzle!")
	
	return options.file, sudokuPuzzle
	
if __name__ == "__main__":
	filename, unSolved  = main()
	io.printPuzzle(unSolved)
	
	# Locate unknowns 
	unKnowns = data.findZeros(unSolved)
	
	# Get sets of options for each row, col, box
	optionSets = data.getSets(unSolved)
	
	# Get cell options
	cellOptions = data.getOptions(optionSets, unKnowns)
	
	# Solve the puzzle
	unSolved, unKnowns, cellOptions  = strategy.implement(unKnowns,cellOptions,unSolved)

	if not unKnowns:	
		io.printPuzzle(unSolved)
		print 'The puzzle is solved!\n'
		print io.listToCSV(unSolved,os.path.splitext(filename)[0]+'_solved.csv\n')
	else:
		print '\nI have failed you.\n'
		io.printPuzzle(unSolved)
		io.printPuzzleAndOptions(unSolved,unKnowns,cellOptions)
