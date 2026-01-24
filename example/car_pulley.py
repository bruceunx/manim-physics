from manim import *
from manim.utils.rate_functions import ease_in_quad

from physics import PhysicsSurface, PhysicsCar, PhysicsPulley, PhysicsPlatform


class FullPhysicsDemo(Scene):
    def construct(self):
        # Objects size
        PLATFORM_LENGTH = 6.5
        PLATFORM_THICKNESS = 0.2
        PLATFORM_WALL_HEIGHT = 1.0

        WALL_LENGTH = 2
        WALL_THICKNESS = 0.1
        WALL_WALL_HEIGHT = 0.2

        CAR_WIDTH = 1.2
        CAR_HEIGHT = 0.6
        CAR_WHEEL_RADIUS = 0.15

        PULLEY_RADIUS = 0.16

        MASS_SIZE = 0.6

        FLOOR_LENGTH = 2

        # Position parameters
        PLATFORM_X = 3

        WALL_X = 1.5
        WALL_Y = 0.4
        GAP = 0.04
        CAR_X = 5

        FLOOR_Y = 3

        # Pulley positions (relative to platform)
        PULLEY_OFFSET_X_CAR = 0.25

        PULLEY_MOUNT_Y = 0.3

        CAR_PULLEY_OFFSET_X = 0.5
        MASS_Y = 1

        CAR_Y = (
            (CAR_HEIGHT + CAR_WHEEL_RADIUS) / 2
            - (PLATFORM_WALL_HEIGHT / 2 - PLATFORM_THICKNESS)
            + GAP
        )

        PLATFORM_POS = LEFT * PLATFORM_X
        CAR_POS = LEFT * CAR_X + UP * CAR_Y

        PULLEY_OFFSET_X = PLATFORM_LENGTH / 2 + PULLEY_OFFSET_X_CAR - PLATFORM_X
        PULLEY_Y = PLATFORM_THICKNESS / 2
        PULLEY_MOUNT_OFFSET_X = PLATFORM_LENGTH / 2 - PLATFORM_X

        CAR_PULLEY_OFFSET = RIGHT * CAR_PULLEY_OFFSET_X
        MASS_X = PULLEY_OFFSET_X + PULLEY_RADIUS

        FLOOR_START = DOWN * FLOOR_Y
        FLOOR_END = RIGHT * FLOOR_LENGTH + DOWN * FLOOR_Y

        WALL_POS = RIGHT * WALL_X + UP * WALL_Y

        # Physics parameters

        # Create objects
        platform = PhysicsPlatform(
            length=PLATFORM_LENGTH,
            thickness=PLATFORM_THICKNESS,
            wall_height=PLATFORM_WALL_HEIGHT,
            color=BLUE_C,
        )
        platform.move_to(PLATFORM_POS)

        wall = PhysicsPlatform(
            length=WALL_LENGTH,
            thickness=WALL_THICKNESS,
            wall_height=WALL_WALL_HEIGHT,
            color=BLUE_C,
        )
        wall.rotate(-90 * DEGREES)
        wall.move_to(WALL_POS)

        car = PhysicsCar(
            width=CAR_WIDTH,
            height=CAR_HEIGHT,
            wheel_radius=CAR_WHEEL_RADIUS,
            color=YELLOW_E,
        )
        car.move_to(CAR_POS)

        car_pulley = PhysicsPulley(
            position=car.get_rope_anchor() + CAR_PULLEY_OFFSET,
            mount_point=car.get_rope_anchor(),
            radius=PULLEY_RADIUS,
        )
        car_pulley_group = VGroup(car, car_pulley)

        floor = PhysicsSurface(start=FLOOR_START, end=FLOOR_END)

        pulley_pos = RIGHT * PULLEY_OFFSET_X + DOWN * PULLEY_Y
        pulley_mount_point = RIGHT * PULLEY_MOUNT_OFFSET_X + DOWN * PULLEY_MOUNT_Y
        pulley = PhysicsPulley(
            position=pulley_pos, mount_point=pulley_mount_point, radius=PULLEY_RADIUS
        )

        mass = Square(side_length=MASS_SIZE, color=RED, fill_opacity=0.8)
        mass.move_to(RIGHT * MASS_X + DOWN * MASS_Y)

        # Ropes
        rope_to_pulley = always_redraw(
            lambda: Line(
                start=car_pulley.wheel.get_bottom(),
                end=pulley.get_tangent_point(car_pulley.wheel.get_bottom()),
                color=WHITE,
            )
        )

        rope_free = always_redraw(
            lambda: Line(
                start=WALL_POS + LEFT * WALL_THICKNESS,
                end=car_pulley.wheel.get_top(),
                color=WHITE,
            )
        )

        rope_v = always_redraw(
            lambda: Line(
                start=pulley.wheel.get_right(),
                end=mass.get_top(),
                color=WHITE,
            )
        )

        # Labels and vectors
        # Mass labels
        mass_weight_label = always_redraw(
            lambda: MathTex("mg", color=GREEN).next_to(mass, RIGHT, buff=0.3)
        )

        mass_velocity_tracker = ValueTracker(0)

        mass_velocity_label = always_redraw(
            lambda: MathTex(
                f"v_m = {mass_velocity_tracker.get_value():.2f}", color=RED
            ).next_to(mass, LEFT, buff=0.5)
        )

        car_velocity_tracker = ValueTracker(0)
        car_velocity_label = always_redraw(
            lambda: MathTex(
                f"v_c = {car_velocity_tracker.get_value():.2f}", color=YELLOW
            ).next_to(car, DOWN, buff=0.5)
        )

        self.add(
            platform,
            floor,
            wall,
            car_pulley_group,
            pulley,
            mass,
            rope_to_pulley,
            rope_free,
            rope_v,
            mass_weight_label,
            mass_velocity_label,
            car_velocity_label,
        )

        # Physics setup
        master_tracker = ValueTracker(0)
        car.attach_physics(master_tracker, 0.5)
        car_pulley_group.add_updater(
            lambda m: car_pulley.update_position(
                car.get_rope_anchor() + CAR_PULLEY_OFFSET, car.get_rope_anchor()
            )
        )
        pulley.attach_physics(master_tracker)

        mass_start_y = mass.get_y()
        mass.add_updater(lambda m: m.set_y(mass_start_y - master_tracker.get_value()))

        # Velocity updaters

        def update_velocities(dt):
            car_v = car.calculate_speed(dt)
            mass_velocity_tracker.set_value(car_v * 2)
            car_velocity_tracker.set_value(car_v)

        self.add_updater(update_velocities)

        # Animation
        distance_to_floor = mass.get_bottom()[1] - floor.get_top()[1] - GAP

        MASS_ACCELERATION = 2
        FALL_TIME = np.sqrt(2 * abs(distance_to_floor) / MASS_ACCELERATION)

        self.play(
            master_tracker.animate.set_value(distance_to_floor),
            run_time=FALL_TIME,
            rate_func=ease_in_quad,
        )

        final_velocity = car.velocity
        car_velocity_tracker.set_value(final_velocity)

        mass.clear_updaters()
        mass_weight_label.clear_updaters()
        mass_velocity_label.clear_updaters()

        def update_velocities_car_only(dt):
            if dt > 0:
                velocity = car.calculate_speed(dt)
                if velocity > 0.01:
                    car_velocity_tracker.set_value(velocity)

        self.remove_updater(update_velocities)
        self.add_updater(update_velocities_car_only)

        self.wait(1)

        DECEL_RATE = 0.5  # mass accelerate -> car

        DECEL_TIME = final_velocity / DECEL_RATE
        print(final_velocity)

        decel_distance = final_velocity * DECEL_TIME - (DECEL_RATE * DECEL_TIME**2) / 2
        self.play(
            master_tracker.animate.set_value(distance_to_floor + decel_distance),
            run_time=DECEL_TIME,
            rate_func=lambda t: 2 * t - t**2,  # Deceleration with constant friction
        )

        car_velocity_tracker.set_value(0)

        self.wait()
