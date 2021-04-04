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

### Local
```
git clone https://github.com/ChadBowman/mercari-scanner.git ~/mercari-scanner
source ~/mercari-scanner/env/bin/activate
python ~/mercari-scanner/mercari-scanner/mercari_scanner.py --min-price 10 --max-price 1000 5700xt
```
