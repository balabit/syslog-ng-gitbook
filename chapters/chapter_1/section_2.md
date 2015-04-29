# git structure

When a lot of people contribute on the same project it is impossible not to use 
some kind of version control system to track the evolution of the development.
For we love open-source solutions and use GitHub to publish our code it was 
natural to use git as a VCS. 

We are going to give you a deeper insight of contributing to the code in
chapter: [contribute](). Here we are trying to keep the focus on the structure
of the repository.

Basically the development happen in forked repos so that's not our concern what 
structure you use. When sending a PR to the upstream there are some guidelines
according to branching and naming conventions, though.

## Branching

### master
Master stands for the absolute upstream. Main branch of the repository.

### f/loremipsum
* **f:** represents that it is a feature or fix branch that adds a new feature or fixes a bug
* **loremipsum:** short name of the content of the branch

_example (feauture)_: f/templatable-recipients

_example (bug)_: f/memleak-in-queueing

### X.X/master
Older version of the project.

X.X stands for a version number 3.5/3.6/3.7 of the project. 

_example_: 3.6/master

### X.X/f/loremipsum
Feature or bugfix branch for an older version of the project.

X.X stands for a version number 3.5/3.6/3.7 of the project. 

_example (bug)_: 3.6/f/memleak-in-queueing

