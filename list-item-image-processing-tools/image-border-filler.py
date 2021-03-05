from PIL import Image
import glob

#===================================================
# starting image index, default start from 0.
skip = 0

# output image size, default 1000x1000.
final_size = (1000,1000) 

# margin to item size percentile, larger margin % = smaller item, default 0.3.
margin_size_percent = 0.3 

# margin color in RGB value, default white.
background_color = (255, 255, 255) 
#===================================================

# add margin to image supplied
def add_margin(img, top, right, bottom, left, background_color):
    width, height = img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(img.mode, (new_width, new_height), background_color)
    result.paste(img, (left, top))
    return result

# auto expand image supplied to square image
def expand_to_square(img, background_color):
    width, height = img.size
    if width == height:
        return img
    elif width > height:
        result = Image.new(img.mode, (width, width), background_color)
        result.paste(img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(img.mode, (height, height), background_color)
        result.paste(img, ((height - width) // 2, 0))
        return result

try:
    # load input folder
    image_dir_list = [item for i in [glob.glob('./cropped/*.%s' % ext) for ext in ["jpg","jpeg"]] for item in i]

    # calculate actual pixel for margin base on ration configured ontop.
    margin_size = (int((final_size[0] * margin_size_percent)/2), int((final_size[1] * margin_size_percent)/2))
    resize = (int(final_size[0] - margin_size[0] * 2), int(final_size[1] - margin_size[1] * 2))

    for filename in image_dir_list[skip:]:
        output = filename.replace("cropped","output")
        print("Processing [{}] --> Saving to [{}]".format(filename,output))
        image = Image.open(filename)
        # expand to squre and resize
        image_new = expand_to_square(image, background_color).resize(resize)
        # add a fix margin to image
        image_new = add_margin(image_new, margin_size[1], margin_size[0], margin_size[1], margin_size[0], background_color)
        # save the new image
        image_new.save(output, quality=100)
except Exception as e:
    print(e)