# Wordle Evaluator

The simple (but deceptively challenging) word-guessing game Wordle has been sweeping the globe recently. I wondered why it seems like it's always possible to guess the word in six turns, even though there are quite a lot of common five-letter words to choose from.

This game ends up somewhere in a gray area among Wheel of Fortune, Mastermind, and Sudoku, with a few interesting side effects.

Currently, this simple evaluator only evaluates your guess against Wordle's response and returns the number of words still valid, displaying the full list once it has dropped under 100.

The included dictionary.txt file is the US Scrabble player's dictionary, containing all common words and some less common ones. Note that Wordle itself appears to accept any word from SOWPODS.TXT (or Collins Scrabble Words \[CSW\]) list, like `EIGHE`, though I'd be surprised if that word were ever chosen.

This script runs only in interactive mode, asking you for your guess and for Wordle's response. The following syntax is used for Wordle's response:

- G for green squares
- Y for yellow squares
- X (or any other character) for not matched

Sample run:

```
INFO:root:Loaded 178691 words
Guess : AEGIS
Result: XYGYX
INFO:root:Wordlist filtered from 178691 to 7 word(s).
INFO:root:['EIGHT\n', 'GIGHE\n', 'GIGUE\n', 'IGGED\n', 'INGLE\n', 'LIGER\n', 'TIGER\n']
INFO:root:Try EIGHT

Guess : EIGHT
Result: YGGXY
INFO:root:Wordlist filtered from 7 to 1 word(s).
INFO:root:The answer is TIGER
```

It's not really intended for helping you cheat at Wordle. Although you could certainly use it for that, I am more interested in the meta-analysis of the game, answering the following sorts of questions:

- How "good" is a given guess against the current word? Against all Wordle words? Against any English word?
- What strategies are most effective across these sets?
- How "hard" is this game? What's the average tree depth to get to a single word?
- How many ambiguous words have the same results right up to the solution (i.e., LIGER-TIGER)? What's the maximum tree depth of ambiguous words?
- Can naive solvers win every time with 6 guesses? What's the min/max for any given algorithm?
- What words minimize initial guesses? (Cracking the Cryptic suggested RISEN/OCTAL to cover top letter frequencies.)

As a result, the current solver strategy is intentionally naive -- it will simply recommend the first valid alphabetical solution. In theory this means it should be harder to guess words towards the end of the alphabet (but maybe not depending on the distribution of those words.)

I do intend to improve this for unattended solving to test these solutions across the entire valid setn to answer at least some of these questions. In the meantime I wanted to release something with initial thoughts in case anyone has already done the work.

## Notes

This script works on non-five-letter words as well. I have no doubt someone will have already cloned Wordle with longer words, so this analysis should apply equally well. The Scrabble dictionary does stop at a certain word length as would be appropriate for that game, so if you wanted to use it for truly monstrous words it would be both impractical, and likely not very fun.
