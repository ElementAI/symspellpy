#!/usr/bin/env bash

###
# This file is required to have `cicleci` work in a non-tty env (pre-commit hooks)
###

exec < /dev/tty

if ! error=$(circleci config validate); then
	echo "CircleCI Configuration Failed Validation."
	echo $error
	exit 1
fi