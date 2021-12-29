def extract_always_win_signal_data(message):
    lower_msg = message.lower()
    lines = list(filter(lambda x: x, lower_msg.split('\n')))
    signal_data = {'source': 'ALWAYS_WIN'}

    if is_primary_signal(lines[0]):
        signal_data['type'] = 'primary'
        signal_data['leverage'] = 11
        extract_primary_setup(signal_data, lines[0])
    elif is_secondary_signal(lower_msg):
        signal_data['type'] = 'secondary'
        extract_secondary_setup(signal_data, lines)
    return signal_data


def is_primary_signal(line0):
    words = line0.split(' ')
    if words[0] in ('short', 'long'):
        try:
            float(words[2])
            return True
        except ValueError:
            pass
    return False


def is_secondary_signal(lower_msg):
    if all(value in lower_msg for value in ['leverage', 'entries', 'target', 'sl']) and \
            any(value in lower_msg for value in ['short', 'long']):
        return True
    return False


def extract_primary_setup(signal_data, line0):
    params = line0.split(' ')
    side = 'buy' if params[0] == 'long' else 'sell'
    signal_data['side'] = side
    symbol = '{}/USDT'.format(params[1].upper())
    signal_data['symbol'] = symbol
    steps = [{'entry_price': float(params[2])}]
    signal_data['steps'] = steps


def extract_secondary_setup(signal_data, lines):
    splitted_line0 = lines[0].split(' ')
    symbol = splitted_line0[0].upper()
    signal_data['symbol'] = symbol
    side = 'buy' if splitted_line0[1] == 'long' else 'sell'
    signal_data['side'] = side
    targets = []
    for line in lines[3:]:
        splitted_line = line.split(' ')
        if line.startswith('target'):
            targets.append({'tp_price': float(splitted_line[2])})
        elif line.startswith('sl'):
            signal_data['stoploss'] = {'trigger_price': float(splitted_line[1])}
    signal_data['targets'] = targets
