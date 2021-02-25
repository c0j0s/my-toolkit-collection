#!/bin/bash
for filename in ./input/*.{jpg,jpeg}
do
    ./target/release/autocrop -i $filename -o ${filename//input/cropped}
done

