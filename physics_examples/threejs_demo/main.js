/**
 * 3D Circular Motion to Sine Wave Visualization
 * Using Three.js for stunning 3D graphics and physics
 */

class PhysicsVisualization {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.animationId = null;
        
        // Physics parameters
        this.time = 0;
        this.angularVelocity = 1.0;
        this.circleRadius = 2.0;
        this.waveAmplitude = 2.0;
        this.waveLength = 100;
        this.isPaused = false;
        
        // 3D objects
        this.sphere = null;
        this.circle = null;
        this.projectionLine = null;
        this.sineWave = null;
        this.waveTrail = [];
        this.maxTrailLength = 200;
        
        // Initialize
        this.init();
        this.setupControls();
        this.animate();
        
        // Hide loading screen
        setTimeout(() => {
            document.getElementById('loading').style.display = 'none';
        }, 1000);
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a0a);
        
        // Create camera
        this.camera = new THREE.PerspectiveCamera(
            75, 
            window.innerWidth / window.innerHeight, 
            0.1, 
            1000
        );
        this.camera.position.set(8, 4, 8);
        this.camera.lookAt(0, 0, 0);
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true 
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        document.getElementById('container').appendChild(this.renderer.domElement);
        
        // Add lights
        this.setupLights();
        
        // Create 3D objects
        this.createCircle();
        this.createSphere();
        this.createAxes();
        this.createSineWave();
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
    }
    
    setupLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Accent lights for visual appeal
        const light1 = new THREE.PointLight(0xff6b6b, 0.5, 20);
        light1.position.set(-5, 3, 0);
        this.scene.add(light1);
        
        const light2 = new THREE.PointLight(0x4ecdc4, 0.5, 20);
        light2.position.set(5, -3, 0);
        this.scene.add(light2);
    }
    
    createCircle() {
        // Create circle geometry
        const geometry = new THREE.RingGeometry(this.circleRadius - 0.05, this.circleRadius + 0.05, 64);
        const material = new THREE.MeshBasicMaterial({ 
            color: 0x666666,
            transparent: true,
            opacity: 0.8,
            side: THREE.DoubleSide
        });
        
        this.circle = new THREE.Mesh(geometry, material);
        this.circle.rotation.x = Math.PI / 2; // Rotate to horizontal
        this.scene.add(this.circle);
        
        // Add circle outline for better visibility
        const outlineGeometry = new THREE.RingGeometry(this.circleRadius - 0.02, this.circleRadius + 0.02, 64);
        const outlineMaterial = new THREE.MeshBasicMaterial({ 
            color: 0xffffff,
            transparent: true,
            opacity: 0.3,
            side: THREE.DoubleSide
        });
        const outline = new THREE.Mesh(outlineGeometry, outlineMaterial);
        outline.rotation.x = Math.PI / 2;
        this.scene.add(outline);
    }
    
    createSphere() {
        // Create sphere (the moving object)
        const geometry = new THREE.SphereGeometry(0.15, 32, 32);
        const material = new THREE.MeshPhongMaterial({ 
            color: 0xff6b6b,
            shininess: 100,
            transparent: true,
            opacity: 0.9
        });
        
        this.sphere = new THREE.Mesh(geometry, material);
        this.sphere.castShadow = true;
        this.scene.add(this.sphere);
        
        // Add glow effect
        const glowGeometry = new THREE.SphereGeometry(0.2, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({
            color: 0xff6b6b,
            transparent: true,
            opacity: 0.3
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        this.sphere.add(glow);
    }
    
    createAxes() {
        // Create coordinate axes
        const axesHelper = new THREE.AxesHelper(4);
        axesHelper.material.transparent = true;
        axesHelper.material.opacity = 0.6;
        this.scene.add(axesHelper);
        
        // Add grid
        const gridHelper = new THREE.GridHelper(10, 20, 0x333333, 0x333333);
        gridHelper.material.transparent = true;
        gridHelper.material.opacity = 0.3;
        this.scene.add(gridHelper);
    }
    
    createSineWave() {
        // Create initial sine wave
        this.updateSineWave();
    }
    
    updateSineWave() {
        // Remove existing sine wave
        if (this.sineWave) {
            this.scene.remove(this.sineWave);
        }
        
        // Create new sine wave geometry
        const points = [];
        for (let i = 0; i < this.waveLength; i++) {
            const x = (i / this.waveLength) * 8 - 4; // Spread from -4 to 4
            const y = this.waveAmplitude * Math.sin((i / this.waveLength) * 4 * Math.PI - this.time);
            const z = 3; // Position behind the circle
            points.push(new THREE.Vector3(x, y, z));
        }
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ 
            color: 0x4ecdc4,
            linewidth: 3,
            transparent: true,
            opacity: 0.8
        });
        
        this.sineWave = new THREE.Line(geometry, material);
        this.scene.add(this.sineWave);
    }
    
    updateProjectionLine() {
        // Remove existing projection line
        if (this.projectionLine) {
            this.scene.remove(this.projectionLine);
        }
        
        // Calculate sphere position
        const angle = this.time * this.angularVelocity;
        const sphereX = this.circleRadius * Math.cos(angle);
        const sphereY = this.circleRadius * Math.sin(angle);
        
        // Create projection line from sphere to sine wave
        const points = [
            new THREE.Vector3(sphereX, sphereY, 0),
            new THREE.Vector3(-4, sphereY, 3) // Project to start of sine wave
        ];
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({ 
            color: 0xffff00,
            linewidth: 2,
            transparent: true,
            opacity: 0.7
        });
        
        this.projectionLine = new THREE.Line(geometry, material);
        this.scene.add(this.projectionLine);
    }
    
    updateTrail() {
        // Add current sphere position to trail
        const angle = this.time * this.angularVelocity;
        const x = (this.time * 0.5) % 8 - 4; // Moving x position
        const y = this.waveAmplitude * Math.sin(angle);
        const z = 3;
        
        this.waveTrail.push(new THREE.Vector3(x, y, z));
        
        // Limit trail length
        if (this.waveTrail.length > this.maxTrailLength) {
            this.waveTrail.shift();
        }
        
        // Remove existing trail
        const existingTrail = this.scene.getObjectByName('waveTrail');
        if (existingTrail) {
            this.scene.remove(existingTrail);
        }
        
        // Create new trail
        if (this.waveTrail.length > 1) {
            const geometry = new THREE.BufferGeometry().setFromPoints(this.waveTrail);
            const material = new THREE.LineBasicMaterial({ 
                color: 0x00ff88,
                linewidth: 2,
                transparent: true,
                opacity: 0.9
            });
            
            const trail = new THREE.Line(geometry, material);
            trail.name = 'waveTrail';
            this.scene.add(trail);
        }
    }
    
    setupControls() {
        // Speed control
        const speedSlider = document.getElementById('speed');
        const speedValue = document.getElementById('speedValue');
        speedSlider.addEventListener('input', (e) => {
            this.angularVelocity = parseFloat(e.target.value);
            speedValue.textContent = `${this.angularVelocity.toFixed(1)} rad/s`;
        });
        
        // Radius control
        const radiusSlider = document.getElementById('radius');
        const radiusValue = document.getElementById('radiusValue');
        radiusSlider.addEventListener('input', (e) => {
            this.circleRadius = parseFloat(e.target.value);
            radiusValue.textContent = `${this.circleRadius.toFixed(1)} units`;
            this.updateCircle();
        });
        
        // Amplitude control
        const amplitudeSlider = document.getElementById('amplitude');
        const amplitudeValue = document.getElementById('amplitudeValue');
        amplitudeSlider.addEventListener('input', (e) => {
            this.waveAmplitude = parseFloat(e.target.value);
            amplitudeValue.textContent = `${this.waveAmplitude.toFixed(1)} units`;
        });
        
        // Wave length control
        const waveLengthSlider = document.getElementById('waveLength');
        const waveLengthValue = document.getElementById('waveLengthValue');
        waveLengthSlider.addEventListener('input', (e) => {
            this.waveLength = parseInt(e.target.value);
            waveLengthValue.textContent = `${this.waveLength} points`;
        });
        
        // Reset button
        document.getElementById('resetButton').addEventListener('click', () => {
            this.time = 0;
            this.waveTrail = [];
        });
        
        // Pause button
        document.getElementById('pauseButton').addEventListener('click', () => {
            this.isPaused = !this.isPaused;
            document.getElementById('pauseButton').textContent = 
                this.isPaused ? 'Resume' : 'Pause';
        });
    }
    
    updateCircle() {
        // Remove existing circle
        if (this.circle) {
            this.scene.remove(this.circle);
        }
        
        // Create new circle with updated radius
        const geometry = new THREE.RingGeometry(
            this.circleRadius - 0.05, 
            this.circleRadius + 0.05, 
            64
        );
        const material = new THREE.MeshBasicMaterial({ 
            color: 0x666666,
            transparent: true,
            opacity: 0.8,
            side: THREE.DoubleSide
        });
        
        this.circle = new THREE.Mesh(geometry, material);
        this.circle.rotation.x = Math.PI / 2;
        this.scene.add(this.circle);
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        if (!this.isPaused) {
            this.time += 0.016; // ~60 FPS
            
            // Update sphere position
            const angle = this.time * this.angularVelocity;
            this.sphere.position.x = this.circleRadius * Math.cos(angle);
            this.sphere.position.y = this.circleRadius * Math.sin(angle);
            this.sphere.position.z = 0;
            
            // Rotate sphere for visual effect
            this.sphere.rotation.y += 0.1;
            
            // Update sine wave
            this.updateSineWave();
            
            // Update projection line
            this.updateProjectionLine();
            
            // Update trail
            this.updateTrail();
            
            // Auto-rotate camera for cinematic effect
            const cameraRadius = 10;
            const cameraAngle = this.time * 0.1;
            this.camera.position.x = cameraRadius * Math.cos(cameraAngle);
            this.camera.position.z = cameraRadius * Math.sin(cameraAngle);
            this.camera.lookAt(0, 0, 0);
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        // Clean up Three.js objects
        this.scene.traverse((object) => {
            if (object.geometry) {
                object.geometry.dispose();
            }
            if (object.material) {
                if (Array.isArray(object.material)) {
                    object.material.forEach(material => material.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });
        
        this.renderer.dispose();
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.physicsViz = new PhysicsVisualization();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (window.physicsViz) {
        window.physicsViz.destroy();
    }
});
