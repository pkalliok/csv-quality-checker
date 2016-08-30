#!/usr/bin/env python

import sys, csv

errors = {}
#errprint = sys.stderr.write

def main(filename):
    with open(filename) as f:
        reader = csv.reader(f, delimiter=';')
        line_count, line_lens, value_distr, value_len_distr = \
                read_quality_data(reader)
    check_quality(line_count, line_lens, value_distr, value_len_distr)
    multiple_errors()

def read_quality_data(reader):
    line_count, line_lens, value_distr, value_len_distr = 0, {}, {}, {}
    for row in reader:
        line_count += 1
        line_lens.setdefault(len(row), []).append(line_count)
        for field in range(len(row)):
            value_distr.setdefault(field,
                    {}).setdefault(row[field], []).append(line_count)
            value_len_distr.setdefault(field,
                    {}).setdefault(len(row[field]), []).append(line_count)
    return (line_count, line_lens, value_distr, value_len_distr)

def check_quality(line_count, line_lens, value_distr, value_len_distr):
    if line_count <= 1: warn("very few lines", line_count, [])
    check_freqs(line_lens, line_count, "field count")
    for field in value_distr:
        check_freqs(value_distr[field], line_count,
                "field %d" % (field+1))
    for field in value_len_distr:
        check_freqs(value_len_distr[field], line_count,
                "length of field %d" % (field+1))

def check_freqs(distr, total, target):
    nulls = len(distr.get('', []))
    if nulls > 0 and nulls < total * .5:
        warn(target + " has null value(s)", nulls, distr[''])
    if seems_enumerated(distr):
        for value in distr:
            if len(distr[value]) < 3:
                warn(target + " has a stray value", value, distr[value])
    else: print(target + " does not seem to have a set of common values")

def seems_enumerated(distr):
    freqs = sorted(len(v) for v in distr.values())
    if len(freqs) <= 1: return True # constant field
    if sum(freqs[:-1]) < 15: return False # too few values to tell
    return sum(freqs[-10:]) > sum(freqs) * .9

def warn(issue, value, lines):
    for line in lines:
        errors.setdefault(line, []).append(issue)
    if len(lines) > 5: lines = lines[:5] + ['...']
    print("Warning: %s (%s), on lines: %s" %
            (issue, str(value), ', '.join(str(l) for l in lines)))

def multiple_errors():
    for l in sorted(errors.keys()):
        if len(errors[l]) > 1:
            print("line %d, multiple errors: %s" % (l, ', '.join(errors[l])))

if __name__ == '__main__':
    main(sys.argv[1])

