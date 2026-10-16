"""A 10-second, no-TeX, coupled-view smoke test for Manim CE 0.22.
Copy into an output project; render with: python -m manim -ql file.py CoupledViews
The amplitude parameter drives the curve, bar and signed stripe colors.
"""
from manim import *
import numpy as np

class CoupledViews(Scene):
    def construct(self):
        self.camera.background_color='#0c1425'
        amplitude=ValueTracker(.25)
        ax=Axes(x_range=[-3,3,1],y_range=[-2,2,1],x_length=5,y_length=3,tips=False).shift(LEFT*3)
        def graph():
            return ax.plot(lambda s:amplitude.get_value()*np.cos(3*s),color=BLUE)
        wave=always_redraw(graph)
        bar=always_redraw(lambda:Rectangle(width=.35,height=max(.01,amplitude.get_value()),fill_color=BLUE,fill_opacity=.9).move_to([0,-1+amplitude.get_value()/2,0]))
        grid=np.linspace(-2,2,120);x,y=np.meshgrid(grid,grid)
        phase=3*(.6*x+.8*y)
        def pixels():
            v=amplitude.get_value()*np.cos(phase)/1.5
            base=np.array([16,28,48]);pos=np.array([84,197,250]);neg=np.array([191,137,247])
            colors=base+abs(v)[:,:,None]*(np.where((v>=0)[:,:,None],pos,neg)-base)
            return colors.astype(np.uint8)
        image=ImageMobject(pixels()).scale_to_fit_width(3).shift(RIGHT*3.5)
        image.add_updater(lambda m:m.pixel_array.__setitem__((slice(None),slice(None),slice(0,3)),pixels()))
        label=Text('A: same parameter, three views',font_size=28).to_edge(UP)
        self.add(ax,wave,bar,image,label)
        self.wait(1)
        self.play(amplitude.animate.set_value(1.5),run_time=6,rate_func=linear)
        self.wait(3)
        for m in (wave,bar,image):m.clear_updaters()
