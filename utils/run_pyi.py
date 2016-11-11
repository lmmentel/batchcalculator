#!/bin/bash

rm -rf build dist

pyinstaller --onedir --windowed BatchCalculator.spec
