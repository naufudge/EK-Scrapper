import httpx, threading, asyncio
from doc import doc
import tkinter as tk
from tkinter import ttk
from async_scrapping import NewsScrapping

class Scrapper:
    def __init__(self, async_loop):
        self.root = tk.Tk()
        self.async_loop = async_loop

        self.root.title("EK Scrapper v1.2")
        try:
            self.root.iconbitmap('icon.ico')
        except Exception as e:
            print(e)

        self.label = tk.Label(self.root, text="އެކިއެކި ކަންކަން ހިނގާ ގޮތް ނެގުމަށްޓަކައި", font=('Faruma', 20))
        self.label.pack(padx=20, pady=20)

        self.textbox = tk.Text(self.root, height=3, font=('Faruma', 14), borderwidth=2)
        self.textbox.pack(padx=20, pady=10)

        self.entry_label = tk.Label(self.root, text="ތިރީގައި ފައިލް ނަން ލިޔުއްވާ", font=('Faruma', 15)).pack()

        self.file_name = tk.StringVar
        self.entry = tk.Entry(self.root, width=35, borderwidth=2, font=('Faruma', 13), textvariable=self.file_name)
        self.entry.pack(padx=20, pady=10)

        self.button1 = ttk.Button(self.root, width=15, text="\n!ނަގާ ޚަބަރު\n", command= lambda: self.do_tasks())
        self.button1.pack(padx=10, pady=10)

        self.updates = tk.Label(self.root, text="Progress Updates:", font=('Faruma', 15))
        self.updates.pack()
        self.progress = tk.Text(self.root, height=10, width=70, state='disabled', font=('Calibri', 12))
        self.progress.pack(pady=10)

        self.root.mainloop()

    def _asyncio_thread(self):
        self.async_loop.run_until_complete(self.documenting())

    def do_tasks(self):
        """ Button-Event-Handler starting the asyncio part. """
        threading.Thread(target=self._asyncio_thread).start()

    # Progress updater below
    def printer(self, msg):
        self.progress['state'] = 'normal'
        self.progress.insert("end-1c", f"{msg}\n")
        self.progress['state'] = 'disabled'
        self.progress.see("end")

    async def documenting(self):
        inputt = (self.textbox.get("1.0", tk.END)).split(',')
        urls, tasks = [], []
        urls.append(inputt)

        new_urls = [url.strip() for sublist in urls for url in sublist]
        file_name = self.entry.get()
        if not new_urls[0]:
            self.printer("No links. Paste the link you would like to take.")
            return
        if not file_name:
            self.printer("Enter a file name.")
            return
        timeout = httpx.Timeout(5, read=None)
        async with httpx.AsyncClient(http2=True, timeout=timeout) as client:
            ns = NewsScrapping(client)

            for url in new_urls:
                if (url.find("sun.mv") > 0):
                    tasks.append(asyncio.create_task(ns.Sun(url)))

                elif (url.find("presidency.gov.mv") > 0):
                    tasks.append(asyncio.create_task(ns.President(url)))

                elif (url.find("mihaaru.com") > 0):
                    tasks.append(asyncio.create_task(ns.Mihaaru(url)))

                elif (url.find("avas.mv") > 0):
                    tasks.append(asyncio.create_task(ns.Avas(url)))
                else:
                    self.printer(f"'{url}' isn't a supported link. Please enter a suitable link.")
                    continue

            results = await asyncio.gather(*tasks)

            #BELOW HERE IS INPUTING THE DATA TO DOCX FILE
            for result in results:
                update_msg = doc(
                    filename = file_name, 
                    url = result['url'], 
                    author = result['author'], 
                    title = result['title'], 
                    image = result['pic'], 
                    paras = result['paras']
                    )
                self.printer(update_msg)

        print("Finished copying all the links!")
        self.printer("Finished copying all the links!")

if __name__ == '__main__':
    aLoop = asyncio.get_event_loop()
    Scrapper(aLoop)
