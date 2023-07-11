from PIL import Image, ImageFont, ImageDraw, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS, IFD
from datetime import datetime
from pathlib import Path
import exifread

def get_exif_from_img(image_path):
    exif_result = {}
    img = Image.open(image_path)
    exif = img.getexif()
    for k, v in exif.items():
        tag = TAGS.get(k, k)
        exif_result[tag] = v
        
    for ifd_id in IFD:
        try:
            ifd = exif.get_ifd(ifd_id)

            if ifd_id == IFD.GPSInfo:
                resolve = GPSTAGS
            else:
                resolve = TAGS

            for k, v in ifd.items():
                tag = resolve.get(k, k)
                exif_result[tag] = v
        except KeyError:
            pass
    return exif_result


def get_fuji_filmmode(image_path):
    # see https://exiftool.org/TagNames/FujiFilm.html
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
    filmmode = tags.get('MakerNote Tag 0x1401')
    if filmmode is None:
        return None
    else:
        filmmode = int(f'{filmmode}')
        match filmmode:
            case 0:
                return 'Standard (Provia)'
            case 512:
                return 'Velvia'
            case 1024:
                return 'Velvia'
            case 1280:
                return 'Pro Neg. Std'
            case 1281:
                return 'Pro Neg. Hi'
            case 1536:
                return 'Classic Chrome'
            case 1792:
                return 'Eterna'
            case 2048:
                return 'Classic Negative'
            case 2304:
                return 'Bleach Bypass'
            case 2560:
                return 'Nostalgic Neg'

def add_border_to_image(image_path, output_path):
    # 读取图片
    image = Image.open(image_path)

    # 读取 exif 信息
    exif_data = get_exif_from_img(image_path)
    if exif_data is None:
        exif_data = {}

    # 获取照片的拍摄日期
    capture_date = datetime.strptime(exif_data.get('DateTimeOriginal'), '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S %a')

    # 获取照片的拍摄机型、iso、快门速度、镜头参数和富士胶片模拟名称
    camera_make = exif_data.get('Make')
    if camera_make is None:
        # 如果没有拍摄机型信息，直接生成原图片
        image.save(output_path, 'JPEG', quality=95)
        return
    camera_model = exif_data.get('Model')
    iso = exif_data.get('ISOSpeedRatings')
    shutter_speed = exif_data.get('ExposureTime')
    if shutter_speed is not None:
        shutter_speed = float(shutter_speed)
        shutter_speed = str(shutter_speed) if shutter_speed >= 1 else f"1/{int(1/shutter_speed)}"

    lens = exif_data.get('LensModel')
    film_mode = get_fuji_filmmode(image_path)

    focal_length = exif_data.get('FocalLengthIn35mmFilm')
    f_number = exif_data.get('FNumber')


    # 创建一个新的图片，添加边框
    border_left = 0.01
    border_top = 0.01
    border_color = (255, 255, 255)  # 设置边框颜色为白色

    border_size = int(image.height * 0.08)  # banner的高度等于照片高度的8%

    new_image = Image.new('RGB', (image.width, image.height + border_size), border_color)
    original_img_ratio = image.width / image.height
    # 将原始图片粘贴在新的图片上，使其位于边框内
    new_image.paste(image, (0, 0))


    text_color = {
        "main": (0, 0, 0),  # 主字体是黑色
        "sub": (100, 100, 100)
    }
    text_font = {
        "main": ImageFont.truetype('SFCompactRounded.ttf', int(image.height * 0.03)),
        "sub": ImageFont.truetype('SFCompactRounded.ttf', int(image.height * 0.02))
    }
    # 在边框内添加照片的拍摄日期、拍摄机型、iso、快门速度、镜头参数和富士胶片模拟名称
   
    text_position = (int(image.width * border_left), image.height + int(image.height * border_top))  # 设置文本位置

    # 添加拍摄日期
    new_image_draw = ImageDraw.Draw(new_image)
    if camera_make is not None:
        new_image_draw.text(text_position, f"{camera_make} {camera_model}", fill=text_color['main'], font=text_font['main'])
        new_image_draw.text((text_position[0], text_position[1] + int(image.height * 0.04)), f"{lens}", fill=text_color['sub'], font=text_font['sub'])
        # lens 的 textsize 可能会比较长，需要先计算一下
        lens_text_size = new_image_draw.textbbox(xy=(text_position[0], text_position[1] + int(image.height * 0.04)), text=f"{lens}", font=text_font['sub'])
        # print(lens_text_size)  # 如果上一行的x=text_position[0]： (77, 5435, 2005, 5527)  如果上一行的x=0： (0, 5435, 1928, 5527)
        # 返回的是4元组，左上右下

        # 添加拍摄机型

        camera_logo = Image.open(f"logos/{camera_make.lower()}.jpg")
        logo_aspect_ratio = camera_logo.width / camera_logo.height
        # 调整机型logo图片的大小，高度为 3% * 原始图片高度，宽度为比例
        logo_new_height = int(image.width * 0.045)
        logo_new_width = int(logo_new_height * logo_aspect_ratio)
        camera_logo = camera_logo.resize((logo_new_width, logo_new_height))
        new_image.paste(camera_logo, (int((image.width - camera_logo.width) / 2) , text_position[1] ))  # 将 logo 图片粘贴在边框内
        # 添加胶片模拟
       
    if focal_length is not None:
        iso_aperture_text = f"{focal_length}mm f/{f_number} {shutter_speed}s ISO{iso}"
        if film_mode is not None:
            iso_aperture_text = f"{film_mode} {iso_aperture_text}"
        iso_text_size = new_image_draw.textbbox(xy=(0, 0), text=iso_aperture_text, font=text_font['main'])
        # print(iso_text_size) iso_text_size[2] 是宽度
        # 计算文本框的位置
        iso_text_xy = (int(image.width * (1 - border_left)) - iso_text_size[2] ,  text_position[1])
        new_image_draw.text(iso_text_xy, iso_aperture_text, fill=text_color['main'], font=text_font['main'])
        new_image_draw.text((iso_text_xy[0], text_position[1] + int(image.height * 0.04)), f"{capture_date}", fill=text_color['sub'], font=text_font['sub'])

    # 保存新图片
    new_image.save(output_path, 'JPEG', quality=95)


# 调用函数并传入需要处理的图片路径和新图片的保存路径
for f in Path('tests').glob('*'):
    add_border_to_image(f, f'output/{f.stem}.jpg')

