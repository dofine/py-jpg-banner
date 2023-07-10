from PIL import Image, ImageFont, ImageDraw
from PIL.ExifTags import TAGS, GPSTAGS, IFD

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

def add_border_to_image(image_path, output_path):
    # 读取图片
    image = Image.open(image_path)

    # 读取 exif 信息
    exif_data = get_exif_from_img(image_path)
    if exif_data is None:
        exif_data = {}

    # 获取照片的拍摄日期
    capture_date = exif_data.get('DateTimeOriginal')

    # 获取照片的拍摄机型、iso、快门速度、镜头参数和富士胶片模拟名称
    camera_make = exif_data.get('Make')
    camera_model = exif_data.get('Model')
    iso = exif_data.get('ISOSpeedRatings')
    shutter_speed = exif_data.get('ExposureTime')
    lens = exif_data.get('LensModel')
    film_simulation = exif_data.get('FilmMode')

    # 创建一个新的图片，添加边框
    border_color = (255, 255, 255)  # 设置边框颜色为白色
    # TODO: 边框大小的问题，太小了文字看不清
    border_size = 100  # 设置边框大小为 20 像素
    new_image = Image.new('RGB', (image.width + border_size * 2, image.height + border_size * 2), border_color)

    # 将原始图片粘贴在新的图片上，使其位于边框内
    new_image.paste(image, (border_size, border_size))

    # 在边框内添加照片的拍摄日期、拍摄机型、iso、快门速度、镜头参数和富士胶片模拟名称
    text_color = (0, 0, 0)  # 设置文本颜色为黑色
    text_font = ImageFont.truetype('SFCompactRounded.ttf', 16)  # 设置文本字体和大小
    text_position = (border_size, image.height + border_size + 10)  # 设置文本位置

    # 添加拍摄日期
    new_image_draw = ImageDraw.Draw(new_image)
    new_image_draw.text(text_position, f"Capture Date: {capture_date}", fill=text_color, font=text_font)

    # 添加拍摄机型
    camera_logo_path = f"logos/{camera_make.lower()}.jpg"  # 根据相机制造商获取对应的 logo 图片路径
    camera_logo = Image.open(camera_logo_path)
    camera_logo_resized = camera_logo.resize((30, 30))  # 调整 logo 图片大小为 30x30 像素
    new_image.paste(camera_logo_resized, (border_size, image.height + border_size + 40))  # 将 logo 图片粘贴在边框内
    new_image_draw.text((border_size + 40, image.height + border_size + 40), f"Camera Model: {camera_model}", fill=text_color, font=text_font)

    # 添加 iso、快门速度、镜头参数和富士胶片模拟名称
    new_image_draw.text((border_size, image.height + border_size + 80), f"ISO: {iso}", fill=text_color, font=text_font)
    new_image_draw.text((border_size, image.height + border_size + 100), f"Shutter Speed: {shutter_speed}", fill=text_color, font=text_font)
    new_image_draw.text((border_size, image.height + border_size + 120), f"Lens: {lens}", fill=text_color, font=text_font)
    new_image_draw.text((border_size, image.height + border_size + 140), f"Film Simulation: {film_simulation}", fill=text_color, font=text_font)

    # 保存新图片
    new_image.save(output_path)

# 调用函数并传入需要处理的图片路径和新图片的保存路径
add_border_to_image('test.jpg', 'output.jpg')