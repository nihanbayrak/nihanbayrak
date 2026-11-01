"""GitHub numbers for the card: repos, stars, commits, followers, lines of code.

Counts only what the nightly workflow's own token can see, so a run by hand and a
run in Actions agree: public, non-fork repos she owns. Commits are her commit
contributions for every year since the account opened, plus the private ones
GitHub reports as restricted. Lines of code are the additions and deletions of
her own commits on each public repo's default branch. A commit that moves more than
50,000 lines is a data file or a vendored folder, not code, and is left out: one such
CSV, added and later deleted, would otherwise swing the total by 2.8 million.

In Actions the workflow's GITHUB_TOKEN is used; by hand, the gh CLI, which holds
its own credentials, so no token passes through this file.

    python tools/stats.py      # writes data/stats.json
"""
import json
import os
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "stats.json"
USER = "nihanbayrak"
DATA_DUMP = 50_000                       # lines in one commit; above this it is not code


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req = urllib.request.Request("https://api.github.com/graphql", data=body.encode(),
                                     headers={"Authorization": f"Bearer {token}",
                                              "Content-Type": "application/json",
                                              "User-Agent": "profile-stats"})
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.load(r)
    else:
        run = subprocess.run(["gh", "api", "graphql", "--input", "-"], input=body,
                             capture_output=True, text=True, timeout=120, check=True)
        out = json.loads(run.stdout)
    if out.get("errors"):
        raise RuntimeError(out["errors"][0].get("message", "GraphQL error"))
    return out["data"]


def collect():
    u = gql("""query($login: String!) { user(login: $login) {
        id createdAt followers { totalCount }
        repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
          totalCount nodes { name stargazerCount defaultBranchRef { name } } }
        repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY], privacy: PUBLIC) { totalCount }
    } }""", {"login": USER})["user"]

    created = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    years = range(created.year, now.year + 1)
    parts = []
    for y in years:
        frm = max(created, datetime(y, 1, 1, tzinfo=timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
        to = min(now, datetime(y, 12, 31, 23, 59, 59, tzinfo=timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
        parts.append(f'y{y}: contributionsCollection(from: "{frm}", to: "{to}") '
                     f'{{ totalCommitContributions restrictedContributionsCount }}')
    c = gql(f'query($login: String!) {{ user(login: $login) {{ {" ".join(parts)} }} }}', {"login": USER})["user"]
    commits = sum(v["totalCommitContributions"] + v["restrictedContributionsCount"] for v in c.values())

    added = deleted = 0
    for repo in u["repositories"]["nodes"]:
        if not repo["defaultBranchRef"]:
            continue
        cursor = None
        while True:
            h = gql("""query($owner: String!, $name: String!, $id: ID!, $after: String) {
                repository(owner: $owner, name: $name) { defaultBranchRef { target { ... on Commit {
                  history(author: {id: $id}, first: 100, after: $after) {
                    pageInfo { hasNextPage endCursor } nodes { additions deletions } } } } } } }""",
                    {"owner": USER, "name": repo["name"], "id": u["id"], "after": cursor})
            hist = h["repository"]["defaultBranchRef"]["target"]["history"]
            for n in hist["nodes"]:
                if n["additions"] + n["deletions"] > DATA_DUMP:
                    continue
                added += n["additions"]
                deleted += n["deletions"]
            if not hist["pageInfo"]["hasNextPage"]:
                break
            cursor = hist["pageInfo"]["endCursor"]

    return {
        "created": u["createdAt"][:10],
        "repos": u["repositories"]["totalCount"],
        "contributed": u["repositoriesContributedTo"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "commits": commits,
        "added": added,
        "deleted": deleted,
    }


def main():
    try:
        stats = collect()
    except Exception as e:                       # keep yesterday's numbers rather than none
        print(f"  could not fetch stats ({type(e).__name__}: {e}); keeping the last ones")
        return
    OUT.write_text(json.dumps(stats, indent=1) + "\n")
    print("  stats.json", stats)


if __name__ == "__main__":
    main()
