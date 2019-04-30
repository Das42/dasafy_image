from PIL import Image, ImageEnhance, ImageDraw, ImageStat
import argparse


def halftone(image, sample=2, scale=15, angle=90):
    im = image
    img_grey = im.convert('1')  # Convert to greyscale.
    channel = img_grey.split()[0]  # Get grey pixels.
    channel = channel.rotate(angle, expand=1)
    size = channel.size[0]*scale, channel.size[1]*scale

    bitmap = Image.new('1', size)
    draw = ImageDraw.Draw(bitmap)

    for x in range(0, channel.size[0], sample):
        for y in range(0, channel.size[1], sample):
            box = channel.crop((x, y, x+sample, y+sample))
            mean = ImageStat.Stat(box).mean[0]
            diameter = (mean/255) ** 0.5
            edge = 0.5 * (1-diameter)
            x_pos, y_pos = (x+edge) * scale, (y+edge) * scale
            box_edge = sample * diameter * scale
            draw.ellipse((x_pos, y_pos, x_pos+box_edge, y_pos+box_edge),
                         fill=255)

    bitmap = bitmap.rotate(-angle, expand=1)
    width_half, height_half = bitmap.size
    xx = (width_half - img.size[0]*scale) / 2
    yy = (height_half - img.size[1]*scale) / 2
    bitmap = bitmap.crop((xx, yy, xx + img.size[0]*scale,
                                  yy + img.size[1]*scale))
    return Image.merge('1', [bitmap])


def apply_gradient(image, gradient_magnitude=2., initial_opacity=.12):
    im = image
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    width, height = im.size
    alpha_gradient = Image.new('L', (1, height), color=0xFF)
    for x in range(height):
        a = int((initial_opacity * 255.) * (4 + gradient_magnitude * float(x) / height))
        alpha_gradient.putpixel((0, x), a)
        if a > 0:
            alpha_gradient.putpixel((0, x), a)
        else:
            alpha_gradient.putpixel((0, x), 0)

    alpha = alpha_gradient.resize(im.size)

    # create & apply gradient
    gradient_im = Image.new('RGBA', (width, height), color=gradient_color)  # das color
    gradient_im.putalpha(alpha)

    # make composite with original image
    output_im = Image.alpha_composite(im, gradient_im)
    return output_im


def enhance(image, scale=1.3):
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(scale)


# input and output files
# img = Image.open('IMG_8015.jpg')
# output = 'dasafied_teresa2.jpg'

# tune parameters
brightness = 1.4
ht_sample = 15
ht_scale = 2
ht_angle = 35
gradient_magnitude = .75
gradient_color = (60, 115, 200)
gradient_opacity = .13


parser = argparse.ArgumentParser()
parser.add_argument('img')
parser.add_argument('output')
args = parser.parse_args()

img = open(args.filename)
output = args.output

enhance(apply_gradient(halftone(img, ht_sample, ht_scale, ht_angle), gradient_magnitude, gradient_opacity), brightness)\
   .save(output, 'PNG')

