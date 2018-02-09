from grid.grid import Grid


def get_distance(srce, dest):
    return abs(dest[0] - srce[0]) + abs(dest[1] - srce[1])

def get_closest_point(grid, srce, dest, avoid_enemies=False):
    if avoid_enemies:
        offsets = Grid.get_closest_points(srce,dest)
        idx = 0
        while (([srce[0] + offsets[idx][0], srce[1] + offsets[idx][1]] not in grid.get_range(srce)
               or [srce[0] + offsets[idx][0], srce[1] + offsets[idx][1]] in grid.get_enemy_range())
                and  idx < len(offsets)-1):
            idx += 1
        return srce[0] + offsets[idx][0], srce[1] + offsets[idx][1]
    else:
        if srce[0] < dest[0]:
            return srce[0] + 1, srce[1]
        elif srce[0] > dest[0]:
            return srce[0] - 1, srce[1]
        elif srce[1] < dest[1]:
            return srce[0], srce[1] + 1
        else:
            return srce[0], srce[1] - 1