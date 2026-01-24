from manim import *


class PhysicsSurface(VGroup):
    def __init__(
        self,
        start=LEFT,
        end=RIGHT,
        hash_len=0.2,
        hash_spacing=0.2,
        color=WHITE,
        stroke_width=4,
        **kwargs,
    ):
        super().__init__(**kwargs)

        main_line = Line(start, end, color=color, stroke_width=stroke_width)
        self.add(main_line)

        line_vec = main_line.get_vector()
        line_length = np.linalg.norm(line_vec)
        unit_vec = line_vec / line_length

        angle = -135 * DEGREES
        hash_vec = rotate_vector(unit_vec, angle) * hash_len

        num_hashes = int(line_length / hash_spacing)

        for i in range(num_hashes + 1):
            alpha = i / num_hashes if num_hashes > 0 else 0.5
            point_on_line = main_line.point_from_proportion(alpha)

            tick = Line(
                point_on_line,
                point_on_line + hash_vec,
                color=color,
                stroke_width=stroke_width * 0.5,
            )
            self.add(tick)
