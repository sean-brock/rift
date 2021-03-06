"""userinterface

Provides a user interface base class and specific gameplay interfaces/menus.
"""

from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
from bearlibterminal import terminal
from engine.game import Game
from engine.settings import Settings

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

class UserInterface(ABC):
    """Base class for defining UI elements in a tree structure."""
    def __init__(self, width: int, height: int,  parent, x: int = 0, y: int = 0):
        """UI arguments:

        width: max UI container width.
        height: max UI container height.
        parent: Parent UI reference or None if top.
        x, y: relative origin (in UI parent).
        """
        self._width = width
        self._height = height
        self._parent = parent
        self._children = []
        self._x = x
        self._y = y

    @property
    def parent(self):
        """Returns parent UI."""
        return self._parent

    @property
    def children(self):
        """Returns list of children UI."""
        return self._children

    @property
    def origin(self):
        """Origin of the UI object as (x, y)."""
        return (self._x, self._y)
    @property
    def size(self):
        """Size of the UI as (width, height)."""
        return (self._width, self._height)

    @abstractmethod
    def _render(self, offset: (int, int) = (0,0)):
        """Renders the UI object. Each subclass will define a separate render method."""
        pass

    def render(self, offset: (int, int) = (0,0)):
        """Renders the UI object and all children. Therefore, only the top UI must be 'rendered.'"""
        self._render(offset)
        for child in self._children:
            # add the origin of the parent as the offset of the child render.
            x, y = offset
            child_offset = (x+self._x, y+self._y)
            child.render(child_offset)

class Interactable(ABC):
    """Base class defining a set of UI interaction methods."""
    def __init__(self):
        self._active = False
    
    @property
    def active(self) -> bool:
        """Returns if Interactable is active."""
        return self._active
    
    def toggle(self):
        """Toggles active status of Interactable."""
        self._active = not self._active

    # Interactions. Should return None or (Statetransition, State) tuple.
    @abstractmethod
    def previous(self):
        """Activates the previous sibling in the sibling list."""
        pass

    @abstractmethod
    def next(self):
        """Activates the next sibling in the sibling list."""
        pass

    @abstractmethod
    def select(self):
        """Activates the interactable, may descend to a child."""
        pass

    @abstractmethod
    def back(self):
        """Activates the parent."""
        pass

# Interactable and UI activation methods.

def activate_parent(ui: UserInterface):
    """Searches and, if found, activates a higher UI Interactable and deactivates the input UI Interactable."""
    if ui.parent is not None:
        if isinstance(ui.parent, Interactable):
            # Found interactable parent, activate it.
            ui.parent.toggle()
            ui.toggle()
            return True
        else:
            # Keep ascending
            return activate_parent(ui.parent)
    return False

def activate_previous_child(ui: UserInterface):
    """Toggles the current active child and activates the previous."""
    for i in range(len(ui.children)):
        if isinstance(ui.children[i], Interactable):
            if ui.children[i].active:
                # If the current child is active, toggle it and the previous one
                if i-1 >= 0:
                    if isinstance(ui.children[i-1], Interactable):
                        ui.children[i].toggle()
                        ui.children[i-1].toggle()
                break

def activate_next_child(ui: UserInterface):
    """Toggles the current active child and activates the next."""
    for i in range(len(ui.children)):
        if isinstance(ui.children[i], Interactable):
            if ui.children[i].active:
                # If the current child is active, toggle it and the next one
                if i+1 < len(ui._children):
                    if isinstance(ui.children[i+1], Interactable):
                        ui.children[i].toggle()
                        ui.children[i+1].toggle()
                break  

def find_active(ui: UserInterface) -> UserInterface:
    """Searches and finds the active UI Interactable."""
    # DFS
    for child in ui.children:
        if isinstance(child, Interactable) and child.active:
            return child
        descend_result = find_active(child)
        if descend_result is not None:
            return descend_result
    return None

# Generic UI items

class Highlight(Enum):
    COLOR = 0
    INVERT = 1
    ASTERISK = 1
    DASH = 2

class HorizAlignment(Enum):
    CENTER = terminal.TK_ALIGN_CENTER
    LEFT = terminal.TK_ALIGN_LEFT
    RIGHT = terminal.TK_ALIGN_RIGHT

class VertAlignment(Enum):
    CENTER = terminal.TK_ALIGN_MIDDLE
    TOP = terminal.TK_ALIGN_TOP
    BOTTOM = terminal.TK_ALIGN_BOTTOM

class Selector(UserInterface, Interactable):
    def __init__(self, text: str, width: int, height: int, parent: UserInterface, action: object,
        x: int = 0, y: int = 0, mode: Highlight = Highlight.COLOR, 
        horiz_align: HorizAlignment = HorizAlignment.LEFT,
        vert_align: VertAlignment = VertAlignment.CENTER):

        UserInterface.__init__(self, width, height, parent, x, y)
        Interactable.__init__(self)

        self._text = text
        self._mode = mode
        self._horiz_align = horiz_align
        self._vert_align = vert_align
        self._action = action

    def _render(self, offset: (int, int) = (0, 0)):
        """Renders the text of the selector."""
        sets = Settings()

        # Position
        x, y = offset
        x += self._x
        y += self._y

        # Text and color
        text = self._text
        fg = sets.colors['default_fg']
        bg = sets.colors['default_bg']

        # Active highlight
        if self.active:
            if self._mode == Highlight.INVERT:
                bg = sets.colors['default_fg']
                fg = sets.colors['default_bg']
            elif self._mode == Highlight.COLOR:
                fg = sets.colors['highlight_fg']
            elif self._mode == Highlight.ASTERISK:
                text = "* "+text
            elif self._mode == Highlight.DASH:
                text = "- "+text

        #console.print(x+self._x, y+self._y, self._text, fg=sets.colors['default_fg'], bg=sets.colors['default_bg'], alignment=self._align)
        # BearLibTerm print
        terminal.color(fg)
        terminal.bkcolor(bg)
        terminal.puts(x, y, text, *self.size, self._horiz_align.value + self._vert_align.value)
    
    def previous(self):
        """Activates the previous sibling in the sibling list."""
        activate_previous_child(self._parent)
        return None

    def next(self):
        """Activates the next sibling in the sibling list."""
        activate_next_child(self._parent)
        return None

    def select(self):
        """Performs the action of the selector."""
        return self._action()

    def back(self):
        """Activates the an interactable up the hierarchy if it exists."""
        activate_parent(self)
        return None

class Text(UserInterface):
    def __init__(self, text: str, color: (int, int, int), width: int, height: int,  parent: UserInterface, 
        x: int = 0, y: int = 0, 
        horiz_align: HorizAlignment = HorizAlignment.LEFT,
        vert_align: VertAlignment = VertAlignment.CENTER):

        super().__init__(width, height, parent, x=x, y=y)
        self._text = text
        self._color = color
        self._horiz_align = horiz_align
        self._vert_align = vert_align

    def _render(self, offset: (int, int) = (0, 0)):
        sets = Settings()

        # Position
        x, y = offset
        x += self._x
        y += self._y

        # Text and color
        fg = sets.colors['default_fg']
        bg = sets.colors['default_bg']

        #console.print(x+self._x, y+self._y, self._text, fg=self._color, bg=sets.colors['default_bg'], alignment=self._align)
        # BearLibTerm print
        terminal.color(fg)
        terminal.bkcolor(bg)
        terminal.puts(x, y, self._text, *self.size, self._horiz_align.value + self._vert_align.value)


