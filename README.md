# csv-quality-checker

A utility script for finding signs of data errors in tabular data (aka
data "cubes").

## Usage

python check_csv.py <file.csv>

## Diagnostics

check_csv.py prints diagnostic messages about things that might be signs
of errors in data.  Here are the explanations for them:

"Warning: field _n_ has a stray value"

The field seems to mostly have values that are from a small set of
values (an "enumeration" or "codeset"), but this particular value only
appears once or twice.  Usually a sign of a typo, or some mixup in
fields.

"Warning: field _n_ has null value(s)"

The field has some kind of value for most rows, but some line(s) don't
have a value for this field.  Usually a sign that fetching the value for
this field is failing for some record(s), depending on how the CSV was
produced.

"Warning: length of field _n_ has a stray value"

The field is usually of some specific length, but has an atypical length
on some rows.  Usually a sign of a typo, or mixup in fields.

"field _n_ does not seem to have a set of common values"
"length of field _n_ does not seem to have a set of common values"

Not really a warning, but just a mention that the field seems to be free
text and so warnings about stray values (or lengths) are being
suppressed.

"line _n_, multiple errors: ..."

This line caused many warnings.  It is usually a sign that the line is
scrambled or doesn't come from the same dataset.

"Warning: very few lines"

The file has at most one line.  Proper CSV files tend to have many.

"Warning: field count has a stray value"

CSV files usually have the same number of fields on every line.  Some
line(s) have a different number of fields than most lines in the file.
This is usually a sign of a scrambled line, or incorrectly escaped field
separator.
