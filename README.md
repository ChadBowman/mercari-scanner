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

```
usage: mercari_scanner.py [-h] [--min-price MIN_PRICE] [--max-price MAX_PRICE] [--delay DELAY] keyword

positional arguments:
  keyword               Mercari search keyword

optional arguments:
  -h, --help            show this help message and exit
  --min-price MIN_PRICE
                        Amount in dollars to filter out items less than min-price
  --max-price MAX_PRICE
                        Amount in dollars to filter out items more than max-price
  --delay DELAY         Time in seconds to wait before the next scan. Default: 60s
```

## Examples

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
