# Hangman-OOP-with-N-gram

Implement an AI player for the game Hangman with an object-oriented approach. 

Each guesser takes in a masked word (e.g. _ha_ever) and a set of guessed letter (e.g. {a, e, v, r, h, c, u}) and returns a letter. If the returned letter is in the word, then all instances of that letter is revealed.

OOP_Hangman.ipynb: provides step-by-step development from 1-gram all the way up to 7-gram.

Guesser_Class.py: contains all (AI) guessers.

Hangman_Implementation.py: provides an interface and a test function that plays/tests Hangman. If guesser is set to be HumanGuesser, then it allows interactive play.

Hangman_Test.py: runs Hangman with 6-gram guesser on the test set. Achieves > 60% success rate.

*.txt: list of words for training and testing purpose.
