import sys
import os
import subprocess

def main():
    username = input("Enter the Chess.com username to process: ").strip().lower()
    data_folder = username
    root_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(root_dir, "scripts")
    data_dir = os.path.join(root_dir, "data")

    connection_to_db_path = os.path.join(scripts_dir, "connection_to_database.py")
    dates_path = os.path.join(data_dir, "dates.py")
    opening_db_path = os.path.join(data_dir, "openingdatabase.py")
    analyze_data_path = os.path.join(scripts_dir, "analyze_data.py")
    visualize_path = os.path.join(scripts_dir, "visualize.py")

    # print("--- Path Debugging ---")
    # print(f"Root Directory: {root_dir}")
    # print(f"Scripts Directory: {scripts_dir}")
    # print(f"Data Directory: {data_dir}")
    # print(f"Connection to DB Path: {connection_to_db_path}")
    # print(f"Dates Path: {dates_path}")
    # print(f"Opening Database Path: {opening_db_path}")
    # print(f"Analyze Data Path: {analyze_data_path}")
    # print(f"Visualize Path: {visualize_path}")
    # print("----------------------")

    # Step 1: Connect to database and potentially insert initial data
    print(f"🔄 Running {os.path.basename(connection_to_db_path)} for {username}...")
    subprocess.run([sys.executable, connection_to_db_path, username])
    print(f"✅ {os.path.basename(connection_to_db_path)} complete.")

    # Step 2: Extract dates from PGNs
    print(f"\n🗓️ Running {os.path.basename(dates_path)} for {username}...")
    subprocess.run([sys.executable, dates_path, username])
    print(f"✅ {os.path.basename(dates_path)} complete.")

    # Step 3: Update database with opening data
    print("\n♟️ Running opening database update...")
    subprocess.run([sys.executable, opening_db_path])
    print(f"✅ {os.path.basename(opening_db_path)} complete.")

    # Step 4: Analyze data
    print(f"\n📊 Running {os.path.basename(analyze_data_path)} for {username}, folder: {data_folder}...")
    subprocess.run([sys.executable, analyze_data_path, username, data_folder])
    print(f"✅ {os.path.basename(analyze_data_path)} complete.")

    # Step 5: Visualize data
    print(f"\n📈 Running {os.path.basename(visualize_path)} for {username}, folder: {data_folder}...")
    subprocess.run([sys.executable, visualize_path, username, data_folder])
    print(f"✅ {os.path.basename(visualize_path)} complete.")

    print("\n✨ Project workflow complete.")

if __name__ == "__main__":
    main()