
from trame.app import TrameApp
from trame.ui.html import DivLayout
from trame.widgets import html, vtklocal


class MyApp(TrameApp):

    def __init__(self, server=None, client_type="vue3"):
        super().__init__(server, client_type)

        self._build_ui()


    def _build_ui(self):

        with DivLayout(self.server) as layout:

            with html.Body(style=   
                                "min-height: 600px;"
                                "border: 8px solid black;"
                                "display: flex;"
                                "flex-direction: column;"
                                "justify-content: center;"
                                "align-items: center;"
                                ):

                html.Input(v_model=("value",),        
                        style=
                            "width: 100px;"
                            "height: 25px;"
                            )

                html.Input(type="range",
                        v_model=("value",3),
                        style=
                            "width: 100px;"
                            "height: 25px;"
                            )

                """
                This same (name, default) convention is used everywhere in trame — not just for v_model,
                but for style, classes, and any other prop you want to drive from state.
                """                  

# Start the application
if __name__ == "__main__":
    app = MyApp()
    app.server.start()