palette.update({
    "source": (add_setting("black", "bold"), "black"),
        "header": ("black", "light gray", "standout"),

        # variables view
        "variables": ("black", "dark gray"),
        "variable separator": ("dark cyan", "light gray"),

        "var label": ("light gray", "dark gray"),
        "var value": ("white", "dark gray"),
        "focused var label": ("light gray", "light blue"),
        "focused var value": ("white", "light blue"),

        "highlighted var label": ("light gray", "dark green"),
        "highlighted var value": ("white", "dark green"),
        "focused highlighted var label": ("light gray", "light blue"),
        "focused highlighted var value": ("white", "light blue"),

        "return label": ("light gray", "dark gray"),
        "return value": ("light cyan", "dark gray"),
        "focused return label": ("yellow", "light blue"),
        "focused return value": ("white", "light blue"),

        # stack view
        "stack": ("black", "dark gray"),

        "frame name": ("light gray", "dark gray"),
        "focused frame name": ("light gray", "light blue"),
        "frame class": ("dark blue", "dark gray"),
        "focused frame class": ("dark blue", "light blue"),
        "frame location": ("white", "dark gray"),
        "focused frame location": ("white", "light blue"),

        "current frame name": (add_setting("white", "bold"),
            "dark gray"),
        "focused current frame name": (add_setting("white", "bold"),
            "light blue", "bold"),
        "current frame class": ("dark blue", "dark gray"),
        "focused current frame class": ("dark blue", "dark green"),
        "current frame location": ("light cyan", "dark gray"),
        "focused current frame location": ("light cyan", "light blue"),

        # breakpoint view
        "breakpoint": ("light gray", "dark gray"),
        "focused breakpoint": ("light gray", "light blue"),
        "current breakpoint": (add_setting("white", "bold"), "dark gray"),
        "focused current breakpoint": (add_setting("white", "bold"), "light blue"),

        # UI widgets
        "selectable": ("light gray", "dark gray"),
        "focused selectable": ("white", "light blue"),

        "button": ("light gray", "dark gray"),
        "focused button": ("white", "light blue"),

        "background": ("black", "light gray"),
        "hotkey": (add_setting("black", "underline"), "light gray", "underline"),
        "focused sidebar": ("light blue", "light gray", "standout"),

        "warning": (add_setting("white", "bold"), "dark red", "standout"),

        "label": ("black", "light gray"),
        "value": ("white", "dark gray"),
        "fixed value": ("light gray", "dark gray"),

        "search box": ("white", "dark gray"),
        "search not found": ("white", "dark red"),

        "dialog title": (add_setting("white", "bold"), "dark gray"),

        # source view
        "breakpoint source": ("light gray", "dark red"),
        "breakpoint focused source": ("black", "dark red"),
        "current breakpoint source": ("black", "dark red"),
        "current breakpoint focused source": ("white", "dark red"),

        # highlighting
        "source": ("white", "black"),
        "focused source": ("white", "light blue"),
        "highlighted source": ("black", "light blue"),
        "current source": ("black", "light gray"),
        "current focused source": (add_setting("white", "underline") , "black"),
        "current highlighted source": ("white", "black"),

        "line number": ("dark gray", "black"),
        "keyword": ("yellow", "black"),

        "literal": ("dark magenta", "black"),
        "string": ("dark magenta", "black"),
        "doublestring": ("dark magenta", "black"),
        "singlestring": ("dark magenta", "black"),
        "docstring": ("dark magenta", "black"),

        "name": ("light cyan", "black"),
        "punctuation": ("yellow", "black"),
        "comment": ("light blue", "black"),
        "bp_star": ("dark red", "black"),

    })
