def package_dependency_resolver(packages: dict[str, list[str]]) -> list[str]:
    order = []
    done = set()
    while len(order) < len(packages):
        ready = []
        for pkg in packages:
            if pkg not in done:
                ok = True
                for dep in packages[pkg]:
                    if dep in packages and dep not in done:
                        ok = False
                if ok:
                    ready.append(pkg)
        if ready == []:
            return []
        for pkg in sorted(ready):
            order.append(pkg)
            done.add(pkg)
    return order