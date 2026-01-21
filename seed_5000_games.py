import os
from pathlib import Path
from src.database import initialize_database
from src.game_repository import GameRepository

def seed_data():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    db_path = data_dir / "game_launcher.db"
    
    initialize_database(str(db_path))
    repo = GameRepository(str(db_path))
    
    print(f"Seeding 5000 games into {db_path}...")
    
    # 大量投入
    for i in range(1, 5001):
        game_data = {
            "title": f"Test Game {i:04d}",
            "description": f"This is a performance test game entry number {i}.",
            "image_path": "res/icon.png",
            "executable_path": "C:/Windows/notepad.exe",
            "pre_command": "",
            "post_command": "",
            "save_folder": "",
            "sync_enabled": 0,
            "remote_sync_path": ""
        }
        repo.add_game(game_data)
        if i % 1000 == 0:
            print(f"Inserted {i} games...")

    print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
