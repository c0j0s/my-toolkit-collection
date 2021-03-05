#!/bin/bash
for filename in ./input/*.{jpg,jpeg}
do
    autocrop -i $filename -o ${filename//input/cropped}
done

