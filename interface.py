

import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.scrolledtext as tkscrolledtext

import world as world
import player as player
import actions as actions
import enemies as enemies
import combat as combat
import npcs as npcs
import objects as objects
import char_gen as character_generator
import tiles as tiles
import skills as skills


class TerminalWindow(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.text_box = tkscrolledtext.ScrolledText(self, width = 120, height = 20)
        self.text_box.pack()

    def print_command(self, text):
        self.text_box.insert("end-1c", text + "\n")
        self.text_box.see(tk.END)

    def print_text(self, text):
        self.text_box.insert("end-1c", text + "\n")
        self.text_box.insert("end-1c", "> ")
        self.text_box.see(tk.END)


class CommandBox(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.user_entry = tk.Entry(self, width=100)
        self.user_entry.pack()
        
    def print_action(self, text):
        self.user_entry.insert("end", text)

class SkillBox(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.parent = parent
        self.skills_window = None

        self.skill_button = tk.Button(self, text="Skills", command=self.change_skills)
        self.skill_button.grid(row=0, column=0)

    def change_skills(self):

        if not self.parent.character_created.get():
            return

        self.skills_window = tk.Toplevel(self.parent)
        skills.Skills(self.skills_window)


class MainApplication(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self.master = master
        self.new = None
        self.load = None
        self.skills_window = None
        self.character_created = tk.BooleanVar(self, value=False)
        self.game_start = tk.BooleanVar(self, value=False)

        self.terminal_window = TerminalWindow(self)
        self.commandbox = CommandBox(self)
        self.skillsbox = SkillBox(self)

        self.terminal_window.grid(row=0, column=0)
        self.commandbox.grid(row=1, column=0)
        self.skillsbox.grid(row=1, column=1)

        player.link_terminal(self.terminal_window)
        actions.link_terminal(self.terminal_window)
        enemies.link_terminal(self.terminal_window)
        combat.link_terminal(self.terminal_window)
        npcs.link_terminal(self.terminal_window)
        objects.link_terminal(self.terminal_window)
        character_generator.link_terminal(self.terminal_window)
        tiles.link_terminal(self.terminal_window)
        skills.link_terminal(self.terminal_window)

        self.splash_screen()
        self.command_index = 0

        self.commandbox.user_entry.bind("<Return>", func=self.game_menu)
        self.commandbox.user_entry.bind("<Up>", func=self.cycle_previous_command)
        self.commandbox.user_entry.bind("<Down>", func=self.cycle_next_command)
        
    def cycle_previous_command(self, event):
        self.command_index += 1
        if self.command_index > len(actions.action_history):
            self.command_index = len(actions.action_history)
        previous_command = actions.action_history[self.command_index - 1]
        self.commandbox.user_entry.delete(0, "end")
        self.commandbox.print_action(previous_command)
        
    def cycle_next_command(self, event):
        self.command_index -= 1
        if self.command_index < 1:
            self.command_index = 0
            self.commandbox.user_entry.delete(0, "end")
            return
        next_command = actions.action_history[self.command_index - 1]
        self.commandbox.user_entry.delete(0, "end")
        self.commandbox.print_action(next_command) 

    def game_menu(self, event):

        if not self.character_created.get():
            entry = self.submit_command()

            if (entry == "New Character") or (entry == "1"):
                self.new_character()
                return

            if (entry == "Load Character") or (entry == "2"):
                self.load_character()
                return

            else:
                self.terminal_window.print_text("That is not a valid entry. Please enter [1] for [New Character] or [2] for [Load Character]")
                return

        if not self.game_start.get():
            entry = self.submit_command()
            self.begin_game()
            self.game_start.set(True)
            return

        if self.game_start.get():
            entry = self.submit_command()

            actions.do_action(action_input=entry, character=player.character)
        
        self.command_index = 0

    def submit_command(self):
        entry = self.commandbox.user_entry.get()
        self.terminal_window.print_command(entry)
        self.commandbox.user_entry.delete(0, "end")
        return entry

    def new_character(self):
        if not self.new:
            self.new = tk.Toplevel(self.master)
            character_generator.CharacterGenerator(self.new, character_created_var=self.character_created)
            self.new.protocol('WM_DELETE_WINDOW',func=lambda: self.character_on_closing(self.new))

    def load_character(self):
        if not self.load:
            self.load = tk.Toplevel(self.master)
            character_generator.CharacterLoader(self.load, character_created_var=self.character_created)
            self.load.protocol('WM_DELETE_WINDOW',func=lambda: self.character_on_closing(self.load))

    def skills_change(self):
        if not self.skills_window:
            self.skills_window = tk.Toplevel(self.master)
            skills.Skills(self.master)

    def begin_game(self):

        if self.new:
            self.new_character_introduction()

        world.load_tiles()

        player.character.room = world.tile_exists(x=player.character.location_x, y=player.character.location_y, area=player.character.area)
        player.character.room.fill_room(character=player.character)
        player.character.room.intro_text()

    def splash_screen(self):
        welcome_screen = """\
        ################################################################
        ####                    Welcome to Dion                     ####
        ################################################################

                                [1] New Character
                                [2] Load Character
        \
        """

        self.terminal_window.print_text(welcome_screen)

    def new_character_introduction(self):
        self.terminal_window.print_text('''\n
    The beast becomes restless...  hungry and tired...

                        ...it trembles with anger, and the earth shakes...

    Far away, you lay in a field surrounded by trees.    
    You close your eyes and an unsettling feeling comes over you. You dread having to go back into town and resume a 
    day you already know is going to be a waste. But you know that people rely on you and your resolve. They trust you,
    at least that's what they say. "{} really knows how to get things done," they would say.

    You open your eyes...
        \
        '''.format(player.character.object_pronoun))

    def character_on_closing(self, _frame):
        if messagebox.askokcancel("Quit", "You don't have your character yet. Do you want to quit?"):
            _frame.destroy()
            _frame = None

    def popupmsg(self, msg):
        self.popup = tk.Tk()
        self.popup.wm_title("Whoops!")
        label = tk.Label(self.popup, text=msg)
        label.pack(side="top", fill="x", pady=10)
        B1 = tk.Button(self.popup, text="Okay", command=self.popup.destroy)
        B1.pack()
        self.popup.mainloop()


if __name__ == "__main__":

    root = tk.Tk()
    app = MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
