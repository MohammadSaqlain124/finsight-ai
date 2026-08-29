from app.services.pdf_parser import parse_pdf, PDFPasswordError

print("PLAIN:")
for r in parse_pdf("statement_plain.pdf"):
    print(" ", r)

print("\nLOCKED + password:")
print(" ", parse_pdf("statement_locked.pdf", password="test123")[0])

print("\nLOCKED, no password:")
try:
    parse_pdf("statement_locked.pdf")
except PDFPasswordError as e:
    print("  ->", e)

print("\nLOCKED, wrong password:")
try:
    parse_pdf("statement_locked.pdf", password="nope")
except PDFPasswordError as e:
    print("  ->", e)