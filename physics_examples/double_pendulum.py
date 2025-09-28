"""
Double Pendulum Physics Animation with Manim
============================================

This demonstrates chaotic motion in a double pendulum system.
A double pendulum consists of two pendulums attached end to end.
Despite its simple structure, it exhibits complex, chaotic behavior
that's highly sensitive to initial conditions.

Physics:
- Two masses connected by rigid rods
- Gravitational force acting downward
- Conservation of energy (in absence of friction)
- Chaotic dynamics - small changes lead to dramatically different outcomes
"""

from manim import *
import numpy as np


class DoublePendulum(Scene):
    def construct(self):
        # Title and description
        title = Text("Double Pendulum: Chaos in Motion", font_size=36, color=YELLOW)
        title.to_edge(UP)
        
        subtitle = Text("Small changes → Dramatically different outcomes", font_size=24, color=BLUE)
        subtitle.next_to(title, DOWN, buff=0.3)
        
        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait(1)
        
        # Move title to corner
        self.play(
            title.animate.scale(0.7).to_corner(UL),
            subtitle.animate.scale(0.6).next_to(title, DOWN, buff=0.1).to_corner(UL)
        )
        
        # Physics parameters
        L1, L2 = 2, 1.5  # Length of pendulum arms
        m1, m2 = 1, 1    # Masses
        g = 9.81         # Gravity
        
        # Initial conditions (slightly different for chaos demonstration)
        theta1_0 = np.pi/2 + 0.1    # Initial angle of first pendulum
        theta2_0 = np.pi/2          # Initial angle of second pendulum
        omega1_0 = 0                # Initial angular velocity
        omega2_0 = 0
        
        # Setup coordinate system
        origin = ORIGIN + DOWN * 0.5
        
        # Create pendulum components
        pivot = Dot(origin, color=WHITE, radius=0.1)
        
        # Animation setup
        dt = 0.02
        total_time = 15
        steps = int(total_time / dt)
        
        # State variables
        theta1, theta2 = theta1_0, theta2_0
        omega1, omega2 = omega1_0, omega2_0
        
        # Create initial pendulum
        pos1 = origin + L1 * np.array([np.sin(theta1), -np.cos(theta1), 0])
        pos2 = pos1 + L2 * np.array([np.sin(theta2), -np.cos(theta2), 0])
        
        rod1 = Line(origin, pos1, color=WHITE, stroke_width=4)
        rod2 = Line(pos1, pos2, color=WHITE, stroke_width=4)
        mass1 = Dot(pos1, color=RED, radius=0.15)
        mass2 = Dot(pos2, color=BLUE, radius=0.15)
        
        # Trail for the second mass (shows chaotic path)
        trail_points = [pos2.copy()]
        trail = VMobject(color=GREEN, stroke_width=2)
        
        # Add objects to scene
        self.add(pivot, rod1, rod2, mass1, mass2, trail)
        
        # Physics simulation loop
        for step in range(steps):
            # Double pendulum equations of motion (Lagrangian mechanics)
            # These are the exact equations - quite complex!
            
            cos_diff = np.cos(theta1 - theta2)
            sin_diff = np.sin(theta1 - theta2)
            
            den1 = (m1 + m2) * L1 - m2 * L1 * cos_diff * cos_diff
            den2 = (L2 / L1) * den1
            
            # First pendulum angular acceleration
            num1 = (-m2 * L1 * omega1**2 * sin_diff * cos_diff +
                    m2 * g * np.sin(theta2) * cos_diff +
                    m2 * L2 * omega2**2 * sin_diff -
                    (m1 + m2) * g * np.sin(theta1))
            alpha1 = num1 / den1
            
            # Second pendulum angular acceleration  
            num2 = (-m2 * L2 * omega2**2 * sin_diff * cos_diff +
                    (m1 + m2) * g * np.sin(theta1) * cos_diff -
                    (m1 + m2) * L1 * omega1**2 * sin_diff -
                    (m1 + m2) * g * np.sin(theta2))
            alpha2 = num2 / den2
            
            # Update velocities and positions (Euler integration)
            omega1 += alpha1 * dt
            omega2 += alpha2 * dt
            theta1 += omega1 * dt
            theta2 += omega2 * dt
            
            # Calculate new positions
            new_pos1 = origin + L1 * np.array([np.sin(theta1), -np.cos(theta1), 0])
            new_pos2 = new_pos1 + L2 * np.array([np.sin(theta2), -np.cos(theta2), 0])
            
            # Update visual elements
            rod1.put_start_and_end_on(origin, new_pos1)
            rod2.put_start_and_end_on(new_pos1, new_pos2)
            mass1.move_to(new_pos1)
            mass2.move_to(new_pos2)
            
            # Update trail
            trail_points.append(new_pos2.copy())
            if len(trail_points) > 200:  # Limit trail length
                trail_points.pop(0)
            
            # Create trail path
            if len(trail_points) > 1:
                trail.set_points_as_corners(trail_points)
            
            # Only update every few frames for performance
            if step % 3 == 0:
                self.wait(dt * 3)
        
        # Final message
        chaos_text = Text("This is deterministic chaos!", font_size=28, color=YELLOW)
        chaos_text.to_edge(DOWN)
        
        explanation = Text(
            "Same physics laws, but tiny changes in starting position\n"
            "create completely different paths over time",
            font_size=20,
            color=WHITE
        )
        explanation.next_to(chaos_text, UP, buff=0.3)
        
        self.play(Write(chaos_text))
        self.play(Write(explanation))
        self.wait(3)


class ElectromagneticField(Scene):
    def construct(self):
        # Title
        title = Text("Electromagnetic Field Around a Current", font_size=32, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Current-carrying wire (vertical)
        wire = Line(UP * 3, DOWN * 3, color=RED, stroke_width=8)
        wire_label = Text("Current I", font_size=20, color=RED)
        wire_label.next_to(wire, RIGHT, buff=0.5)
        
        # Current direction arrow
        current_arrow = Arrow(UP * 2, UP * 1, color=RED, stroke_width=4)
        current_arrow.next_to(wire, LEFT, buff=0.1)
        
        self.play(Create(wire), Write(wire_label))
        self.play(Create(current_arrow))
        
        # Create magnetic field lines (circles around the wire)
        field_lines = VGroup()
        field_arrows = VGroup()
        
        radii = [0.5, 1.0, 1.5, 2.0, 2.5]
        colors = [BLUE, LIGHT_BLUE, GREEN, YELLOW, ORANGE]
        
        for i, (radius, color) in enumerate(zip(radii, colors)):
            # Circular field line
            circle = Circle(radius=radius, color=color, stroke_width=3)
            circle.move_to(wire.get_center())
            field_lines.add(circle)
            
            # Direction arrows on the circle
            for angle in np.arange(0, 2*np.pi, np.pi/4):
                # Position on circle
                pos = radius * np.array([np.cos(angle), np.sin(angle), 0])
                # Tangent direction (perpendicular to radius)
                direction = np.array([-np.sin(angle), np.cos(angle), 0]) * 0.3
                
                arrow = Arrow(
                    pos - direction/2, 
                    pos + direction/2, 
                    color=color,
                    stroke_width=2,
                    max_tip_length_to_length_ratio=0.3
                )
                field_arrows.add(arrow)
        
        # Animate field creation
        self.play(Create(field_lines), run_time=2)
        self.play(Create(field_arrows), run_time=2)
        
        # Add field strength indication
        field_text = Text("B ∝ 1/r", font_size=24, color=WHITE)
        field_text.to_corner(DR)
        field_explanation = Text(
            "Magnetic field strength decreases\nwith distance from wire",
            font_size=18,
            color=GRAY
        )
        field_explanation.next_to(field_text, UP, buff=0.2)
        
        self.play(Write(field_text))
        self.play(Write(field_explanation))
        
        # Animate field pulsing to show dynamic nature
        for _ in range(3):
            self.play(
                field_lines.animate.set_stroke(width=6),
                field_arrows.animate.scale(1.2),
                run_time=0.5
            )
            self.play(
                field_lines.animate.set_stroke(width=3),
                field_arrows.animate.scale(1/1.2),
                run_time=0.5
            )
        
        self.wait(2)


class WaveInterference(Scene):
    def construct(self):
        # Title
        title = Text("Wave Interference Pattern", font_size=32, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Two wave sources
        source1 = Dot(LEFT * 3, color=RED, radius=0.2)
        source2 = Dot(RIGHT * 3, color=BLUE, radius=0.2)
        
        source1_label = Text("Source 1", font_size=16, color=RED)
        source1_label.next_to(source1, DOWN)
        source2_label = Text("Source 2", font_size=16, color=BLUE)
        source2_label.next_to(source2, DOWN)
        
        self.play(Create(source1), Create(source2))
        self.play(Write(source1_label), Write(source2_label))
        
        # Wave parameters
        wavelength = 1.0
        frequency = 2.0
        amplitude = 0.5
        
        # Create grid of points to show interference
        grid_points = []
        interference_dots = VGroup()
        
        for x in np.arange(-4, 4.5, 0.3):
            for y in np.arange(-2, 2.5, 0.3):
                if abs(x) < 2.5 or abs(y) > 0.3:  # Avoid sources
                    point = np.array([x, y, 0])
                    grid_points.append(point)
                    dot = Dot(point, radius=0.05, color=WHITE)
                    interference_dots.add(dot)
        
        self.add(interference_dots)
        
        # Animation loop
        for t in np.arange(0, 8, 0.1):
            new_dots = VGroup()
            
            for i, point in enumerate(grid_points):
                # Distance from each source
                r1 = np.linalg.norm(point - source1.get_center())
                r2 = np.linalg.norm(point - source2.get_center())
                
                # Wave from each source
                wave1 = amplitude * np.sin(2*np.pi * (frequency*t - r1/wavelength))
                wave2 = amplitude * np.sin(2*np.pi * (frequency*t - r2/wavelength))
                
                # Interference (superposition)
                total_amplitude = wave1 + wave2
                
                # Color based on amplitude
                if total_amplitude > 0.5:
                    color = RED
                    radius = 0.08
                elif total_amplitude < -0.5:
                    color = BLUE
                    radius = 0.08
                else:
                    color = WHITE
                    radius = 0.05
                
                dot = Dot(point, radius=radius, color=color)
                new_dots.add(dot)
            
            # Update dots
            self.remove(interference_dots)
            interference_dots = new_dots
            self.add(interference_dots)
            
            # Pulse sources
            source1.set_radius(0.2 + 0.1 * np.sin(2*np.pi*frequency*t))
            source2.set_radius(0.2 + 0.1 * np.sin(2*np.pi*frequency*t))
            
            self.wait(0.1)
        
        # Add explanation
        explanation = Text(
            "Red: Constructive interference (waves add)\n"
            "Blue: Destructive interference (waves cancel)\n"
            "White: Neutral interference",
            font_size=18,
            color=WHITE
        )
        explanation.to_edge(DOWN)
        self.play(Write(explanation))
        self.wait(3)


# Main scene that shows all examples
class PhysicsShowcase(Scene):
    def construct(self):
        # Main title
        title = Text("Cool Physics with Manim", font_size=48, color=GOLD)
        subtitle = Text("Mathematical Animation Engine", font_size=24, color=WHITE)
        subtitle.next_to(title, DOWN)
        
        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait(2)
        
        # Show what we'll demonstrate
        demos = VGroup(
            Text("• Double Pendulum (Chaos Theory)", color=YELLOW),
            Text("• Electromagnetic Fields", color=BLUE),
            Text("• Wave Interference", color=GREEN),
            Text("• Projectile Motion", color=RED)
        )
        demos.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        demos.next_to(subtitle, DOWN, buff=1)
        
        for demo in demos:
            self.play(Write(demo))
            self.wait(0.5)
        
        self.wait(2)
        self.clear()
