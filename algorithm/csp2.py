from pyscipopt import Model, quicksum
from algorithm.greedy import get_distance


def csp(grid):
    model = Model()
    a, h, b = {}, {}, {}

    # a : une variable a[i] par allié, de la forme (nb d'alliés, (x,y))
    i = 0
    for al in grid.allies:
        a[i] = (grid.allies[al], al)
        i += 1
    m = i

    # h : une variable h[j] par groupe d'humains, de la forme (nb d'humains, (x,y))
    j = 0
    for hu in grid.humans:
        h[j] = (grid.humans[hu], hu)
        j += 1
    n = j

    # b : une variable b[j] booléenne indiquant si on attaque ou non ce groupe
    for j in range(n):
        b[j] = model.addVar(name='%s' % j, vtype='B')

    model.addCons(quicksum(b[j]*(h[j][0]+1) for j in range(n)) <= quicksum(a[i][0] for i in range(m)))
    model.setObjective(quicksum(b[j]*h[j][0] for j in range(n)), 'maximize')
    model.optimize()
    print(model.getObjVal())
    vars = model.getVars()
    for v in vars:
        if model.getVal(v) == 1:
            print(v.name)