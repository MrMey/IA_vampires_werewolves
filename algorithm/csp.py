from pyscipopt import Model, quicksum
from algorithm.greedy import get_distance


def csp(grid):
    model = Model()
    a, h, D, M = {}, {}, {}, {}

    # a : une variable a[i] par allié, indiquant la position (x,y)
    i = 0
    for al in grid.allies:
        for k in range(grid.allies[al]):
            a[i] = al
            i += 1
    m = i

    # h : une variable h[j] par groupe d'humains, de la forme (nb d'humains, (x,y))
    j = 0
    for hu in grid.humans:
        h[j] = (grid.humans[hu], hu)
        j += 1
    n = j

    # D : matrice indiquant la distance entre l'allié i et l'humain j
    # M : matrice indiquant 1 si l'allié i attaque l'humain j
    for i,j in zip(range(m),range(n)):
        D[(i,j)] = get_distance(a[i], h[j][1])
        M[(i,j)] = model.addVar(vtype='B')

    for k in range(n):
        model.addCons(quicksum(M[(i,k)] for i in range(m)) >= h[k][0])

    model.setObjective(quicksum(M[(i,j)]*D[(i,j)] for i,j in zip(range(m),range(n))), 'minimize')
    model.optimize()
    print(model.getObjVal())
    #vars = model.getVars()
