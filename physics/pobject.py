from manim import *


class PhysicsCar(VGroup):
    def __init__(self, width=2.0, height=1.0, wheel_radius=0.25, color=BLUE, **kwargs):
        super().__init__(**kwargs)
        self.wheel_radius = wheel_radius

        self.body = Rectangle(width=width, height=height, color=color, fill_opacity=0.5)

        def create_wheel():
            g = VGroup()
            tire = Circle(radius=wheel_radius, color=color, stroke_width=4)
            axle = Dot(color=color, radius=wheel_radius / 8)
            spoke = Line(UP * wheel_radius, DOWN * wheel_radius, color=color)
            g.add(tire, spoke, axle)
            return g

        self.wheel_left = create_wheel()
        self.wheel_right = create_wheel()

        y_pos = -height / 2
        x_offset = width / 3
        self.wheel_left.move_to(self.body.get_center() + LEFT * x_offset + UP * y_pos)
        self.wheel_right.move_to(self.body.get_center() + RIGHT * x_offset + UP * y_pos)

        self.add(self.body, self.wheel_left, self.wheel_right)

    def attach_physics(self, tracker, speed_ratio=1):
        """
        Links this car to a ValueTracker.
        The car will automatically move and rotate wheels based on the tracker's value.
        """
        self.tracker = tracker
        self.speed_ratio = speed_ratio
        self.last_distance = tracker.get_value() * self.speed_ratio
        self.add_updater(self._update_physics)

    def _update_physics(self, mob):
        """Internal function called every frame"""
        current_dist = self.tracker.get_value() * self.speed_ratio

        delta_x = current_dist - self.last_distance

        mob.shift(RIGHT * delta_x)

        delta_angle = -delta_x / self.wheel_radius
        self.wheel_left.rotate(delta_angle)
        self.wheel_right.rotate(delta_angle)

        self.delta_x = delta_x
        self.last_distance = current_dist

    def get_rope_anchor(self):
        return self.body.get_right()

    def calculate_speed(self, dt):
        if dt > 0:
            self.velocity = abs(self.delta_x / dt)
            return self.velocity
        return 0


class PhysicsPulley(VGroup):
    def __init__(
        self, position, mount_point, radius=0.3, color=WHITE, rope_color=WHITE, **kwargs
    ):
        super().__init__(**kwargs)
        self.radius = radius
        self.center_pos = position
        self.mount_point = mount_point

        self.mount_rod = Line(
            start=mount_point, end=position, color=GREY, stroke_width=5
        )

        self.axle_pin = Dot(point=position, color=GREY_A, radius=0.08)

        self.wheel = VGroup()

        rim = Circle(radius=radius, color=color, stroke_width=4)

        inner = Circle(
            radius=radius * 0.8, color=color, stroke_width=1, stroke_opacity=0.5
        )

        spoke_h = Line(LEFT * radius, RIGHT * radius, color=color, stroke_width=2)
        spoke_v = Line(UP * radius, DOWN * radius, color=color, stroke_width=2)

        self.wheel.add(rim, inner, spoke_h, spoke_v)
        self.wheel.move_to(position)

        self.rope_arc = Arc(
            radius=radius,
            start_angle=90 * DEGREES,  # Top
            angle=90 * DEGREES,  # To Left
            arc_center=position,
            color=rope_color,
            stroke_width=4,
        )

        self.add(self.mount_rod, self.wheel, self.rope_arc, self.axle_pin)

        self.last_distance = 0

    def attach_physics(self, tracker):
        """
        Links pulley rotation to the movement tracker.
        Note: The pulley stays in place, but the wheel rotates.
        """
        self.tracker = tracker
        self.last_distance = tracker.get_value()
        self.add_updater(self._update_rotation)

    def _update_rotation(self, mob):
        current_dist = self.tracker.get_value()
        delta_x = current_dist - self.last_distance

        delta_angle = -delta_x / self.radius

        self.wheel.rotate(delta_angle)

        self.last_distance = current_dist

    def get_tangent_point(self, point, direction=1):
        """
        Calculates the point on the circle where a line from 'point' is tangent.
        circle: The Circle Mobject
        point: The [x,y,z] coordinate of the external point
        direction: 1 for 'top/left' tangent, -1 for 'bottom/right' tangent
        """
        vec = point - self.center_pos
        dist = np.linalg.norm(vec)

        if dist <= self.radius:
            return point  # Point is inside circle; return point itself to avoid error

        # 1. Angle of the vector connecting Center -> Point
        base_angle = np.arctan2(vec[1], vec[0])

        # 2. Angle offset for the tangent point (Standard Trig)
        # cos(alpha) = Adjacent / Hypotenuse = radius / dist
        alpha = np.arccos(self.radius / dist)

        # 3. Calculate final angle
        tangent_angle = base_angle + (-direction * alpha)

        # 4. Convert polar back to cartesian [x,y,z]
        tangent_point = self.center_pos + self.radius * np.array(
            [np.cos(tangent_angle), np.sin(tangent_angle), 0]
        )

        return tangent_point

    def update_position(self, new_position, new_mount_point=None):
        """Update pulley position and optionally mount point"""
        if new_mount_point is not None:
            self.mount_point = new_mount_point

        self.center_pos = new_position

        self.mount_rod.put_start_and_end_on(self.mount_point, new_position)
        self.wheel.move_to(new_position)
        self.axle_pin.move_to(new_position)
        self.rope_arc.move_arc_center_to(new_position)


class PhysicsPlatform(VGroup):
    def __init__(
        self,
        length=6,
        thickness=0.5,
        wall_height=2.0,
        wall_side=LEFT,
        color=WHITE,
        fill_opacity=0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)

        d = 1 if wall_side is LEFT else -1

        p1 = [0, 0, 0]  # Bottom-Left (Outer corner)
        p2 = [d * length, 0, 0]  # Bottom-Right
        p3 = [d * length, thickness, 0]  # Top-Right (The "Open" end)
        p4 = [d * thickness, thickness, 0]  # Inner Corner
        p5 = [d * thickness, wall_height, 0]  # Top of Wall (Inner)
        p6 = [0, wall_height, 0]  # Top of Wall (Outer)

        self.outline = Polygon(p1, p2, p3, p4, p5, p6, color=color, stroke_width=4)  # type: ignore
        if fill_opacity > 0:
            self.outline.set_fill(color, opacity=fill_opacity)

        self.add(self.outline)

        self.add_hatching(length, wall_height, color)

    def add_hatching(self, length, height, color):
        """Creates diagonal lines inside the shape"""
        # Create a large rectangle of hash lines covering the whole area
        hatching_group = VGroup()
        step = 0.3

        max_dim = max(length, height)
        for i in range(int(-max_dim / step), int(max_dim / step) * 2):
            line = Line(
                start=UP * 5 + RIGHT * (i * step),
                end=DOWN * 5 + LEFT * 5 + RIGHT * (i * step),
                stroke_width=2,
                color=color,
                stroke_opacity=0.5,
            )
            hatching_group.add(line)

        try:
            mask = self.outline.copy().set_fill(WHITE, 1).set_stroke(width=0)

            hashed_shape = Intersection(
                mask, hatching_group, color=color, stroke_width=2
            )
            self.add(hashed_shape)

        except Exception:
            pass

    def get_floor_y(self):
        return self.outline.get_vertices()[2][1] + self.get_y()

    def get_wall_top(self):
        return (
            self.outline.get_vertices()[5]
            + self.get_center()
            - self.outline.get_center()
        )
