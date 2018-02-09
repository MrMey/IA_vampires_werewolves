humans = {(1, 1): 6, (2, 5): 2, (5, 2): 1}
allies = {(2, 3): 3, (5, 5): 3, (2, 1): 1}
enemies = {(2, 4): 12, (2, 4): 1}
group = (2, 3)

# quelques remarques générales:

# 1. Les fusion possibles sont "prise en compte" c'est à dire que pour fuire un groupe un peu plus grand que nous
# on peut tenter de fusioner avec un groupe proche suffisament grand. Néanmoins, l'autre groupe ne doit pas bouger
# pour cela, ce qui n'est pas prévu par ce code car les groupes sont traités ici indépendemment

# 2. Comme les groupes sont traités indépendemment, deux groupes riquent d'attaquer le même groupe d'humain ou d'enemis

# 3. Il n'y a pour le moment pas séparation de groupe de faite, ça peut être une quatrième stratégie à implémenter

# 4. J'ai mis des erreurs pour find_closest à rattraper!!

# 5. Attention il peut y avoir des doublons en fonction des stratégies


def best_next_move_for_strategy(strategy, group):
    # getting the imediate context of the group
    just_around = {"humans":[], "enemies":[], "allies":[]}
    i = group[0]
    j = group[1]
    for h in humans:
        if (h[0]==i-1 or h[0]==i or h[0]==i+1) and (h[1]==j-1 or h[1]==j or h[1]==j+1):
            just_around["humans"].append(h)
    for e in enemies:
        if (e[0]==i-1 or e[0]==i or e[0]==i+1) and (e[1]==j-1 or e[1]==j or e[1]==j+1):
            just_around["enemies"].append(e)
    for a in allies:
        if (a[0] == i - 1 or a[0] == i or a[0] == i + 1) and (a[1] == j - 1 or a[1] == j or a[1] == j + 1):
            just_around["allies"].append(a)

    # best move depending of the strategy
    if strategy == "convert":
        # si il y a des humains juste à côté, on les convertit en priorité, si ça ne nous occasionne pas de perte
        if len(just_around["humans"]) > 0:
            best = (None, 0)
            for h in range(len(just_around["humans"])):
                if humans[just_around["humans"][h]] > best[1] and humans[just_around["humans"][h]] < allies[group]:
                    best = (humans[just_around["humans"][h]], humans[just_around["humans"][h]])
            if not best[0]is None:
                return best[0] # la maison juste à côté avec le meilleur potentiel
        # si il n'y a pas d'humains autour, ou en trop grand nombre, on cherche une maison plus loin
        target = find_closest(group, humans, 1, 3)
        moves = []
        for t in target:
            # trouve la direction à prendre...
            i_new = group[0]
            j_new = group[1]
            if t[0] > i:
                i_new = i+1
            elif t[0]<i:
                i_new = i-1
            if t[1] > j:
                j_new = j+1
            elif t[1]<i:
                j_new = j-1
            # vérifie qu'il n'y a pas d'obstacles
            # on suppose qu'un groupe allié sur le chemin ne pose pas de problème, car soit il bouge, soit il fusionne
            if (i_new,j_new) in just_around["enemies"]:
                # si l'enemi est faible, on le "mange" au passage
                # pas la peine de répéter
                # si l'enemi est moyen -> on l'évite
                # si l'enemi est fort -> on abandonne d'aller convertir la maison dans cette direction
                # car un déplacement vers elle nous ferait tuer le groupe
                if enemies[(i_new,j_new)] * 1.5 < allies[group]:
                    moves.append((i_new,j_new))
                elif enemies[(i_new,j_new)] <  1.5 * allies[group] < 1.5 * 1.5 *enemies[(i_new,j_new)]:
                    (i1, j1, i2, j2) =  try_avoiding(i, j, i_new, j_new)
                    if not((i1, j1) in just_around["humans"]):
                        if (i1, j1) in just_around["enemies"]:
                            if enemies[(i1, j1)] *1.5 < allies[group]:
                                moves.append((i1, j1))
                        else:
                            moves.append((i1, j1))
                    if not((i2, j2) in just_around["humans"]):
                        if (i2, j2) in just_around["enemies"]:
                            if enemies[(i2, j2)] *1.5 < allies[group]:
                                moves.append((i2, j2))
                        else:
                            moves.append((i1, j1))
            elif (i_new,j_new) in just_around["humans"]:
                # le groupe d'humain est forcément trop grand pour être converti,
                # sinon le résultat aurait déjà été renvoyé
                (i1, j1, i2, j2) = try_avoiding(i, j, i_new, j_new)
                if not (i1, j1) in just_around["humans"]:
                    moves.append(i1, j1)
                if not (i2, j2) in just_around["humans"]:
                    moves.append(i2, j2)
            else:
                moves.append((i_new, j_new))
    elif strategy == "attack":
        target = find_closest(group, enemies, 1.5, 3)
    elif strategy == "flee":
        to_avoid = find_closest(group, enemies, 0.3, 3)
        possible_merge = find_closest(group, allies, 0, 2)
    else:
        raise Exception("unknown strategy, please implement it")


def find_closest(group, category, rate, max_return):
    """
    renvoie la liste des max_return plus proches cases correspondant à des groupes de catégory, en
    evitant les confrontations qui ne mènent pas à la victoire de façon certaine"""
    if category.isempty():
        raise Exception ("nothing to go after")
    best_choice = []
    for loc, nb in category.items():
        distance = max(loc[0] - group[0], loc[1] - group[1])
        if rate * nb < allies[group] :  # bataille que l'on peut gagner
            best_choice.append(loc)
            if len(best_choice)> max_return:
                m = len(best_choice)
                for i in range(best_choice):
                    if max(best_choice[i][0] - group[0] , best_choice[i][1] - group[1])>distance:
                        distance = max(best_choice[i][0] - group[0], best_choice[i][1] - group[1])
                        m = i
                best_choice.pop(m)
    return best_choice

def try_avoiding(i, j, i_new, j_new):
    if i == i_new:
        return (i+1, j, i-1, j)
    elif j == j_new:
        return (i, j+1, i, j-1)
    return (i, j_new, i_new, j)

