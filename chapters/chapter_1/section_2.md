# Git structure

When a lot of people contribute on the same project it is impossible not to use
some kind of version control system to track the evolution of the development.
Because we love open source solutions and use GitHub to publish our code it was 
natural to use Git as a version control system. 

We are going to give you a deeper insight of contributing to the code in
chapter: [contribute](). Here we are trying to keep the focus on the structure
of the repository.

Basically the development happens in forked repos so that is not our concern what 
structure you use. When sending a PR to the upstream there are some guidelines
according to branching and naming conventions, though.

## Branching

### master
Master stands for the absolute upstream, most of the development happens on this branch. If you
want to contribute a new feature of you should send your Pull Request against this branch.

### X.X/master
Older version of the project.

X.X stands for a version number 3.5/3.6/3.7 of the project. These branches receive mostly
bug fixes.

_example_: 3.7/master

### loremipsum
Every other branch either adds a new feature of fixes a bug. We used to prefix all feature
branches with `f/` but we no longer maintain this practice.

If you send a bug fix, use the `fix-` prefix, like `fix-memleak-in-queueing`. If you implemented a new feature,
use some descriptive name for your branch, like `add-kafka-destination`.
