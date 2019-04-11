from PIL import Image, ImageChops, ImageEnhance
import os

BG_img_path = os.path.join("img_reader", "BG.png")


def read_board_image(fptr):
    Background_IMAGE = Image.open(BG_img_path)
    WIDTH, HEIGHT = Background_IMAGE.size
    Background_IMAGE = Background_IMAGE.crop((0, 200, WIDTH, HEIGHT - 200))

    Board_IMAGE = Image.open(fptr)
    WIDTH, HEIGHT = Board_IMAGE.size
    fptr_2 = os.path.join("img_reader", "Result_IMAGE.png")
    Board_IMAGE = Board_IMAGE.crop((0, 200, WIDTH, HEIGHT - 200))

    Result_IMAGE = ImageChops.difference(Board_IMAGE, Background_IMAGE)
    Result_IMAGE = Result_IMAGE.convert('LA')
    enhancer = ImageEnhance.Brightness(Result_IMAGE)
    Result_IMAGE = enhancer.enhance(5)

    Result_IMAGE.save(fptr_2)


if __name__ == "__main__":
    fptr = os.path.join("img_reader", "Mad_7.jpg")
    read_board_image(fptr)
