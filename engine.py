import tcod
import tcod.event
from input_handlers import InputHandler
from render_functions import clear_all, render_all
from map_objects.game_map import GameMap
from entity import Entity

def main():
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'player': tcod.white,
        'npc': tcod.yellow
    }

    player = Entity(int(screen_width / 2), int(screen_height / 2), '@', tcod.white)
    npc = Entity(int(screen_width / 2 - 5), int(screen_height / 2), '@', tcod.yellow)
    entities = [npc, player]

    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(screen_width, screen_height, 'tcod tutorial revised', False)

    con = tcod.console_new(screen_width, screen_height)
    
    game_map = GameMap(map_width, map_height)

    """
    root_console = tcod.console_init_root(80, 60)
    state = State()
    while True:
    tcod.console_flush()
    for event in tcod.event.wait():
        state.dispatch(event)
    """
    state = InputHandler()

    while not tcod.console_is_window_closed():
        #tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)
        for event in tcod.event.get():
            action = state.dispatch(event)
            if action != None:
                cmd, val = action
                if cmd == 'move':
                    dx, dy = val
                    if not game_map.is_blocked(player.x + dx, player.y + dy):
                        player.move(dx, dy)

                if cmd == 'exit':
                    return True

        clear_all(con, entities)
        render_all(con, entities, game_map, screen_width, screen_height, colors)
        tcod.console_flush()
        
if __name__ == '__main__':
    main()