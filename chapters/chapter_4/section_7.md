# Process

[ar:issue-tracker]: https://github.com/balabit/syslog-ng/issues 

Of course, we also accept patches. If you want to submit a patch, the
guidelines the following:

 1. Open an issue first, if there is none open for the particular
    issue for the topic already in the
    [issue tracker][ar:issue-tracker]. That way, other contributors
    and developers can comment on the issue and the patch.
 2. If you submit a pull request that fixes an existing issue, mention
    the issue somewhere in the pull request, so we can close the
    original issue as well.
 3. We are using a coding style very similar to
    [GNU Coding Standards](https://www.gnu.org/prep/standards/standards.html#Writing-C)
    for syslog-ng. Please try to follow the existing conventions.
 4. Always add a `Signed-off-by` tag to the end of **every** commit
    message you submit.
 5. Always create a separate branch for the pull request, forked off
    from the appropriate syslog-ng branch.
 6. If your patch should be applied to multiple branches, submit
    against the latest one only, and mention which other branches are
    affected. There is no need to submit pull requests for each
    branch.
 7. If possible, write tests. We love tests.
 8. A well-documented pull request is much easier to review and merge.


Before submitting a separate module, please consider submitting it to
the [Incubator](https://github.com/balabit/syslog-ng-incubator) first, because it is easier to have your code accepted there. The Incubator is the repository of new and experimental modules.
