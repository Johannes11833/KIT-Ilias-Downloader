from typing import Any


def show_selection_dialog(options_display, options_short=None, title=None):
    if options_short is None:
        options_short = [i for i in range(0, len(options_display))]

    try:
        from simple_term_menu import TerminalMenu
        terminal_menu = TerminalMenu(options_display, title=title)
        index = terminal_menu.show()
        return options_short[index]
    except:
        msg = f'{title}\n'

        for o_display, o_short in zip(options_display, options_short):
            msg += f' ({o_short}) {o_display}\n'

        msg += '> '
        i = input(msg)

        if i.isdigit() and int(i) in options_short:
            return int(i)
        elif is_float(i) and float(i) in options_short:
            return float(i)
        elif i in options_short:
            return i
        else:
            return show_selection_dialog(options_display, options_short=options_short, title=title)


def is_float(element: Any) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False
