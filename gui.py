import httpx, threading, asyncio, json, os
from doc import doc
import customtkinter as ctk
from tkcalendar import Calendar
from hijridate import Gregorian
from datetime import datetime
from async_scrapping import NewsScrapping

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

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

def load_settings():
    """Load settings from JSON file, return defaults if file doesn't exist."""
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"theme": "dark"}

def save_settings(settings):
    """Save settings to JSON file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

# Load saved theme preference
settings = load_settings()
ctk.set_appearance_mode(settings.get("theme", "dark"))
ctk.set_default_color_theme("blue")

class Scrapper:
    def __init__(self, async_loop):
        self.root = ctk.CTk()
        self.async_loop = async_loop

        self.root.title("EK Scrapper")
        self.root.geometry("850x600")
        self.root.minsize(800, 600)

        try:
            self.root.iconbitmap('icon.ico')
        except Exception as e:
            print(e)

        # Configure grid weights for responsive layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        # ===== HEADER FRAME =====
        self.header_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Theme toggle button (left side)
        self.is_dark_mode = settings.get("theme", "dark") == "dark"
        self.theme_button = ctk.CTkButton(
            self.header_frame,
            text="🌙" if self.is_dark_mode else "🌞",
            text_color="white" if self.is_dark_mode else "#000000",
            width=40,
            height=40,
            corner_radius=20,
            font=('Segoe UI Emoji', 18),
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=0, sticky="w")

        # Title (center)
        self.label = ctk.CTkLabel(
            self.header_frame,
            text="އެކިއެކި ކަންކަން ހިނގާ ގޮތް ނެގުމަށްޓަކައި",
            font=('Faruma', 24, 'bold')
        )
        self.label.grid(row=0, column=1)

        # Empty label to balance the layout (right side)
        self.spacer = ctk.CTkLabel(self.header_frame, text="", width=100)
        self.spacer.grid(row=0, column=2, sticky="e")

        # ===== URL INPUT FRAME =====
        self.url_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.url_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.url_frame.grid_columnconfigure(0, weight=1)

        self.url_label = ctk.CTkLabel(
            self.url_frame,
            text="ލިންކްތައް ޖައްސަވާ (ކޮމާ އިން ވަކިކޮށްފައި)",
            font=('Faruma', 16),
        )
        self.url_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))

        self.textbox = ctk.CTkTextbox(
            self.url_frame,
            height=80,
            font=('Segoe UI', 13),
            corner_radius=8
        )
        self.textbox.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))

        # ===== MAIN CONTENT FRAME =====
        self.content_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # ===== LEFT SIDE - Calendar Section =====
        self.calendar_container = ctk.CTkFrame(self.content_frame, corner_radius=10, fg_color="transparent")
        self.calendar_container.grid(row=0, column=0, sticky="n", padx=(0, 15))

        self.date_label = ctk.CTkLabel(
            self.calendar_container,
            text="ތާރީޚު ނަންގަވާ",
            font=('Faruma', 16)
        )
        self.date_label.pack(pady=(0, 10))

        self.calendar_frame = ctk.CTkFrame(self.calendar_container, corner_radius=10)
        self.calendar_frame.pack()

        self.calendar = Calendar(
            self.calendar_frame,
            selectmode="day",
            firstweekday="sunday",
            weekenddays=[6, 7],
            font=('Segoe UI', 11),
            showweeknumbers=False,
            date_pattern='dd/MM/yyyy',
            background='#2b2b2b',
            foreground='white',
            headersbackground='#1f538d',
            headersforeground='white',
            selectbackground='#1f538d',
            selectforeground='white',
            normalbackground='#333333',
            normalforeground='white',
            weekendbackground='#3d3d3d',
            weekendforeground='white',
            othermonthbackground='#252525',
            othermonthforeground='#666666',
            othermonthwebackground='#252525',
            othermonthweforeground='#666666',
            borderwidth=0
        )
        self.calendar.pack(padx=15, pady=15)

        # Apply correct calendar colors based on saved theme
        self.apply_calendar_theme()

        # ===== RIGHT SIDE - Progress Section =====
        self.progress_container = ctk.CTkFrame(self.content_frame, corner_radius=10, fg_color="transparent")
        self.progress_container.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        self.progress_container.grid_rowconfigure(1, weight=1)
        self.progress_container.grid_columnconfigure(0, weight=1)

        self.progress_label = ctk.CTkLabel(
            self.progress_container,
            text="މިންވަރު",
            font=('Faruma', 16)
        )
        self.progress_label.grid(row=0, column=0, pady=(0, 10))

        self.progress = ctk.CTkTextbox(
            self.progress_container,
            font=('Consolas', 12),
            corner_radius=10,
            state='disabled'
        )
        self.progress.grid(row=1, column=0, sticky="nsew")

        # ===== BUTTON FRAME =====
        self.button_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        self.button_frame.grid(row=3, column=0, pady=20)

        self.button1 = ctk.CTkButton(
            self.button_frame,
            text="ޚަބަރު ނަގާ",
            font=('Faruma', 16, 'bold'),
            width=200,
            height=45,
            corner_radius=10,
            command=self.do_tasks
        )
        self.button1.pack()

        self.root.mainloop()

    def apply_calendar_theme(self):
        """Apply the correct calendar colors based on current theme."""
        if self.is_dark_mode:
            self.calendar.configure(
                background='#2b2b2b',
                foreground='white',
                headersbackground='#1f538d',
                headersforeground='white',
                selectbackground='#1f538d',
                selectforeground='white',
                normalbackground='#333333',
                normalforeground='white',
                weekendbackground='#3d3d3d',
                weekendforeground='white',
                othermonthbackground='#252525',
                othermonthforeground='#666666',
                othermonthwebackground='#252525',
                othermonthweforeground='#666666'
            )
        else:
            self.calendar.configure(
                background='#ffffff',
                foreground='#333333',
                headersbackground='#3b8ed0',
                headersforeground='white',
                selectbackground='#3b8ed0',
                selectforeground='white',
                normalbackground='#f0f0f0',
                normalforeground='#333333',
                weekendbackground='#e8e8e8',
                weekendforeground='#333333',
                othermonthbackground='#fafafa',
                othermonthforeground='#aaaaaa',
                othermonthwebackground='#fafafa',
                othermonthweforeground='#aaaaaa'
            )

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode

        # Save the preference
        save_settings({"theme": "dark" if self.is_dark_mode else "light"})

        if self.is_dark_mode:
            ctk.set_appearance_mode("dark")
            self.theme_button.configure(text="🌙", text_color="white")
        else:
            ctk.set_appearance_mode("light")
            self.theme_button.configure(text="🌞", text_color="#000000")

        self.apply_calendar_theme()

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
        self.progress.configure(state='normal')
        self.progress.insert("end", f"{msg}\n")
        self.progress.configure(state='disabled')
        self.progress.see("end")

    async def documenting(self):
        inputt = (self.textbox.get("1.0", "end-1c")).split(',')
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
