# Commits

Commits are the main source of traces in the history of a project.
That is why commit messages should be informative and simple. There is no ultimate way of writing a good commit message, but we have collected some ideas that are worth being followed.

### Bulletpoints
* Name of the module you changed something in
* Simple and informative description about the content
* Some explanations about the solutions
* References to documents and issues
* `Signed-off-by: Lorem Ipsum <lorem.ipsum@doloreth.et>`

### References
GitHub uses a reference system that helps the developers to create
connections between issues, comments and commits.
Another option of GitHub is informing someone about a commit by mentioning their names.

#### Referencing an issue in commit message
```
  foo: This patch corrects the memleak in queueing in module foo.
  See here: #42
```

#### Referencing an issue in comment
```
  This patch #42 should be ported to version 4.2 because it is affected too.
  See PR: #52
```

#### Mentioning someone 
```
  @daniel look at this PR #66
```

