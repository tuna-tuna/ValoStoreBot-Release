from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import requests

class ImageEdit:
    def __init__(self) -> None:
        pass

    def pasteCentered(self, image, frameX, frameY, startX, startY, useImage):
        centerX = int(frameX/2)
        centerY = int(frameY/2)
        imageWidthHalf = int(useImage.width / 2)
        imageHeightHalf = int(useImage.height / 2)
        image.paste(useImage, (startX + centerX - imageWidthHalf, startY + centerY - imageHeightHalf), useImage)

    def createImage(self, author_id: str, image: Image, skin, fontpath):
        name, icon, price, tier, classic = skin
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(fontpath, size=30)
        textColor = '#ffffff'
        
        #WIP
        #Background color with alpha
        skin1 = Image.open(BytesIO(requests.get(icon[0]).content))
        skin2 = Image.open(BytesIO(requests.get(icon[1]).content))
        skin3 = Image.open(BytesIO(requests.get(icon[2]).content))
        skin4 = Image.open(BytesIO(requests.get(icon[3]).content))
        if classic[0] == False:
            skin1 = skin1.resize((420, int(420*skin1.height/skin1.width)))
        else:
            skin1 = skin1.resize((int(skin1.width/2), int(skin1.height/2)))
        if classic[1] == False:
            skin2 = skin2.resize((420, int(420*skin2.height/skin2.width)))
        else:
            skin2 = skin2.resize((int(skin2.width/2), int(skin2.height/2)))
        if classic[2] == False:
            skin3 = skin3.resize((420, int(420*skin3.height/skin3.width)))
        else:
            skin3 = skin3.resize((int(skin3.width/2), int(skin3.height/2)))
        if classic[3] == False:
            skin4 = skin4.resize((420, int(420*skin4.height/skin4.width)))
        else:
            skin4 = skin4.resize((int(skin4.width/2), int(skin4.height/2)))
        self.pasteCentered(image, 640, 360, 0, 0, skin1)
        self.pasteCentered(image, 640, 360, 640, 0, skin2)
        self.pasteCentered(image, 640, 360, 0, 360, skin3)
        self.pasteCentered(image, 640, 360, 640, 360, skin4)

        draw.text((460,310), price[0],font=font,fill=textColor)
        draw.text((1092,310), price[1],font=font,fill=textColor)
        draw.text((460,673), price[2],font=font,fill=textColor)
        draw.text((1092,673), price[3],font=font,fill=textColor)

        draw.text((30,250), name[0],font=font,fill=textColor)
        draw.text((670,250), name[1],font=font,fill=textColor)
        draw.text((30,620), name[2],font=font,fill=textColor)
        draw.text((670,620), name[3],font=font,fill=textColor)

        tier1 = Image.open(BytesIO(requests.get(tier[0]).content)).resize((50,50))
        tier2 = Image.open(BytesIO(requests.get(tier[1]).content)).resize((50,50))
        tier3 = Image.open(BytesIO(requests.get(tier[2]).content)).resize((50,50))
        tier4 = Image.open(BytesIO(requests.get(tier[3]).content)).resize((50,50))
        image.paste(tier1, (20,30), tier1)
        image.paste(tier2, (660,30), tier2)
        image.paste(tier3, (20,390), tier3)
        image.paste(tier4, (660,390), tier4)

        filepath = './tmp/' + author_id + '_store_offers.png'
        image.save(filepath)
        return filepath

