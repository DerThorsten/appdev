


class GameViewCanvasWidget(Widget):
    """ 
        This is a Widget without Any
        child widgets, just the 
        plain canvas.
        It is used to draw the
        game physic.

        Game canvas can do the transformations
        between canvas and physic-world coordinates
    """
    def __init__(self, *args, **kwargs):
        super(GameViewCanvasWidget, self).__init__(*args, **kwargs)

        self.world_on_touch_down = None
        self.world_on_touch_move = None
        self.world_on_touch_up = None


    ##########################################
    # transform points from canvas to world
    # and vice versa
    ##########################################
    def canvas_point_to_world(point,out=None):
        pass

    def canvas_length_to_world(length,out=None):
        pass

    def world_point_to_canvas(point,out=None):
        pass

    def world_length_to_canvas(length,out=None):
        pass

    ##########################################
    # handle touch events on canvas
    # 
    ##########################################
    def on_touch_down(self, touch):
        f = self.world_on_touch_down
        if f is not None:
            wpos = canvas_point_to_world(touch.pos)
            return f(wpos, touch)
        return False

    def on_touch_move(self, touch):
        f = self.world_on_touch_move
        if f is not None:
            wpos = canvas_point_to_world(touch.pos)
            f(wpos, touch)

    def on_touch_up(self, touch):
        f = self.world_on_touch_up
        if f is not None:
            wpos = canvas_point_to_world(touch.pos)
            f(wpos, touch)


    ##########################################
    # zoom in and out
    # and navigate world to position
    ##########################################
    def zoom_in(self, zoom_factor):
        pass

    def zoom_out(self, zoom_factor):
        pass

    def navigate_world_to(self, wpoint):
        pass





class GameViewWidget(Widget):
    pass
