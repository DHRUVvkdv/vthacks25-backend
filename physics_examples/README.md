# Cool Physics Examples with Manim

This directory contains impressive physics animations created with Manim (Mathematical Animation Engine).

## What's Included

### 1. Double Pendulum (`DoublePendulum` scene)

- **Physics Concept**: Chaotic dynamics in mechanical systems
- **What it shows**: How tiny changes in initial conditions lead to dramatically different outcomes
- **Cool Factor**: The beautiful, unpredictable trails created by the second pendulum
- **Real Physics**: Uses actual Lagrangian mechanics equations

### 2. Electromagnetic Field (`ElectromagneticField` scene)

- **Physics Concept**: Magnetic fields around current-carrying conductors
- **What it shows**: Circular magnetic field lines and how field strength decreases with distance
- **Cool Factor**: Animated pulsing fields that visualize invisible forces
- **Real Physics**: Demonstrates Ampère's Law (B ∝ 1/r)

### 3. Wave Interference (`WaveInterference` scene)

- **Physics Concept**: Superposition of waves from multiple sources
- **What it shows**: Constructive and destructive interference patterns
- **Cool Factor**: Dynamic color-coded visualization of wave interactions
- **Real Physics**: Shows how waves add and cancel in real-time

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install individually
pip install manim>=0.18.0
pip install manim-physics>=0.3.0
pip install numpy>=1.21.0
```

## Running the Animations

```bash
# Run individual scenes
manim double_pendulum.py DoublePendulum -pql
manim double_pendulum.py ElectromagneticField -pql
manim double_pendulum.py WaveInterference -pql

# Run the full showcase
manim double_pendulum.py PhysicsShowcase -pql

# For high quality output
manim double_pendulum.py DoublePendulum -pqh
```

### Command Line Options:

- `-p`: Preview the animation when complete
- `-ql`: Low quality (faster rendering)
- `-qm`: Medium quality
- `-qh`: High quality (slower but beautiful)

## Why These Examples Are Cool

### Double Pendulum

This is one of the most famous examples of **deterministic chaos**. Despite following simple, predictable physics laws, the system becomes unpredictable over time. This demonstrates:

- Sensitivity to initial conditions (butterfly effect)
- How simple systems can exhibit complex behavior
- The beauty of mathematical chaos

### Electromagnetic Fields

Visualizes invisible forces that surround us everywhere:

- Shows how electric current creates magnetic fields
- Demonstrates the 3D nature of electromagnetic phenomena
- Helps understand concepts like motors, generators, and transformers

### Wave Interference

Fundamental to understanding:

- Sound and acoustics
- Optics and light behavior
- Quantum mechanics
- Signal processing

## The Physics Behind the Code

Each animation uses real physics equations:

- **Double Pendulum**: Lagrangian mechanics with coupled differential equations
- **EM Fields**: Ampère's Law and the Biot-Savart Law
- **Wave Interference**: Superposition principle and wave equations

## Extending These Examples

You can modify the code to explore:

- Different initial conditions for the pendulum
- Various current patterns for EM fields
- Different wave frequencies and phases
- Add damping, friction, or other real-world effects

## Performance Notes

- The double pendulum simulation runs real-time physics calculations
- For smoother animations, adjust the `dt` (time step) parameter
- Trail length can be modified to show more or less history
- Use lower quality settings for faster iteration during development

Enjoy exploring the beautiful intersection of physics, mathematics, and visual art!
