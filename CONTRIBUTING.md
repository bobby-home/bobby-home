# Bobby Contributing Guide
Hi! I'm really excited that you are interested in contributing to Bobby Home.
Before submitting your contribution, please make sure to take a moment and read through the following document.

## Versioning
- We use [Semantic Versioning](https://semver.org) for releases.

## Commits
The commit message guideline is adapted from the [AngularJS Git Commit Guidelines](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines).

### Types
Types define which kind of changes you made to the project.

| Types         | Description |
| ------------- |-------------|
| BREAKING      | Changes including breaking changes. |
| build         | New build version. |
| chore         | Changes to the build process or auxiliary tools such as changelog generation. No production code change. |
| ci            | Changes related to continuous integration only (GitHub Actions, CircleCI, ...). |
| docs          | Documentation only changes. |
| feat          | A new feature. |
| fix           | A bug fix. |
| perf          | A code change that improves performance. |
| refactor      | A code change that neither fixes a bug nor adds a feature. |
| style         | Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.). |
| test          | Adding missing or correcting existing tests. |
| trans          | Changes related to translations. |

### Scopes
Scopes define high-level applications of Bobby.
- core
- smart-camera

### Examples

```sh
git commit -m "feat(core): awesome new core feature"
git commit -m "docs(smart-camera): fix spelling"
git commit -m "chore: split training script into awesome blocks"
git commit -m "style(core): remove telegram bot useless parentheses"
```
