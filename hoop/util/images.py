def select_resized_image(image_url, size, quality):
    image_url = image_url.split('.')

    image_url[-2] += '_%sq%d' % (size, quality)
    image_url[-1] = 'jpg'

    return '.'.join(image_url)
