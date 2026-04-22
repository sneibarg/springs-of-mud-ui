"""
Springs of MUD UI - A graphical MUD client built with Pyxel.

Command-line interface for starting the MUD client with configurable options.
"""
import argparse
import sys
from pathlib import Path


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="springs-of-mud-ui",
        description="Springs of MUD UI - A graphical MUD client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Examples:
  %(prog)s -i /path/to/installation
  %(prog)s --install-dir C:\Games\SpringsOfMUD
  %(prog)s -i ~/mud --verbose

For more information, visit: https://github.com/yourusername/springs-of-mud-ui
        """
    )

    parser.add_argument(
        "-i", "--install-dir",
        type=str,
        metavar="PATH",
        required=True,
        help="Installation directory for the MUD client (required)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    return parser.parse_args()


def setup_install_dir(install_dir: str, verbose: bool = False) -> Path:
    """
    Setup and validate the installation directory structure.

    Creates the installation directory and required subdirectories if they don't exist.

    Args:
        install_dir: Installation directory path
        verbose: Whether to print verbose output

    Returns:
        Path: Resolved absolute path to installation directory

    Raises:
        SystemExit: If directory cannot be created or is invalid
    """
    path = Path(install_dir).resolve()

    # Create installation directory if it doesn't exist
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
            if verbose:
                print(f"Created installation directory: {path}")
        except Exception as e:
            print(f"Error: Cannot create installation directory '{path}': {e}", file=sys.stderr)
            sys.exit(1)

    # Verify it's a directory
    if not path.is_dir():
        print(f"Error: '{path}' is not a directory", file=sys.stderr)
        sys.exit(1)

    # Create resources subdirectory
    resources_dir = path / "resources"
    if not resources_dir.exists():
        try:
            resources_dir.mkdir(exist_ok=True)
            if verbose:
                print(f"Created resources directory: {resources_dir}")
        except Exception as e:
            print(f"Warning: Could not create resources directory: {e}", file=sys.stderr)

    return path


def main():
    """Main entry point for the application."""
    args = parse_arguments()

    # Setup installation directory and create resources folder
    install_dir = setup_install_dir(args.install_dir, verbose=args.verbose)

    if args.verbose:
        print(f"Springs of MUD UI starting...")
        print(f"Installation directory: {install_dir}")

    # Import UI only when needed (after argument parsing)
    # This allows --help and --version to work without dependencies
    try:
        from ui.MudClientUI import MudClientUI
    except ImportError as e:
        print(f"Error: Failed to import MudClientUI: {e}", file=sys.stderr)
        print("Make sure all dependencies are installed (pyxel, etc.)", file=sys.stderr)
        sys.exit(1)

    # TODO: Pass install_dir to MudClientUI when it's updated to accept it
    # For now, we'll store it and make it available for future use
    try:
        # You can pass install_dir to MudClientUI constructor once it's updated
        # ui = MudClientUI()
        ui = MudClientUI(install_dir=install_dir, verbose=args.verbose)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting UI: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
