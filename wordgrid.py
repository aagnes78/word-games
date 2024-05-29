#!/usr/bin/env python3
# -*-coding: utf-8 -*-
"""
Suggesting words to find in a letter of grid.

You can build your own grid via the command line,
by specifying the size of the grid (the number of rows and columns),
and giving the letters (line by line).

Similar to e.g. squaredle, huntedle. 

Hence the default size of grid is 4 by 4, but you can define your own.

The script will give you a list of words that may or may not be in the grid.
The suggested words are
 taken from a file with a list of words (1 word per line)
 and 
 consist only of 3-letter sequences that are possible based on the given grid.

It's still up to you to find the words in the grid.

Notes:

I used the word list of the Think Python book, available at:
https://github.com/AllenDowney/ThinkPython2/blob/master/code/words.txt

If you play squaredle or huntedle, you will find that they are using different lists.
You may miss some words, while they might not accept some of yours.

Also, the script works with 3-letter sequences for words of at least 4 letters.
It is possible that some word is suggested that is not possibly found in the grid, 
if the grid has letters appearing repeatedly, in different areas.


"""
import numpy as np
from collections import Counter

def is_letter_eng(char):
    return char.lower() in "abcdefghijklmnopqrstuvwxyz"


# this is one possible way to check whether word has n-long substring
def check_ngrams_in_word(word, ngramset, n):
    for i in range(len(word)-n+1):
        if word[i : i+n] not in ngramset:
            return False
    return True


# will use this to exclude words containing letters occurring more times than in the grid
def check_lettercount_in_word(word, lettercount):
    lettercount_word = Counter(word)
    for letter in lettercount_word:
        if letter not in lettercount:
            return False
        else:
            if lettercount_word[letter] > lettercount[letter]:
                return False
    return True


def ordinalending(n):
    suff = "th"
    if (n % 10 == 1 and n % 100 != 11):
        suff = "st"
    if (n % 10 == 2 and n % 100 != 12):
        suff = "nd"
    if (n % 10 == 3 and n % 100 != 13):
        suff = "rd"
    return suff


def read_posint_from_cmdline_withct(text, maxct, defvalue):
    """Get positive integer as user input from command line,
    repeat if user gives invalid input, until a valid input is given or max number of attempts reached.
    
    Arguments:
      text (string): the text to be displayed to prompt the user
      maxct (int): the number of attempts allowed for the user to get a valid number in
      defvalue (int): a default value to be returned in case user fails a valid number
    
    Returns:
      int: ideally a positive integer inputted by user.
           a pre-defined integer value in case user exceeded number of attempts without giving valid number.
    """
    ct = 0
    while True:
        ct += 1
        try:
            number = int(input(text))
        except:
            if ct >= maxct:
                print("Stop now. Got invalid input just too many times.")
                print("will be using", defvalue, "as a default value\n")
                number = defvalue
                break
            else:
                print("It should be a whole number. Try again")
                continue
        
        if number < 1:
            if ct >= maxct:
                print("Stop now. Got invalid input just too many times.")
                print("will be using", defvalue, "as a default value\n")
                number = defvalue
                break
            else:
                print("Not a good number. It should be positive. Try again\n")
                number = defvalue
                continue
        else:
            break
    return number


class WordGrid:
    """A grid of letters.
    Shape is 4x4 by default, but could be any of size.
    """
    
    def __init__(self, m=4, n=4):
        self.grid = np.empty(shape=(n, n), dtype=str)
        self.rows = m
        self.cols = n

    def __str__(self):
        return str(self.grid).upper()

    # delegating checking validity of given index to this function
    def is_valid_index(self, row, col):
        if (0 <= row < self.rows and 0 <= col < self.cols):
            return True
        return False
    
    def update_grid_onefield(self, row, col, letter):
        try:
            self.grid[row, col] = letter
        except:
            print("it should be 1 letter")

    def update_gridline_from_string(self, row, string):
        if len(string) == self.rows:
            self.grid[row, :] = list(string)
        else:
            print("Your string of letters doesn't really fit into the grid")
    
    def update_gridline_from_list(self, row, lst):
        if len(lst) == self.rows:
            self.grid[row, :] = lst
        else:
            print("Your list of letters doesn't really fit into the grid")
    
    def get_element(self, row, col):
        return self.grid[row, col]
    
    def lettercount(self):
        """Returns a Counter object with the count for each letter occurring in the grid
        """
        return Counter(self.grid.flatten())
    
    def get_neighbours_index(self, row, col):
        """will return a list of index (row, col) pairs of all the neighbouring slots."""
        # every slot has 3, 5 or 8 neighbours (depending on position in the grid (edge/middle))
        neighbours = []
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if self.is_valid_index(row+i, col+j) and not (i == 0 and j == 0):
                    neighbours.append((row+i, col+j))
        return neighbours

      
    def get_two_neighbours(self, row, col):
        """Get the neighbours of a given slot, and also the neighbours of the neighbours,
        i.e. letter 3-grams (stepping back to original slot is not allowed)
        """
        # neighbour paths with 2 steps, stored in a dict
        # dict keys: all the possible neighbours the starting point has
        # dict elements: a list of neighbours for the given neighbour (excluding the start)
        neighbour_dict = {}
        neighbours = self.get_neighbours_index(row, col)
        for neighbour in neighbours:
            neighbour_dict[neighbour] = []
            nextrow, nextcol = neighbour
            nextneighbours = self.get_neighbours_index(nextrow, nextcol)
            for nextneighbour in nextneighbours:
                if nextneighbour != (row, col):
                    neighbour_dict[neighbour].append(nextneighbour)
        
        threegrams = []
        for key, itemlist in neighbour_dict.items():
            keyrow, keycol = key
            gram = self.get_element(row, col) + self.get_element(keyrow, keycol)
            
            for item in itemlist:
                itemrow, itemcol = item
                threegrams.append(gram+self.get_element(itemrow, itemcol))
        # same 3-gram may occur in different directions, so converting to set
        return set(threegrams)
            
    def get_all_threegrams(self):
        allgrams = []
        for row in range(self.rows):
            for col in range(self.cols):
                grams = self.get_two_neighbours(row, col)
                allgrams.extend(grams)
        #allgrams_set = set(allgrams)
        return set(allgrams)


# some grid-related functions

def fill_grid_from_cmdline(grid):
    for i in range(grid.rows):
        suff = ordinalending(i+1)
        print(f"{i+1}{suff} line:")
        line = input()
        grid.update_gridline_from_string(i, line)
    return grid
    

def create_grid_from_cmdline():
    # limiting the user to 3 attempt to give a valid number
    # setting default value to 4, in case user doesn't give anything valid in those attempts
    rows = read_posint_from_cmdline_withct("number of rows: \n", 3, 4)

    cols = read_posint_from_cmdline_withct("number of columns: \n", 3, 4)

    print("ok, number of rows: ", rows, "\n")
    print("ok, number of columns: ", cols, "\n")
    
    # rows and cols come from a function with a default value, 
    # so 'grid' cannot error out when created
    grid = WordGrid(rows, cols)

    print("""Now fill the grid with letters, line by line.
             Just the letters without spaces, like 'abcd' or 'ABCD'.
             Your grid may actually have gaps 
             - you can use space for that, like 'AB D'
          """)
    fill_grid_from_cmdline(grid)
    return grid
    

def filter_wordlistfile(filename, grid):
    lettercount = grid.lettercount()
    threegrams = grid.get_all_threegrams()
    possible_words = []
    fin = open(filename, "r")
    for line in fin:
        word = line.strip()
        if (len(word) > 3 and check_lettercount_in_word(word, lettercount)):
            if check_ngrams_in_word(word, threegrams, 3):
                possible_words.append(word)
    return possible_words


### the main part comes here

print("""You can create your own letter grid, to search for words.\n
             First specify the size of the grid (number of rows and columns),
             then give the letters of the word grid, line by line.\n
             So, what's the size of the word grid?""")
             
grid = create_grid_from_cmdline()

print("\nYour grid looks like:\n", grid, "\n")

poss_words = filter_wordlistfile("words.txt", grid)
if len(poss_words) == 0:
    print("oh, can't seem to find any good words :o")
else:
    if len(poss_words) == 1:
        print("How about this word?")
    else:
        print("How about these words?")
    for word in poss_words:
        print(word)

