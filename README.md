# Exco

[![Build](https://github.com/thegangtechnology/exco/workflows/Build/badge.svg)](https://github.com/thegangtechnology/exco/actions?query=workflow%3ABuild)
[![Sonarqube](https://github.com/thegangtechnology/exco/workflows/Sonarqube/badge.svg)](https://github.com/thegangtechnology/exco/actions?query=workflow%3ASonarqube)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=thegangtechnology_exco&metric=alert_status)](https://sonarcloud.io/dashboard?id=thegangtechnology_exco)
[![CodeQL](https://github.com/thegangtechnology/exco/workflows/CodeQL/badge.svg)](https://github.com/thegangtechnology/exco/actions?query=workflow%3ACodeQL)
[![codecov](https://codecov.io/gh/thegangtechnology/exco/branch/master/graph/badge.svg?token=8BrjxREw2O)](https://codecov.io/gh/thegangtechnology/exco)
[![PyPI version](https://badge.fury.io/py/exco.svg)](https://badge.fury.io/py/exco)

Excel Comment ORM. Declare ORM Spec descriptively right on the excel file.

# What it does

The package allows you to declare orm mapping right in the excel file in the comments
 then use it to extract data from other similar files.
 
An example of a template is shown below.

![Template](notebooks/quickstart/template.png)

Dynamic Location, Validation, Assumptions, custom Parser are also supported.


# Installation

```
pip install exco
```

# Simple Usage

```
import exco
processor = exco.from_excel('./quickstart_template.xlsx')
result = processor.process_excel('./quickstart_data_file.xlsx')
print(result.to_dict())
```

See Also [Quick Start Notebook](notebooks/quickstart/0%20Quick%20Start.ipynb)

# Exco Block

Exco relies on yml blocks inside excel comment to build a spec.
Each comment can contain multiple blocks.
There are three types of echo block: a cell block, a table block, and a column block.

## Cell Block

A cellblock is a block of yml that is surrounded by `{{--` and `--}}`
```
{{--
key: some_int
parser: int
--}}
```

This means that parse this cell as `int` and put it in the result with key `some_int`.



Other advance features like, fallback, locator, assumptions, validator are optional.
The full specification is shown below.

```
{{--
key: some_value
# Optional default at_comment_cell
locator: {name: at_comment_cell} 
assumptions: # Optional
    - {key: right_of, name: right_of, label: marker}
parser: int
# Optional
fallback: 7 
# Optional. Dict[name, value].
params: {} 
validators: # Optional
    - {key: between, name: between, low: 5, high: 10 }
metadata: {unit: km}
--}}
```

### Processing Flow.

The cell processing flow is

1. Locating the Cell
2. Check Assumption
3. Parse
4. Validation

### Features

#### `key`
Key where the result will be put. This is required.

#### `fallback`

This is the most useful one where if the cell is failed locating, testing assumption, parsing.
The fallback value is assumed. If it is not specified, the value None is used. (yml's none is `null`).

#### `locator`
Locator is a dictionary. The key `name` is the class name to be used to locate the cell. Other parameters
can be flattened and put in the same dictionary. These parameters will be pass through the constructor
of such class.

If the locator is left out, it is assumed to be `at_comment_cell` which locate the cell with exactly
the same coordinate as the commented cell in the template.

#### `assumptions`
List of dictionaries. The `key` is the name of the check. `name` is the name of the class to be used in
testing an assumption. Other parameters can be flattened and included in the same dictionary.

#### `parser`
Required. Name of the parser class.

#### `params`
Optional. Dictionary of the parameter name to its value. The spread values are passed through the parser
constructor.

#### `validations`
Optional. List of Dictionary. Each dictionary must have `key` for the validation key and `name`,
validator's class name, specified. Other parameters to be passed to the validator constructor can be flattened and specified in this dictionary as well.

### `metadata`
Optional. Metadata. Dictionary of any object can be put here. The object will be parsed on to the result.

## Table Block
A table block is for specifying the properties of the table. The table block is surrounded by
`{{--table` and `--}}`. The simplest table block is
```
{{--table
key: some_table
--}}
```
This is typically what you need. A more complicated example is shown below:

```
{{--table
key: some_table
# optional. default at_comment_cell
locator: {name: at_comment_cell}
# optional. default downward
item_direction: downward
end_conditions:
    - {name: all_blank}
    - {name: max_row, n: 10, inclusive: true}
--}}
```
### Features
#### `key`
where the table will be put in the result. The output for the table is a list of dictionaries
where the key in the dictionaries is the column name specified in column blocks.

#### `locator`
Optional. Default at_comment_cell. Locator for the table anchor cell. Same as a cell block.

#### `item_direction`
Optional Direction for items in the table. Default downward. (rightward or downward)

#### `end_conditions`
A list of dictionary specifying each termination condition. The dictionary contains `name` and flattened
parameters.

If any of the end condition is met then the parsing for the table terminates. Depending on the end condition's
class, it may or may not include the matching row.

## Column Block

Column block specifications are very similar to the cell block. The simplest example is shown below.
```
{{--col
table_key: some_table
key: some_col
parser: int
}}
```
The column block is very similar to the cell block. It is the cell block with `table_key` and without
`locator`. The `table_key` tells which table it belongs to. It must match one of the table's `key` defined in the table block.

The position of the column cell when extracting value is computed from the relative position to the table
 block in the template.
 
 All other features like fallback, assumptions, validations are also supported in the same
 fashion as the cell block.

# Built-in Functions

## Locator
### `at_comment_cell`
Locate the cell right at the comment cell's coordinate in the template.

### `right_of`
Locate the cell to the right of the cell or merged cell with the given label.
In the case of a merged cell, right_of will pick the rightmost column and 
topmost row of the merged cell togo to the right of.

Parameters:
- `label` label to match.
- `n` Optional. Default value is 1. Indicates the number of columns to move from label cell to located cell.

### `search_right_of`
Searches for non-empty cell right of the cell with the given value.

Parameters:
- `label` label to match.
- `max_empty_col_search` Indicates the maximum number of columns to search for non-empty cell right of label.
### `right_of_regex`
Locate the cell to the right of the cell with a regex match.
Similarly, in the case of a merged cell, right_of_regex will 
pick the rightmost column and topmost row of the merged cell 
togo to the right of.

Parameters:
- `regex` string for the regular expression.
- `n` Optional. Default value is 1. Indicates the number of columns to move from regex matched cell to located cell.

### `below_of`
Locate the cell below of the cell with the given label.
In the case of a merged cell, below_of will pick the 
bottommost row and leftmost column of the merged cell togo 
to the bottom of.

Parameters:
- `label` label to match.
- `n` Optional. Default value is 1. Indicates the number of rows to skip from label cell to located cell.

### `search_below_of`
Searches for non-empty cell below of the cell with the given label.

Parameters:
- `label` label to match.
- `max_empty_row_search` Indicates the maximum number of rows to search for non-empty cell below of label.

### `below_of_regex`
Locate the cell below of the cell with a regex match.
Similarly, in the case of a merged cell, below_of_regex will 
pick the bottommost row and leftmost row of the merged cell 
togo to the bottom of.

Parameters:
- `regex` string for the regular expression.
- `n` Optional. Default value is 1. Indicates the number of rows to move from regex matched cell to located cell.


### `within`
Locate the cell between a cell with the given label.
This function searches to the right of or below of the
cell with the given label. If it is to the right of, the function
searches row by row while staying in between the column ranges
of the cell with the given label. If it is below of, similarly,
we search row by row while staying in between the row ranges of
the cell with the given label. On top of this you have the option
on how to pick your data (to the right of or beneath of) once you have found your desired key within
the cell range.

Parameters:
- `label` label of cell you want to search in between
- `find` the name of the cell you want to find in between the cell with that label's range
- `direction` direction you want to search for your value, choices are:
  - `right_of` this will search the right of the cell between the columns row wise
  - `below_of` this will search the beneath the cell between the rows row wise
- `perform` the action you want to perform to fetch your data, your options are:
  - `right_of` fetch the value to the right of the cell labeled in `find`
  - `below_of` fetch the value to beneath of the cell labeled in `find`
- `n` pick the value n values away in the specified perform direction (right_of or below_of)


## Assumption

### `left_cell_match`
This is useful in batch processing allowing us to check that we have the correct label to the left.

Parameters:

- `label` string to check that it matches.

## Parser
### `string`
parse value as string.

### `int`
parse the value as an integer. 

### `float`
parse the value as float

### `date`
parser the value as a date.

## Validator

### `between`
valid if the value is between(inclusively) `high` and `low`

#### Parameters

- `high` upper bound value.
- `low` lower bound value

## TableEndCondition

### `all_blank`
Evaluate to true if all columns are blank.

### `max_row`
Evaluate to true if the row number(start from 1) including the parsing row is greater than or
equal to `n`.

#### Parameters
- `n` number of row
- `inclusive` Optional. Default True. Whether to include the row in which it evaluates to true.

### `cell_value`
Evaluate to true if any column in row contains matching `cell_value`. Table terminates the row before.

#### Parameters
- `cell_value` cell value to match.
# Dereferencing
There are two types of dereferencing
- Spec Creation time dereferencing. The string similar to ``<<A1>>`` will be resolved 
to the value at A1 of the template file.
- Extraction time dereferencing. This string similar to ``==A1==`` will be resolved
to the value at A1 of the extracted file.

Here is an example
```
{{--
key: ==D2==
assumptions: # Optional
    - {key: right_of, name: right_of, label: <<A1>>}
parser: int
fallback: ==D3== 
--}}
```

# Handle Identical Sheet with Different Names

When an excel file to be extracted has a different sheet name than the one in the template file,
use ``sheet_name_checkers`` parameter in ``exco.from_excel()`` to create ``ExcelProcessor`` 
with sheet name alias checker.

For example, when the sheet name in the template file is 'Test 1/1/2021', 
but sheet names can be varied in the extracting files, i.e., 'Test 2/2/2022, 'Test 3/3/2023', etc.
```
import exco

SheetName = str
SheetNameAliasChecker = Callable[[SheetName], bool]
test_sheet_checker: SheetNameAliasChecker = lambda sheetname: 'Test' in sheetname
checkers: Dict[SheetName, SheetNameAliasChecker] = {'Test 1/1/2021': test_sheet_checker}
processor = exco.from_excel(template_excel_path, sheet_name_checkers=checkers)
```

In the case where there are hidden sheets that might have information that you dont want to extract,
make sure to set the accept_only_visible_sheets parameter to True

```
processor = exco.from_excel(template_excel_path, sheet_name_checkers=checkers, accept_only_visible_sheets=True)
```

# Custom Locator/Parser Etc.

See [Advance Features Notebook](notebooks/quickstart/1%20Advance%20Features.ipynb). But, in essence,
```python
processor = exco.from_excel('./custom_locator/custom_locator_template.xlsx',
                            extra_locators={'diagonal_of': DiagonalOfLocator})
```
# Working with .xls files.

Exco will not read Excel 97-2003 workbook (.xls) files. Use [XLS2XLSX](https://pypi.org/project/xls2xlsx/) to convert .xls files to the supported .xlsx format.