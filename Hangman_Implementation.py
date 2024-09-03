def hangman(secret, guesser, max_mistakes=6, recalibrate=False, verbose=True):
    """
        This function plays the hangman game with the provided guesser and returns the number of incorrect guesses.
        secret: a string of alphabetic characters, i.e., the answer to the game
        guesser: an object of the class Guesser which guesses the next character at each stage in the game
        max_mistakes: limit on length of game, in terms of number of allowed mistakes
        recalibrate: whether to dynamically update the guesser's dictionary
        verbose: silent or verbose diagnostic prints
    """
    secret = secret.lower()
    masked_word = ['_'] * len(secret)
    guessed = set()
    if recalibrate:
        guesser.adapt(guesser.original_corpus) # start from the original dictionary if recalibrate
    if verbose:
        print("Starting hangman game. Target is", ' '.join(masked_word), 'of length', len(secret))

    mistakes = 0
    while mistakes < max_mistakes:
        if verbose:
            print("You have", (max_mistakes - mistakes), "attempts remaining.")

        guess = guesser.guess(masked_word, guessed) # make a guess with guesser
        if verbose:
            print('Your guess is', guess)
        if guess in guessed:
            if verbose:
                print('Already guessed this before.')
            mistakes += 1
        else:
            guessed.add(guess)
            if guess in secret and len(guess) == 1: # correct guess
                for i, char in enumerate(secret):
                    if char == guess:
                        masked_word[i] = char # reveal correctly guessed letters
                if verbose:
                    print('Good guess:', ' '.join(masked_word))
            else: # incorrect guess
                if len(guess) != 1:
                    print('Please guess with only 1 character.')
                if verbose and mistakes < max_mistakes:
                    print('Sorry, try again.')

                mistakes += 1
            if recalibrate:
                guesser.recalibrate(masked_word, guessed)

        if '_' not in masked_word:
            if verbose:
                print('Congratulations! You won.')
            return mistakes

    if verbose:
        print('Out of guesses. The secret word was', secret)
    return mistakes

def test_guesser(guesser, test_set, recalibrate = False, verbose = False):
    total = 0
    num_success = 0
    recalibrate_str = " with recalibration" if recalibrate else ""
    print(f"\nTesting the {guesser.name} guesser using every word in test set" + recalibrate_str)
    for word in test_set:
        num_guesses = hangman(word, guesser, 26, recalibrate = recalibrate, verbose = verbose)
        total += num_guesses
        num_success += int(num_guesses <= 6)
    print("Average number of guesses used: ", total / float(len(test_set)))
    print("Success rate with 6 tries: ", num_success / float(len(test_set)))
    return num_success / float(len(test_set))
