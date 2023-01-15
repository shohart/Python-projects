# Project 1. Task 8.1 from SkillFactory python course.

## Table of contents

[1. Project description](README.md#Project-description)  
[2. What kind of case are we solving?](README.md#What-kind-of-case-are-we-solving)  
[3. Data summary](README.md#Data-summary)  
[4. Stages in the project](README.md#Stages-in-the-project)  
[5. Results and conclusions](README.md#Results-and-conclusions)

### Project description

This game is used to find a random number in a minimum number of tries possible.
To play, the computer generates a random integer between 1 and 100, and the user has to guess what number it is.
Creating an algorithm to guess the number the computer guessed in the minimum number of tries possible.

:arrow_up:[to table of contents](README.md#Table-of-contents)

### What kind of case are we solving?

We have to write a program that guesses the number in the minimum number of tries.

**Conditions for the contest:**

- The computer guesses an integer from 0 to 100, and we have to guess it. By "guess", we mean "write a program that guesses the number".
- The algorithm takes into account information about whether a random number is greater or less than the number we want.

**Quality metrics**.  
Results are estimated by the average number of attempts at 1000 repetitions. Number of tries shold be less than 20.

**What we practice**  
Learning to write good code in python

### Data summary

No additional data used in this project.

:arrow_up:[to table of contents](README.md#Table-of-contents)

### Stages in the project

- We need to write a function to guess an integer, using the info wheter random number is bigger or less than the number we want. We can use function from project 0, but instead of printing a tip for the user we can adjust algorithm's logic accordingly.
- We need to write a function to rate results of our project to be sure that it fulfills the conditions. We also can use a code from project 0 for this task with minor changes.
- Then we need to check our code if it maches PEP standarts.
- Finally we need to upload a code to GitHub and make shure that GitHub-project page is designed accordingly (including documentation, file structure, code repeatability, etc).

:arrow_up:[to table of contents](README.md#Table-of-contents)

### Results and conclusions:

We got an algorithm that can guess an integer in 5 tries average. We froze requirements using pip in requirements.txt.

Function **random_predict_midl()** can be used with a set up integer or can calculate a random number by itself. Thus it has built in protection to check whether provided value is in acceptable range.

Function **score_game_midl()** runs predict function 1000 times and returns average function as a result.

Task conditions are fulfilled.

:arrow_up:[to table of contents](README.md#Table-of-contents)

If you find the information on this project interesting or useful I would be very grateful if you would mark the repository and profile ⭐️⭐️⭐️- by Shohart (with SkillFactory)
