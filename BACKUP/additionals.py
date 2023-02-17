from design import design_scheme

def on_enter(e):
    e.widget['background'] = design_scheme.btn_color

def on_leave(e):
    e.widget['background'] = design_scheme.bg_color


