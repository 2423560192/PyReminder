from app import create_app
from app.config.config import Config

app = create_app()

if __name__ == '__main__':
    debug_mode = Config.DEBUG
    app.run(debug=debug_mode, host=Config.HOST, port=Config.PORT) 