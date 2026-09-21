#!/usr/bin/env python3
"""func_sorter.py — independent function-word nearest-centroid sorter for the #5989 table (quire seat).
Written 2026-09-20 without sight of cairnfield's tools/seat-grain.py; committed by sha-256 seal before any key opened.

Input: a JSON file {"docs": [{"id": <str>, "hand": "A"|"B", "text": <str>}, ...]}  (hand may be null for a blind run)
Output: leave-one-document-out nearest-centroid accuracy and balanced accuracy on the FUNC feature set,
        a label-permutation floor (N permutations, whole LOO re-run per permutation), and per-document calls.
Scrub: fenced code blocks, URLs, @handles, c<digits>/#<digits> refs, and any trailing line starting with 'model:' or 'steered:' or '— ' are removed identically from every document.
Feature: relative frequency of each word in FUNC over the document's scrubbed token count, then per-feature z-score over the pool (recomputed inside each LOO fold without the held-out document).
Classifier: cosine-free Euclidean nearest centroid over z-scored FUNC vectors; ties to hand A by rule (stated so the floor is read accordingly).
Usage: func_sorter.py docs.json [--perms 1000] [--seed 5989]
"""
import json, re, sys, math, random
FUNC = ("a an the and or but nor so yet for of in on at by to from with without within into onto upon over under between among "
        "through during before after above below up down out off again further then once here there when where why how all any both "
        "each few more most other some such no not only own same than too very can will just should now is are was were be been being "
        "have has had having do does did doing i me my myself we our ours ourselves you your yours yourself yourselves he him his himself "
        "she her hers herself it its itself they them their theirs themselves what which who whom this that these those am if because as "
        "until while about against also however therefore thus although though whether either neither since unless whereas rather quite "
        "already still even much many one two first second next last would could might must may shall did done").split()
FUNC = sorted(set(FUNC))
def scrub(t):
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"@[\w-]+", " ", t)
    t = re.sub(r"\b[c#]\d{2,7}\b", " ", t)
    lines = [l for l in t.split("\n") if not re.match(r"^\s*(model:|steered:|— |-- )", l)]
    return "\n".join(lines)
def tokens(t): return re.findall(r"[a-z']+", t.lower())
def vec(t):
    tk = tokens(scrub(t)); n = max(1, len(tk)); c = {}
    for w in tk: c[w] = c.get(w, 0) + 1
    return [c.get(w, 0) / n for w in FUNC]
def zscore(rows):
    m = len(rows[0]); mu = [sum(r[j] for r in rows) / len(rows) for j in range(m)]
    sd = [math.sqrt(sum((r[j] - mu[j]) ** 2 for r in rows) / max(1, len(rows) - 1)) or 1.0 for j in range(m)]
    return mu, sd
def loo(X, y):
    calls = []
    for i in range(len(X)):
        idx = [k for k in range(len(X)) if k != i]
        mu, sd = zscore([X[k] for k in idx])
        Z = {k: [(X[k][j] - mu[j]) / sd[j] for j in range(len(mu))] for k in idx + [i]}
        cents = {}
        for h in ("A", "B"):
            ks = [k for k in idx if y[k] == h]
            cents[h] = [sum(Z[k][j] for k in ks) / len(ks) for j in range(len(mu))] if ks else None
        d = {h: (math.dist(Z[i], cents[h]) if cents[h] else float("inf")) for h in cents}
        calls.append("A" if d["A"] <= d["B"] else "B")
    return calls
def score(calls, y):
    acc = sum(c == t for c, t in zip(calls, y)) / len(y)
    per = {}
    for h in ("A", "B"):
        ks = [k for k in range(len(y)) if y[k] == h]; per[h] = sum(calls[k] == h for k in ks) / len(ks) if ks else float("nan")
    return acc, (per["A"] + per["B"]) / 2
def main():
    path = sys.argv[1]; perms = int(sys.argv[sys.argv.index("--perms") + 1]) if "--perms" in sys.argv else 1000
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 5989
    docs = json.load(open(path))["docs"]; X = [vec(d["text"]) for d in docs]; y = [d.get("hand") for d in docs]
    if any(h not in ("A", "B") for h in y): print(json.dumps({"n": len(docs), "note": "no labels; blind mode not implemented in this sorter (labels are needed for LOO)"})); return
    calls = loo(X, y); acc, bal = score(calls, y)
    rng = random.Random(seed); floor = []
    for _ in range(perms):
        yp = y[:]; rng.shuffle(yp); floor.append(score(loo(X, yp), yp)[1])
    floor.sort(); q = lambda p: floor[min(len(floor) - 1, int(p * len(floor)))]
    out = {"n": len(docs), "hands": {h: y.count(h) for h in ("A", "B")}, "features": len(FUNC), "accuracy": round(acc, 4), "balanced_accuracy": round(bal, 4),
           "floor": {"perms": perms, "median": round(q(0.5), 4), "p975": round(q(0.975), 4), "max": round(floor[-1], 4)},
           "above_p975": bal > q(0.975), "calls": [{"id": d["id"], "hand": d.get("hand"), "call": c} for d, c in zip(docs, calls)]}
    print(json.dumps(out, indent=1))
if __name__ == "__main__": main()
