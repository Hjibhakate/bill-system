import speech_recognition as sr
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.message import EmailMessage
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# ================= GLOBAL DATA =================
bill_items = []

SENDER_EMAIL = "hjibhakate2004@gmail.com"
APP_PASSWORD = "frlwxqaduxlzkkrb"  # <-- put App Password here

# ================= VOICE INPUT =================
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

# ================= PARSE VOICE =================
def parse_data(text):
    try:
        quantity = float(re.search(r"quantity ([\d\.]+)", text).group(1))
        rate = float(re.search(r"rate ([\d\.]+)", text).group(1))
        vehicle = re.search(r"vehicle (.*)", text).group(1).upper()

        total = round(quantity * rate, 2)

        return {
            "date": datetime.now().strftime("%d/%m/%Y"),
            "vehicle": vehicle,
            "quantity": quantity,
            "rate": rate,
            "total": total
        }
    except:
        print("❌ Could not parse command")
        return None

# ================= ADD ITEM =================
def add_item(item):
    bill_items.append(item)
    print(f"✅ Entry Added | Total = {item['total']}")

# ================= TOTAL =================
def grand_total():
    return round(sum(i["total"] for i in bill_items), 2)

# ================= PDF GENERATION =================
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

    c.drawString(50, y - 30, f"GRAND TOTAL : {grand_total()}")

    c.save()
    print("📄 PDF Generated:", filename)
    return filename

# ================= SEND EMAIL =================
def send_email(to_email, pdf_file):
    msg = EmailMessage()
    msg["Subject"] = "Fuel Bill"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.set_content("Please find attached your fuel bill.")

    with open(pdf_file, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=pdf_file
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)

# ================= EMAIL UI =================
def open_email_window(pdf_file):
    def submit():
        email = email_entry.get()
        if not email:
            messagebox.showerror("Error", "Please enter email")
            return

        send_email(email, pdf_file)
        messagebox.showinfo("Success", "📧 Bill sent successfully!")
        root.destroy()

    root = tk.Tk()
    root.title("Send Fuel Bill")
    root.geometry("350x180")

    tk.Label(root, text="Enter Customer Email", font=("Arial", 12)).pack(pady=10)
    email_entry = tk.Entry(root, width=35)
    email_entry.pack(pady=5)

    tk.Button(root, text="Submit", command=submit, bg="green", fg="white").pack(pady=15)
    root.mainloop()

# ================= MAIN FLOW =================
print("🎙️ Voice Billing System Started")
print("Say: add entry quantity 100 rate 90 vehicle MH34CQ7748")
print("Say: generate bill")

while True:
    command = listen()

    if "add entry" in command:
        item = parse_data(command)
        if item:
            add_item(item)

    elif "generate bill" in command:
        pdf = generate_pdf()
        open_email_window(pdf)
        break
