import argparse
from go_touch_grass.tracker import TimeTracker
from go_touch_grass.outputs.discord import DiscordOutput
from go_touch_grass.outputs.file import FileOutput
from go_touch_grass.outputs.console import ConsoleOutput

def main():
    parser = argparse.ArgumentParser(description='Time tracking tool with multiple output options.')
    parser.add_argument('--username', required=True, help='Username to include in messages')

    # Output handler options.
    parser.add_argument('--discord', action='store_true', help='Enable Discord output')
    parser.add_argument('--file', nargs='?', const="activity_log.txt", 
                       help='Enable file output (default filename: activity_log.txt)')
    parser.add_argument('--console', action='store_true', help='Enable console output')
    
    args = parser.parse_args()

    if not any([args.discord, args.file, args.console]):
        parser.error('At least one output handler must be specified (--discord, --file, or --console)')

    tracker = TimeTracker(args.username)
    
    if args.discord:
        discord_output = DiscordOutput(args.username)
        tracker.add_output_handler(discord_output)
    
    if args.file:
        filename = args.file if args.file != "" else "activity_log.txt"
        file_output = FileOutput(args.username, filename)
        tracker.add_output_handler(file_output)
    
    if args.console:
        console_output = ConsoleOutput(args.username)
        tracker.add_output_handler(console_output)

    print(f"Time tracking started for user: {args.username}")
    print("Active handlers:", 
          "Discord" if args.discord else "",
          f"File({args.file})" if args.file else "",
          "Console" if args.console else "")
    
    tracker.run()

if __name__ == "__main__":
    main()