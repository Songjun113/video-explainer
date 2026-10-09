"""Original Manim Community example: rotate a basis, then project data.

Render with: python -m manim -ql --renderer cairo manim_scene.py ProjectionExplainer
All points are synthetic teaching data. Text uses Pango, without a TeX dependency.
"""
import numpy as np
import manimpango
from manim import (
    Scene, NumberPlane, Dot, VGroup, Arrow, Line, Text, ValueTracker,
    Create, FadeIn, ReplacementTransform, always_redraw,
    ORIGIN, UP, DOWN, RIGHT, linear,
)

cyan, gold, red, muted = '#65c8d3', '#f0d37c', '#e88585', '#707780'
points = np.array([
    [-3, -2.1], [3, 2.1], [-2, -1], [2, 1],
    [-1, .4], [1, -.4], [0, 1.1], [0, -1.1],
], dtype=float)
centered = points - points.mean(axis=0)
eigenvalues, eigenvectors = np.linalg.eigh(np.cov(centered.T, bias=True))
principal = eigenvectors[:, -1]
if principal[0] < 0:
    principal = -principal
projected = np.outer(centered @ principal, principal)


def chinese_font():
    available = set(manimpango.list_fonts())
    for candidate in ('Microsoft YaHei', 'Noto Sans CJK SC', 'SimHei', 'SimSun'):
        if candidate in available:
            return candidate
    raise RuntimeError('Install/select a Chinese font; check manimpango.list_fonts().')


class ProjectionExplainer(Scene):
    def construct(self):
        self.camera.background_color = '#080a0d'
        font = chinese_font()

        def label(s, size=27, color='#e7e8e8'):
            return Text(s, font=font, font_size=size, color=color)

        title = label('换坐标后，投影丢失了什么？', 34).to_edge(UP, buff=.35)
        caption = label('先看同一组点。灰色坐标轴保持为参照。', 25).to_edge(DOWN, buff=.3)

        def narrate(s):
            nonlocal caption
            next_caption = label(s, 25).to_edge(DOWN, buff=.3)
            self.play(ReplacementTransform(caption, next_caption), run_time=.4)
            caption = next_caption

        plane = NumberPlane(
            x_range=[-4, 4, 1], y_range=[-3, 3, 1],
            x_length=6.8, y_length=5.1,
            background_line_style={'stroke_color': muted, 'stroke_opacity': .18},
            axis_config={'stroke_color': muted, 'stroke_width': 1.5},
        ).shift(2.65 * -RIGHT + .08 * UP)
        original = VGroup(*(Dot(plane.c2p(*p), radius=.065, color=cyan) for p in centered))
        tag = label('固定二维示意点', 20, muted).move_to(plane.c2p(0, -2.75))
        self.add(title, caption)
        self.play(Create(plane), FadeIn(original), FadeIn(tag), run_time=1.2)
        self.wait(1)

        angle = ValueTracker(0)

        def basis_end():
            return np.array([np.cos(angle.get_value()), np.sin(angle.get_value())])

        basis = always_redraw(lambda: VGroup(
            Arrow(plane.c2p(0, 0), plane.c2p(*(3.6 * basis_end())), buff=0, color=gold),
            Arrow(plane.c2p(0, 0), plane.c2p(*(-2.5 * basis_end()[::-1] * np.array([1, -1]))), buff=0, color=cyan),
        ))
        self.play(FadeIn(basis), run_time=.5)
        narrate('只转坐标轴：点的位置保持不变。')
        self.play(angle.animate.set_value(np.arctan2(principal[1], principal[0])), run_time=3, rate_func=linear)
        summary = VGroup(
            label('黄色：第一主方向', 25, gold),
            label('蓝色：垂直方向', 25, cyan),
            label('换坐标保留完整信息', 24),
        ).arrange(DOWN, aligned_edge=-RIGHT, buff=.35).move_to(3.75 * RIGHT + 1.05 * UP)
        self.play(FadeIn(summary), run_time=.6)
        self.wait(1)

        alpha = ValueTracker(0)
        moving = always_redraw(lambda: VGroup(*(
            Dot(plane.c2p(*(p + alpha.get_value() * (q - p))), radius=.06, color=gold)
            for p, q in zip(centered, projected)
        )))
        self.add(moving)
        narrate('再沿蓝色方向投影，把第二坐标设为零。')
        self.play(alpha.animate.set_value(1), original.animate.set_opacity(.35), run_time=3, rate_func=linear)
        residuals = VGroup(*(
            Arrow(plane.c2p(*q), plane.c2p(*p), buff=0, color=red, stroke_width=2,
                  max_tip_length_to_length_ratio=.15)
            for p, q in zip(centered, projected)
        ))
        self.play(Create(residuals), run_time=.8)
        last_summary = VGroup(
            label('黄色点：保留的主坐标', 24, gold),
            label('红色箭头：被舍弃的分量', 24, red),
            label('从投影点指向原始点', 22, muted),
        ).arrange(DOWN, aligned_edge=-RIGHT, buff=.35).move_to(summary)
        self.play(ReplacementTransform(summary, last_summary), run_time=.6)
        narrate('红色残差就是投影丢掉的信息。')
        self.wait(2)
        basis.clear_updaters()
        moving.clear_updaters()
