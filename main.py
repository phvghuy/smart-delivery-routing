import sys
import uvicorn


def run_api() -> None:
    uvicorn.run(
        "smart_delivery_routing.interface.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


def run_ui() -> None:
    from streamlit.web import cli as st_cli
    sys.argv = [
        "streamlit", "run",
        "src/smart_delivery_routing/interface/streamlit_app.py",
        "--server.port=8501",
    ]
    st_cli.main()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "ui"

    if mode == "api":
        run_api()
    elif mode == "ui":
        run_ui()
    else:
        print("Usage: python main.py [ui|api]")
        sys.exit(1)
