import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import matplotlib.animation as animation

def read_floorplan(flp_filename):
    """Parses the .flp file into a dictionary of dimensions."""
    blocks = {}
    with open(flp_filename, "r") as fp:
        for line in fp:
            if line.strip() == "" or line.startswith('#'):
                continue
            parts = line.split()
            name = parts[0]
            width = float(parts[1])
            height = float(parts[2])
            x = float(parts[3])
            y = float(parts[4])
            blocks[name] = {'w': width, 'h': height, 'x': x, 'y': y}
    return blocks

def main(flp_filename, ttrace_filename):
    # 1. Parse Data
    print(f"Reading floorplan: {flp_filename}...")
    blocks = read_floorplan(flp_filename)
    
    print(f"Reading trace file: {ttrace_filename}...")
    df = pd.read_csv(ttrace_filename, delim_whitespace=True)
    
    # Filter columns to only include blocks that actually exist in the floorplan
    valid_names = [col for col in df.columns if col in blocks]
    
    # Convert temperatures from Kelvin to Celsius if they are > 200
    if df[valid_names].iloc[0].mean() > 200:
        df[valid_names] -= 273.15
        temp_unit = "°C"
    else:
        temp_unit = "K (Relative to Ambient)"

    # 2. Setup Figure (Explicitly setting white backgrounds)
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
    ax.set_facecolor('white')
    
    max_x = max(b['x'] + b['w'] for b in blocks.values())
    max_y = max(b['y'] + b['h'] for b in blocks.values())
    
    # Add a tiny bit of padding (2%) so the heatmap doesn't touch the exact edge of the window
    padding_x = max_x * 0.02
    padding_y = max_y * 0.02
    ax.set_xlim(-padding_x, max_x + padding_x)
    ax.set_ylim(-padding_y, max_y + padding_y)
    
    ax.set_aspect('equal')
    ax.set_xlabel("X (m)", fontsize=12)
    ax.set_ylabel("Y (m)", fontsize=12)
    
    # 3. Create Rectangles (Patches)
    rects = []
    for name in valid_names:
        b = blocks[name]
        rect = patches.Rectangle((b['x'], b['y']), b['w'], b['h'])
        rects.append(rect)
        
    # Create PatchCollection
    # CHANGED: 'turbo' gives the classic blue->green->red heatmap look.
    # CHANGED: edgecolor='none' removes the black borders for a smooth heatmap
    pc = PatchCollection(rects, cmap='OrRd', edgecolor='none')
    
    # Set color scale limits based on the min and max of the ENTIRE trace
    global_min = df[valid_names].min().min()
    global_max = df[valid_names].max().max()
    pc.set_clim(vmin=global_min, vmax=global_max)
    
    ax.add_collection(pc)
    
    # Format the colorbar
    cbar = plt.colorbar(pc, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(f'Temperature ({temp_unit})', fontsize=12)

    # 4. Save Static Image for t = 0
    print("Generating static image for t=0...")
    t0_temps = df[valid_names].iloc[0].values
    pc.set_array(t0_temps)
    ax.set_title("Initial Thermal Map (t=0)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("hotspot_t0.png", dpi=300, facecolor='white')
    print("Saved 'hotspot_t0.png'")

    # 5. Create Animation
    print(f"Generating animation for {len(df)} frames... (This may take a minute)")
    
    def update(frame):
        temps = df[valid_names].iloc[frame].values
        pc.set_array(temps)
        ax.set_title(f"Thermal Map - Step {frame}", fontsize=14, fontweight='bold')
        return pc,
        
    anim = animation.FuncAnimation(
        fig, update, frames=len(df), interval=50, blit=False
    )
    
    gif_name = "hotspot_animation.gif"
    
    # Enforce a white background when saving the animation
    anim.save(gif_name, writer='pillow', fps=20, savefig_kwargs={'facecolor':'white'})
    print(f"Saved animation to '{gif_name}'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python animate_hotspots.py <flp_file> <ttrace_file>")
        sys.exit(1)
        
    flp_file = sys.argv[1]
    ttrace_file = sys.argv[2]
    
    main(flp_file, ttrace_file)

