#!/bin/bash

# It's just fun.
find ./app ./tests -name "*.py" | xargs cat | sed '/^\s*#/d;/^\s*$/d' | wc -l
