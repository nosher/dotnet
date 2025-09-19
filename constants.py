import re
import os

WEBROOT = "http://10.1.203.1"

DOCROOT = "archives/computers"
ROOT = "/home/httpd/nosher.net/docs/" + DOCROOT
CLEANER = re.compile("<.*?>|\[.*?\]", flags=re.MULTILINE|re.IGNORECASE)
CHARS = 200
TLAS = {
    "PCN": "Personal Computer News",
    "PCW": "Personal Computer World",
    "CCI": "Commodore Computing International",
    "YC": "Your Computer",
    "POCW": "Popular Computing Weekly",
    "TCOW": "\"The Collapse of Work\", Clive Jenkins and Barrie Sherman, 3rd Edition, 1980, ISBN 0-41345760-5",
    "HCW": "\"The Home Computer Wars\", Michael S. Tomczyk, 1st ed., ISBN 0-942386-78-8",
    "PRAC": "Practical Computing",
    "BLUM": "\"Blue Magic: The people, politics and power behind the IB​M personal computer\", Chposky and Leonsis, ISBN 0-8160-1391-8",
    "TCA": "\"The Computer Age: A Twenty Year View\", ed. Michael L. Dertouzos and Joel Moses, MIT, ISBN 0-262-04055-7"
}
INFLATION = {"2024": 3.9, "2023": 7.3, "2022": 9.1, "2021": 2.6, "2020": 0.9, "2019": 1.8, "2018": 2.5, "2017": 3.6, "2016": 1.8, "2015": 1.0, "2014": 2.4, "2013": 3.0, "2012": 3.2, "2011": 5.2, "2010": 4.6, "2009": -0.5, "2008": 4.0, "2007": 4.3, "2006": 3.2, "2005": 2.8, "2004": 3.0, "2003": 2.9, "2002": 1.7, "2001": 1.8, "2000": 3.0, "1999": 1.5, "1998": 3.4, "1997": 3.1, "1996": 2.4, "1995": 3.5, "1994": 2.4, "1993": 1.6, "1992": 3.7, "1991": 5.9, "1990": 9.5, "1989": 7.8, "1988": 4.9, "1987": 4.2, "1986": 3.4, "1985": 6.1, "1984": 5.0, "1983": 4.6, "1982": 8.6, "1981": 11.9, "1980": 18.0, "1979": 13.4, "1978": 8.3, "1977": 15.8, "1976": 16.5, "1975": 24.2, "1974": 16.0, "1973": 9.2, "1972": 7.1, "1971": 9.4, "1970": 6.4, "1969": 5.4, "1968": 4.7, "1967": 2.5, "1966": 3.9, "1965": 4.8, "1964": 3.3, "1963": 2.0, "1962": 4.3, "1961": 3.4, "1960": 1.0, "1959": 0.6, "1958": 3.0, "1957": 3.7, "1956": 4.9, "1955": 4.5, "1954": 1.8, "1953": 3.1, "1952": 9.2, "1951": 9.1, "1950": 3.1, "1949": 2.8, "1948": 7.7, "1947": 7.0, "1946": 3.1, "1945": 2.8}

NEW_PHOTO_CUTOFF = 60

CPUS = {                                                        
    "6502": {"name":"MOS Technology 6502", "bits": "8", "add": "16"},
    "6509": {"name":"MOS Technology 6509", "bits": "8", "add": "20", "note": "extra memory accessed via bank switching"},
    "8080": {"name":"Intel 8080", "bits": "8", "add": "16", "note": ""},
    "8085": {"name":"Intel 8085", "bits": "8", "add": "16", "note": "A faster 5V version of 8080"},
    "80C85": {"name":"Intel 80C85", "bits": "8", "add": "16", "note": "CMOS version of 8085"},
    "8086": {"name":"Intel 8086", "bits": "16", "add": "20"},   
    "80C86": {"name":"Intel 80C86", "bits": "16", "add": "20", "note": "CMOS version of 8086"},   
    "8086-2": {"name":"Intel 8086-2", "bits": "16", "add": "20", "note": "faster version of the 8086"},   
    "8088": {"name":"Intel 8088", "bits": "16", "add": "20", "note": "modified version of 8086 with only 8-bit data bus"},    
    "80C88": {"name":"Intel 80C88", "bits": "16", "add": "20", "note": "CMOS version of 8088"},    
    "80186": {"name":"Intel 80186", "bits": "16", "add": "20"}, 
    "80286": {"name":"Intel 80286", "bits": "16", "add": "24"},   
    "80386": {"name":"Intel 80386", "bits": "32", "add": "32"}, 
    "80486": {"name":"Intel 80486", "bits": "32", "add": "32"}, 
    "68000": {"name":"Motorola 68000", "bits": "32", "add": "24", "note": "16-bit data bus"},
    "68008": {"name":"Motorola 68008", "bits": "32", "add": "20", "note": "8 bit data bus"},
    "68020": {"name":"Motorola 68020", "bits": "32", "add": "32"},
    "6800": {"name":"Motorola 6800", "bits": "8", "add": "16"}, 
    "6809": {"name":"Motorola 6809", "bits": "8", "add": "16"}, 
    "6510": {"name":"MOS Technology 6510", "bits": "8", "add": "16", "note": "improved 6502"},
    "6512": {"name":"MOS Technology 6512", "bits": "8", "add": "16", "note": "same as the 6502 but requires an external clock"},
    "SCMP": {"name":"National Semiconductor SC/MP \"Scamp\"", "bits": "8", "add": "16"},
    "Z80": {"name":"Zilog Z80", "bits": "8", "add": "16", "note": "compatible with Intel 8080"},
    "6507": {"name":"MOS Technology 6507", "bits": "8", "add": "13", "note": "modified 6502 with 7-bit data bus"},
    "TMS9900": {"name":"Texas Instruments TMS9900", "bits": "16", "add": "16", "note": "world's first single-chip 16 bit CPU"},
    "WD16": {"name":"Western Digital WD16", "bits": "16", "add": "16"},
    "Z8000": {"name":"Zilog Z8000", "bits": "16", "add": "16", "note": "evolution of Z80"},
    "ARM2": {"name":"Acorn RISC Machines ARM2", "bits": "32", "add": 26},
    "8502": {"name":"MOS Technology 8502", "bits": "8", "add": "16", "note": "improved version of 6510"},
    "V20": {"name":"NEC V20", "bits": "16", "add": "20", "note": "8 bit data bus, compatible with 8088"},
    "V30": {"name":"NEC V30", "bits": "16", "add": "20", "note": "same as V20 but with 16-bit data bus"},
    "7501": {"name":"MOS Technology 7501", "bits": "8", "add": "16", "note": "variant of the 6510"},
    "8501": {"name":"MOS Technology 8501", "bits": "8", "add": "16", "note": "variant of the 6510"},
    "65SC12": {"name":"Western Design Center 65SC12", "bits": "8", "add": "16", "note": "improved CMOS version of the 6502"},
    "PD780C-1": {"name":"NEC PD780C-1", "bits": "8", "add": "16", "note": "compatible with the Zilog Z80A"},
    "mN601G": {"name":"Data General mN601G", "bits": "16", "add": "16"},
    "CDP1802": {"name":"RCA CDP-1802 \"COSMAC\"", "bits": "8", "add": "16", "note": "address bus was 8-bit multiplexed"},
    "6301": {"name":"Hitachi 6301/6309", "bits": "8", "add": "16", "note": "version of Motorola's 6809"},
    "LSI-11": {"name":"Western Digital LSI-11", "bits": "16", "add": "16", "note": "four-chip LSI version of the DEC PDP-11"},
    "6100": {"name":"Intersil 6100", "bits": "12", "add": "12", "note": "CMOS clone of DEC's PDP-8"},
    "Capricorn": {"name":"Hewlett-Packard Capricorn", "bits": "8", "add": "16", "note": "proprietary HP CPU, with built-in advanced maths features. Address bus was 8 bit multiplexed"},
    "FOCUS": {"name":"Hewlett-Packard FOCUS", "bits": "32", "add": "32", "note": "proprietary HP CPU, the first commercial 32-bit chip on the market"},
    "LH5801": {"name":"Sharp LH5801", "bits": "8", "add": "16", "note": "a CMOS chip similar to the Z80"},
} 
