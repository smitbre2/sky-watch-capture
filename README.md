# sky-watch-capture and meteor-motion-detection
Video capture that will selectively save footage only when specific objects are detected.
Camera resolution is aquired and FPS is calculated on startup.

## Limitations of Hardware
* Video capture will be conducted through a usb camera.
* Initial testing will be done on a local machine, but will be ported to run on a Raspberry Pi.

## Gaols of Software
* The software should be able to monitor the entire night; Only saving footage with selected object detection.
* The video detection will work by detecting changes in light to detect possible meteors in the night sky.
* For now the software stores information locally, but may be pushed to some cloud service later in production.
