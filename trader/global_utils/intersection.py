def intersection(*lsts):
    ilst = lsts[0]
    for i in range(1, len(lsts)):
        ilst = list(set(ilst) & set(lsts[i]))
    return ilst


