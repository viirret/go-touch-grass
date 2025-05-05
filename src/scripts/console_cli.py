import argparse
from go_touch_grass.tracker import TimeTracker
from go_touch_grass.outputs.console import ConsoleOutput


def main():
    parser = argparse.ArgumentParser(description='Time tracking with console output.')
    parser.add_argument('--username', required=True, help='Username to include in messages')
    args = parser.parse_args()

    tracker = TimeTracker(args.username)
    console_output = ConsoleOutput(args.username)
    tracker.add_output_handler(console_output)

    print(f"Time tracking started for user: {args.username} (Console output)")
    tracker.run()


if __name__ == "__main__":
    main()
