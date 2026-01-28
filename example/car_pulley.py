"""
Title: 90% of Physics Students Get This WRONG! 😱
"""

from manim import *
from manim.utils.rate_functions import ease_in_quad

from physics import PhysicsSurface, PhysicsCar, PhysicsPulley, PhysicsPlatform
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService


class FullPhysicsDemoLightMood(VoiceoverScene):
    def construct(self):
        service = AzureService(
            voice="en-US-GuyNeural",
            style="cheerful",
        )
        self.set_speech_service(service)

        # Soften the background for a lighter feel
        self.camera.background_color = "#1e1e1e"  # type:ignore

        # 2. Define Object Parameters
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
        PLATFORM_X = 3
        WALL_X = 1.5
        WALL_Y = 0.4
        GAP = 0.04
        CAR_X = 5
        FLOOR_Y = 3
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

        # 3. Create Objects (Using brighter/softer colors where appropriate)
        platform = PhysicsPlatform(
            length=PLATFORM_LENGTH,
            thickness=PLATFORM_THICKNESS,
            wall_height=PLATFORM_WALL_HEIGHT,
            color=TEAL_C,  # Lighter blue
        )
        platform.move_to(PLATFORM_POS)

        wall = PhysicsPlatform(
            length=WALL_LENGTH,
            thickness=WALL_THICKNESS,
            wall_height=WALL_WALL_HEIGHT,
            color=TEAL_C,
        )
        wall.rotate(-90 * DEGREES)
        wall.move_to(WALL_POS)

        car = PhysicsCar(
            width=CAR_WIDTH,
            height=CAR_HEIGHT,
            wheel_radius=CAR_WHEEL_RADIUS,
            color=YELLOW,  # Bright Yellow
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

        mass = Square(side_length=MASS_SIZE, color=RED_C, fill_opacity=0.9)
        mass.move_to(RIGHT * MASS_X + DOWN * MASS_Y)

        # Ropes
        rope_to_pulley = always_redraw(
            lambda: Line(
                start=car_pulley.wheel.get_bottom(),
                end=pulley.get_tangent_point(car_pulley.wheel.get_bottom()),
                color=WHITE,
                stroke_width=3,
            )
        )

        rope_free = always_redraw(
            lambda: Line(
                start=WALL_POS + LEFT * WALL_THICKNESS,
                end=car_pulley.wheel.get_top(),
                color=WHITE,
                stroke_width=3,
            )
        )

        rope_v = always_redraw(
            lambda: Line(
                start=pulley.wheel.get_right(),
                end=mass.get_top(),
                color=WHITE,
                stroke_width=3,
            )
        )

        # Labels
        mass_weight_label = always_redraw(
            lambda: MathTex("mg", color=GREEN_B).next_to(mass, RIGHT, buff=0.3)
        )

        mass_velocity_tracker = ValueTracker(0)
        mass_velocity_label = always_redraw(
            lambda: MathTex(
                "v_{mass}", "=", f"{mass_velocity_tracker.get_value():.2f}", color=RED_C
            ).next_to(mass, LEFT, buff=0.5)
        )

        car_velocity_tracker = ValueTracker(0)
        car_velocity_label = always_redraw(
            lambda: MathTex(
                "v_{car}", "=", f"{car_velocity_tracker.get_value():.2f}", color=YELLOW
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

        # 4. Physics Binding
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

        # --- UPDATER FOR ACCELERATION ---
        # "Latches" the value so it doesn't drop to zero when the animation finishes
        def update_velocities_acceleration(dt):
            car_v = car.calculate_speed(dt)
            if car_v > 0.01:
                mass_velocity_tracker.set_value(car_v * 2)
                car_velocity_tracker.set_value(car_v)

        self.add_updater(update_velocities_acceleration)

        # ---------------------------------------------------------------------
        # NARRATIVE AND ANIMATION
        # ---------------------------------------------------------------------

        # Introduction
        with self.voiceover(
            text="This is a classic physics problem. The double-pulley geometry creates a constraint that is deceptive and surprisingly counterintuitive."
        ) as tracker:
            self.play(
                Indicate(car, color=WHITE),
                Indicate(mass, color=WHITE),
                run_time=tracker.duration,
            )

        # Misconception
        tension_arrow = Arrow(
            start=pulley.get_right(),
            end=pulley.get_right() + DOWN,
            color=ORANGE,
            buff=0,
        )
        tension_label = MathTex("T", color=ORANGE).next_to(
            tension_arrow, RIGHT * 0.5 + UP * 0.1
        )

        misconception_eq = (
            MathTex("T", "=", "m", "g", color=ORANGE)
            .scale(0.7)
            .next_to(mass, RIGHT, buff=1.5)
            .shift(UP)
        )
        with self.voiceover(
            text="It's very intuitive to think the tension in the rope is the same as the weight of the mass"
        ) as tracker:
            self.play(
                Create(tension_arrow),
                Write(tension_label),
                Write(misconception_eq),
                run_time=1,
            )

        box = SurroundingRectangle(misconception_eq, color=YELLOW, buff=0.1)

        # Create text to the right of the box
        condition_text = Tex(
            r"Condition:\\Statics or in Uniform Motion", color=YELLOW, font_size=20
        ).next_to(box, RIGHT)

        with self.voiceover(
            text="But not so fast, That's only true if everything is standing perfectly still or in uniform motion."
        ) as tracker:
            self.play(
                Create(box),
                FadeIn(condition_text, shift=LEFT),
                run_time=tracker.duration,
            )

        correct_eq = (
            MathTex("T", "=", "m", "g", "-", "m", "a_{mass}", color=ORANGE)
            .scale(0.7)
            .next_to(mass, RIGHT, buff=1.5)
            .shift(UP)
        )
        correct_eq[4:].set_color(RED)

        with self.voiceover(
            text="The tension in the rope is reduced instantly when the mass drops, that is amazing,"
        ) as tracker:
            self.play(
                FadeOut(box),
                FadeOut(condition_text),
                TransformMatchingTex(misconception_eq, correct_eq),
                run_time=1,
            )

        # Constraint Explanation
        acc_label_car = MathTex("a_{car}").next_to(car, UP)
        acc_label_mass = (
            MathTex("a_{mass} = 2a_{car}").next_to(mass, RIGHT, buff=1.5).shift(DOWN)
        )

        with self.voiceover(
            text="Given the pulley setup, the mass downwards twice as fast as the car moves right."
        ) as tracker:
            self.play(Write(acc_label_car), Write(acc_label_mass), run_time=0.5)

        # Cleanup
        self.play(
            FadeOut(tension_arrow),
            FadeOut(tension_label),
            FadeOut(acc_label_car),
            FadeOut(acc_label_mass),
        )

        # --- Motion Animation ---
        distance_to_floor = mass.get_bottom()[1] - floor.get_top()[1] - GAP
        MASS_ACCELERATION = 2
        FALL_TIME = np.sqrt(2 * abs(distance_to_floor) / MASS_ACCELERATION)

        with self.voiceover(
            text="Ok. Let's drop the mass. Three, two, one... drop! <bookmark mark='start_drop'/>"
        ) as tracker:
            self.wait_until_bookmark("start_drop")
            self.play(
                master_tracker.animate.set_value(distance_to_floor),
                run_time=FALL_TIME,
                rate_func=ease_in_quad,
            )

        # --- TRANSITION LOGIC ---

        # 1. Remove the acceleration updater.
        self.remove_updater(update_velocities_acceleration)

        # 2. Freeze the mass (it hit the floor).
        mass.clear_updaters()
        mass_weight_label.clear_updaters()
        mass_velocity_label.clear_updaters()
        car_velocity_tracker.clear_updaters()

        mass_velocity_tracker.set_value(0)

        # 3. CRITICAL: Manually calculate the peak velocity at this exact moment.
        # This ensures that even if there was a micro-pause, the label shows the max speed, not 0.
        final_velocity = car_velocity_tracker.get_value()

        car_velocity_tracker1 = ValueTracker(car_velocity_tracker.get_value())
        car_velocity_label1 = always_redraw(
            lambda: MathTex(
                "v_{car}", "=", f"{car_velocity_tracker1.get_value():.2f}", color=RED
            ).next_to(car_velocity_label, DOWN, buff=0.5)
        )

        print(f"{car_velocity_tracker.get_value() = }")
        self.wait(1)

        self.add(car_velocity_label1)

        # 4. Add deceleration updater.
        # This standard updater is fine now because we *want* it to track the speed down to 0.
        def update_velocities_deceleration(dt):
            if dt > 0:
                velocity = car.calculate_speed(dt)
                car_velocity_tracker1.set_value(velocity)

        self.add_updater(update_velocities_deceleration)

        # 5. Deceleration Calculation
        DECEL_RATE = 0.5
        DECEL_TIME = final_velocity / DECEL_RATE
        decel_distance = final_velocity * DECEL_TIME - (DECEL_RATE * DECEL_TIME**2) / 2

        with self.voiceover(
            text="Boom! It hits the floor, tension is gone, and the car coasts to a smooth stop."
        ):
            self.play(
                master_tracker.animate.set_value(distance_to_floor + decel_distance),
                run_time=DECEL_TIME,
                rate_func=lambda t: 2 * t - t**2,  # ease_out_quad
            )

        # Final cleanup
        car_velocity_tracker1.set_value(0)
        self.remove_updater(update_velocities_deceleration)
        self.wait(2)
