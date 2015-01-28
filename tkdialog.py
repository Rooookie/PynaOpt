__author__ = 'Yisu Nie'
import os
import sys
# Use Tkinter for python 2, tkinter for python 3
if sys.version_info[0] < 3:
    import Tkinter as Tk 
else:
    import tkinter as Tk
    

class Dialog(Tk.Toplevel):

    def __init__(self, parent, *args, **kwargs):

        Tk.Toplevel.__init__(self, parent, *args, **kwargs)
        
        self.transient(parent)
        self.parent = parent
        self.result = None

        body = Tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.construct_body()
        self.construct_button()

        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.cancel_action)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    
    #: construction hooks

    def construct_body(self):
        """Create dialog body.  Return widget that should have
        initial focus. This method should be overridden.
        """
        pass

    def construct_button(self):
        """Add standard button box. override if you don't want the
        standard buttons
        """
        box = Tk.Frame(self)

        button_yes = Tk.Button(box, text="OK", width=10, command=self.ok_action)
        button_yes.pack(side='left', padx=5, pady=5)
        button_no = Tk.Button(box, text="Cancel", width=10, command=self.cancel_action)
        button_no.pack(side='left', padx=5, pady=5)

        self.bind("<Return>", self.ok_action)
        self.bind("<Escape>", self.cancel_action)

        box.pack()

    
    #: standard button semantics

    def ok_action(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel_action()

    def cancel_action(self, event=None):

        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    
    #: command hooks

    def validate(self):

        return True # override

    def apply(self):

        pass # override
