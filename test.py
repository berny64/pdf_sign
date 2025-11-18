from spire.pdf import PdfDocument, PdfImage

from PIL import Image

pdf = PdfDocument()
page = pdf.Pages.Add()
image = Image.open("test.jpg")

# Použití s určením velikosti:
x, y, width, height = 100, 150, 200, 120
page.Canvas.DrawImage(image, x, y, width, height)

# ...nebo bez určení velikosti (jen x, y):
# page.Canvas.DrawImage(image, x, y)

pdf.SaveToFile("output.pdf")
pdf.Close()