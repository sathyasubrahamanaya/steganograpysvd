from PIL import Image

def genData(data):
    return [format(ord(i), '08b') for i in data]

def modPix(pix, data):
    datalist = genData(data)
    lendata = len(datalist)
    imdata = iter(pix)
    
    for i in range(lendata):
        pix = [value for value in imdata.__next__()[:3] +
                                imdata.__next__()[:3] +
                                imdata.__next__()[:3]]

        for j in range(8):
            if (datalist[i][j] == '0' and pix[j] % 2 != 0):
                pix[j] -= 1
            elif (datalist[i][j] == '1' and pix[j] % 2 == 0):
                pix[j] = pix[j] - 1 if pix[j] != 0 else pix[j] + 1

        if (i == lendata - 1):
            if (pix[-1] % 2 == 0):
                pix[-1] = pix[-1] - 1 if pix[-1] != 0 else pix[-1] + 1
        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]

def encode_enc(newimg, data):
    w = newimg.size[0]
    (x, y) = (0, 0)
    for pixel in modPix(newimg.getdata(), data):
        newimg.putpixel((x, y), pixel)
        x = 0 if x == w - 1 else x + 1
        y += 1 if x == 0 else 0

def encode(image_path: str, data: str, output_path: str):
    image = Image.open(image_path, 'r')
    if not data:
        raise ValueError('Data is empty')
    newimg = image.copy()
    encode_enc(newimg, data)
    newimg.save(output_path)

def decode(image_path: str) -> str:
    image = Image.open(image_path, 'r')
    data = ''
    imgdata = iter(image.getdata())
    while True:
        pixels = [value for value in imgdata.__next__()[:3] +
                                imgdata.__next__()[:3] +
                                imgdata.__next__()[:3]]
        binstr = ''.join('0' if i % 2 == 0 else '1' for i in pixels[:8])
        data += chr(int(binstr, 2))
        if (pixels[-1] % 2 != 0):
            return data
