import os
from importlib.resources import contents
import json
import codecs

from pypdf import PdfReader, PdfWriter
from dotenv import load_dotenv
import openai
import base64

INPUT_FOLDER = 'INPUT_FOLDER/'
OUTPUT_FOLDER = 'OUTPUT_FOLDER/'
SIGNATURE_IMAGE = ''
MODEL = "gpt-5"
SYSTEM_MESSAGE = ("""V příloze ti posílám PDF nájemní smlouvy. Doplň mi prosím souřadnice (x,y v pixelech), na které patří podpis nájemníka.
                     Předpokládej standardní velikost stránky (A4) na výšku, předpokládej standardní rozlišení. Odvoď DPI.
                     Formát odpovědi bude JSON:
                     {
                     "page": 2,
                     "x_coordinate": 100,
                     "y_coordinate": 200,
                     "dpi": 100
                     "result" : "ok"
                     }
                     Pokud nebudeš vědět, vrať
                     {
                     "result":"nok",
                     "reason": "why nok"
                     }
                    """)
SYSTEM_MESSAGE_2 = """V příloze ti zísálám jpg soubor. 
                      Chci abys i vygeneroval jpeg, kde bude obrázek na následujících souřadnicích níže. 
                      Ignoruj "page" atribut. Jedná se standardní PDF A4, a standardní rozlišení. 
                      Vrať mi pouze base64 zakodovaný obrázek """

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
chatgpt_client = openai.OpenAI(api_key=OPENAI_API_KEY)

with open("signature.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode('utf-8')

for filename in os.listdir(INPUT_FOLDER):

    contract = chatgpt_client.files.create(
        file=open("INPUT_FOLDER/Najemni_smlouva.pdf", "rb"),
        purpose='user_data'
    )

    completion = chatgpt_client.chat.completions.create(model=MODEL, messages= [ { "role":"user",          "content": [
                {
                    "type": "file",
                    "file": {
                        "file_id": contract.id,
                    }
                },
                {
                    "type": "text",
                    "text": SYSTEM_MESSAGE,
                },
            ]}])
    json_response =  json.loads(completion.choices[0].message.content)
    print(json_response)
    if json_response['result'] == 'ok':
        completion = chatgpt_client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
            {
                "type": "text",
                "text": SYSTEM_MESSAGE_2 + str(json_response),
            },
        ]}])
        print(completion.choices[0].message.content)
        content = chatgpt_client.files.content(completion.choices[0].message.content)
        with open("test.pdf", "wb") as f:
            f.write(codecs.decode(chatgpt_client.files.content(completion.choices[0].message.content), "base64"))
    else:
        content = None





print(type(content))






def add_watermark(wmFile, pageObj):
    # creating pdf reader object of watermark pdf file
    reader = PdfReader(wmFile)

    # merging watermark pdf's first page with passed page object.
    pageObj.merge_page(reader.pages[0])

    # returning watermarked page object
    return pageObj

def main():
    # watermark pdf file name
    mywatermark = 'watermark.pdf'

    # original pdf file name
    origFileName = 'PDFs/test.pdf'

    # new pdf file name
    newFileName = 'watermarked_example.pdf'

    # creating pdf File object of original pdf
    pdfFileObj = open(origFileName, 'rb')

    # creating a pdf Reader object
    reader = PdfReader(pdfFileObj)

    # creating a pdf writer object for new pdf
    writer = PdfWriter()

    # adding watermark to each page
    for page in reader.pages:
        # creating watermarked page object
        if page == reader.pages[-1]:
            page_adj = page
            add_signature = PdfReader("signed_placeholder.pdf").pages[0]

            page_adj.merge_page(add_signature)
        else:
            page_adj = page
        # adding watermarked page object to pdf writer
        writer.add_page(page_adj)

    # writing watermarked pages to new file
    with open(newFileName, 'wb') as newFile:
        writer.write(newFile)

    # closing the original pdf file object
    pdfFileObj.close()

if __name__ == "__main__":
    # calling the main function
    main()