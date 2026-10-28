# How we work with Git (team guide)

1. Never work directly on `main`. `main` always contains working code for the demo.
2. Create a branch for each task:  `git checkout -b feature/resume-upload`
3. Commit small and often, with clear messages:  `git commit -m "Add resume upload form"`
4. Push your branch:  `git push origin feature/resume-upload`
5. Open a Pull Request on GitHub. Another member reviews it, then merges into `main`.
6. Before starting new work, update your copy:  `git checkout main` then `git pull`

## Branch names
- `feature/<name>`  new functionality
- `fix/<name>`      bug fix
- `docs/<name>`     documentation

## Rules
- Never commit `.env`, API keys, passwords or real resumes.
- Run `pytest` before opening a Pull Request.

## Module owners (edit this as a team)
| Module | Owner |
|---|---|
| Backend, database, reports | |
| Frontend, proctoring | |
| AI, assessment, code runner | |
