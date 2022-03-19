



def skip_comments(data):
    lines_skipped = 0
    idx = 0
    while idx < len(data) and data[idx] == ';':
        next_line = data.find('\n', idx)
        idx = next_line + 1
        lines_skipped += 1
    return data[idx:], lines_skipped

def find_matching_brace(openb, closeb, idx, text):
    assert text[idx] == openb, 'find_matching_brace was passed an index that didn\'t point at a valid opening brace!'

    count = 1
    while count > 0 and idx < len(text):
        idx += 1
        ch = text[idx]
        if ch == openb:
            count += 1
        if ch == closeb:
            count -= 1
    if idx == len(text):
        return -1
    else:
        return idx
