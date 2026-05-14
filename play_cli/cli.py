import argparse
import auto_installer

def main():
    parser = argparse.ArgumentParser(description="Google Play Auto Installer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # install command
    install_parser = subparsers.add_parser("install", help="Install an app by package ID")
    install_parser.add_argument("--id", type=str, required=True, help="Package ID (e.g. com.tencent.mm)")

    args = parser.parse_args()

    if args.command == "install":
        auto_installer.install_app(args.id)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
