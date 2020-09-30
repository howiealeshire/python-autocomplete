"""
tkentrycomplete.py

A tkinter widget that features autocompletion.

Created by Mitja Martini on 2008-11-29.
Updated by Russell Adams, 2011/01/24 to support Python 3 and Combobox.
Updated by Dominic Kexel to use tkinter and ttk instead of tkinter and tkinter.ttk
   Licensed same as original (not specified?), or public domain, whichever is less restrictive.
"""
import sys
import tkinter
from tkinter import ttk
from os import listdir, mkdir, system, startfile
from os.path import isfile, join, isdir, basename
from pprint import pprint

import uuid
from shutil import copyfile

__version__ = "1.1"

# I may have broken the unicode...
tkinter_umlauts = ['odiaeresis', 'adiaeresis', 'udiaeresis', 'Odiaeresis', 'Adiaeresis', 'Udiaeresis', 'ssharp']

"""
Requirements:
 *  1.) Autocomplete box (default value "Edmund") (list of potential customers populate (each customer is a directory name), typical autocomplete)
 *  2.) Second input to interface is Print or DWG number, which is in <customer_name>/Prints directory
 *  3.) After selecting the file, program opens up Adobe Acrobat (in full screen)
 *  4.) After closing the PDF viewer, main interface window reappears, remembering the user's selections, and
 *  allows them to keep inputting file selections for Print or DWG Number (though, of course, they should be able to edit the first
 *  field as well, since it seems like a simple enough interface)
"""


class AutocompleteEntry(tkinter.Entry):
    """
        Subclass of tkinter.Entry that features autocompletion.

        To enable autocompletion use set_completion_list(list) to define
        a list of possible strings to hit.
        To cycle through hits use down and up arrow keys.
        """

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)  # Work with a sorted list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)

    def autocomplete(self, delta=0):
        """autocomplete the Entry, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, tkinter.END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):  # Match case-insensitively
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.delete(0, tkinter.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tkinter.END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(tkinter.INSERT), tkinter.END)
            self.position = self.index(tkinter.END)
        if event.keysym == "Left":
            if self.position < self.index(tkinter.END):  # delete the selection
                self.delete(self.position, tkinter.END)
            else:
                self.position = self.position - 1  # delete one character
                self.delete(self.position, tkinter.END)
        if event.keysym == "Right":
            self.position = self.index(tkinter.END)  # go to end (no selection)
        if event.keysym == "Down":
            self.autocomplete(1)  # cycle to next hit
        if event.keysym == "Up":
            self.autocomplete(-1)  # cycle to previous hit
        if len(event.keysym) == 1 or event.keysym in tkinter_umlauts:
            self.autocomplete()


class AutocompleteCombobox(ttk.Combobox):

    def set_completion_list(self, completion_list):
        """Use our completion list as our drop down selection menu, arrows move through menu."""
        self._completion_list = sorted(completion_list, key=str.lower)  # Work with a sorted list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, tkinter.END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):  # Match case insensitively
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.delete(0, tkinter.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tkinter.END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(tkinter.INSERT), tkinter.END)
            self.position = self.index(tkinter.END)
        if event.keysym == "Left":
            if self.position < self.index(tkinter.END):  # delete the selection
                self.delete(self.position, tkinter.END)
            else:
                self.position = self.position - 1  # delete one character
                self.delete(self.position, tkinter.END)
        if event.keysym == "Right":
            self.position = self.index(tkinter.END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion


def test(first_list, customer_names, needle="", needle_second=""):
    """Run a mini application to test the AutocompleteEntry Widget."""
    root = tkinter.Tk(className=' AutocompleteEntry demo')
    entry = AutocompleteEntry(root)
    entry.set_completion_list(customer_names)
    entry.pack()
    entry.focus_set()
    combo = AutocompleteCombobox(root)

    combo.set_completion_list(customer_names)
    combo.pack()
    combo.focus_set()

    needle_index = 0
    if (needle != ""):
        needle_index = first_list.index(needle)

    combo.current(needle_index)

    # ---------------------------

    entry2 = AutocompleteEntry(root)
    entry2.pack()
    entry2.focus_set()
    combo2 = AutocompleteCombobox(root)

    needle_index2 = 0
    if (needle_second != ""):
        needle_index2 = first_list.index(needle)
    if needle_index2 == 0:
        combo2.current()
    else:
        combo2.current(needle_index2)

    def callback(eventObject):
        customer_name_dir = combo.get()
        for elem in first_list:
            if basename(elem) == customer_name_dir:
                customer_name_dir = elem
        customer_name_dir = join(customer_name_dir, "Prints")
        onlyfiles = [f for f in listdir(customer_name_dir) if isfile(join(customer_name_dir, f))]
        combo2.set_completion_list(onlyfiles)
        entry2.set_completion_list(onlyfiles)

    combo2.pack()
    combo2.focus_set()

    def open_btn_callback():
        customer_name_dir = combo.get()
        for elem in first_list:
            if basename(elem) == customer_name_dir:
                customer_name_dir = elem
        customer_name_dir = join(customer_name_dir,"Prints",combo2.get())
        startfile(customer_name_dir)


    open_btn = tkinter.Button(root, text="Open PDF", command=open_btn_callback)
    open_btn.pack()
    # I used a tiling WM with no controls, added a shortcut to quit
    combo.bind("<<ComboboxSelected>>", callback)

    root.bind('<Control-Q>', lambda event=None: root.destroy())
    root.bind('<Control-q>', lambda event=None: root.destroy())



    root.mainloop()


def main():
    file_to_copy = "dummy.pdf"
    customer_names_dir = "AccuCoat Info/Customer Information"
    customer_names = [dI for dI in listdir(customer_names_dir) if isdir(join(customer_names_dir, dI))]
    full_customer_paths = []
    for customer_name in customer_names:
        full_customer_path = join(customer_names_dir, customer_name)
        full_customer_paths.append(full_customer_path)
    #    full_prints_path = join(full_customer_path,"Prints")

    pprint(full_customer_paths)
    test(full_customer_paths, customer_names)


if __name__ == '__main__':
    main()
