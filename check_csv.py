#!/usr/bin/env python

import sys, csv, argparse

errors = {}

parser = argparse.ArgumentParser(description="""
A utility script for finding signs of data errors in tabular data""")
parser.add_argument('csvfile', metavar='file.csv', help='data file to analyse')
parser.add_argument('-d', '--csv-delimiter', metavar='char', type=str,
        default=',', help='character used to delimit fields in CSV')
parser.add_argument('--csv-quote', metavar='char', type=str,
        default='"', help='character used to surround (text) fields in CSV')
parser.add_argument('--csv-dialect', metavar='dialect', type=str,
        default='excel', help='CSV dialect (default excel)')
parser.add_argument('--null-threshold', metavar='x', type=float, default=0.5,
        help='maximum ratio of nulls to other rows to produce a warning')
parser.add_argument('--stray-threshold', metavar='n', type=int, default=2,
        help='number or rows with a common value that are still considered stray')
parser.add_argument('--code-count', metavar='n', type=int, default=10,
        help='how many most common values to look at when deciding whether a field is a codeset field')
parser.add_argument('--code-ratio', metavar='x', type=float, default=0.9,
        help='how much of rows should the most common values cover for a field to be considered a codeset field')
parser.add_argument('--multiple-threshold', metavar='n', type=int, default=2,
        help='minimum number of errors a line should have to have "multiple" errors')

def main(args):
    with open(args.csvfile) as f:
        reader = csv.reader(f, dialect=args.csv_dialect,
                delimiter=args.csv_delimiter, quotechar=args.csv_quote)
        line_count, line_lens, value_distr, value_len_distr = \
                read_quality_data(reader)
    check_quality(args, line_count, line_lens, value_distr, value_len_distr)
    multiple_errors(args)

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

def check_quality(args, line_count, line_lens, value_distr, value_len_distr):
    if line_count <= 1: warn("very few lines", line_count, [])
    check_freqs(args, line_lens, line_count, "field count")
    for field in value_distr:
        check_freqs(args, value_distr[field], line_count,
                "field %d" % (field+1))
    for field in value_len_distr:
        check_freqs(args, value_len_distr[field], line_count,
                "length of field %d" % (field+1))

def check_freqs(args, distr, total, target):
    nulls = len(distr.get('', []))
    if nulls > 0 and nulls < total * args.null_threshold:
        warn(target + " has null value(s)", nulls, distr[''])
    if seems_enumerated(args, distr):
        for value in distr:
            if len(distr[value]) <= args.stray_threshold:
                warn(target + " has a stray value", value, distr[value])
    else: print(target + " does not seem to have a set of common values")

def seems_enumerated(args, distr):
    freqs = sorted(len(v) for v in distr.values())
    return sum(freqs[-abs(args.code_count):]) > sum(freqs) * args.code_ratio

def warn(issue, value, lines):
    for line in lines:
        errors.setdefault(line, []).append(issue)
    if len(lines) > 6: lines = lines[:5] + ['...']
    print("Warning: %s (%s), on lines: %s" %
            (issue, str(value), ', '.join(str(l) for l in lines)))

def multiple_errors(args):
    for l in sorted(errors.keys()):
        if len(errors[l]) >= args.multiple_threshold:
            print("line %d, multiple errors: %s" % (l, ', '.join(errors[l])))

if __name__ == '__main__':
    main(parser.parse_args())

