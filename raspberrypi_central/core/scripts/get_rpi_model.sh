#!/bin/bash

cat /proc/device-tree/model | awk -F 'Rev' '{print $1}'
