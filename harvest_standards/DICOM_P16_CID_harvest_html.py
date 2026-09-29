"""Harvest a DICOM PS3.16 context group (CID) table from the NEMA HTML rendering.

Usage (from the repository root):
    python harvest_standards/DICOM_P16_CID_harvest_html.py 4010

Writes files/DICOM Standard/part16_cid<CID>_<keyword>.csv with one row per coded
entry: CID, Keyword, Version, Coding Scheme Designator, Code Value, Code Meaning,
SNOMED-RT ID, UMLS Concept Unique ID (the last two only where the table has them).
"""
import re
import sys

import pandas as pd
import requests
from bs4 import BeautifulSoup

URL = "https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_{cid}.html"
OUT = "files/DICOM Standard/part16_cid{cid}_{name}.csv"


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def parse_cid_html(html, cid):
    soup = BeautifulSoup(html, "html.parser")
    meta = clean(soup.find(class_="variablelist").get_text(" "))
    keyword = re.search(r"(?<!FHIR )Keyword:\s*(\S+)", meta).group(1)
    version = re.search(r"Version:\s*(\S+)", meta).group(1)
    table = next(t for t in soup.find_all("table")
                 if "Code Value" in [clean(th.get_text()) for th in t.find_all("th")])
    header = [clean(th.get_text()) for th in table.find("thead").find_all("th")]
    rows = [[clean(td.get_text()) for td in tr.find_all("td")]
            for tr in table.find("tbody").find_all("tr")]
    df = pd.DataFrame(rows, columns=header)
    df.insert(0, "Version", version)
    df.insert(0, "Keyword", keyword)
    df.insert(0, "CID", str(cid))
    return df


def snake(keyword):
    return re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", keyword).lower()


if __name__ == "__main__":
    for cid in sys.argv[1:] or ["4010"]:
        html = requests.get(URL.format(cid=cid), timeout=60).text
        df = parse_cid_html(html, cid)
        out = OUT.format(cid=cid, name=snake(df["Keyword"].iloc[0]))
        df.to_csv(out, index=False)
        print(out, df.shape)
