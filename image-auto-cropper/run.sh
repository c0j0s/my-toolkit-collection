#!/bin/bash
for filename in ./input/*
do
    if [[ $filename != *.rs ]]; then
        echo "Cropping $filename"
        ./target/release/autocrop -i $filename -o ${filename//input/output}
    fi
done