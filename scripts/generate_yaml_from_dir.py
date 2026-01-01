import os
import argparse
import numpy as np
import yaml
from pathlib import Path

def create_motion_entry(
    motion_file: str, end_time: float, fps: float, idx: int
) -> dict:
    """Create a motion entry for the YAML file"""
    motion_entry = {
        "file": motion_file,
        "fps": float(fps),
        "weight": 1.0,
        "idx": idx,
    }
    if end_time is not None:
        end_time = float(end_time)
        sub_motions = [{"timings": {"start": 0.0, "end": end_time}}]
        motion_entry["sub_motions"] = sub_motions
    return motion_entry

def main():
    parser = argparse.ArgumentParser(description="Generate YAML from motion directory")
    parser.add_argument("--input_dir", type=str, required=True, help="Input directory containing motion files")
    parser.add_argument("--output_file", type=str, required=True, help="Output YAML file path")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_file = Path(args.output_file)

    motions = []
    idx = 0
    
    print(f"Scanning {input_dir}...")

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".npz") and not file.endswith("stagei.npz") and not file.endswith("shape.npz"):
                full_path = os.path.join(root, file)
                
                motion_path_entry = os.path.abspath(full_path)
                
                motion_path_entry = (
                    motion_path_entry.replace(".npz", ".motion")
                    .replace("-", "_")
                    .replace(" ", "_")
                    .replace("(", "_")
                    .replace(")", "_")
                )
                
                try:
                    data = np.load(full_path)
                    
                    if "mocap_framerate" in data:
                        fps = float(data["mocap_framerate"])
                    elif "mocap_frame_rate" in data:
                        fps = float(data["mocap_frame_rate"])
                    else:
                        print(f"Warning: No FPS found in {file}, skipping.")
                        continue
                        
                    if "poses" in data:
                        num_frames = data["poses"].shape[0]
                        duration = num_frames / fps
                    else:
                        print(f"Warning: No poses found in {file}, skipping.")
                        continue
                    
                    entry = create_motion_entry(motion_path_entry, duration, fps, idx)
                    motions.append(entry)
                    idx += 1
                    
                except Exception as e:
                    print(f"Error processing {file}: {e}")
                    continue

    yaml_data = {"motions": motions}
    
    os.makedirs(output_file.parent, exist_ok=True)
    
    with open(output_file, "w") as f:
        yaml.dump(yaml_data, f, sort_keys=False)
        
    print(f"Generated YAML with {len(motions)} entries at {output_file}")

if __name__ == "__main__":
    main()
