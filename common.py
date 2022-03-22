
import logging

logger = logging.getLogger('common')


def skip_comments(data):
    lines_skipped = 0
    idx = 0
    while idx < len(data) and data[idx] == ';':
        next_line = data.find('\n', idx)
        idx = next_line + 1
        lines_skipped += 1
    return data[idx:], lines_skipped

def find_matching_brace(openb, closeb, idx, text):
    assert len(text) > idx, f'find_matching_brace was passed index {idx} that\'s out of the range of text {text}!'
    assert text[idx] == openb, f'find_matching_brace was passed index {idx} for text {text} that didn\'t point at a valid opening brace! Instead, it pointed at {text[idx]}.'
    assert len(text) > idx + 1, f'find_matching_brace was passed text {text} that doesn\'t have any characters after the opening brace.'
    og_idx = idx

    count = 1
    while count > 0 and idx < len(text):
        idx += 1
        ch = text[idx]
        if ch == openb:
            count += 1
        if ch == closeb:
            count -= 1
    if idx == len(text) and count != 0:
        raise ValueError(f'Passed text {text} that didn\'t have a closing brace for the one in position {og_idx}!')
    else:
        return idx
