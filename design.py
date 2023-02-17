



class Colors():

    def __init__(self):
        super().__init__()
        #weightshift scheme: ["#31363C", "#999999", "#CCCCCC", "#CC9900", "#FFCC33"]
        self.green_palette = ["#A4DE02", "#76BA1B", "#4C9A2A", "#ACDF87", "#68BB59"]
        self.color_scheme = ["#31363C", "#999999", "#CCCCCC", "#CC9900", "#FFCC33"]
        self.color_scheme_graph = ["#00BEFF", "#AEFF00", "#FF6C00", "#CC9900", "#33ffc5", "#d90b0b", "#db07d4", "#CC9900", "#FFCC33"]
        self.border_color = self.color_scheme[1]
        self.font_color = self.color_scheme[2]
        self.bg_color = self.color_scheme[0]
        self.h_thickness = 2
        self.h_thickness_child = 1
        self.border_color_child = self.color_scheme[1]
        self.bg_optionmenu = self.color_scheme[1]
        self.btn_relief = "solid"
        self.btn_color = self.green_palette[1]
        self.btn_color_active = self.green_palette[0]
        self.btn_color_disabled = self.green_palette[0]
        self.btn_border_color = self.green_palette[2]
        self.windowsize_main = [1650,1000]
        self.windowsize_enlarged_graph = [1390,850]

    def getDesignSettings(self):
        settings = {
            "TFrame": {
                "configure": {
                    "background": design_scheme.bg_color,  # Your margin color
                    "relief": "solid",
                    "borderwidth": 0,
                    # "highlightbackground": "red",
                    # "highlightthickness": 2
                    # "bordercolor": "red"
                },
                "map": {
                    # "background": [("selected", design_scheme.border_color_child)],  # Tab color when selected
                    # "background": [("active",design_scheme.border_color),("selected", design_scheme.border_color)],
                    # "highlightbackground": [("active","red"),("selected",design_scheme.border_color_child)]
                }
            },
            "TEntry": {
                "configure": {

                    "font": ('Helvetica', 10, 'bold'),
                    "foreground": design_scheme.bg_color,
                    "background": design_scheme.bg_color,
                    "activebackground": "blue",
                    "borderwidth": 0,
                    #"relief": "solid",
                     #"padding": [5, 5],
                     #"highlightbackground": "red",
                     #"highlightthickness": 2,
                    # "bordercolor": design_scheme.font_color,
                    # "anchor": "center"
                },
                "map": {
                     "foreground": [('active', '!disabled', design_scheme.btn_color_active)]  ,
                    "background": [('active', design_scheme.font_color)]
                }
            },
            "TButton": {
                "configure": {
                    "font": ('Helvetica', 9, 'bold'),
                    "background": design_scheme.btn_color,  # Your margin color
                    "relief": "solid",
                    "borderwidth": 0,
                    "bordercolor": design_scheme.btn_border_color,
                    "anchor": "center",
                    "padding": [3,3]
                },
                "map": {
                    "foreground": [('active', '!disabled', 'black'), ('active', 'disabled', 'grey')],
                    "background": [('active', design_scheme.btn_color_active), ('disabled', 'grey')]
                }
            },
            "TLabel": {
                "configure": {
                    "font": ('Helvetica', 10, 'bold'),
                    "foreground": design_scheme.font_color,
                    "background": design_scheme.bg_color,  # Your margin color
                    "borderwidth": 0,
                    # "relief": "solid",
                    # "highlightbackground": "red",
                    # "highlightthickness": 2,
                    # "bordercolor": design_scheme.font_color,
                    "anchor": "center"
                },
                "map": {
                    "foreground": [('active', '!disabled', 'black'), ('active', 'disabled', 'grey')],
                    "background": [('active', design_scheme.btn_color_active), ('disabled', 'grey')]
                }
            },
            "TCheckbutton": {
                "configure": {
                    "font": ('Helvetica', 10, 'bold'),
                    "foreground": design_scheme.bg_color,
                    "background": design_scheme.bg_color,  # Your margin color
                    "borderwidth": 0,
                    # "relief": "solid",
                    # "highlightbackground": "red",
                    # "highlightthickness": 2,
                    # "bordercolor": design_scheme.font_color,
                    "anchor": "center"
                },
                "map": {
                    "foreground": [('active', '!disabled', design_scheme.btn_color_active)]  # ,
                    # "background": [('active', design_scheme.font_color)]
                }
            },
            "TMenubutton": {
                "configure": {
                    "font": ('Helvetica', 10, 'bold'),
                    "foreground": design_scheme.font_color,
                    "background": design_scheme.bg_color,  # Your margin color
                    "activebackground": "blue",
                    "borderwidth": 1,
                    "relief": "solid",
                    "padding": [5, 5],
                    # "highlightbackground": "red",
                    # "highlightthickness": 2,
                    "bordercolor": design_scheme.font_color,
                    # "anchor": "center"
                },
                "map": {
                    # "foreground": [('active', '!disabled', design_scheme.btn_color_active)]  # ,
                    # "background": [('active', design_scheme.font_color)]
                }
            },
            "TNotebook": {
                "configure": {
                    "background": design_scheme.bg_color,  # Your margin color
                    "tabmargins": [10, -1, 0, 0],  # margins: left, top, right, separator
                    "relief": "solid",

                    "highlightbackground": "red",
                    "highlightthickness": 0
                }
            },
            "TNotebook.Tab": {
                "configure": {
                    "borderwidth": 0,
                    "font": ('Helvetica', 10),
                    "background": design_scheme.border_color,  # tab color when not selected
                    "padding": [20, 5],
                    "foreground": "black",
                    "highlightbackground": "red",
                    "highlightthickness": 9
                },
                "map": {
                    # "background": [("selected", design_scheme.border_color_child)],  # Tab color when selected
                    "background": [("active", design_scheme.border_color), ("selected", design_scheme.border_color)],
                    "expand": [("selected", [1, 3, 1, 0])],  # text margins
                    "foreground": [("active", "black"), ("selected", "black")],
                    # "lightcolor": [("active", design_scheme.bg_color)],
                    "highlightbackground": [("selected", "blue")]
                }
            }
        }
        return settings



design_scheme = Colors()