def extract_bnc_signal_data(message):
    if is_signal(message):
        lines = list(filter(lambda x: x, message.upper().split('\n')))
        signal_data = {}
        for line in lines:
            splitted_line = line.split(':')
            if len(splitted_line) == 2:
                key = splitted_line[0]
                value = splitted_line[1].strip()
                if key in parameter_extractor_mapping:
                    parameter_extractor_mapping[key](signal_data, value)
        return signal_data


def is_signal(message):
    lower_message = message.lower()
    if all(value in lower_message for value in ('coin', 'direction', 'leverage', 'entry', 'targets', 'stop loss')):
        return True


def extract_symbol(signal_data, value):
    symbol = value.split('$')[1]
    signal_data['symbol'] = symbol


def extract_side(signal_data, value):
    side = 'buy' if 'LONG' in value else 'sell'
    signal_data['side'] = side


def extract_leverage(signal_data, value):
    leverage = int(value.replace('X', ''))
    signal_data['leverage'] = leverage


def extract_steps(signal_data, value):
    entry_prices = value.replace(' ', '').split('-')
    steps_data = [{'entry_price': float(entry_price)} for entry_price in entry_prices]
    signal_data['steps'] = steps_data


def extract_targets(signal_data, value):
    tp_prices = value.replace(' ', '').split('-')
    targets_data = [{'tp_price': float(tp_price)} for tp_price in tp_prices]
    signal_data['targets'] = targets_data


def extract_stoploss(signal_data, value):
    trigger_price = float(value)
    stoploss_data = {'trigger_price': trigger_price}
    signal_data['stoploss'] = stoploss_data


parameter_extractor_mapping = {
    'COIN': extract_symbol,
    'DIRECTION': extract_side,
    'LEVERAGE': extract_leverage,
    'ENTRY': extract_steps,
    'TARGETS': extract_targets,
    'STOP LOSS': extract_stoploss,
}
