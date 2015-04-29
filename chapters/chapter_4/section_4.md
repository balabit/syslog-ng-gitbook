# commits

Commits are the main source of traces in the history of a project.
That’s why they should be informative and simple. There is no ultimate
way of writing a good commit message. Some ideas worth being followed.

### Bulletpoints
* name of the module you changed something in
* simple and informative description about the content
* some explanations about the solutions
* references to docs and issues
* `Signed-off-by: Lorem Ipsum <lorem.ipsum@doloreth.et>`

### References
GitHub uses a reference system that helps the developers to create
connections between issues, comments and commits.
Another option of GitHub is mentioning someone that she/he will be
notified about.

#### Reference an issue in commit message
```
  foo: This patch correct the memleak in queueing in module foo.
  See here: #42
```

#### Reference an issue in comment
```
  This patch #42 should be ported to version 4.2 for it’s affected.
  See PR: #52
```

#### Mentioning someone 
```
  @daniel should look at this PR #66
```

