def sliding_window_maximum(nums: list[int], k: int) -> list[int]:
    if k <= 0 or k > len(nums):
        return []
    dq, res = [], []          # indices, valeurs décroissantes (O(n) amorti)
    head = 0
    for i, x in enumerate(nums):
        while len(dq) > head and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[head] <= i - k:
            head += 1
        if i >= k - 1:
            res.append(nums[dq[head]])
    return res
