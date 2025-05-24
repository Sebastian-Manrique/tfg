#!/bin/bash
# This bash file was created because is easier to do in bash than in Python (obviously)
hostname -I | awk '{print $1}'
