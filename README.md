# FishNet

<p align="center">
  <img src="https://img.shields.io/github/stars/randysim/fish-net?style=for-the-badge" alt="GitHub Repo stars">
  <img src="https://img.shields.io/github/forks/randysim/fish-net?style=for-the-badge" alt="GitHub forks">
  <img src="https://img.shields.io/github/issues/randysim/fish-net?style=for-the-badge" alt="GitHub issues">
  <img src="https://img.shields.io/github/license/randysim/fish-net?style=for-the-badge" alt="GitHub license">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python">
</p>

FishNet is an advanced automated fishing script designed for Arcane Odyssey. It utilizes computer vision techniques to detect fishing indicators and automate the fishing process, providing an efficient and hands-free fishing experience.

## How It Works

![FishNet Diagram](https://github.com/randysim/fish-net/blob/main/resource/FishNetDiagram.png)

FishNet employs sophisticated image recognition algorithms to identify fishing indicators on the screen. By analyzing the visual cues, it accurately determines the optimal moment to reel in your catch, maximizing your fishing efficiency.

## Installation and Usage

To get started with FishNet, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/randysim/fish-net.git
   ```

2. Navigate to the project directory:
   ```bash
   cd fish-net
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment (windows):
   ```bash
   venv\Scripts\activate
   ```

5. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Run the script:
   ```bash
   python main.py
   ```

## Keybinds and Configuration

- **Ctrl + F1**: Toggle the script on/off
- **Ctrl + Q**: Quit the script

You can customize the script's behavior by editing the `config.json` file.

## Setup

Ensure your character's head is positioned at the center of the screen, with the fishing indicator touching or slightly above the top edge. This positioning is crucial for optimal performance of the auto-eat and auto-fish features.

## Edge Cases and Precautions

While FishNet is designed to handle most fishing scenarios, there are a few edge cases to be aware of:

- **Inventory Management**: Occasionally, a weapon might occupy a food slot, causing unexpected movement. Choose a safe fishing spot to prevent falling.
- **Large Fish**: Big catches may land in front of your character, requiring manual intervention to move them.
- **Environmental Factors**: Lightning, weather effects, or player abilities might interfere with detection or cause false positives. For instance, cold environments with blue tints may affect indicator recognition.
- **Safety Precautions**: Large fish have the potential to knock your character off platforms. Always fish from a secure location.

By being mindful of these scenarios, you can ensure a smooth and effective fishing experience with FishNet. Happy fishing!

<p align="center">
    <img src=https://github.com/randysim/fish-net/blob/main/resource/fishnet_pfp.png alt="FishNet Logo" width="175" height="175">
</p>