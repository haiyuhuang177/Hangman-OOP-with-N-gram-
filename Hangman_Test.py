from Guesser import UnigramGuesser, BigramGuesser, NgramGuesser, CombinationGuesser
from PlayHangman import hangman, test_guesser

training_set = []
test_set = []

with open("brown_shuffled.txt", "r") as f:
    brown = f.read().splitlines()

training_set = brown[1000:]
test_set = brown[:1000]

#with open("words_alpha.txt", "r") as f:
#    vocab = f.read().splitlines()

#training_set = vocab

onegram_guesser = NgramGuesser(1, by_length = True)
twogram_guesser = NgramGuesser(2)
threegram_guesser = NgramGuesser(3)
fourgram_guesser = NgramGuesser(4)
fivegram_guesser = NgramGuesser(5)
sixgram_guesser = NgramGuesser(6)
combination_guesser = CombinationGuesser([onegram_guesser, twogram_guesser, threegram_guesser, 
                                          fourgram_guesser, fivegram_guesser, sixgram_guesser],
                                         [0.1, 0.2, 0.1, 0.2, 0.1, 0.3])
combination_guesser.upload(training_set)
test_guesser(combination_guesser, test_set)
