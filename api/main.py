from src.app import create_patrol_app

app = create_patrol_app()

if __name__ == '__main__':
    app.run(host="localhost", port=5001)