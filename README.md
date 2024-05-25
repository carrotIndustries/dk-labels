DigiKey label generator
=======================

Small ring binders like [these](https://www.ebay.de/itm/252799830563) 
are really convenient for efficiently storing components on cut tape. 
What's not so convenient is manually cutting and pasting the labels 
from DigiKey pouches or manually copying part numbers.

To reduce the ever-growing pile of DigiKey pouches I needed an 
efficient way to generate labels to apply to the sample book pages.

https://github.com/carrotIndustries/dk-labels/assets/877304/2ee3b475-abf8-4c23-9cb7-c60ba25efb4c

# Implementation

Every product shipped from DigiKey comes with a Data Matrix code that 
contains the contents of the product label. The [Cognex Barcode Scanner 
app](https://play.google.com/store/apps/details?id=com.manateeworks.barcodescanners)
scans Data Matrix code with ease (compared to the ZXing app) and 
supports automatically opening an URL after a successful scan.

A flask app running on my laptop then uses [DigiKey's 
API](https://developer.digikey.com/products/barcode/barcoding/product2dbarcode)
for converting the barcode to MPN and description.

<img alt="Form with MPN, description and DK PN" src="https://raw.githubusercontent.com/carrotIndustries/dk-labels/main/media/app.png" width="50%" />

After confirming and optionally making edits it then prints the label 
on a [Phomemo 
D30](https://phomemo.com/de-de/products/d30-etikettenhersteller) label 
printer via bluetooth.

# Setup

These scripts piggy-back on the DigiKey API integration in Horizon EDA, 
so [set it 
up](https://horizon-eda.readthedocs.io/en/latest/digikey-api.html) 
first.

Then create the `config.py` like this:
```python
printer_mac = '00:00:00:00:00:00'
```

Then start the flask app: `flask --app server run -p 8337 -h 0.0.0.0`

Configure the barcode scanner to point to the computer running the 
flask app.

# Anticipated questions

## Why directly talk to the printer?

Directly connecting to the printer via bluetooth has less ways to wrong 
than using cups for example.

## The web app looks so bland

I know, I suck at webdev.

## Why not run it all on the phone?

I can't be bothered to learn how to make Android Apps.
