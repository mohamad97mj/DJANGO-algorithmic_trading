def intersection(*lsts):
    ilst = lsts[0]
    for i in range(1, len(lsts)):
        ilst = list(set(ilst) & set(lsts[i]))
    return ilst


def union(*lsts):
    ulist = lsts[0]
    for i in range(1, len(lsts)):
        ulist += lsts[i]
    return ulist



