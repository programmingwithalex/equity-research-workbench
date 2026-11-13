#!/usr/bin/env bash
# Run only for same-repository PRs; workflow permissions enforce that boundary.
set -euo pipefail

"${FORMAT_PYTHON:-python}" -m ruff format .
if git diff --quiet; then
  echo "changed=false" >> "$GITHUB_OUTPUT"
  exit 0
fi

# Explicit identity avoids bot/AI attribution in the formatting commit metadata.
export GIT_AUTHOR_NAME=programmingwithalex
export GIT_AUTHOR_EMAIL=programmingwithalex3@gmail.com
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
git add --update
git commit -m "Format Python with Ruff"

# A normal push refuses to overwrite newer contributor commits.
git push origin "HEAD:refs/heads/$PR_BRANCH"

# GITHUB_TOKEN pushes cannot be relied on to start fresh checks automatically.
gh workflow run ci.yml --repo "$GH_REPO" --ref "$PR_BRANCH"
echo "changed=true" >> "$GITHUB_OUTPUT"
