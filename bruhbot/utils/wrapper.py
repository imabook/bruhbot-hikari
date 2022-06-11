import math
import asyncio  # thanks norizon :weary:


async def wrap_word(font, text, max_width, max_height):
    width, height = font.getsize(text)
    max_row = math.ceil(max_height / height) + 2
    current_text = text
    remainder = ''
    ret = ''
    row = 0

    while current_text and row <= max_row:
        await asyncio.sleep(0)
        if width > max_width:
            remainder = f'{remainder}{current_text[-1]}'
            current_text = current_text[:-1]
        else:
            if remainder:
                remainder = f'{remainder}{current_text[-1]}'
                if (not current_text[-2].isspace()
                        and not current_text[-1].isspace()):
                    current_text = f'{current_text[:-1]}-'
                else:
                    current_text = current_text[:-1]

            ret = f'{ret}{current_text.strip()}\n'
            row += 1
            current_text = remainder[::-1]
            remainder = ''

        width = font.getsize(current_text)[0]

    return ('\n'.join(ret.split('\n')[:max_row])).strip()
