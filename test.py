








# region Character Generator
# import tkinter as tk
# import char_gen as character_generator
# import interface as interface
# 
# 
# if __name__ == "__main__":
# 
#     root = tk.Tk()
#     app = character_generator.CharacterGenerator(root)
#     root.mainloop()
# endregion

# region Items 
# import items as items
#  
# item = items.create_item(item_category='clothing', item_name='a simple shirt')
# print(item)
# endregion

# region Object
# import objects as objects
# 
# object = objects.create_object(object_category='door', object_name='dochas_south_gate', room='the room')
# print(object)
# endregion


# region Player
# import player as player
# import world as world
# 
# world.load_tiles()
# character = player.Player(player_name='new_player')
# print(character)
# endregion


# region Combat
import player as player
import world as world
import combat as combat

world.load_tiles()
character = player.Player(player_name='new_player')

defense_strength = combat.calculate_defense_strength(character)
print(defense_strength)

# endregion


