import os
from app import create_app, db
from waitress import serve

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    env = os.environ.get('FLASK_ENV', 'development')
    
    print(f"\n{'='*40}")
    print(f" CORALS4CHEAP STARTING UP")
    print(f" Environment: {env}")
    print(f" Port:        {port}")
    print(f"{'='*40}\n")

    if env == 'development':
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        print(f"Serving with Waitress on http://0.0.0.0:{port}")
        serve(app, host='0.0.0.0', port=port)
