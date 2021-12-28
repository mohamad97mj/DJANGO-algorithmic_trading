from global_utils import my_get_logger


def extract_bnc_signal_data(message):
    if is_signal(message):
        lines = list(filter(lambda x: x, message.upper().split('\n')))
        signal_data = {'source': 'BNC'}
        for line in lines:
            splitted_line = line.split(':')
            if len(splitted_line) == 2:
                key = splitted_line[0].strip()
                value = splitted_line[1].strip()
                if key in parameter_extractor_mapping:
                    for f in parameter_extractor_mapping[key]:
                        f(signal_data, value)
        if is_valid(signal_data):
            return signal_data


def is_signal(message):
    lower_message = message.lower()
    if all(value in lower_message for value in ('coin', 'direction', 'leverage', 'entry', 'targets', 'stop loss')):
        return True


def is_valid(signal_data):
    return signal_data['side'] == 'buy' and \
           signal_data['risk_level'] in ('medium', 'risky') and \
           double_check_side(signal_data)


def extract_symbol(signal_data, value):
    symbol = value.split('$')[1]
    signal_data['symbol'] = symbol


def extract_side(signal_data, value):
    side = 'buy' if 'LONG' in value else 'sell'
    signal_data['side'] = side


def extract_risk_level(signal_data, value):
    if 'RISKY' in value:
        if 'HIGH' in value:
            level = 'high_risky'
        else:
            level = 'risky'
    else:
        level = 'medium'

    signal_data['risk_level'] = level


def extract_leverage(signal_data, value):
    leverage = int(value.replace('X', ''))
    signal_data['leverage'] = leverage


def extract_steps(signal_data, value):
    entry_prices = list(filter(lambda x: x, value.replace('-', ' ').split(' ')))
    steps_data = []
    for entry_price in entry_prices:
        try:
            steps_data.append({'entry_price': float(entry_price)})
        except ValueError:
            pass

    signal_data['steps'] = steps_data


def extract_targets(signal_data, value):
    tp_prices = list(filter(lambda x: x, value.replace('-', ' ').split(' ')))[:5]
    targets_data = []
    for tp_price in tp_prices:
        try:
            targets_data.append({'tp_price': float(tp_price)})
        except ValueError:
            pass

    signal_data['targets'] = targets_data


def extract_stoploss(signal_data, value):
    trigger_price = float(value)
    stoploss_data = {'trigger_price': trigger_price}
    signal_data['stoploss'] = stoploss_data


def double_check_side(signal_data):
    if check_side_by_steps(signal_data) and check_side_by_targets(signal_data):
        return True
    return False


def check_side_by_steps(signal_data):
    steps = signal_data['steps']
    if (steps[0]['entry_price'] <= steps[1]['entry_price'] and signal_data['side'] == 'buy') or \
            (steps[0]['entry_price'] >= steps[1]['entry_price'] and signal_data['side'] == 'sell'):
        return True
    else:
        logger = my_get_logger()
        logger.error('signal side does not match steps!')
        return False


def check_side_by_targets(signal_data):
    targets = signal_data['targets']
    if (targets[0]['tp_price'] <= targets[1]['tp_price'] and signal_data['side'] == 'buy') or \
            (targets[0]['tp_price'] >= targets[1]['tp_price'] and signal_data['side'] == 'sell'):
        return True
    else:
        logger = my_get_logger()
        logger.error('signal side does not match targets!')
        return False


parameter_extractor_mapping = {
    'COIN': (extract_symbol,),
    'DIRECTION': (extract_side, extract_risk_level),
    'LEVERAGE': (extract_leverage,),
    'ENTRY': (extract_steps,),
    'TARGETS': (extract_targets,),
    'STOP LOSS': (extract_stoploss,),
}
