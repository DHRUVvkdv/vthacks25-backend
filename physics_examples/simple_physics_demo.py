"""
Simple Physics Demonstrations without Manim
===========================================

Cool physics simulations using just matplotlib and numpy.
These run immediately without complex dependencies!
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, FancyArrowPatch
from matplotlib.patches import Rectangle
import math


class DoublePendulumSimple:
    """Double pendulum simulation with matplotlib"""
    
    def __init__(self):
        # Physics parameters
        self.L1, self.L2 = 1.0, 1.0  # Length of pendulum arms
        self.m1, self.m2 = 1.0, 1.0  # Masses
        self.g = 9.81                # Gravity
        
        # Initial conditions (slightly different for chaos)
        self.theta1 = np.pi/2 + 0.1
        self.theta2 = np.pi/2
        self.omega1 = 0.0
        self.omega2 = 0.0
        
        # For visualization
        self.trail_x, self.trail_y = [], []
        self.dt = 0.02
        
        # Setup plot
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.set_xlim(-2.5, 2.5)
        self.ax.set_ylim(-2.5, 1.0)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('Double Pendulum: Deterministic Chaos', fontsize=16, color='darkred')
        
        # Create visual elements
        self.line, = self.ax.plot([], [], 'k-', linewidth=3, alpha=0.8)
        self.trail_line, = self.ax.plot([], [], 'r-', linewidth=1, alpha=0.6)
        self.mass1_circle = Circle((0, 0), 0.08, color='blue', zorder=10)
        self.mass2_circle = Circle((0, 0), 0.08, color='red', zorder=10)
        self.ax.add_patch(self.mass1_circle)
        self.ax.add_patch(self.mass2_circle)
        
        # Add physics info
        self.info_text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes, 
                                     verticalalignment='top', fontsize=10,
                                     bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def equations_of_motion(self, theta1, theta2, omega1, omega2):
        """Double pendulum equations using Lagrangian mechanics"""
        cos_diff = np.cos(theta1 - theta2)
        sin_diff = np.sin(theta1 - theta2)
        
        den1 = (self.m1 + self.m2) * self.L1 - self.m2 * self.L1 * cos_diff * cos_diff
        den2 = (self.L2 / self.L1) * den1
        
        # First pendulum angular acceleration
        num1 = (-self.m2 * self.L1 * omega1**2 * sin_diff * cos_diff +
                self.m2 * self.g * np.sin(theta2) * cos_diff +
                self.m2 * self.L2 * omega2**2 * sin_diff -
                (self.m1 + self.m2) * self.g * np.sin(theta1))
        alpha1 = num1 / den1
        
        # Second pendulum angular acceleration  
        num2 = (-self.m2 * self.L2 * omega2**2 * sin_diff * cos_diff +
                (self.m1 + self.m2) * self.g * np.sin(theta1) * cos_diff -
                (self.m1 + self.m2) * self.L1 * omega1**2 * sin_diff -
                (self.m1 + self.m2) * self.g * np.sin(theta2))
        alpha2 = num2 / den2
        
        return alpha1, alpha2
    
    def animate(self, frame):
        """Animation function called by matplotlib"""
        # Update physics
        alpha1, alpha2 = self.equations_of_motion(self.theta1, self.theta2, 
                                                 self.omega1, self.omega2)
        
        self.omega1 += alpha1 * self.dt
        self.omega2 += alpha2 * self.dt
        self.theta1 += self.omega1 * self.dt
        self.theta2 += self.omega2 * self.dt
        
        # Calculate positions
        x1 = self.L1 * np.sin(self.theta1)
        y1 = -self.L1 * np.cos(self.theta1)
        x2 = x1 + self.L2 * np.sin(self.theta2)
        y2 = y1 - self.L2 * np.cos(self.theta2)
        
        # Update trail
        self.trail_x.append(x2)
        self.trail_y.append(y2)
        if len(self.trail_x) > 500:  # Limit trail length
            self.trail_x.pop(0)
            self.trail_y.pop(0)
        
        # Update visual elements
        self.line.set_data([0, x1, x2], [0, y1, y2])
        self.trail_line.set_data(self.trail_x, self.trail_y)
        self.mass1_circle.center = (x1, y1)
        self.mass2_circle.center = (x2, y2)
        
        # Calculate and display energy
        # Kinetic energy
        v1_sq = (self.L1 * self.omega1)**2
        v2_sq = (self.L1 * self.omega1)**2 + (self.L2 * self.omega2)**2 + \
                2 * self.L1 * self.L2 * self.omega1 * self.omega2 * np.cos(self.theta1 - self.theta2)
        KE = 0.5 * self.m1 * v1_sq + 0.5 * self.m2 * v2_sq
        
        # Potential energy
        PE = -(self.m1 + self.m2) * self.g * self.L1 * np.cos(self.theta1) - \
             self.m2 * self.g * self.L2 * np.cos(self.theta2)
        
        total_energy = KE + PE
        
        info = f'Time: {frame * self.dt:.1f}s\n'
        info += f'Kinetic Energy: {KE:.3f}\n'
        info += f'Potential Energy: {PE:.3f}\n'
        info += f'Total Energy: {total_energy:.3f}\n'
        info += f'θ₁: {self.theta1:.2f} rad\n'
        info += f'θ₂: {self.theta2:.2f} rad'
        
        self.info_text.set_text(info)
        
        return self.line, self.trail_line, self.mass1_circle, self.mass2_circle
    
    def run(self):
        """Start the animation"""
        anim = animation.FuncAnimation(self.fig, self.animate, frames=2000, 
                                     interval=20, blit=False, repeat=True)
        plt.show()
        return anim


class WaveInterferenceSimple:
    """Wave interference demonstration"""
    
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        
        # Wave parameters
        self.wavelength = 1.0
        self.frequency = 2.0
        self.amplitude = 1.0
        
        # Source positions
        self.source1_pos = np.array([-3, 0])
        self.source2_pos = np.array([3, 0])
        
        # Create grid
        x = np.linspace(-6, 6, 100)
        y = np.linspace(-4, 4, 80)
        self.X, self.Y = np.meshgrid(x, y)
        
        # Setup plot
        self.ax.set_xlim(-6, 6)
        self.ax.set_ylim(-4, 4)
        self.ax.set_title('Wave Interference: Two Sources', fontsize=16, color='darkblue')
        self.ax.set_xlabel('Distance (m)')
        self.ax.set_ylabel('Distance (m)')
        
        # Create colormap plot
        self.im = self.ax.imshow(np.zeros_like(self.X), extent=[-6, 6, -4, 4], 
                               cmap='RdBu', vmin=-2, vmax=2, origin='lower')
        
        # Add source markers
        self.ax.plot(self.source1_pos[0], self.source1_pos[1], 'ro', markersize=10, label='Source 1')
        self.ax.plot(self.source2_pos[0], self.source2_pos[1], 'bo', markersize=10, label='Source 2')
        self.ax.legend()
        
        # Add colorbar
        cbar = plt.colorbar(self.im, ax=self.ax)
        cbar.set_label('Wave Amplitude')
        
        self.time = 0
    
    def animate(self, frame):
        """Animation function"""
        self.time = frame * 0.05
        
        # Calculate distance from each source
        r1 = np.sqrt((self.X - self.source1_pos[0])**2 + (self.Y - self.source1_pos[1])**2)
        r2 = np.sqrt((self.X - self.source2_pos[0])**2 + (self.Y - self.source2_pos[1])**2)
        
        # Wave from each source
        wave1 = self.amplitude * np.sin(2*np.pi * (self.frequency*self.time - r1/self.wavelength))
        wave2 = self.amplitude * np.sin(2*np.pi * (self.frequency*self.time - r2/self.wavelength))
        
        # Interference (superposition)
        total_wave = wave1 + wave2
        
        # Update plot
        self.im.set_array(total_wave)
        self.ax.set_title(f'Wave Interference: t = {self.time:.1f}s', fontsize=16, color='darkblue')
        
        return [self.im]
    
    def run(self):
        """Start the animation"""
        anim = animation.FuncAnimation(self.fig, self.animate, frames=1000, 
                                     interval=50, blit=False, repeat=True)
        plt.show()
        return anim


class SpringMassSystem:
    """Simple harmonic oscillator with damping"""
    
    def __init__(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 10))
        
        # Physics parameters
        self.k = 10.0    # Spring constant
        self.m = 1.0     # Mass
        self.b = 0.5     # Damping coefficient
        self.omega0 = np.sqrt(self.k / self.m)  # Natural frequency
        
        # Initial conditions
        self.x = 1.0     # Initial displacement
        self.v = 0.0     # Initial velocity
        self.t = 0.0
        self.dt = 0.01
        
        # For plotting
        self.time_history = []
        self.position_history = []
        self.energy_history = []
        
        # Setup spring visualization
        self.ax1.set_xlim(-0.5, 3)
        self.ax1.set_ylim(-1.5, 1.5)
        self.ax1.set_title('Spring-Mass System with Damping', fontsize=14)
        self.ax1.set_aspect('equal')
        
        # Create spring (zigzag line)
        spring_x = np.linspace(0, 1, 20)
        spring_y = 0.1 * np.sin(20 * np.pi * spring_x)
        self.spring_line, = self.ax1.plot(spring_x, spring_y, 'k-', linewidth=2)
        
        # Mass
        self.mass_circle = Circle((1, 0), 0.1, color='red', zorder=10)
        self.ax1.add_patch(self.mass_circle)
        
        # Wall
        wall_x = [0, 0]
        wall_y = [-0.5, 0.5]
        self.ax1.plot(wall_x, wall_y, 'k-', linewidth=5)
        
        # Setup time series plot
        self.ax2.set_xlim(0, 20)
        self.ax2.set_ylim(-1.2, 1.2)
        self.ax2.set_xlabel('Time (s)')
        self.ax2.set_ylabel('Displacement (m)')
        self.ax2.grid(True, alpha=0.3)
        
        self.position_line, = self.ax2.plot([], [], 'b-', label='Position')
        self.energy_line, = self.ax2.plot([], [], 'r--', label='Energy/10')
        self.ax2.legend()
        
        # Info text
        self.info_text = self.ax1.text(0.02, 0.98, '', transform=self.ax1.transAxes,
                                     verticalalignment='top', fontsize=10,
                                     bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    def animate(self, frame):
        """Animation function"""
        # Physics update (damped harmonic oscillator)
        acceleration = -(self.k/self.m) * self.x - (self.b/self.m) * self.v
        
        self.v += acceleration * self.dt
        self.x += self.v * self.dt
        self.t += self.dt
        
        # Calculate energy
        kinetic_energy = 0.5 * self.m * self.v**2
        potential_energy = 0.5 * self.k * self.x**2
        total_energy = kinetic_energy + potential_energy
        
        # Store history
        self.time_history.append(self.t)
        self.position_history.append(self.x)
        self.energy_history.append(total_energy / 10)  # Scale for plotting
        
        # Limit history length
        if len(self.time_history) > 2000:
            self.time_history.pop(0)
            self.position_history.pop(0)
            self.energy_history.pop(0)
        
        # Update spring visualization
        spring_length = 1 + self.x
        spring_x = np.linspace(0, spring_length, 20)
        spring_y = 0.1 * np.sin(20 * np.pi * spring_x / spring_length)
        self.spring_line.set_data(spring_x, spring_y)
        
        # Update mass position
        self.mass_circle.center = (1 + self.x, 0)
        
        # Update time series
        self.position_line.set_data(self.time_history, self.position_history)
        self.energy_line.set_data(self.time_history, self.energy_history)
        
        # Update plot limits if needed
        if self.t > self.ax2.get_xlim()[1] - 2:
            self.ax2.set_xlim(self.t - 18, self.t + 2)
        
        # Update info
        period = 2 * np.pi / self.omega0
        info = f'Time: {self.t:.1f}s\n'
        info += f'Position: {self.x:.3f}m\n'
        info += f'Velocity: {self.v:.3f}m/s\n'
        info += f'KE: {kinetic_energy:.3f}J\n'
        info += f'PE: {potential_energy:.3f}J\n'
        info += f'Total E: {total_energy:.3f}J\n'
        info += f'Period: {period:.2f}s'
        
        self.info_text.set_text(info)
        
        return self.spring_line, self.mass_circle, self.position_line, self.energy_line
    
    def run(self):
        """Start the animation"""
        anim = animation.FuncAnimation(self.fig, self.animate, frames=5000,
                                     interval=20, blit=False, repeat=True)
        plt.show()
        return anim


class ProjectileMotion:
    """Projectile motion with air resistance and multiple trajectories"""
    
    def __init__(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Physics parameters
        self.g = 9.81        # Gravity (m/s²)
        self.air_density = 1.225  # Air density (kg/m³)
        self.drag_coefficient = 0.47  # Sphere drag coefficient
        self.projectile_radius = 0.05  # Projectile radius (m)
        self.projectile_mass = 0.145   # Baseball mass (kg)
        
        # Calculate drag constant
        self.drag_area = np.pi * self.projectile_radius**2
        self.drag_constant = 0.5 * self.air_density * self.drag_coefficient * self.drag_area
        
        # Launch parameters
        self.launch_angles = [15, 30, 45, 60, 75]  # degrees
        self.launch_speed = 25  # m/s
        self.launch_height = 1.0  # m
        
        # Simulation parameters
        self.dt = 0.01
        self.trajectories = []
        self.current_projectiles = []
        
        # Setup trajectory plot
        self.ax1.set_xlim(0, 70)
        self.ax1.set_ylim(0, 25)
        self.ax1.set_xlabel('Horizontal Distance (m)', fontsize=12)
        self.ax1.set_ylabel('Height (m)', fontsize=12)
        self.ax1.set_title('Projectile Motion: Multiple Launch Angles', fontsize=14, color='darkgreen')
        self.ax1.grid(True, alpha=0.3)
        
        # Add ground
        ground = Rectangle((0, 0), 70, 0.2, color='brown', alpha=0.8)
        self.ax1.add_patch(ground)
        
        # Setup comparison plot (range vs angle)
        self.ax2.set_xlim(0, 90)
        self.ax2.set_ylim(0, 70)
        self.ax2.set_xlabel('Launch Angle (degrees)', fontsize=12)
        self.ax2.set_ylabel('Range (m)', fontsize=12)
        self.ax2.set_title('Range vs Launch Angle', fontsize=14, color='darkblue')
        self.ax2.grid(True, alpha=0.3)
        
        # Theoretical curve (no air resistance)
        angles_theory = np.linspace(5, 85, 100)
        ranges_theory = (self.launch_speed**2 * np.sin(2 * np.radians(angles_theory))) / self.g
        self.ax2.plot(angles_theory, ranges_theory, 'k--', linewidth=2, 
                     label='No Air Resistance (Theory)', alpha=0.7)
        
        # Colors for different angles
        self.colors = ['red', 'orange', 'green', 'blue', 'purple']
        
        # Initialize trajectories
        self.reset_simulation()
        
        # Info text
        self.info_text = self.ax1.text(0.02, 0.98, '', transform=self.ax1.transAxes,
                                     verticalalignment='top', fontsize=10,
                                     bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
        
        # Legend
        self.ax2.legend()
    
    def reset_simulation(self):
        """Reset all projectiles"""
        self.trajectories = []
        self.current_projectiles = []
        
        for i, angle in enumerate(self.launch_angles):
            angle_rad = np.radians(angle)
            
            # Initial conditions
            projectile = {
                'x': 0,
                'y': self.launch_height,
                'vx': self.launch_speed * np.cos(angle_rad),
                'vy': self.launch_speed * np.sin(angle_rad),
                'angle': angle,
                'color': self.colors[i],
                'trajectory_x': [0],
                'trajectory_y': [self.launch_height],
                'active': True,
                'max_height': self.launch_height,
                'range': 0,
                'flight_time': 0
            }
            
            self.current_projectiles.append(projectile)
    
    def update_physics(self, projectile):
        """Update projectile physics with air resistance"""
        if not projectile['active']:
            return
        
        # Current velocity magnitude
        v_mag = np.sqrt(projectile['vx']**2 + projectile['vy']**2)
        
        # Air resistance force components
        if v_mag > 0:
            drag_force = self.drag_constant * v_mag**2 / self.projectile_mass
            drag_x = -drag_force * (projectile['vx'] / v_mag)
            drag_y = -drag_force * (projectile['vy'] / v_mag)
        else:
            drag_x = drag_y = 0
        
        # Acceleration components
        ax = drag_x
        ay = -self.g + drag_y
        
        # Update velocity
        projectile['vx'] += ax * self.dt
        projectile['vy'] += ay * self.dt
        
        # Update position
        projectile['x'] += projectile['vx'] * self.dt
        projectile['y'] += projectile['vy'] * self.dt
        
        # Update trajectory
        projectile['trajectory_x'].append(projectile['x'])
        projectile['trajectory_y'].append(projectile['y'])
        
        # Update max height
        if projectile['y'] > projectile['max_height']:
            projectile['max_height'] = projectile['y']
        
        # Update flight time
        projectile['flight_time'] += self.dt
        
        # Check if projectile hits ground
        if projectile['y'] <= 0 and projectile['active']:
            projectile['active'] = False
            projectile['range'] = projectile['x']
            projectile['y'] = 0  # Ensure it's exactly on ground
    
    def animate(self, frame):
        """Animation function"""
        # Clear previous frame
        self.ax1.clear()
        
        # Reset plot settings
        self.ax1.set_xlim(0, 70)
        self.ax1.set_ylim(0, 25)
        self.ax1.set_xlabel('Horizontal Distance (m)', fontsize=12)
        self.ax1.set_ylabel('Height (m)', fontsize=12)
        self.ax1.set_title('Projectile Motion: Multiple Launch Angles', fontsize=14, color='darkgreen')
        self.ax1.grid(True, alpha=0.3)
        
        # Add ground
        ground = Rectangle((0, 0), 70, 0.2, color='brown', alpha=0.8)
        self.ax1.add_patch(ground)
        
        # Update physics for all projectiles
        for projectile in self.current_projectiles:
            self.update_physics(projectile)
        
        # Draw trajectories and current positions
        active_projectiles = 0
        info_lines = []
        
        for i, projectile in enumerate(self.current_projectiles):
            # Draw trajectory
            self.ax1.plot(projectile['trajectory_x'], projectile['trajectory_y'], 
                         color=projectile['color'], linewidth=2, alpha=0.7,
                         label=f"{projectile['angle']}°")
            
            # Draw current position if active
            if projectile['active']:
                active_projectiles += 1
                # Projectile
                circle = Circle((projectile['x'], projectile['y']), 0.3, 
                              color=projectile['color'], zorder=10)
                self.ax1.add_patch(circle)
                
                # Velocity vector (scaled for visibility)
                if frame % 3 == 0:  # Update every few frames for clarity
                    scale = 0.5
                    arrow = FancyArrowPatch(
                        (projectile['x'], projectile['y']),
                        (projectile['x'] + projectile['vx']*scale, 
                         projectile['y'] + projectile['vy']*scale),
                        arrowstyle='->', mutation_scale=15,
                        color=projectile['color'], alpha=0.8
                    )
                    self.ax1.add_patch(arrow)
            
            # Collect info for display
            if projectile['active']:
                status = "Flying"
                range_text = f"{projectile['x']:.1f}m"
            else:
                status = "Landed"
                range_text = f"{projectile['range']:.1f}m"
            
            info_lines.append(f"{projectile['angle']}°: {status}, Range: {range_text}")
        
        # Update range vs angle plot
        if frame == 1:  # Initialize once
            self.ax2.clear()
            self.ax2.set_xlim(0, 90)
            self.ax2.set_ylim(0, 70)
            self.ax2.set_xlabel('Launch Angle (degrees)', fontsize=12)
            self.ax2.set_ylabel('Range (m)', fontsize=12)
            self.ax2.set_title('Range vs Launch Angle', fontsize=14, color='darkblue')
            self.ax2.grid(True, alpha=0.3)
            
            # Theoretical curve
            angles_theory = np.linspace(5, 85, 100)
            ranges_theory = (self.launch_speed**2 * np.sin(2 * np.radians(angles_theory))) / self.g
            self.ax2.plot(angles_theory, ranges_theory, 'k--', linewidth=2, 
                         label='No Air Resistance', alpha=0.7)
        
        # Plot completed ranges
        completed_angles = []
        completed_ranges = []
        for projectile in self.current_projectiles:
            if not projectile['active'] and projectile['range'] > 0:
                completed_angles.append(projectile['angle'])
                completed_ranges.append(projectile['range'])
        
        if completed_ranges:
            self.ax2.scatter(completed_angles, completed_ranges, 
                           c=[self.colors[self.launch_angles.index(a)] for a in completed_angles],
                           s=100, alpha=0.8, label='With Air Resistance', zorder=10)
        
        # Add legend if we have data
        if completed_ranges:
            self.ax2.legend()
        
        # Update info text
        info_text = f"Time: {frame * self.dt:.1f}s\n"
        info_text += f"Active Projectiles: {active_projectiles}\n"
        info_text += f"Launch Speed: {self.launch_speed}m/s\n"
        info_text += f"Launch Height: {self.launch_height}m\n\n"
        info_text += "\n".join(info_lines)
        
        self.info_text = self.ax1.text(0.02, 0.98, info_text, transform=self.ax1.transAxes,
                                     verticalalignment='top', fontsize=9,
                                     bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
        
        # Reset if all projectiles have landed
        if active_projectiles == 0 and frame > 100:
            if frame % 300 == 0:  # Reset every 3 seconds after landing
                self.reset_simulation()
        
        # Add legend to trajectory plot
        if frame < 50:  # Show legend early in animation
            self.ax1.legend(loc='upper right', fontsize=10)
        
        return []
    
    def run(self):
        """Start the animation"""
        anim = animation.FuncAnimation(self.fig, self.animate, frames=2000,
                                     interval=30, blit=False, repeat=True)
        plt.tight_layout()
        plt.show()
        return anim


def main():
    """Run physics demonstrations"""
    print("🎯 Cool Physics Demonstrations")
    print("=" * 40)
    print("1. Double Pendulum (Chaos)")
    print("2. Wave Interference")
    print("3. Spring-Mass System")
    print("4. Projectile Motion")
    print("5. Run all demos")
    
    choice = input("\nChoose a demo (1-5): ").strip()
    
    if choice == '1':
        print("🔄 Starting Double Pendulum simulation...")
        demo = DoublePendulumSimple()
        demo.run()
    
    elif choice == '2':
        print("🌊 Starting Wave Interference simulation...")
        demo = WaveInterferenceSimple()
        demo.run()
    
    elif choice == '3':
        print("🔄 Starting Spring-Mass System simulation...")
        demo = SpringMassSystem()
        demo.run()
    
    elif choice == '4':
        print("🎯 Starting Projectile Motion simulation...")
        demo = ProjectileMotion()
        demo.run()
    
    elif choice == '5':
        print("🚀 Running all demos sequentially...")
        demos = [DoublePendulumSimple(), WaveInterferenceSimple(), SpringMassSystem(), ProjectileMotion()]
        for i, demo in enumerate(demos, 1):
            print(f"Running demo {i}/4...")
            demo.run()
    
    else:
        print("Invalid choice. Running Double Pendulum by default...")
        demo = DoublePendulumSimple()
        demo.run()


if __name__ == "__main__":
    main()
