def blit_text(screen: object, position:(float,float), text:str, font:object = None):
    return font.render(text, True, (0,0,0))