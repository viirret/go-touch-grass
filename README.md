# go-touch-grass

Tracks computer usage time and reports online/offline durations to Discord.

## Installation
1. Clone the repository
```bash
git clone https://github.com/viirret/go-touch-grass.git
cd go-touch-grass
```

2. Install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install .
```

3. Create the `.env` file:
```bash
echo 'DISCORD_WEBHOOK_URL="your_webhook_url_here"' > .env
```

## Usage

### Basic Run
```bash
./venv/bin/go-touch-grass --username "YourName" --discord
```

### Systemd Service
1. Create `/etc/systemd/system/go-touch-grass.service`:
```ini
[Unit]
Description=Go Touch Grass Service
After=network.target
Before=shutdown.target reboot.target halt.target
RefuseManualStop=no

[Service]
Type=simple
User=yourusername
TimeoutStopSec=30
ExecStart=/path/to/go-touch-grass/venv/bin/go-touch-grass --username "YourName" --discord
KillMode=control-group
Restart=no
RemainAfterExit=yes
EnvironmentFile="/path/to/go-touch-grass/.env"

[Install]
WantedBy=default.target
```

2. Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable go-touch-grass.service
sudo systemctl start go-touch-grass.service
```

## Configuration

### Environment Variables
- `DISCORD_WEBHOOK_URL`: Your Discord webhook URL

### Command Line Arguments
- `--username`: Required. Name to show in Discord notifications

## Files
Follows XDG Base Directory Specification:
- Persistent Data (state.json): `~/.local/state/go_touch_grass/state.json`
- Temporary Logs (log.log): `~/.cache/go_touch_grass/log.log`

Custom Paths:
Set XDG_STATE_HOME or XDG_CACHE_HOME environment variables to override defaults.

## Dependencies
- See [pyproject.toml](pyproject.toml)

## TODO
- Tests

## Contributing
Via Pull Request.