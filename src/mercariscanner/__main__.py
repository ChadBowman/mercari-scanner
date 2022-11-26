import os
import sys
import argparse
import logging
import configparser
from mercariscanner.mercari_scanner import MercariScanner
from mercariscanner.alerters.slack import SlackAlerter

log = logging.getLogger(__name__)


class HelpParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"error: {message}" + '\n')
        self.print_help()
        sys.exit(2)


def parse_args():
    parser = HelpParser()
    parser.add_argument('keyword', help='Mercari search keyword')
    parser.add_argument('--min-price',
                        help='Amount in dollars to filter out items less than min-price',
                        type=float)
    parser.add_argument('--max-price',
                        help='Amount in dollars to filter out items more than max-price',
                        type=float)
    parser.add_argument('--delay',
                        help='Time in seconds to wait before the next scan (default: %(default)s)',
                        type=int,
                        default=60)
    parser.add_argument('--slack-token', help='Slack API token')
    parser.add_argument('--slack-channel',
                        help='Slack channel to publish alerts to')
    parser.add_argument('--tiers',
                        help='Semi-colon-separated key-value pairs that define tier message templates. '
                             'A template will be used if an item is less than or equal to the amount. '
                             'Example: "420=Wow! {name} is an amazing deal! Only ${price}; '
                             '1000=Hey check out this less cool deal{newline}{url}". '
                             'Available variables: price, name, url, newline')
    parser.add_argument('--start-stop-alert',
                        help='Alert when scanner starts and stops',
                        default=True,
                        action=argparse.BooleanOptionalAction)
    return parser.parse_args()


def parse_config():
    config = configparser.ConfigParser()
    config.read('mercari-scanner/config.ini')
    return config


def build_messages(config, args):
    messages = {}
    if config.has_section('messages'):
        messages = config['messages']
    return messages


def build_slack_alerter(config, args):
    token, channel = None, None
    if config.has_section('slack'):
        token = config['slack']['token']
        channel = config['slack']['channel']
    # override config file with args
    if args.slack_token:
        token = args.slack_token
    if args.slack_channel:
        channel = args.slack_channel

    if not token and not channel:
        return None

    return SlackAlerter(token, channel)


def build_alerters(config, args):
    alerters = []
    slack = build_slack_alerter(config, args)
    if slack:
        alerters.append(slack)
    else:
        log.info('No Slack configuration detected')

    if not alerters:
        log.warn('No alerters configured')

    return alerters


def build_tiers(config, args):
    tiers = {}
    if config.has_section('tiers'):
        tiers = config['tiers']
    if args.tiers:
        tiers = dict(s.split('=') for s in args.tiers.split(';'))
    return tiers


def alert(alerters, message):
    for alerter in alerters:
        alerter.alert(message)


def remove_file(file_name):
    if file_name and os.path.exists(file_name):
        os.remove(file_name)


def main():
    items_file_name = None
    args = None
    alerters = []
    try:
        config = parse_config()
        args = parse_args()
        alerters = build_alerters(config, args)
        tiers = build_tiers(config, args)

        min = None
        max = None
        if args.min_price:
            min = int(args.min_price * 100)  # multiplied by 100 because Mercari search uses pennies
        if args.max_price:
            max = int(args.max_price * 100)

        items_file_name = f"{hash(args.keyword)}.json"
        remove_file(items_file_name)
        if args.start_stop_alert:
            alert(alerters, f":scan: {args.keyword} scanning started")

        scanner = MercariScanner(args.keyword,
                                 min,
                                 max,
                                 args.delay,
                                 items_file_name,
                                 alerters,
                                 tiers)
        scanner.start()
    except Exception as e:
        log.exception(e)
        alert(alerters, f":warning: unhandled exception: {e}")
    finally:
        remove_file(items_file_name)
        if args and args.start_stop_alert:
            alert(alerters, f":octagonal_sign: {args.keyword} scanning stopped")


if __name__ == "__main__":
    main()
