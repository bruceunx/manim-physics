# Manim Physics Simulation

A physics demonstration animation created using [Manim](https://www.manim.community/). This simulation visualizes the kinematics of a car on a platform being accelerated by a falling mass connected via a compound pulley system.

## 🎥 Preview

<div align="center">
  <video src="https://github.com/user-attachments/assets/8c4bba65-854c-4201-bc30-896ff8dc6ab0" width="100%" controls autoplay loop muted></video>
</div>

## 🚀 Features

- **Compound Pulley System**: Visualizes the relationship between the falling mass ($v_m$) and the car's velocity ($v_c$).
- **Real-time Metrics**: Displays dynamic velocity labels and force vectors as the animation plays.
- **Physics Phases**:
  1. **Acceleration**: The mass falls, accelerating the car.
  2. **Coasting/Deceleration**: The mass hits the floor, and the car continues with momentum, decelerating due to friction.

## 📂 Project Structure

- **`main.py`**: The entry point containing the `FullPhysicsDemo` scene and animation logic.
- **`physics.py`**: Custom module containing the Manim classes for physics objects (`PhysicsCar`, `PhysicsPulley`, `PhysicsPlatform`, `PhysicsSurface`).
- **`docs/`**: Contains the generated video output.

## 🛠️ Usage

### Prerequisites

You need Python installed along with the Manim library.

```bash
pip install manim
```
