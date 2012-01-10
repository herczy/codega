def reverse(xml):
    if xml.text is not None:
        xml.text = ''.join(reversed(xml.text))

    if xml.tail is not None:
        xml.tail = ''.join(reversed(xml.tail))

    for subnode in xml:
        reverse(subnode)

    return xml

def uppercase(xml):
    if xml.text is not None:
        xml.text = xml.text.upper()

    if xml.tail is not None:
        xml.tail = xml.tail.upper()

    for subnode in xml:
        uppercase(subnode)

    return xml
