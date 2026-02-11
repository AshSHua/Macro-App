import tkinter as tk
from tkinter import ttk
from macro import *
from library import *
from recording import *
from pynput import mouse, keyboard
import os

class GUI:
    '''A simple GUI for this macro app, made with Tkinter.'''

    OUTER_PADDING = 20
    INNER_PADDING = 10

    def __init__(self, macro:ActionManager, library:MacroLibrary, recorder:ActionRecorder):
        '''Takes in the three core classes as parameters for dependency injection.'''

        self.current_macro = macro #This will change dynamically during runtime
        self.library = library
        self.recorder = recorder

        self._settings = self.library.load_settings()

        self._reset_settings()

        self.root = tk.Tk()

        self._setup_root()
        self._setup_saves_widgets()
        self._setup_macro_widgets()

        self._refresh_ui()

        self.root.mainloop()

    def _on_ss_hotkey_detection(self, key):
        if key == self._start_stop_hotkey:
            if self.current_macro.running:
                self._on_stop()
            else:
                self._on_start()

    def _reset_settings(self, start_listener:bool = True):
        if hasattr(self, "_ss_hotkey_listener") and self._ss_hotkey_listener.is_alive():
            self._ss_hotkey_listener.stop()
        self._ss_hotkey_listener = keyboard.Listener(on_press=self._on_ss_hotkey_detection)
        self._start_stop_hotkey = str_to_key(self._settings["start_stop_hotkey"])
        self._ss_hotkey_listener.daemon = True #hotkey listener has to stop when gui is closed
        if start_listener:
            self._ss_hotkey_listener.start()
        else:
            return

    def _setup_root(self):
        root_width = 600
        root_height = 400
        self.root.geometry(f"{root_width}x{root_height}+{(self.root.winfo_screenwidth() - root_width)//2}+{(self.root.winfo_screenheight() - root_height)//2}") #width x height + x_offset + y_offset
        self.root.minsize(width=600, height=400)
        self.root.title("Macro")
        img_path = os.path.join(os.path.dirname(__file__), r"Macro App Icon.png")
        icon = tk.PhotoImage(file=img_path)
        self.root.iconphoto(True, icon)

        self.root_frame = tk.Frame(self.root)
        self.root_frame.rowconfigure(0, weight=1)
        self.root_frame.columnconfigure(0, weight=1)
        self.root_frame.columnconfigure(1, weight=3)
        self.root_frame.columnconfigure(2, weight=3)
        self.root_frame.columnconfigure(3, weight=3)
        self.root_frame.pack(fill="both", expand=True)

    def _setup_saves_widgets(self):
        frame = self.saves_frame = ttk.LabelFrame(self.root_frame, text="Saves", padding=GUI.INNER_PADDING)
        frame.rowconfigure(0, weight=10)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.grid(row=0, column=0, columnspan=1, padx=(GUI.OUTER_PADDING, GUI.OUTER_PADDING/2), pady=GUI.OUTER_PADDING, sticky="nsew")

        self.saves_list = tk.Frame(frame) #frame to hold listbox + scrollbar
        self.saves_list.grid(row=0, column=0, pady=(0, GUI.INNER_PADDING/2), sticky="nsew")

        self.saves_list_lb = tk.Listbox(self.saves_list)
        self.saves_list_sb = tk.Scrollbar(self.saves_list)
        self.saves_list_lb.config(yscrollcommand=self.saves_list_sb.set)
        self.saves_list_lb.bind("<<ListboxSelect>>", self._on_select_save)
        self.saves_list_sb.config(command=self.saves_list_lb.yview)
        self.saves_list_lb.pack(side="left", fill="both", expand=True)
        self.saves_list_sb.pack(side="right", fill="y")
        
        self.load_macro_button = ttk.Button(frame, text="Load Macro", command=self._on_load_macro, takefocus=False)
        self.load_macro_button.grid(row=1, column=0, pady=(GUI.INNER_PADDING/2, GUI.INNER_PADDING/2), sticky="nsew")
        self.load_macro_button.config(state="disabled")

        self.delete_macro_button = ttk.Button(frame, text="Delete Macro", command=self._on_delete_macro)
        self.delete_macro_button.grid(row=2, column=0, pady=(GUI.INNER_PADDING/2, 0), sticky="nsew")
        self.delete_macro_button.config(state="disabled")

    def _setup_macro_widgets(self):
        frame = self.macro_frame = ttk.LabelFrame(self.root_frame, text="Macro", padding=GUI.INNER_PADDING)
        frame.rowconfigure(0, weight=3)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.grid(row=0, column=1, columnspan=3, padx=(GUI.OUTER_PADDING/2, GUI.OUTER_PADDING), pady=GUI.OUTER_PADDING, sticky="nsew")

        self.editor_frame = ttk.LabelFrame(frame, text="Editor", padding=GUI.INNER_PADDING)
        self.editor_frame.rowconfigure(0, weight=2)
        self.editor_frame.rowconfigure(1, weight=2)
        self.editor_frame.rowconfigure(2, weight=1)
        self.editor_frame.columnconfigure(0, weight=1)
        self.editor_frame.columnconfigure(1, weight=4)
        self.editor_frame.columnconfigure(2, weight=4)
        self.editor_frame.grid(row=0, column=0, pady=(0, GUI.INNER_PADDING/2), sticky="nsew")

        self.action_list = tk.Frame(self.editor_frame) #frame to hold listbox + scrollbar
        self.action_list.grid(row=0, column=0, rowspan=2, columnspan=1, padx=(0, GUI.INNER_PADDING/2), pady=(0, GUI.INNER_PADDING/2), sticky="nsew")

        self.action_list_lb = tk.Listbox(self.action_list)
        self.action_list_sb = tk.Scrollbar(self.action_list)
        self.action_list_lb.config(yscrollcommand=self.action_list_sb.set)
        self.action_list_lb.bind("<<ListboxSelect>>", self._on_select_action)
        self.action_list_sb.config(command=self.action_list_lb.yview)
        self.action_list_lb.pack(side="left", fill="both", expand=True)
        self.action_list_sb.pack(side="left", fill="y")

        self.add_action_button = ttk.Button(self.editor_frame, text="Add Action", command=self._on_add_action, takefocus=False)
        self.add_action_button.grid(row=2, column=0, padx=(0, GUI.INNER_PADDING/2), pady=(GUI.INNER_PADDING/2, 0), sticky="nsew")

        self.current_action_display = tk.Frame(self.editor_frame, bd=1, relief="sunken")
        self.current_action_display.rowconfigure(0, weight=1)
        self.current_action_display.rowconfigure(1, weight=1)
        self.current_action_display.rowconfigure(2, weight=1)
        self.current_action_display.rowconfigure(3, weight=1)
        self.current_action_display.rowconfigure(4, weight=1)
        self.current_action_display.columnconfigure(0, weight=1)
        self.current_action_display.grid(row=0, column=1, rowspan=3, columnspan=2, padx=(GUI.INNER_PADDING/2, 0), sticky="nsew")
        self.current_action_display.grid_remove()
        #current action data
        self.current_action_type = ttk.Label(self.current_action_display, text="Type")
        self.current_action_type.grid(row=0, column=0, columnspan=2)

        self.current_action_input = ttk.Label(self.current_action_display, text="Input:")
        self.current_action_input.grid(row=1, column=0, columnspan=2)

        self.current_action_timestamp = ttk.Label(self.current_action_display, text="Timestamp:")
        self.current_action_timestamp.grid(row=2, column=0, columnspan=2)

        self.current_action_location = ttk.Label(self.current_action_display, text="Location:")
        self.current_action_location.grid(row=3, column=0, columnspan=2)

        self.delete_action_btn = ttk.Button(self.current_action_display, text="Delete Action", command=self._on_delete_action, takefocus=False)
        self.delete_action_btn.grid(row=4, column=0, padx=2, pady=2, sticky="nsew")

        self.misc_buttons_frame = tk.Frame(frame)
        self.misc_buttons_frame.rowconfigure(0, weight=1)
        self.misc_buttons_frame.rowconfigure(1, weight=1)
        self.misc_buttons_frame.columnconfigure(0, weight=1)
        self.misc_buttons_frame.columnconfigure(1, weight=1)
        self.misc_buttons_frame.columnconfigure(2, weight=1)
        self.misc_buttons_frame.grid(row=1, column=0, rowspan=1, pady=(GUI.INNER_PADDING/2, 0), sticky="nsew")

        self.start_button = ttk.Button(self.misc_buttons_frame, text=f"Start ({key_to_str(self._start_stop_hotkey)})", command=self._on_start, takefocus=False)
        self.start_button.grid(row=0, column=0, sticky="nsew")

        self.stop_button = ttk.Button(self.misc_buttons_frame, text=f"Stop ({key_to_str(self._start_stop_hotkey)})", command=self._on_stop, takefocus=False)
        self.stop_button.grid(row=0, column=1, sticky="nsew")

        self.loop_state = tk.BooleanVar(self.root_frame, value=False)
        self.looping_check_btn = ttk.Checkbutton(self.misc_buttons_frame, text="Loop", variable=self.loop_state)
        self.looping_check_btn.grid(row=0, column=2)

        self.save_macro_button = ttk.Button(self.misc_buttons_frame, text="Save Macro", command=self._on_save_macro, takefocus=False)
        self.save_macro_button.grid(row=1, column=0, sticky="nsew")

        self.record_button = ttk.Button(self.misc_buttons_frame, text="Record", command=self._on_record, takefocus=False)
        self.record_button.grid(row=1, column=2, sticky="nsew")

        self.hotkey_settings_btn = ttk.Button(self.misc_buttons_frame, text="Hotkey Settings", command=self._on_hotkey_settings, takefocus=False)
        self.hotkey_settings_btn.grid(row=1, column=1, sticky="nsew")

    def _update_btn_state(self):
        '''Examines and updates states of buttons that are dependent on internal state.'''
        if not self.saves_list_lb.curselection():
            self.load_macro_button.config(state="disabled")
            self.delete_macro_button.config(state="disabled")
        else:
            self.load_macro_button.config(state="normal")
            self.delete_macro_button.config(state="normal")

        if not self.action_list_lb.curselection():
            self.current_action_display.grid_remove()
        else:
            self.action_list.grid()

        if self.current_macro.running:
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

        self.start_button.config(text=f"Start ({key_to_str(self._start_stop_hotkey)})")
        self.stop_button.config(text=f"Stop ({key_to_str(self._start_stop_hotkey)})")

    def _clear_lb_selections(self):
        '''Clears the listboxes' selections and sets related attributes to None.'''
        self.saves_list_lb.selection_clear(0, tk.END)
        self.selected_macro_save = None
        self.action_list_lb.selection_clear(0, tk.END)
        self.selected_action = None
        self.selected_action_data = None
    
    def _populate_save_list(self):
        self.saves_list_lb.delete(0, tk.END)
        for macro in self.library.index.keys():
            self.saves_list_lb.insert(tk.END, macro)

    def _on_select_save(self, event=None):
        selection = self.saves_list_lb.curselection()
        if selection:
            save = self.saves_list_lb.get(int(selection[0]))
            self.selected_macro_save = ActionManager(self.library.retrieve_macro(save))
        self._update_btn_state()

    def _open_confirm_toplevel(self) -> bool:
        '''When called, opens a confirmation_window. Returns True if confirmation was given, and False if not.'''
        result = None

        top_width, top_height = 150, 50
        pos_x, pos_y = (self.root.winfo_x() + (self.root.winfo_width() - top_width)//2), (self.root.winfo_y() + (self.root.winfo_height() - top_height)//2)

        confirmation_window = tk.Toplevel(self.root)
        confirmation_window.title("Confirmation")
        confirmation_window.grab_set()
        confirmation_window.transient(self.root)
        confirmation_window.geometry(f"{top_width}x{top_height}+{pos_x}+{pos_y}")
        confirmation_window.resizable(False, False)

        def set_result(value:bool):
            nonlocal result
            result = value
            confirmation_window.destroy()

        ays = ttk.Label(confirmation_window, text="Are you sure?")
        yes_btn = ttk.Button(confirmation_window, text="Yes", command=lambda: set_result(True), takefocus=False)
        no_btn = ttk.Button(confirmation_window, text="No", command=lambda: set_result(False), takefocus=False)

        ays.pack(side="top")
        yes_btn.pack(side="left")
        no_btn.pack(side="right")

        self.root.wait_window(confirmation_window)
        return result
    
    def _on_load_macro(self):
        if not self._open_confirm_toplevel():
            return
        if self.selected_macro_save:
            self.current_macro = self.selected_macro_save
            self.selected_macro_save = None
            self._clear_lb_selections()
            self._refresh_ui()
    
    def _on_delete_macro(self):
        if not self._open_confirm_toplevel():
            return
        selection = self.saves_list_lb.curselection()
        if selection:
            save = self.saves_list_lb.get(int(selection[0]))
            try:
                self.library.delete_macro(save)
                self.saves_list_lb.delete(int(selection[0]))
                self._clear_lb_selections()
                self._refresh_ui()
            except:
                return
            
    def _populate_action_list(self):
        self.action_list_lb.delete(0, tk.END)
        for action in self.current_macro.save:
            action_data = action.to_dict()
            action_desc = f'{action_data["type"]} - {action_data["input"]}'
            self.action_list_lb.insert(tk.END, action_desc)

    def _on_select_action(self, event=None):
        selection = self.action_list_lb.curselection()
        if selection:
            self.current_action_display.grid()
            action = self.current_macro.save[int(selection[0])]
            self.selected_action = action
            self.selected_action_data = self.selected_action.to_dict()  
            self._populate_action_display() 

    def _populate_action_display(self):
        if not hasattr(self, "selected_action") or self.selected_action is None:
            return
        self.current_action_type.config(text=f'Type: {self.selected_action_data["type"]}')
        self.current_action_input.config(text=f'Input: {self.selected_action_data["input"]}')
        self.current_action_timestamp.config(text=f'Timestamp: {round(self.selected_action_data["timestamp"], 3)}')
        self.current_action_location.config(text=f'Location: {self.selected_action_data["location"]}')

    def _open_action_toplevel(self) -> Action:
        '''Creates a toplevel window where you can manually create an Action and return it upon closing.'''
        recorder = self.recorder

        return_result = False
        action_reflection = Action(type=None, input=None, timestamp="0", location=None).to_dict()

        top_width, top_height = 250, 150
        pos_x, pos_y = (self.root.winfo_x() + (self.root.winfo_width() - top_width)//2), (self.root.winfo_y() + (self.root.winfo_height() - top_height)//2)
        editor = tk.Toplevel(self.root)
        editor.title("Action Editor")
        editor.grab_set()
        editor.transient(self.root)
        editor.geometry(f"{top_width}x{top_height}+{pos_x}+{pos_y}")
        editor.minsize(top_width, top_height)

        def on_type_switch():
            match action_reflection["type"]:
                case "key_down":
                    action_reflection["type"] = "key_up"
                case "key_up":
                    action_reflection["type"] = "key_down"
                case "mouse_down":
                    action_reflection["type"] = "mouse_up"
                case "mouse_up":
                    action_reflection["type"] = "mouse_down"
                case _:
                    return
            type_display.config(text=f"Type: {action_reflection["type"]}")     
            
        def on_timestamp_change(*args):
            try:
                selection = float(timestamp_var.get())
                action_reflection["timestamp"] = selection
            except ValueError:
                timestamp_var.set("") 

        def on_capture():
            nonlocal action_reflection
            action_reflection = None
            action_reflection = recorder.capture().to_dict()

            type_display.config(text=f"Type: {action_reflection["type"]}")
            input_display.config(text=f"Input: {action_reflection["input"]}")
            timestamp_var.set(str(round(action_reflection["timestamp"], 3)))
            location_display.config(text=f"Location: {action_reflection["location"]}")

            return

        def on_add_action():
            nonlocal return_result
            return_result = True
            editor.destroy()

        def on_discard_action():
            nonlocal return_result
            return_result = False
            editor.destroy()

        editor.rowconfigure(0, weight=1)
        editor.rowconfigure(1, weight=1)
        editor.rowconfigure(2, weight=1)
        editor.rowconfigure(3, weight=1)
        editor.rowconfigure(4, weight=1)
        editor.rowconfigure(5, weight=1)
        editor.columnconfigure(0, weight=1)
        editor.columnconfigure(1, weight=1)

        type_display = ttk.Label(editor, text="Type:")
        type_display.grid(row=0, column=0, sticky="nsew")
        type_flip_btn = ttk.Button(editor, text="Switch Type", command=on_type_switch, takefocus=False)
        type_flip_btn.grid(row=0, column=1, sticky="nsew")

        input_display = ttk.Label(editor, text="Input:")
        input_display.grid(row=1, column=0, columnspan=2, sticky="nsew")

        timestamp_frame = tk.Frame(editor)
        timestamp_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        timestamp_label = tk.Label(timestamp_frame, text="Timestamp: ")
        timestamp_label.pack(side="left")
        timestamp_var = tk.StringVar(editor)
        timestamp_var.set("0")
        timestamp_var.trace_add("write", on_timestamp_change)
        timestamp_entry = tk.Entry(timestamp_frame, textvariable=timestamp_var)
        timestamp_entry.pack(side="right", fill="x", expand=True)

        location_display = ttk.Label(editor, text="Location:")
        location_display.grid(row=3, column=0, columnspan=2, sticky="nsew")

        capture_action_btn = ttk.Button(editor, text="Capture", command=on_capture, takefocus=False)
        capture_action_btn.grid(row=4, column=0, columnspan=2, sticky="nsew")

        add_action_btn = ttk.Button(editor, text="Add Action", command=on_add_action, takefocus=False)
        add_action_btn.grid(row=5, column=0, sticky="nsew")

        discard_action_btn = ttk.Button(editor, text="Discard Action", command=on_discard_action, takefocus=False)
        discard_action_btn.grid(row=5, column=1, sticky="nsew")

        self.root.wait_window(editor)
        
        if return_result:
            return Action.from_dict(action_reflection)
        else:
            return

    def _on_add_action(self):
        action = self._open_action_toplevel()
        #validation
        if not isinstance(action, Action):
            return
        if action.type is None or action.input is None or action.timestamp < 0:
            print("Invalid action.")
            return
        try:
            self.current_macro.add_action(action)
            self._refresh_ui()
        except AttributeError: #attribute error because current_macro.add_action accesses Action's timestamp
            return
    
    def _on_delete_action(self):
        if not self._open_confirm_toplevel():
            return
        self.current_macro.remove_action(self.selected_action)
        self.selected_action = None
        self.selected_action_data = None
        self._refresh_ui()
    
    def _on_start(self):
        if hasattr(self, "current_macro") and self.current_macro is not None:
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

            if self.loop_state.get():
                self.current_macro.looping = True
            else:
                self.current_macro.looping = False

            self.current_macro.start()
            self.root.after(100, self._check_macro_state)

    def _check_macro_state(self): #helper to _on_start()
        '''Checks if the macro is currently running. If it is, poll again. If not, resets button state.'''
        if not self.current_macro.running:
            self._update_btn_state()
        else:
            self.root.after(100, self._check_macro_state)
    
    def _on_stop(self):
        if hasattr(self, "current_macro") and self.current_macro is not None:
            self.current_macro.stop()

    def _on_save_macro(self):
        if not hasattr(self, "current_macro") or self.current_macro is None:
            return
        
        name = None
        overwrite_existing = False
        
        top_width, top_height = 250, 125
        pos_x, pos_y = (self.root.winfo_x() + (self.root.winfo_width() - top_width)//2), (self.root.winfo_y() + (self.root.winfo_height() - top_height)//2)
        
        save_window = tk.Toplevel(self.root)
        save_window.title("Save")
        save_window.grab_set()
        save_window.transient(self.root)
        save_window.geometry(f"{top_width}x{top_height}+{pos_x}+{pos_y}")
        save_window.resizable(False, False)

        def confirm_save():
            nonlocal name, overwrite_existing, save_window, name_var
            name = name_var.get()
            try:
                self.library.validate_name(name)
            except ValueError:
                name_var.set("Invalid Name")
                save_window.after(1000, lambda: name_var.set(""))
                return
            if self.library.index_collision(name=name):
                overwrite_existing = open_overwrite()
                save_window.destroy()
            save_window.destroy()
            
        def open_overwrite() -> bool:
            #If True is returned, that means save overwrite is confirmed. If False, then don't overwrite.
            nonlocal name, save_window

            overwrite = False

            top_width, top_height = 200, 75
            pos_x, pos_y = (self.root.winfo_x() + (self.root.winfo_width() - top_width)//2), (self.root.winfo_y() + (self.root.winfo_height() - top_height)//2)

            overwrite_window = tk.Toplevel(save_window)
            overwrite_window.title("Overwrite")
            overwrite_window.grab_set()
            overwrite_window.transient(save_window)
            overwrite_window.geometry(f"{top_width}x{top_height}+{pos_x}+{pos_y}")
            overwrite_window.resizable(False, False)

            def set_overwrite(value:bool):
                nonlocal overwrite, overwrite_window
                overwrite = value
                overwrite_window.destroy()

            message = ttk.Label(overwrite_window, text=f"Name: {name} is taken, overwrite?")
            message.pack(side="top")

            yes_btn = ttk.Button(overwrite_window, text="Yes", command=lambda: set_overwrite(True), takefocus=False)
            yes_btn.pack(side="left")

            no_btn = ttk.Button(overwrite_window, text="No", command=lambda: set_overwrite(False), takefocus=False)
            no_btn.pack(side="right")

            save_window.wait_window(overwrite_window)
            return overwrite
        
        name_restrictions = ttk.Label(save_window, text="Name can only contain letters,\nnumbers, underscores, and hyphens.\nName must be between 1 and 20\ncharacters long.") #newline to make it fit
        name_restrictions.pack(side="top")

        name_var = tk.StringVar(save_window)
        name_entry = ttk.Entry(save_window, textvariable=name_var)
        name_entry.pack(side="left", expand=True)

        confirm_button = ttk.Button(save_window, text="Confirm", command=confirm_save, takefocus=False)
        confirm_button.pack(side="right", expand=True)

        self.root.wait_window(save_window)
        try:
            self.library.save_macro(macro=self.current_macro, name=name, overwrite=overwrite_existing)
        except ValueError:
            return
        self._refresh_ui()
        return

    def _on_record(self):
        recorded_macro = ActionManager()

        top_width, top_height = 200, 100
        pos_x, pos_y = (self.root.winfo_x() + (self.root.winfo_width() - top_width)//2), (self.root.winfo_y() + (self.root.winfo_height() - top_height)//2)

        record_window = tk.Toplevel(self.root)
        record_window.title("Record")
        record_window.grab_set()
        record_window.transient(self.root)
        record_window.geometry(f"{top_width}x{top_height}+{pos_x}+{pos_y}")
        record_window.resizable(False, False)

        record_window.rowconfigure(0, weight=1)
        record_window.rowconfigure(1, weight=1)
        record_window.columnconfigure(0, weight=1)
        record_window.columnconfigure(1, weight=1)

        def start_recording():
            nonlocal start_record_btn, stop_record_btn, recorded_macro
            start_record_btn.config(state="disabled")
            stop_record_btn.config(state="normal")
            self.recorder.start_record()

        def stop_recording():
            nonlocal start_record_btn, stop_record_btn, recorded_macro
            start_record_btn.config(state="normal")
            stop_record_btn.config(state="disabled")
            self.recorder.stop_record()
            recorded_macro = ActionManager(self.recorder.retrieve_record())

        def confirm():
            record_window.destroy()

        start_record_btn = ttk.Button(record_window, text="Start", command=start_recording, takefocus=False)
        start_record_btn.grid(row=0, column=0, sticky="nsew")

        stop_record_btn = ttk.Button(record_window, text="Stop", command=stop_recording, takefocus=False)
        stop_record_btn.config(state="disabled")
        stop_record_btn.grid(row=0, column=1, sticky="nsew")

        confirm_btn = ttk.Button(record_window, text="Confirm", command=confirm, takefocus=False)
        confirm_btn.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.root.wait_window(record_window)

        self.current_macro = recorded_macro
        self._refresh_ui()
    
    def _on_hotkey_settings(self):
        self._reset_settings(False) #prevents listener from activating when setting the hotkey

        hotkey = self._start_stop_hotkey

        top_width, top_height = 200, 100
        pos_x, pos_y = (self.root.winfo_x() + (self.root.winfo_width() - top_width)//2), (self.root.winfo_y() + (self.root.winfo_height() - top_height)//2)

        settings_window = tk.Toplevel(self.root)
        settings_window.title("Hotkey Settings")
        settings_window.grab_set()
        settings_window.transient(self.root)
        settings_window.geometry(f"{top_width}x{top_height}+{pos_x}+{pos_y}")
        settings_window.resizable(False, False)

        settings_window.rowconfigure(0, weight=1)
        settings_window.rowconfigure(1, weight=1)
        settings_window.columnconfigure(0, weight=1)
        settings_window.columnconfigure(1, weight=1)

        def change_hotkey():
            nonlocal hotkey
            hotkey = self.recorder.capture(mode="keyboard").input
            htky_var.set(key_to_str(hotkey))

        def save_htky():
            nonlocal hotkey
            self.library.save_settings({"start_stop_hotkey": key_to_str(hotkey)})
            self._settings = self.library.load_settings()
            self._reset_settings()
            self._refresh_ui()
            settings_window.destroy()
        
        def cancel():
            settings_window.destroy()

        start_stop_htky_btn = ttk.Button(settings_window, text="Start/Stop", command=change_hotkey, takefocus=False)
        start_stop_htky_btn.grid(row=0, column=0, sticky="nsew")

        htky_var = tk.StringVar(settings_window)
        htky_var.set(key_to_str(self._start_stop_hotkey))
        current_htky_display = ttk.Label(settings_window, textvariable=htky_var)
        current_htky_display.grid(row=0, column=1)

        save_btn = ttk.Button(settings_window, text="Save", command=save_htky, takefocus=False)
        save_btn.grid(row=1, column=0, sticky="nsew")

        cancel_btn = ttk.Button(settings_window, text="Cancel", command=cancel, takefocus=False)
        cancel_btn.grid(row=1, column=1, sticky="nsew")

        self.root.wait_window(settings_window)

    def _refresh_ui(self):
        '''Calls all functions that (meaningfully) update the ui. Note: can be slow if lots of changes occur.'''
        self._populate_save_list()
        self._populate_action_list()
        self._populate_action_display()
        self._update_btn_state()