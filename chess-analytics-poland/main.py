import sys
import os
import subprocess

# Ensures all imports in chess-analytics-poland/ work no matter where main.py is run from
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


def main():
    username = input("Enter the Chess.com username to process: ").strip().lower()
    data_folder = username
    root_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(root_dir, "scripts")
    data_dir = os.path.join(root_dir, "data")
    # chess_web_viz_dir = os.path.join(root_dir, "chess_web_viz")
    # app_path = os.path.join(chess_web_viz_dir, "app.py")

    connection_to_db_path = os.path.join(scripts_dir, "connection_to_database.py")
    dates_path = os.path.join(data_dir, "dates.py")
    opening_db_path = os.path.join(data_dir, "openingdatabase.py")
    analyze_data_path = os.path.join(scripts_dir, "analyze_data.py")
    visualize_path = os.path.join(scripts_dir, "visualize.py")

    # print("--- Path Debugging ---")
    # print(f"Root Directory: {root_dir}")
    # print(f"Scripts Directory: {scripts_dir}")
    # print(f"Data Directory: {data_dir}")
    # print(f"Chess Web Viz Directory: {chess_web_viz_dir}")
    # print(f"Flask App Path: {app_path}")
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
    subprocess.run([sys.executable, opening_db_path, username]) # Pass username
    print(f"✅ {os.path.basename(opening_db_path)} complete.")

    # Step 4: Analyze data
    print(f"\n📊 Running {os.path.basename(analyze_data_path)} for {username}, folder: {data_folder}...")
    subprocess.run([sys.executable, analyze_data_path, username, data_folder])
    print(f"✅ {os.path.basename(analyze_data_path)} complete.")

    # Step 5: Visualize data (optional - if you still want the CLI plots)
    print(f"\n📈 Running {os.path.basename(visualize_path)} for {username}, folder: {data_folder}...")
    subprocess.run([sys.executable, visualize_path, username, data_folder])
    print(f"✅ {os.path.basename(visualize_path)} complete.")

    # # Step 6: Run the Flask web application
    # print("\n🌐 Starting Flask web application...")
    # try:
    #     subprocess.run([sys.executable, app_path, username], check=True) # Pass username
    # except subprocess.CalledProcessError as e:
    #     print(f"❌ Error running Flask app: {e}")
    # except FileNotFoundError:
    #     print(f"❌ Error: Flask app file not found at {app_path}")

    # print("\n✨ Project workflow complete.")

if __name__ == "__main__":
    main()