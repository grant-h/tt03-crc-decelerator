import requests
import re

URLS = ["https://reveng.sourceforge.io/crc-catalogue/1-15.htm", "https://reveng.sourceforge.io/crc-catalogue/16.htm", "https://reveng.sourceforge.io/crc-catalogue/17plus.htm"]

r_crc = re.compile(r'width=([0-9]{1,2})\s+poly=(0x[a-fA-F0-9]+)\s+init=(0x[a-fA-F0-9]+)\s+refin=(true|false)\s+refout=(true|false)\s+xorout=(0x[a-fA-F0-9]+)\s+check=(0x[a-fA-F0-9]+)\s+residue=(0x[a-fA-F0-9]+)\s+name="([^"]+)')

crcs = []
for url in URLS:
    res = requests.get(url)
    for r in r_crc.findall(res.text):
        width, poly, init, reflect_in, reflect_out, xorout, check, residue, name = r
        reflect_in = reflect_in == "true"
        reflect_out = reflect_out == "true"
        name = f'"{name}":'

        print(f'{name: <30}CC({width},\t{check},\t{poly},\t{init},\t{reflect_in},\t{reflect_out},\t{xorout}),')
