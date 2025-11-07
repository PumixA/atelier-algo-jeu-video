import hashlib
from typing import Iterable, List

# ---------- E1 — SHA-256 ----------

def sha256_text(text: str, salt: str = "") -> str:
    """
    Hash SHA-256 d'un texte (optionnellement salé).
    """
    h = hashlib.sha256()
    if salt:
        h.update(salt.encode("utf-8"))
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def sha256_file(fileobj, salt: str = "", chunk_size: int = 65536) -> str:
    """
    Hash SHA-256 d'un fichier streamé (request.files['file']).
    On lit par chunks pour éviter de charger en RAM.
    """
    h = hashlib.sha256()
    if salt:
        h.update(salt.encode("utf-8"))
    while True:
        chunk = fileobj.read(chunk_size)
        if not chunk:
            break
        h.update(chunk)
    # repositionne à 0 si on veut relire ailleurs
    try:
        fileobj.seek(0)
    except Exception:
        pass
    return h.hexdigest()


# ---------- E2 — Bloom Filter ----------

class BloomFilter:
    """
    Filtre de Bloom simple en mémoire (non persistant).
    - m: taille du bitset (nombre de bits)
    - k: nombre de fonctions de hachage
    Collisions → faux positifs possibles, jamais de faux négatifs.
    """
    def __init__(self, m: int = 2048, k: int = 4):
        assert m > 0 and k > 0
        self.m = m
        self.k = k
        self.bits = [0] * m

    def _hash(self, i: int, key: str) -> int:
        # h_i(key) = blake2b(i|key) mod m (rapide, bien distribué)
        h = hashlib.blake2b(digest_size=8)
        h.update(f"{i}|{key}".encode("utf-8"))
        return int.from_bytes(h.digest(), "big") % self.m

    def add(self, key: str) -> None:
        for i in range(self.k):
            idx = self._hash(i, key)
            self.bits[idx] = 1

    def add_many(self, keys: Iterable[str]) -> None:
        for k in keys:
            self.add(str(k))

    def check(self, key: str) -> bool:
        for i in range(self.k):
            idx = self._hash(i, key)
            if self.bits[idx] == 0:
                return False
        return True

    def check_many(self, keys: Iterable[str]) -> List[bool]:
        return [self.check(str(k)) for k in keys]
