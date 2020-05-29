
import pathlib as pathlib
import threading as threading

path_maps = pathlib.Path.cwd() / "Resources" / "maps"
map_list = path_maps.glob('*.txt')

_world = {}
starting_position = (0, 0)

lock = threading.Lock()


def load_tiles():
    """Parses a file that describes the world space into the _world object."""
    for path in map_list:
        _area = {}
        with open(path.resolve().as_posix(), 'r') as f:
            rows = f.readlines()
        x_max = len(rows[0].split('\t')) #assumes all rows contain the same number of tabs
        area = path.stem.split('.')[0]
        for y in range(len(rows)):
            cols = rows[y].split('\t')
            for x in range(x_max):
                tile_name = cols[x].replace('\n', '')
                if tile_name == 'field_glade':
                    global starting_position
                    starting_position = (x, y)
                _area[(x, y)] = None if tile_name == '' else getattr(__import__('tiles'), area)(x, y, area, tile_name)
                _world[area] = _area


def tile_exists(x, y, area):
    with lock:
        area = area.replace(" ", "")
        return _world[area].get((x, y))


def area_rooms(area):
    area = area.replace(" ", "")
    return _world[area]


def area_enemies(area):
    area = area.replace(" ", "")
    all_enemies = []
    all_rooms = area_rooms(area)
    for room in all_rooms:
        if tile_exists(x=room[0], y=room[1], area=area):
            all_enemies.extend(all_rooms[room].enemies)
    return all_enemies


