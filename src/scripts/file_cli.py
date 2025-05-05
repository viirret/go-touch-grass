import argparse
from go_touch_grass.tracker import TimeTracker
from go_touch_grass.outputs.file import FileOutput


def main():
    parser = argparse.ArgumentParser(description='Time tracking with file output.')
    parser.add_argument('--username', required=True, help='Username to include in messages')
    parser.add_argument('--filename', default="activity_log.txt", help='Output filename')
    args = parser.parse_args()

    tracker = TimeTracker(args.username)
    file_output = FileOutput(args.username, args.filename)
    tracker.add_output_handler(file_output)

    print(f"Time tracking started for user: {args.username} (File output: {args.filename})")
    tracker.run()


if __name__ == "__main__":
    main()
