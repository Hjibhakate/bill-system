import speech_recognition as sr
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.message import EmailMessage
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


# ---------------- GLOBAL DATA ----------------
bill_items = []

# ---------------- VOICE INPUT ----------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Speak now...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        print("🗣️ You said:", text)
        return text.lower()
    except:
        print("❌ Could not recognize voice")
        return ""

# ---------------- PARSE COMMAND ----------------
def parse_data(text):
    try:
        quantity = float(re.search(r"quantity ([\d\.]+)", text).group(1))
        rate = float(re.search(r"rate ([\d\.]+)", text).group(1))
        vehicle = re.search(r"vehicle (.*)", text).group(1).upper()

        total = round(quantity * rate, 2)

        item = {
            "date": datetime.now().strftime("%d/%m/%Y"),
            "vehicle": vehicle,
            "quantity": quantity,
            "rate": rate,
            "total": total
        }
        return item
    except:
        print("❌ Could not parse command")
        return None

# ---------------- ADD ITEM ----------------
def add_item(item):
    bill_items.append(item)
    print(f"✅ Entry Added | Total = {item['total']}")

# ---------------- CALCULATE TOTAL ----------------
def grand_total():
    return round(sum(i["total"] for i in bill_items), 2)

# ---------------- GENERATE PDF ----------------
def generate_pdf():
    filename = "Fuel_Bill.pdf"
    c = canvas.Canvas(filename, pagesize=A4)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 820, "P.G. WANDILE PETROLEUM")
    c.setFont("Helvetica", 10)
    c.drawString(50, 800, "TAX INVOICE")

    y = 760
    c.drawString(50, y, "DATE")
    c.drawString(120, y, "VEHICLE")
    c.drawString(260, y, "QTY")
    c.drawString(320, y, "RATE")
    c.drawString(380, y, "TOTAL")

    y -= 20

    for i in bill_items:
        c.drawString(50, y, i["date"])
        c.drawString(120, y, i["vehicle"])
        c.drawString(260, y, str(i["quantity"]))
        c.drawString(320, y, str(i["rate"]))
        c.drawString(380, y, str(i["total"]))
        y -= 20

    c.drawString(50, y - 20, f"GRAND TOTAL : {grand_total()}")

    c.save()
    print("📄 PDF Generated:", filename)
    return filename

# ---------------- SEND EMAIL ----------------
def send_email(to_email, pdf_file):
    msg = EmailMessage()
    msg["Subject"] = "Fuel Bill"
    msg["From"] = "yourgmail@gmail.com"
    msg["To"] = to_email
    msg.set_content("Please find attached your fuel bill.")

    with open(pdf_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=pdf_file
        )

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login("yourgmail@gmail.com", "YOUR_APP_PASSWORD")
    server.send_message(msg)
    server.quit()

    print("📧 Email sent successfully!")

# ---------------- MAIN FLOW ----------------
print("🎙️ Voice Billing System Started")
print("Say: 'add entry quantity 100 rate 90 vehicle MH34CQ7748'")
print("Say: 'generate bill' when finished")

while True:
    command = listen()

    if "add entry" in command:
        item = parse_data(command)
        if item:
            add_item(item)

    elif "generate bill" in command:
        pdf = generate_pdf()
        email = input("📧 Enter customer email: ")
        send_email(email, pdf)
        break
# more feature will be added soon 
