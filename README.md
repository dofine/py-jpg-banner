## Description
Since Xiaomi launched [Xiaomi 12s ultra](https://www.mi.com/global/product/xiaomi-12s-ultra/), it has been popular to add watermark to the photo, showing camera model, logo, iso and other parameters. Many third party apps, such as [Liit](https://apps.apple.com/us/app/liit-photo-editor/id1547215938) also provide this functionaliy. 

This repo is aimed at fuji cameras, with film simulation info on the wartermark.

## Requirements
- Python 3.10
- Pillow >= 10.0 (built with libraqm)
- [exifread](https://pypi.org/project/ExifRead/) >= 3.0.0

## Examples
![](output/test4.jpg)

## TODO
- [ ] Add support for iPhone, as I don't have any other camera models.
- [x] Add support for fuji film simulation exif.
- [ ] https://github.com/dofine/py-jpg-banner/issues/1 Portrait view.
- [ ] Add option to copy original photo's exif to the new edited output photo.
