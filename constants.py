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
INFLATION = {"2018": 2.5, "2017": 3.6, "2016": 1.8, "2015": 1.0, "2014": 2.4, "2013": 3.0, "2012": 3.2, "2011": 5.2, "2010": 4.6, "2009": -0.5, "2008": 4.0, "2007": 4.3, "2006": 3.2, "2005": 2.8, "2004": 3.0, "2003": 2.9, "2002": 1.7, "2001": 1.8, "2000": 3.0, "1999": 1.5, "1998": 3.4, "1997": 3.1, "1996": 2.4, "1995": 3.5, "1994": 2.4, "1993": 1.6, "1992": 3.7, "1991": 5.9, "1990": 9.5, "1989": 7.8, "1988": 4.9, "1987": 4.2, "1986": 3.4, "1985": 6.1, "1984": 5.0, "1983": 4.6, "1982": 8.6, "1981": 11.9, "1980": 18.0, "1979": 13.4, "1978": 8.3, "1977": 15.8, "1976": 16.5, "1975": 24.2, "1974": 16.0, "1973": 9.2, "1972": 7.1, "1971": 9.4, "1970": 6.4, "1969": 5.4, "1968": 4.7, "1967": 2.5, "1966": 3.9, "1965": 4.8, "1964": 3.3, "1963": 2.0, "1962": 4.3, "1961": 3.4, "1960": 1.0, "1959": 0.6, "1958": 3.0, "1957": 3.7, "1956": 4.9, "1955": 4.5, "1954": 1.8, "1953": 3.1, "1952": 9.2, "1951": 9.1, "1950": 3.1, "1949": 2.8, "1948": 7.7, "1947": 7.0, "1946": 3.1, "1945": 2.8}

NEW_PHOTO_CUTOFF = 60
