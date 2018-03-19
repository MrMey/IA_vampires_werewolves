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
    for i in range(m):
        for j in range(n):
            print(i, j)
            D[(i,j)] = get_distance(a[i], h[j][1])
            M[(i,j)] = model.addVar(name='%s, %s' % (i,j), vtype='B')

    # Nb d'alliés > Nb d'humains
    for k in range(n):
        model.addCons(quicksum(M[(i,k)] for i in range(m)) >= h[k][0])

    # Un allié n'attaque qu'un seul groupe d'humains
    for k in range(m):
        model.addCons(quicksum(M[(k,j)] for j in range(n)) <= 1)

    alpha, beta = 0.5, 0.5
    # On optimise le nombre d'alliés par rapport au nombre d'humains
    obj_1 = quicksum(quicksum(M[(i,j)] for i in range(m))-h[j][0] for j in range(n))
    # On minimise la distance totale parcourue par les alliés
    obj_2 = quicksum(M[(i,j)]*D[(i,j)] for i in range(m) for j in range(n))
    model.setObjective(alpha*obj_1+beta*obj_2, 'minimize')

    model.optimize()
    print(model.getObjVal())
    vars = model.getVars()
    for v in vars:
        if model.getVal(v) == 1:
            print(v.name)