import sys
import os

def main():
    """
    Main entry point for the M3U8 Downloader application.
    Routes to CLI mode if arguments are present, otherwise launches the GUI.
    """
    if len(sys.argv) > 1:
        # Run Command Line Interface
        from cli.parser import run_cli
        run_cli()
    else:
        # Run Graphical User Interface
        try:
            from gui.app import M3U8DownloaderApp
            app = M3U8DownloaderApp()
            app.mainloop()
        except ImportError as e:
            print(f"Failed to load the GUI layer. Error: {e}")
            print("Please ensure customtkinter is installed, or pass arguments to use the CLI.")
            sys.exit(1)

if __name__ == "__main__":
    # Ensure local packages (core, cli, gui) can be imported
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    main()
