#!/bin/bash

echo "🔧 Installing Manim on macOS - Fixing Cairo dependencies"
echo "=================================================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "✅ Homebrew found"
fi

# Update Homebrew
echo "🔄 Updating Homebrew..."
brew update

# Install required system dependencies
echo "📦 Installing Cairo and related dependencies..."
brew install cairo
brew install pkg-config
brew install ffmpeg

# Optional but recommended for better performance
echo "📦 Installing additional graphics libraries..."
brew install pango
brew install glib
brew install fontconfig

echo "🐍 Installing Python packages..."

# Install Manim with specific versions that work well together
pip install --upgrade pip
pip install wheel setuptools

# Install Cairo Python bindings first
pip install pycairo

# Install Manim
pip install manim

# Install physics extension
pip install manim-physics

echo "✅ Installation complete!"
echo ""
echo "🧪 Testing installation..."
python -c "import manim; print('Manim version:', manim.__version__)"
python -c "import manim_physics; print('Manim-physics imported successfully!')"

echo ""
echo "🚀 Ready to create physics animations!"
echo "Try running: manim double_pendulum.py DoublePendulum -pql"
