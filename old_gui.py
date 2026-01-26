import httpx, threading, asyncio
from doc import doc
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkcalendar import *
from hijridate import Gregorian
from datetime import datetime
from async_scrapping import NewsScrapping

weekday_to_dhivehi = {
    0: "ހޯމަ",
    1: "އަންގާރަ",
    2: "ބުދަ",
    3: "ބުރާސްފަތި",
    4: "ހުކުރު",
    5: "ހޮނިހިރު",
    6: "އާދިއްތަ"
}

month_num = {
    'jan' : 1,
    'feb' : 2,
    'mar' : 3,
    'apr' : 4,
    'may' : 5,
    'jun' : 6,
    'jul' : 7,
    'aug' : 8,
    'sep' : 9,
    'oct' : 10,
    'nov' : 11,
    'dec' : 12,
}

short_to_long_month = {
    'jan' : 'january',
    'feb' : 'february',
    'mar' : 'march',
    'apr' : 'april',
    'may' : 'may',
    'jun' : 'june',
    'jul' : 'july',
    'aug' : 'august',
    'sep' : 'september',
    'oct' : 'october',
    'nov' : 'november',
    'dec' : 'december',
}

hijri_num_to_month = {
    1: "މުޙައްރަމް",
    2: "ޞަފަރު",
    3: "ރަބީޢުލްއައްވަލް",
    4: "ރަބީޢުލްއާޚިރު",
    5: "ޖުމާދުލްއޫލާ",
    6: "ޖުމާދަލްއާޚިރާ",
    7: "ރަޖަބު",
    8: "ޝަޢުބާން",
    9: "ރަމަޟާން",
    10: "ޝައްވާލް",
    11: "ޛުލްޤައިދާ",
    12: "ޛުލްޙިއްޖާ",
}

month_num_in_dhivehi = {
    'ޖަނަވަރީ': 1,
    'ފެބުރުވަރީ' : 2,
    'މާރިޗު' : 3,
    'އޭޕްރިލް' : 4,
    'މޭ' : 5,
    'ޖޫން' : 6,
    'ޖުލައި' : 7,
    'އޮގަސްޓް' : 8,
    'ސެޕްޓެންބަރު': 9,
    'އޮކްޓޫބަރު' : 10,
    'ނޮވެންބަރު': 11,
    'ޑިސެންބަރު' : 12
}


class Scrapper:
    def __init__(self, async_loop):
        self.root = tk.Tk()
        self.async_loop = async_loop

        self.root.title("EK Scrapper")
        try:
            self.root.iconbitmap('icon.ico')
        except Exception as e:
            print(e)

        self.label = tk.Label(self.root, text="އެކިއެކި ކަންކަން ހިނގާ ގޮތް ނެގުމަށްޓަކައި", font=('Faruma', 20))
        self.label.grid(row=0, column=0, columnspan=2)

        self.textbox = tk.Text(self.root, height=3, font=('Faruma', 13), borderwidth=2)
        self.textbox.grid(row=2, column=0, padx=20, pady=5, columnspan=2)

        self.date = tk.Label(self.root, text="ތާރީޚު ނަންގަވާ", font=('Faruma', 14))
        self.date.grid(row=3, column=0, pady=5)

        self.calendar = Calendar(self.root,
                                 selectmode="day",
                                 firstweekday="sunday",
                                 weekenddays=[6,7],
                                 font=('Faruma', 10),
                                 showweeknumbers=False,
                                 date_pattern='dd/MM/yyyy'
                                )
        self.calendar.grid(row=4, column=0, pady=10, padx=20)

        # self.entry_label = tk.Label(self.root, text="ތިރީގައި ފައިލް ނަން ލިޔުއްވާ", font=('Faruma', 15))
        # self.entry_label.grid()
        # self.entry = tk.Entry(self.root, width=35, borderwidth=2, font=('Faruma', 14), textvariable=self.file_name)
        # self.entry.pack(padx=20, pady=10)

        self.updates = tk.Label(self.root, text="މިންވަރު", font=('Faruma', 14))
        self.updates.grid(row=3, column=1)

        self.progress = tk.Text(self.root, height=10, width=70, state='disabled', font=('Calibri', 12))
        self.progress.grid(row=4, column=1, padx=20)

        self.button1 = ttk.Button(self.root, width=15, text="\n!ނަގާ ޚަބަރު\n", command= lambda: self.do_tasks())
        self.button1.grid(row=5, column=1, pady=10)

        self.root.mainloop()

    def _asyncio_thread(self):
        self.async_loop.run_until_complete(self.documenting())

    def do_tasks(self):
        """ Button-Event-Handler starting the asyncio part. """

        self.file_name = self.calendar.get_date()
        threading.Thread(target=self._asyncio_thread).start()

    def get_file_name(self, date: list):
        """Returns the filename based on the date [dd,MM,yyyy] passed in."""
        months = {v: k for k, v in month_num.items()}
        day = int(date[0])
        if day < 10:
            day = str(date[0])
        month = short_to_long_month[months[int(date[1])]].capitalize()

        return f"{day} {month} {date[2]}"

    def get_greg_date(self, date: list):
        """Returns Gregorian Date [dd, MM, yyy] converted to Dhivehi as a string"""
        date = [int(num) for num in date]
        months = {v: k for k,v in month_num_in_dhivehi.items()}
        Date = datetime(date[2], date[1], date[0]).weekday()
        return f"{date[0]} {months[int(date[1])]} {date[2]} ({weekday_to_dhivehi[Date]})"

    def get_hijri_date(self, date: list):
        """Returns Gregorian Date [dd, MM, yyy] converted into Hijri Date in Dhivehi as a string"""
        date = [int(num) for num in date]
        converted_date = str(Gregorian(date[2], date[1], date[0]).to_hijri())
        converted_date_list = converted_date.split('-')
        converted_date_list[1] = hijri_num_to_month[int(converted_date_list[1])]

        return ' '.join(reversed(converted_date_list))

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

        date = self.calendar.get_date().split('/')
        file_name = self.get_file_name(date)

        hijri_date = self.get_hijri_date(date)
        dhivehi_date = self.get_greg_date(date)

        if not new_urls[0]:
            self.printer("No links. Paste the link you would like to take.")
            return
        if not file_name:
            self.printer("Please choose a date.")
            return

        timeout = httpx.Timeout(5, connect_timeout=None, read_timeout=None)
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
                    self.printer(f"\"{url}\" isn't a supported link. Please enter a suitable link.")
                    continue

            results = await asyncio.gather(*tasks)

            # BELOW HERE IS INPUTING THE DATA TO DOCX FILE
            for result in results:
                try:
                    update_msg = doc(
                        filename = file_name,
                        hijri_date=hijri_date,
                        dhivehi_date=dhivehi_date,
                        url = result['url'],
                        author = result['author'],
                        title = result['title'],
                        image = result['pic'],
                        paras = result['paras']
                        )
                    self.printer(update_msg)
                except Exception as e:
                    self.printer(f"An error occured {e.__class__.__name__}, when trying to process: {result['url']}")
                    self.printer(e)

        print("Finished copying all the links!")
        self.printer("Finished copying all the links!")

if __name__ == '__main__':
    aLoop = asyncio.get_event_loop()
    Scrapper(aLoop)
