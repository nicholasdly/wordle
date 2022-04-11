import random
import time

ALLOWED_GUESSES = 6  # Maximum allowed guesses

def get_words():
    with open("words.txt", "r") as file:
        return file.read().split()

def main():
    words = get_words()
    answer = random.choice(words)
    answer = "shape"
    
    print(answer)

    count = 0
    while count < ALLOWED_GUESSES:
        guess = input("\nGuess the word: ").lower()
        
        # Check if guess was of correct length
        if len(guess) != 5:
            print("Error! Please guess a 5 letter word!")
            continue

        # Check if guess is in list of valid words
        if guess not in words:
            print("Error! That word is invalid!")
            continue
        
        for i in range(len(guess)):
            c = guess[i]

            # Check if character is in correct spot
            if c == answer[i]:
                print(f"{c.upper()} :: In the word and correct spot!")

            # Check if character is in word
            elif c in answer:
                print(f"{c.upper()} :: In the word but wrong spot!")

            else:
                print(f"{c.upper()} :: Not in the word!")
            
            time.sleep(0.3)

        # Check if guess is correct answer
        if guess == answer:
            print("\nNice job! You guessed the correct word!")
            print(f"The word was: {answer.upper()}\n")
            return

        count += 1
    
    print("\nAw shucks! You ran out of guesses!")
    print(f"The word was: {answer.upper()}\n")

if __name__ == "__main__":
    main()
