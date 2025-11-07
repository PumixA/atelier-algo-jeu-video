import heapq, random
from collections import deque


def topk_heap(scores: list[float], k: int) -> list[float]:
    if k <= 0:
        return []
    heap = scores[:k]
    heapq.heapify(heap)
    for s in scores[k:]:
        if s > heap[0]:
            heapq.heapreplace(heap, s)
    return sorted(heap, reverse=True)


def partition(arr, low, high):
    pivot = arr[high]
    i = low
    for j in range(low, high):
        if arr[j] > pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[high] = arr[high], arr[i]
    return i


def quickselect(arr, low, high, k):
    if low < high:
        pi = partition(arr, low, high)
        if pi == k:
            return
        elif pi < k:
            quickselect(arr, pi + 1, high, k)
        else:
            quickselect(arr, low, pi - 1, k)


def topk_quickselect(scores: list[float], k: int) -> list[float]:
    if k <= 0:
        return []
    arr = scores.copy()
    quickselect(arr, 0, len(arr) - 1, k)
    return sorted(arr[:k], reverse=True)


def sliding_window_max(arr: list[int], w: int) -> list[int]:
    if w <= 0 or not arr:
        return []
    dq, res = deque(), []
    for i, n in enumerate(arr):
        while dq and dq[0] <= i - w:
            dq.popleft()
        while dq and arr[dq[-1]] < n:
            dq.pop()
        dq.append(i)
        if i >= w - 1:
            res.append(arr[dq[0]])
    return res


if __name__ == "__main__":
    print("====================================")
    print("🏆 B1 — Top-K : Classement des meilleurs joueurs")
    print("====================================")

    random.seed(0)
    scores = [random.randint(0, 10000) for _ in range(100000)]
    k = 10

    print(f"Top {k} (tas min) :", topk_heap(scores, k))
    print(f"Top {k} (quickselect) :", topk_quickselect(scores, k))

    print("\n====================================")
    print("📈 B2 — Score maximum sur fenêtre glissante")
    print("====================================")

    arr = [1, 3, -1, -3, 5, 3, 6, 7]
    w = 3
    print("Scores :", arr)
    print("Fenêtre :", w)
    print("Résultat :", sliding_window_max(arr, w))
