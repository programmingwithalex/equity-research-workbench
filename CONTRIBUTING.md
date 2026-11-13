# Contributing

## Increment and review workflow

1. Explain the concept, alternatives, dependencies, and runtime flow for one small
   increment. Review the proposed files and behavior before editing.
2. Create a feature branch from `main`; keep unrelated changes out of the PR.
3. Add behavioral tests alongside application logic. Use focused fixtures for SEC
   metadata and mock HTTP responses; ordinary CI must not use live SEC or model
   APIs.
4. Run the README quality commands and `python -m pytest` using
   the project virtual environment. Inspect the diff and update documentation.
   Install the documented pre-commit hook in each clone. When formatting changes
   a file, review and restage it before retrying the commit; do not bypass hooks.
5. Open a PR describing behavior, verification, and limitations. Keep the learning
   checkpoints for each implementation increment; passing CI alone does not prove
   application correctness.
6. Before every future merge, run the installed `$simplify-review-rebase` skill,
   then verify required CI against the resulting head revision. The skill fixes
   blocking and should-fix findings automatically within its edit boundary; minor
   findings remain report-only unless a fix or acceptance is separately authorized.
7. Alex authorizes automatic merging in this repository when the workflow has no
   outstanding findings and required CI passes for the exact reviewed head. No
   additional per-PR merge approval is needed. Unresolved findings of any severity,
   unavailable workflow instructions, or failing/pending checks block automatic
   merge; report them rather than bypassing the gate. A finding explicitly accepted
   by Alex is resolved for this gate.

The only direct-to-main exception is the initial README bootstrap commit. After
the first `quality` check is registered, protect `main` against direct changes,
force pushes, and deletion, including administrator bypass.

CI can commit Ruff corrections to trusted same-repository PR branches. Any such
commit invalidates review of the earlier head. Fetch and review the actual new
head, then verify its required checks before applying the automatic merge gate.
Fork and Dependabot PRs remain read-only. A failed concurrent push or workflow
dispatch remains a failure; inspect the logs and branch rather than bypassing it.

## Code and documentation

- Annotate function parameters and returns; keep mypy strict mode enabled.
- Use Google-style docstrings. Explain inputs, outputs, side effects, and
  exceptions when they are relevant to the function.
- Comments explain non-obvious decisions and assumptions, rather than repeat
  individual Python statements.
- Prefer direct, readable code. Assume project-owned inputs are well-formed;
  enforce meaningful source provenance, external-data, and correctness boundaries
  without surrounding every operation with generic exception handling.
- Keep the README current. Record learning in `docs/LEARNING_LOG.md` and technical
  handoff state in `docs/PROJECT_STATUS.md`; keep both distinct from the changelog.
- Ruff enforces docstring conventions but cannot establish that an explanation is
  informative. Human review must check that.

## Versions and public content

Use semantic release tags such as `v0.1.0` and describe changes in `CHANGELOG.md`.
Release automation starts with the first complete filing-library release;
deployment automation follows later.

Only public-source fixtures and synthetic portfolio examples may be committed.
Keep downloads, personal financial data, credentials, and environment files local.
Check the exact staged file list before every commit.
