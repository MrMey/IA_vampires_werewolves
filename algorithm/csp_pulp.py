import pulp

from algorithm.greedy import get_distance


def csp(grid):
    # === INTRO ===
    a, h, D = {}, {}, {}

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

    # ==== PULPPPP ====
    problem = pulp.LpProblem('Men', pulp.LpMinimize)

    # Variables
    """ D : matrice indiquant la distance entre l'allié i et l'humain j
        M : matrice indiquant 1 si l'allié i attaque l'humain j"""
    for i in range(m):
        for j in range(n):
            # print(i, j)
            D[(i,j)] = get_distance(a[i], h[j][1])
            # M[(i,j)] = pulp.LpVariable('%s,%s' % (i,j), cat='Binary')
            # print('M[i,j]', M[(i,j)])
    M = pulp.LpVariable.dicts('M', ((i,j) for i in range(m) for j in range(n)), cat='Binary')

    # Constraints
    """Nb d'alliés > Nb d'humains"""
    for k in range(n):
        problem += pulp.lpSum(M[i,k] for i in range(m)) >= h[k][0]

    """Un allié n'attaque qu'un seul groupe d'humains"""
    for k in range(m):
        problem += pulp.lpSum(M[k,j] for j in range(n)) <= 1

    # Objective
    alpha, beta = 1, 0
    """On optimise le nombre d'alliés par rapport au nombre d'humains"""
    obj_1 = pulp.lpSum(pulp.lpSum(M[i,j] for i in range(m))-h[j][0] for j in range(n))
    """On minimise la distance totale parcourue par les alliés"""
    obj_2 = pulp.lpSum(M[i,j]*D[(i,j)] for i in range(m) for j in range(n))

    problem += alpha*obj_1+beta*obj_2, 'Z'

    # Solve and show results
    problem.solve()
    print(pulp.LpStatus[problem.status])
    for v in problem.variables():
        print(f'Coucou {v.name} = {v.varValue}' )