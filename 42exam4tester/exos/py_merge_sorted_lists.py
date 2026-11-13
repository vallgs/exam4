def merge_sorted_lists(lists: list[list[int]]) -> list[int]:
    result = []
    for lst in lists:
        merged = []
        i = 0
        j = 0
        while i < len(result) and j < len(lst):
            if result[i] <= lst[j]:
                merged.append(result[i])
                i += 1
            else:
                merged.append(lst[j])
                j += 1
        result = merged + result[i:] + lst[j:]
    return result