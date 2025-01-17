from dotenv import load_dotenv

load_dotenv(override=True)


import os  # noqa: E402

from app import app  # noqa: E402

if __name__ == "__main__":
    import sys

    port = int(os.getenv("PORT", 5000))
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    app.run(host="0.0.0.0", port=port, debug=True)
