# Mercari Scanner

![Image of Mercari](https://upload.wikimedia.org/wikipedia/commons/7/7f/Mercari_logo_2018.svg)

## Alerters

### Slack

Modify `config.ini` to include your Slack API token and the channel you want to alert to:

```
[slack]
token = xoxb-blah-blah
channel = mercari
```

## Usage

### Docker
```
docker pull chadbowman0/mercari-scanner:latest
docker run chadbowman0/mercari-scanner:latest --min-price 300 --max-price 1010 --delay 30 5700xt
```

### Local
```
git clone https://github.com/ChadBowman/mercari-scanner.git ~/mercari-scanner
python3 -m venv env && source env/bin/activate
python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt
python ~/mercari-scanner/mercari-scanner/mercari_scanner.py --min-price 10 --max-price 1000 --delay 30 5700xt
```
