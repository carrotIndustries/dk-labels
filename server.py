from flask import Flask, request, render_template, Response
import urllib.parse
from api import DigiKeyApi
import draw
import io
from d30 import Printer
import config
app = Flask(__name__)

dk = DigiKeyApi()

@app.route("/")
def hello_world():
    qs = request.query_string.decode()
    r = {'DigiKeyPartNumber': '', 'ManufacturerPartNumber': '', 'ProductDescription': ''}

    if len(qs) :
        barcode = urllib.parse.unquote(qs).replace(chr(0x1e), chr(0x241E)).replace('\x1d', chr(0x241d))
        r= dk.get_barcode(barcode)
    #r = {'DigiKeyPartNumber': '311-1061-1-ND', 'ManufacturerPartNumber': 'CC0603JRNPO9BN180', 'CustomerPartNumber': '', 'ManufacturerName': 'YAGEO (VA)', 'ProductDescription': 'CAP CER 18PF 50V C0G/NPO 0603', 'Quantity': 50, 'SalesorderId': 0, 'InvoiceId': 0, 'PurchaseOrder': '', 'CountryOfOrigin': 'TW', 'LotCode': None, 'DateCode': None}
    return render_template('barcode.html', **r)

@app.route("/img")
def img():
    buf = io.BytesIO()
    surf = draw.render_small_label(request.args.get("mpn"), request.args.get("descr"), request.args.get("qr", ""))
    surf.write_to_png(buf)
    response = Response(buf.getbuffer().tobytes(), 200)
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route("/print", methods=['POST'])
def print_post():
    surf = draw.render_small_label(request.form.get("mpn"), request.form.get("descr"), request.form.get("qr", ""))
    printer = Printer(config.printer_mac)
    battery = printer.get_battery()
    printer.print_surface(surf)
    return f"Printed<br/>Battery: {battery}"
