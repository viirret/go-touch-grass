import argparse
from go_touch_grass.tracker import TimeTracker
from go_touch_grass.outputs.discord import DiscordOutput


def main():
    parser = argparse.ArgumentParser(description='Time tracking tool that reports to Discord on shutdown.')
    parser.add_argument('--username', required=True, help='Username to include in the Discord message')
    args = parser.parse_args()

    tracker = TimeTracker(args.username)
    discord_output = DiscordOutput(args.username)
    tracker.add_output_handler(discord_output)

    print(f"Time tracking started for user: {args.username}")
    tracker.run()


if __name__ == "__main__":
    main()
