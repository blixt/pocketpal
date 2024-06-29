from app import app

if __name__ == "__main__":
    import sys

    port = 5000
    if len(sys.argv) > 1:
        port = sys.argv[1]

    app.run(host="0.0.0.0", port=port, debug=True)