# Instructions
Custom scripts to run [auto-image-cropper](https://github.com/ritiek/auto-image-cropper).

```bash
$  ./auto-cropper.sh
```
- feeds .jpg files from `/input` folder.
- auto cropper outputs final product in `/cropped` folder.

```bash
$  python3 image-border-filler.py
```
- image-border-filler script adds border to all cropped images.
- outputs the final product in `/output` folder.

- Options that can be changed in image-border-filler.py:
  ```python 
    # starting image index
    skip = 0

    # output image size
    final_size = (1000,1000) 

    # margin to item size percentile, larger margin % = smaller item
    margin_size_percent = 0.3 

    # margin color in RGB value, default white
    background_color = (255, 255, 255) 
    ```

# Installation
1. Follow guide at [auto-image-cropper](https://github.com/ritiek/auto-image-cropper).
2. Add the scripts to the installation folder.
3. Run the scripts.