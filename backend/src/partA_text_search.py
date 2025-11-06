def build_lps(pattern: str) -> list[int]:
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            length = lps[length - 1] if length else 0
            if not length:
                i += 1
    return lps


def find_all_occurrences(text: str, pattern: str) -> list[int]:
    if not pattern:
        return []
    lps = build_lps(pattern)
    i = j = 0
    res = []
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
            if j == len(pattern):
                res.append(i - j)
                j = lps[j - 1]
        else:
            j = lps[j - 1] if j else 0
            if not j:
                i += 1
    return res


def rabin_karp_multi(text: str, patterns: list[str], base=257, mod=10**9+7):
    res = {p: [] for p in patterns}
    if not patterns:
        return res

    grouped = {}
    for p in patterns:
        grouped.setdefault(len(p), []).append(p)

    for m, group in grouped.items():
        if len(text) < m:
            continue
        pow_base = pow(base, m - 1, mod)
        phash = {p: 0 for p in group}
        for p in group:
            for ch in p:
                phash[p] = (phash[p] * base + ord(ch)) % mod

        h = 0
        for i in range(m):
            h = (h * base + ord(text[i])) % mod

        for i in range(len(text) - m + 1):
            for p, hp in phash.items():
                if h == hp and text[i:i + m] == p:
                    res[p].append(i)
            if i < len(text) - m:
                h = (h - ord(text[i]) * pow_base) % mod
                h = (h * base + ord(text[i + m])) % mod
                h = (h + mod) % mod
    return res


if __name__ == "__main__":
    print("====================================")
    print("🔎 A1 — Détection de messages suspects (KMP)")
    print("====================================")

    chat = "gg noob lol cheater gg noob cheater cheater gg"
    motif = "cheater"
    print("💬 Message du chat :", chat)
    print(f"🔍 Recherche du mot '{motif}' ...")
    occ = find_all_occurrences(chat, motif)
    print("📍 Occurrences trouvées :", occ)
    print(f"➡️ Total : {len(occ)}")

    print("\n🧪 Cas limites :")
    print("Motif vide :", find_all_occurrences(chat, ""))
    print("Motif inexistant :", find_all_occurrences(chat, "hack"))

    print("\n====================================")
    print("🧾 A2 — Recherche multi-motifs (Rabin–Karp)")
    print("====================================")

    text = "error 200 ok error 404 error 500 internal error 500 retry"
    patterns = ["error 500", "error 404", "ok error"]
    print("🧾 Logs :", text)
    print("🔍 Recherche :", patterns)
    hits = rabin_karp_multi(text, patterns)
    print("\nRésultats :")
    for p, pos in hits.items():
        print(f" - {p} trouvé aux positions {pos}")
