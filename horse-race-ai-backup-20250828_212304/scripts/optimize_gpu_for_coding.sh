#!/bin/bash
# 🚀 NVIDIA GPU Optimization for Coding Models & GitHub Copilot
# System: Intel i7-9750H, GTX 1650 4GB, 16GB RAM

echo "🔧 Optimizing NVIDIA GTX 1650 for AI Coding Models..."

# 1. Set GPU to Performance Mode
echo "Setting GPU to performance mode..."
sudo nvidia-settings -a '[gpu:0]/GPUPowerMizerMode=1' 2>/dev/null || echo "Note: nvidia-settings may require GUI"

# 2. Optimize GPU Memory and Power
echo "Optimizing GPU settings..."
sudo nvidia-smi -pl 50  # Set power limit to maximum (50W for GTX 1650)
sudo nvidia-smi -lgc 1395,1560  # Lock GPU clocks for consistency

# 3. System Memory Optimization
echo "Optimizing system memory..."
# Increase swap priority for AI workloads
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf

# 4. Ollama Optimization Settings
echo "Creating Ollama optimization config..."
mkdir -p ~/.ollama
cat > ~/.ollama/config.json << EOF
{
  "gpu_memory_fraction": 0.8,
  "num_thread": 6,
  "numa_node": 0,
  "use_mlock": true,
  "low_vram": true
}
EOF

# 5. Environment Variables for AI Models
echo "Setting environment variables..."
cat >> ~/.bashrc << 'EOF'

# 🤖 AI Coding Models Optimization
export CUDA_VISIBLE_DEVICES=0
export OLLAMA_GPU_OVERHEAD=512  # Reserve 512MB for system
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_NUM_PARALLEL=1    # Limit concurrent models for 4GB VRAM
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export TF_GPU_ALLOCATOR=cuda_malloc_async
export TOKENIZERS_PARALLELISM=true

# GitHub Copilot Optimization
export NODE_OPTIONS="--max-old-space-size=4096"
export VSCODE_DISABLE_CRASH_REPORTER=true
EOF

# 6. Create Ollama Service Override for Performance
echo "Creating Ollama service optimization..."
sudo mkdir -p /etc/systemd/system/ollama.service.d/
cat << EOF | sudo tee /etc/systemd/system/ollama.service.d/override.conf > /dev/null
[Service]
Environment="OLLAMA_GPU_OVERHEAD=512"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="CUDA_VISIBLE_DEVICES=0"
LimitNOFILE=1048576
LimitNPROC=1048576
PrivateTmp=false
EOF

# 7. Restart Ollama with new settings
echo "Restarting Ollama with optimizations..."
sudo systemctl daemon-reload
sudo systemctl restart ollama

# 8. Install CUDA toolkit if needed (lightweight version)
if ! command -v nvcc &> /dev/null; then
    echo "Installing minimal CUDA toolkit..."
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.0-1_all.deb
    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo apt-get update
    sudo apt-get install -y cuda-toolkit-12-4
fi

echo "✅ Optimization complete!"
echo ""
echo "📊 Current GPU Status:"
nvidia-smi --query-gpu=name,memory.used,memory.free,utilization.gpu,temperature.gpu --format=csv,noheader,nounits

echo ""
echo "🎯 Optimizations Applied:"
echo "  ✅ GPU set to performance mode"
echo "  ✅ Power limit maximized (50W)"
echo "  ✅ Memory settings optimized for AI workloads"
echo "  ✅ Ollama configured for 4GB VRAM"
echo "  ✅ Environment variables set for coding models"
echo "  ✅ GitHub Copilot memory optimized"
echo ""
echo "🔄 Please run 'source ~/.bashrc' or restart terminal for environment changes"
echo "💡 Recommended: Restart VS Code for GitHub Copilot optimizations"
