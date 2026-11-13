def array_rotation_detector(arr1, arr2):
    if len(arr1) != len(arr2):
        return False
    if not arr1:
        return True
    return any(arr1[i:] + arr1[:i] == arr2 for i in range(len(arr1)))