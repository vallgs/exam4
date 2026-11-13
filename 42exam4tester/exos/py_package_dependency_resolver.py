def package_dependency_resolver(packages: dict[str, list[str]]) -> list[str]:
    indeg = {p: 0 for p in packages}
    users = {p: [] for p in packages}
    for p, deps in packages.items():
        for d in deps:
            if d in packages:          # dépendances inconnues ignorées
                indeg[p] += 1
                users[d].append(p)
    queue = sorted(p for p in packages if indeg[p] == 0)
    order = []
    while queue:
        p = queue.pop(0)
        order.append(p)
        for u in users[p]:
            indeg[u] -= 1
            if indeg[u] == 0:
                queue.append(u)
    return order if len(order) == len(packages) else [] 