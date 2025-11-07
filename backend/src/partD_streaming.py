import random
import hashlib

# ---------- D1 — Reservoir Sampling ----------

def reservoir_sampling(stream, k, seed=None):
    """
    stream: iterable (list d'entiers/strings/etc.)
    k: taille du réservoir
    seed: pour rendre le tirage reproductible (optionnel)

    Retourne un échantillon uniforme de taille min(k, len(stream)).
    """
    if k <= 0:
        return []
    if seed is not None:
        random.seed(seed)

    reservoir = []
    i = 0
    for item in stream:
        if i < k:
            reservoir.append(item)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = item
        i += 1
    return reservoir


# ---------- D2 — Count-Min Sketch ----------

class CountMinSketch:
    """
    Implémentation simple de CMS.

    - depth (d): nb de fonctions de hachage (lignes)
    - width (w): largeur de chaque ligne (colonnes)
    - add(key, count): augmente la fréquence approx
    - estimate(key): estimation avec biais positif (min des compteurs)
    """

    def __init__(self, depth: int, width: int):
        assert depth > 0 and width > 0, "depth/width doivent être > 0"
        self.d = depth
        self.w = width
        self.table = [[0] * width for _ in range(depth)]

    def _hash(self, i: int, key: str) -> int:
        # h_i(key) = blake2b(str(i) + "|" + key) mod width
        m = hashlib.blake2b(digest_size=8)
        m.update(f"{i}|{key}".encode("utf-8"))
        return int.from_bytes(m.digest(), "big") % self.w

    def add(self, key: str, count: int = 1):
        if count <= 0:
            return
        for i in range(self.d):
            col = self._hash(i, key)
            self.table[i][col] += count

    def estimate(self, key: str) -> int:
        vals = []
        for i in range(self.d):
            col = self._hash(i, key)
            vals.append(self.table[i][col])
        return min(vals) if vals else 0
