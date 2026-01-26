from manim import *
from manim.utils.rate_functions import ease_in_quad

from physics import PhysicsSurface, PhysicsCar, PhysicsPulley, PhysicsPlatform
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService


class FullPhysicsDemoWithVoice(VoiceoverScene):
    def construct(self):
        # 1. Setup Voiceover Service
        service = AzureService(
            voice="en-HK-SamNeural",
        )
        self.set_speech_service(service)

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

        # 3. Create Objects
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

        # Labels
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

        # --- UPDATER FIX PART 1 ---
        # We only update the tracker if the calculated velocity is significant (> 0.01).
        # This prevents the label from dropping to 0 when the animation finishes
        # but the scene is waiting for the voiceover to finish.
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
            text="Consider this mechanical system. We have a car connected to a hanging mass via a set of pulleys."
        ) as tracker:
            self.play(Indicate(car), Indicate(mass), run_time=tracker.duration)

        # Misconception
        tension_arrow = Arrow(
            start=mass.get_top(), end=mass.get_top() + UP, color=ORANGE, buff=0
        )
        tension_label = MathTex("T", color=ORANGE).next_to(tension_arrow, LEFT)
        misconception_eq = (
            MathTex("T", "=", "m", "g", color=ORANGE)
            .next_to(mass, RIGHT, buff=1.5)
            .shift(UP)
        )

        with self.voiceover(
            text="A common mistake is to assume that the tension in the rope, T, is simply equal to the weight of the mass, m g."
        ) as tracker:
            self.play(
                Create(tension_arrow),
                Write(tension_label),
                Write(misconception_eq),
                run_time=tracker.duration,
            )

        # Correction
        cross = Cross(misconception_eq, color=RED)
        with self.voiceover(
            text="However, this is incorrect. That equation only holds true if the mass is stationary."
        ) as tracker:
            self.play(Create(cross), run_time=tracker.duration)

        # Derivation
        fbd_eq = (
            MathTex("m", "g", "-", "T", "=", "m", "a")
            .move_to(misconception_eq)
            .shift(DOWN * 1.5)
        )
        with self.voiceover(
            text="Because the system accelerates downwards, we must use Newton's Second Law. Weight minus Tension equals mass times acceleration."
        ) as tracker:
            self.play(Write(fbd_eq), run_time=tracker.duration)

        correct_eq = MathTex("T", "=", "m", "g", "-", "m", "a").move_to(fbd_eq)
        with self.voiceover(
            text="Rearranging this, we see that the tension is actually the weight, minus the force required to accelerate the mass."
        ) as tracker:
            self.play(
                TransformMatchingTex(fbd_eq, correct_eq), run_time=tracker.duration
            )

        # Constraint Explanation
        acc_label_car = MathTex("a_{car}").next_to(car, UP)
        acc_label_mass = (
            MathTex("a_{mass} = 2a_{car}").next_to(mass, RIGHT, buff=1.5).shift(DOWN)
        )

        with self.voiceover(
            text="Also, due to the pulley geometry, the mass accelerates twice as fast as the car. This further reduces the tension acting on the car."
        ) as tracker:
            self.play(
                Write(acc_label_car), Write(acc_label_mass), run_time=tracker.duration
            )

        # Cleanup
        self.play(
            FadeOut(misconception_eq),
            FadeOut(cross),
            FadeOut(correct_eq),
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
            text="Let's observe the actual motion. Notice the acceleration."
        ):
            self.play(
                master_tracker.animate.set_value(distance_to_floor),
                run_time=FALL_TIME,
                rate_func=ease_in_quad,
            )

        # --- TRANSITION LOGIC ---

        # 1. Remove the acceleration updater.
        # Because we added the conditional check (>0.01), the label should still show
        # the peak velocity (approx 2.5) even if the scene waited for voiceover.
        self.remove_updater(update_velocities_acceleration)

        # 2. Freeze the mass.
        mass.clear_updaters()
        mass_weight_label.clear_updaters()
        mass_velocity_label.clear_updaters()
        mass_velocity_tracker.set_value(0)  # Mass stops visually

        # 3. Calculate accurate theoretical velocity to correct any minor drift
        mass_final_v = MASS_ACCELERATION * FALL_TIME
        final_velocity = mass_final_v * 0.5
        car_velocity_tracker.set_value(final_velocity)

        # 4. Add deceleration updater.
        # This one doesn't need the >0 check because we want to see it go to 0.
        def update_velocities_deceleration(dt):
            if dt > 0:
                velocity = car.calculate_speed(dt)
                car_velocity_tracker.set_value(velocity)

        self.add_updater(update_velocities_deceleration)

        # 5. Deceleration Calculation
        DECEL_RATE = 0.5
        DECEL_TIME = final_velocity / DECEL_RATE
        decel_distance = final_velocity * DECEL_TIME - (DECEL_RATE * DECEL_TIME**2) / 2

        with self.voiceover(
            text="Once the mass hits the floor, the tension drops to zero, and friction slows the car to a stop."
        ):
            self.play(
                master_tracker.animate.set_value(distance_to_floor + decel_distance),
                run_time=DECEL_TIME,
                rate_func=lambda t: 2 * t - t**2,  # ease_out_quad
            )

        # Final cleanup
        car_velocity_tracker.set_value(0)
        self.remove_updater(update_velocities_deceleration)
        self.wait(2)
