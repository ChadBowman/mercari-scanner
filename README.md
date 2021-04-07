# Mercari Scanner

![Image of Mercari](https://upload.wikimedia.org/wikipedia/commons/7/7f/Mercari_logo_2018.svg)

## Alerters

### Slack

Pass the --slack-token argument:
```
mercari-scanner --slack-token xoxb-blah-blah --slack-channel mercari "pokemon pillows"
```

or

Modify `config.ini` to include your Slack API token and the channel you want to alert to:

```
[slack]
token = xoxb-blah-blah
channel = mercari
```

## Usage

```
usage: mercari_scanner.py [-h] [--min-price MIN_PRICE] [--max-price MAX_PRICE] [--delay DELAY] [--slack-token SLACK_TOKEN] [--slack-channel SLACK_CHANNEL] [--tiers TIERS] [--start-stop-alert | --no-start-stop-alert] keyword

positional arguments:
  keyword               Mercari search keyword

optional arguments:
  -h, --help            show this help message and exit
  --min-price MIN_PRICE
                        Amount in dollars to filter out items less than min-price
  --max-price MAX_PRICE
                        Amount in dollars to filter out items more than max-price
  --delay DELAY         Time in seconds to wait before the next scan (default: 60)
  --slack-token SLACK_TOKEN
                        Slack API token
  --slack-channel SLACK_CHANNEL
                        Slack channel to publish alerts to
  --tiers TIERS         Semi-colon-separated key-value pairs that define tier message templates. A template will be used if an item is less than or equal to the amount.Example: "420=Wow! {name} is an amazing deal! Only ${price};
                        1000=Hey check out this less cool deal{newline}{url}". Available variables: price, name, url, newline
  --start-stop-alert, --no-start-stop-alert
                        Alert when scanner starts and stops (default: True)
```

## Examples

### Docker
```
docker pull chadbowman0/mercari-scanner:latest
docker run chadbowman0/mercari-scanner:latest --slack-token xoxb-blah-blah --min-price 300 --max-price 1010 --delay 30 5700xt
```

### Local
```
git clone https://github.com/ChadBowman/mercari-scanner.git ~/mercari-scanner
python3 -m venv env && source env/bin/activate
python3 -m pip install --upgrade pip && python3 -m pip install -r requirements.txt
python ~/mercari-scanner/mercari-scanner/mercari_scanner.py --min-price 10 --max-price 1000 --delay 30 5700xt
```
