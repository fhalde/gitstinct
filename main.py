import attr
from collections import Counter


@attr.define
class Commit:
    sha: str
    files: set[str]


@attr.define
class History:
    commits: list[Commit]


def likely(history: History, changeset: set) -> dict:
    """
    Returns a dict with an entry for every file.
    For a given changeset B, calculate the following metrics for every other file F in the repo:
    - probability: P(F | B) – How often F changes when B changes.
    - lift: P(F | B) / P(F) – How much more likely F is to change when B changes, compared to F's overall change frequency.
    - risk: P(F | B) / P(F | !B) – How much more likely F is to change when B changes, compared to when B doesn't change.
    """
    sample = [c for c in history.commits if c.files & changeset]

    if not sample:
        return {}

    counts = Counter(f for c in sample for f in c.files)

    global_counts = Counter(f for c in history.commits for f in c.files)

    n = len(sample)
    total = len(history.commits)

    result = {}

    for file, count in counts.items():
        if file == changed_file:
            continue

        prob = (count + 1) / (n + 2)
        baseline = global_counts[file] / total

        outside = total - n
        outside_count = global_counts[file] - count

        lift = prob / baseline
        risk = prob / ((outside_count + 1) / (outside + 2)) if outside else None

        result[file] = {
            "probability": prob,
            "lift": lift,
            "risk": risk,
        }

    return result


def fixrate(
    history: History,
    changeset: set[str],
) -> float:
    sample = [c for c in history.commits if c.files & changeset]

    fixes = sum(
        "fix" in c.message.lower() or "patch" in c.message.lower() for c in sample
    )

    return (fixes + 1) / (len(sample) + 2)
