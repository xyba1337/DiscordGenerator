# PreInstalled PyPackages
import asyncio
import logging
import os
import random
import re
import time
import tempfile

# Pip Install Packages
import numpy as np
import scipy.interpolate
import playwright_stealth
import httpx
from playwright.async_api import async_playwright
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import discum
from TempMail import TempMail

# Imports from Files
from hcaptcha_challenger import (DIR_CHALLENGE, DIR_MODEL, PATH_OBJECTS_YAML,
                                 ArmorCaptcha)


class Faker():
    def __init__(self, client):
        self.client = client
        return

    async def person(self, gender="random"):
        url = f"https://api.namefake.com/english-united-states/{gender}"
        r = await self.client.get(url)
        data = r.json()
        self.name = data.get("name")
        self.maiden_name = data.get("maiden_name")
        self.birth_date = data.get("birth_data")
        self.birth_year = self.birth_date.split("-")[0]
        # self.birth_month = self.birth_date.split("-")[1]
        # self.birth_day = self.birth_date.split("-")[2]
        self.birth_month = str(random.randint(1, 12))
        self.birth_day = str(random.randint(1, 12))
        self.email_name = data.get("email_u")
        self.email_domain = data.get("email_d")
        self.email = f"{self.email_name}@{self.email_domain}"
        self.username = data.get("username")
        self.password = data.get("password")
        self.domain = data.get("domain")
        self.company = data.get("company")
        self.pheight = data.get("height")
        self.pweight = data.get("weight")
        self.eye = data.get("eye")
        self.hair = data.get("hair")
        self.sport = data.get("sport")

    async def geolocation(self, country=""):
        url = f"https://api.3geonames.org/randomland.{country}.json"
        r = await self.client.get(url)
        data = r.json()["nearest"]
        self.latitude = data.get("latt")
        self.longitude = data.get("longt")
        self.city = data.get("city")
        self.country = data.get("prov")
        self.state = data.get("state")
        self.region = data.get("region")
        self.elevation = data.get("elevation")
        self.timezone = data.get("timezone")

    async def computer(self):
        try:
            # Sometimes the API is offline
            while True:
                url = "http://fingerprints.bablosoft.com/preview?rand=0.1&tags=Firefox,Desktop,Microsoft%20Windows"
                r = await self.client.get(url, timeout=5.0)
                data = r.json()
                self.useragent = data.get("ua")
                self.vendor = data.get("vendor")
                self.renderer = data.get("renderer")
                self.width = data.get("width")
                self.height = data.get("height")
                self.avail_width = data.get("availWidth")
                self.avail_height = data.get("availHeight")
                # If the Window is too small for the captcha
                if self.height > 810 and self.avail_height > 810:
                    return
        except Exception as e:
            # If Bablosoft Website is offline
            software_names = [SoftwareName.FIREFOX.value]
            operating_systems = [OperatingSystem.WINDOWS.value]
            user_agent_rotator = UserAgent(
                software_names=software_names, operating_systems=operating_systems, limit=1)
            self.useragent = user_agent_rotator.get_random_user_agent()
            self.vendor = "Google Inc."
            self.renderer = "Google Inc. (AMD)"
            self.width = 1280
            self.height = 720
            self.avail_width = 1280
            self.avail_height = 720

    # Shit Method To Get Locale of Country code
    async def locale(self, country_code="US"):
        url = f"https://restcountries.com/v3.1/alpha/{country_code}"
        r = await self.client.get(url)
        data = r.json()[0]
        self.languages = data.get("languages")
        self.language_code = list(self.languages.keys())[0][:2]
        self.locale = f"{self.language_code.lower()}-{country_code.upper()}"


class Proxy():
    def __init__(self, client):
        self.client = client
        return

    def Split(self, proxy):
        if "@" in proxy:
            first, second = proxy.split("@")
            _1, _2 = first.split(":")
            _3, _4 = second.split(":")
            return [_3, _4, _1, _2]
        else:
            return proxy.split(":")

    # OldCheck (Rate Limitation)
    class OldCheck():
        def __init__(selff, client, proxy):
            proxies = {"http": f"http://{proxy}",
                       "https": f"http://{proxy}"} if proxy else {}
            r = httpx.get("http://ip-api.com/json/", proxies=proxies)
            data = r.json()
            selff.country = data.get("country")
            selff.country_code = data.get("countryCode")
            selff.region = data.get("region")
            selff.city = data.get("city")
            selff.zip = data.get("zip")
            selff.country = data.get("country")
            selff.latitude = data.get("lat")
            selff.longitude = data.get("lon")
            selff.timezone = data.get("timezone")
            selff.ip = data.get("query")

        def __str__(selff):
            return str(selff.__dict__)

    async def check(self, proxy):
        ip_request = await self.client.get('https://ifconfig.me/ip')
        self.ip = ip_request.text
        r = await self.client.get(f"http://ip-api.com/json/{self.ip}")
        data = r.json()
        self.country = data.get("country")
        self.country_code = data.get("countryCode")
        self.region = data.get("regionName")
        self.city = data.get("city")
        self.zip = data.get("zip")
        self.latitude = data.get("lat")
        self.longitude = data.get("lon")
        self.timezone = data.get("timezone")


class Generator:
    async def initialize(self, proxy, mode=None, output_file="output.txt", email=True, humanize=True):
        # Initializing the Thread
        self.last_x, self.last_y = 0, 0
        self.proxy, self.mode, self.output_file, self.email_verification, self.humanize = proxy, mode, output_file, email, humanize
        # SettingUp Logger
        logging.basicConfig(
            format='\033[34m[%(levelname)s] - \033[94mLine %(lineno)s  - \033[36m%(funcName)s() - \033[96m%(message)s\033[0m')
        self.logger = logging.getLogger('logger')
        self.logger.setLevel(logging.DEBUG)
        # Initializing Faker, ComputerInfo, PersonInfo and ProxyInfo
        httpx_proxy = {
            "http://": f"http://{self.proxy}",
        } if self.proxy else None
        self.httpx = httpx.AsyncClient(proxies=httpx_proxy, verify=False)

        self.faker, self.prox = Faker(self.httpx), Proxy(self.httpx)

        await self.prox.check(self.proxy)
        if not self.prox.country:
            self.logger.error("Couldnt load the Proxy info")
            return

        await self.faker.computer()
        await self.faker.person()
        await self.faker.locale(self.prox.country_code)

        # Initializing LocaleInfo and Browser
        await self.initialize_browser()
        self.logger.info("Spawned Browser successfully")

        if mode == 1:
            await self.generate_unclaimed()
        elif mode == 2:
            await self.generate_token()
        elif mode == 3:
            await self.check_captcha()
        return

    async def initialize_browser(self):
        # Browser Proxy Formatter
        if self.proxy:
            self.split_proxy = self.prox.Split(self.proxy)
            if len(self.split_proxy) == 4:
                self.browser_proxy = {
                    "server": f"http://{self.split_proxy[0]}:" + self.split_proxy[1], "username": self.split_proxy[2], "password": self.split_proxy[3]}
            else:
                self.browser_proxy = {
                    "server": f"http://{self.split_proxy[0]}:" + self.split_proxy[1]}
        else:
            self.browser_proxy = {}
        # Starting Playwright
        self.playwright = await async_playwright().start()
        # Launching Firefox with Human Emulation
        main_browser = await self.playwright.firefox.launch(devtools=True, headless=False, proxy=self.browser_proxy if self.proxy else None)
        # Context for more options
        browser = await main_browser.new_context(
            locale="en-US",  # self.faker.locale
            geolocation={'longitude': self.prox.longitude,
                         'latitude': self.prox.latitude, "accuracy": 0.7},
            timezone_id=self.prox.timezone,
            permissions=['geolocation'],
            screen={"width": self.faker.avail_width,
                    "height": self.faker.avail_height},
            user_agent=self.faker.useragent,
            viewport={"width": self.faker.width,
                      "height": self.faker.height},
            proxy=self.browser_proxy if self.proxy else None,
            http_credentials={
                "username": self.split_proxy[2], "password": self.split_proxy[3]} if self.proxy else None
        )
        # Grant Permissions to Discord to use Geolocation
        await browser.grant_permissions(["geolocation"], origin="https://discord.com")
        # Create new Page and do something idk why i did that lol
        page = await browser.new_page()
        await page.emulate_media(color_scheme="dark", media="screen", reduced_motion="reduce")
        # Stealthen the page with custom Stealth Config
        config = playwright_stealth.StealthConfig()
        config.navigator_languages, config.permissions, config.navigator_platform, config.navigator_vendor, config.outerdimensions = False, False, False, False, False
        config.vendor, config.renderer, config.nav_user_agent, config.nav_platform = self.faker.vendor, self.faker.renderer, self.faker.useragent, "Win32"
        config.languages = ('en-US', 'en', self.faker.locale,
                            self.faker.language_code)
        await playwright_stealth.stealth_async(page, config)
        self.browser, self.page = browser, page

    async def close(self):
        try:
            await self.page.close()
        except:
            pass
        try:
            await self.browser.close()
        except:
            pass
        try:
            await self.playwright.stop()
        except:
            pass
        try:
            await self.httpx.aclose()
        except:
            pass

    async def type_humanly(self, locator, text):
        # Get the Element by Selector and click it
        element = self.page.locator(locator)
        await self.click_humanly(element, "")
        # Wait some random time and
        await self.page.wait_for_timeout(random.randint(2, 4)*100)
        await element.type(text, delay=random.randint(150, 250))
        await self.page.wait_for_timeout(random.randint(4, 8)*100)

    async def click_xy_humanly(self, x, y):
        # Move mouse humanly to the Coordinates and wait some random time
        await self.humanize_mouse_movement(x, y)
        await self.page.wait_for_timeout(random.randint(4, 8)*100)
        # Click the Coordinates and wait some random time
        await self.page.mouse.click(x, y, delay=random.randint(40, 100))
        await self.page.wait_for_timeout(random.randint(4, 8)*100)

    async def click_humanly(self, element="", locator="", timeout=30000):
        # Getting Element by Selector if Element isnt passed
        if not element:
            element = self.page.locator(locator)
        # Get a random coordinate inside the element
        coordinates = await element.bounding_box(timeout=timeout)
        x, y = coordinates["x"] + \
            random.randint(10, 20), coordinates["y"] + random.randint(10, 20)
        # Click the Coordinates and return them
        await self.click_xy_humanly(x, y)
        return x, y

    async def humanize_mouse_movement(self, x, y):
        xp, yp = [x, self.last_x], [y, self.last_y]

        def midpoints(xp, yp):
            new_x, new_y = xp[:], yp[:]
            for x, y in zip(xp, yp):
                last_x, last_y = xp[-1], yp[-1]
                calc_x, calc_y = ((x + last_x)/2, (y + last_y)/2)
                if calc_x not in new_x and calc_y not in new_y:
                    new_x.append(calc_x)
                    new_y.append(calc_y)
            return new_x, new_y

        for i in range(5):
            xp, yp = midpoints(xp, yp)

        # Every item but the first and last one
        xp, yp = sorted(xp), sorted(yp)
        nxp, nyp = xp[1:-1], yp[1:-1]
        # Randomize points
        sxp, syp = [], []
        for x, y in zip(nxp, nyp):
            sxp.append(random.uniform(x-0.4, x+0.4))
            syp.append(random.uniform(y-0.4, y+0.4))
        # Combine First, Last Point and new random points
        xp = [*sxp, xp[-1]]
        yp = [*syp, yp[-1]]
        # Move Mouse to new random locations
        for x, y in zip(xp, yp):
            await self.page.mouse.move(x, y)
            await self.page.wait_for_timeout(random.randint(20, 60))
        # Set LastX and LastY cause Playwright doesnt have mouse.current_location
        self.last_x, self.last_y = xp[-1], yp[-1]

    def smooth_out_mouse(self):
        # Get the Captcha X- and Y-Coordinates
        self.x_coordinates, self.y_coordinates = [
            _[0] for _ in self.captcha_points], [_[1] for _ in self.captcha_points]
        # Devide x and y coordinates into two arrays
        x, y = np.array(self.x_coordinates), np.array(self.y_coordinates)
        # i dont even know, copy pasted from this so https://stackoverflow.com/a/47361677/16523207
        x_new = np.linspace(x.min(), x.max(), 200)
        f = scipy.interpolate.interp1d(x, y, kind='quadratic')
        y_new = f(x_new)
        # Converting NpArrays to lists
        y_new = y_new.tolist()
        x_new = x_new.tolist()
        # Randomize Points to emulate human mouse wobblyness
        x_new = [random.uniform(
            x-random.randint(5, 20)/10, x+random.randint(5, 20)/10) for x in x_new]
        y_new = [random.uniform(
            y-random.randint(5, 20)/10, y+random.randint(5, 20)/10) for y in y_new]

        return x_new, y_new

    async def log_captcha(self):
        async def check_json(route, request):
            await route.continue_()
            try:
                response = await request.response()
                await response.finished()
                json = await response.json()
                if json.get("generated_pass_UUID"):
                    self.captcha_token = json.get("generated_pass_UUID")
            except Exception:
                pass

        await self.page.route("https://hcaptcha.com/checkcaptcha/**", check_json)

    async def captcha_solver(self):
        # Setup CaptchaToken Logger
        self.captcha_token = None
        await self.log_captcha()
        # Second Frame is Captcha Frame (With Captcha Images)
        # captcha_frame = self.page.frames[1]
        try:
            captcha_frames = self.page.frame_locator(
                "//iframe[contains(@title,'content')]")
            captcha_frame = captcha_frames.first
        except Exception as e:
            self.logger.debug(f"Captcha Exception: {str(e)}")
            self.logger.info("Captcha Passed successfully!")
            return True
        # Getting Question and Label of the Captcha
        try:
            question_locator = captcha_frame.locator(
                "//h2[@class='prompt-text']")
            question = await question_locator.text_content()
        except Exception as e:
            self.logger.error("Captcha Question didnt load")
            await self.close()
            return False
        self.label = re.split(
            r"containing a", question)[-1][1:].strip() if "containing" in question else question
        self.label = self.label.replace(".", "")
        self.logger.info(f"Got Captcha QuestionLabel: {self.label}")
        # Initializing ArmorCaptcha
        self.challenger = ArmorCaptcha(dir_workspace=DIR_CHALLENGE, dir_model=DIR_MODEL, lang='en', debug=True,
                                       path_objects_yaml=PATH_OBJECTS_YAML, onnx_prefix="yolov5s6")
        # Getting Lavel and Model from AI
        self.challenger.label = self.label
        self.model = self.challenger.switch_solution()  # DIR_MODEL, None
        # Solving Captcha with AI
        self.results, timee = [], time.perf_counter()
        # Getting first 9 of the logged Images (First nine are the CaptchaImages)
        for image_url in self.images[:9]:
            # Getting Content of Image
            data = httpx.get(image_url).content
            # Getting Result from AI and appending it to list
            try:
                result = self.model.solution(
                    img_stream=data, label=self.challenger.label_alias[self.label])
            except KeyError:
                self.logger.error(f"AI doesnt support {self.label} yet!")
                self.images = []
                await self.click_humanly(self.checkbox, "")
                await self.page.wait_for_timeout(2000)
                await self.click_humanly(self.checkbox, "")
                await self.captcha_solver()
                return
            self.results.append(result)
        await self.page.wait_for_timeout(1000)
        # If Results are Invalid Reload Captcha and Recurse
        if not any(self.results):
            self.logger.warning("AI Results were incorrect, redoing Captcha")
            self.images = []
            await self.click_humanly(self.checkbox, "")
            await self.page.wait_for_timeout(2000)
            await self.click_humanly(self.checkbox, "")
            await self.captcha_solver()
        self.logger.info(
            f"AI-Results (solved in {round(time.perf_counter() - timee, 5)}s): {self.results}")
        # More Realistic Human Behaviour
        await self.page.wait_for_timeout(6000)
        # Get All of the Images
        image_locator = captcha_frame.locator("//div[@class='task-image']")
        self.image_elements = await image_locator.element_handles()
        # Define Captcha Points and Used Captha points
        self.captcha_points, self.used_captcha_points = [], []
        # Getting Random Coordinate from Image if Image is Correct
        for result, element in zip(self.results, self.image_elements):
            if result:
                # Getting X,Y, Width and Height of Captcha Image if its True/Valid
                boundings = await element.bounding_box()
                x, y, width, height = boundings.values()
                # Clicking on random Location in the Picture for better MotionData
                while True:
                    random_x, random_y = random.randint(int(x), int(
                        x + width)), random.randint(int(y), int(y + height))
                    if random_x not in [_[0] for _ in self.captcha_points]:
                        self.captcha_points.append([random_x, random_y])
                        break

        self.logger.debug(self.captcha_points)
        # Get Coodinates of Smooth out mouse line
        self.x_new, self.y_new = self.smooth_out_mouse()
        # Method to insert the Original Captcha Points into the Curve Points
        self.zipped_rounded_points = [list(a) for a in zip(
            [int(x) for x in self.x_new], [int(y) for y in self.y_new])]
        for point in self.captcha_points:
            # Check if Point is not in the Curve Points
            if point not in self.zipped_rounded_points:
                best_index, best_difference = 0, 1000
                for i, difference_point in enumerate(self.zipped_rounded_points):
                    # Check Difference between Point and DifferencePoint
                    x_difference = point[0] - difference_point[0]
                    y_difference = point[1] - difference_point[1]
                    # Make Negative Number Positive with the Abs() Function
                    difference = abs(x_difference) + abs(y_difference)
                    # Check if DifferencePoint is newest to given Point
                    if difference < best_difference:
                        best_index, best_difference = i, difference
                # Insert the Point at the best calculated Point
                self.x_new.insert(best_index+1, point[0])
                self.y_new.insert(best_index+1, point[1])

        for x, y in zip(self.x_new, self.y_new):
            x, y = int(x), int(y)
            # Check if coordinate is in the captcha_point (If yes, click it)
            # Also Check if the captcha was already clicked
            if any(x == int(_) for _ in self.x_coordinates) and x not in self.used_captcha_points:
                await self.page.mouse.move(x, y)
                await self.page.wait_for_timeout(random.randint(100, 300))
                await self.page.mouse.click(x, y, delay=random.randint(40, 100))
                # Append Coordinat to Used Captcha Points
                self.used_captcha_points.append(x)
                await self.page.wait_for_timeout(random.randint(5, 20))
            else:
                await self.page.mouse.move(x, y)
                await self.page.wait_for_timeout(random.randint(5, 20))

        await self.page.wait_for_timeout(600)
        # Clicking Submit Button
        submit_button = captcha_frame.locator(
            "//div[@class='button-submit button']").first
        await self.click_humanly(submit_button, "")
        # Checking if Captcha was Bypassed
        for _ in range(100):
            if self.captcha_token:
                censored_token = f"{self.captcha_token.split('.')[0]}.{self.captcha_token.split('.')[1][:10]}*****"
                self.logger.info(
                    f"Bypassed Captcha Successfully: {censored_token}")
                return True
            else:
                await self.page.wait_for_timeout(100)

        # If Captcha Token wasnt fetched redo Captcha
        self.logger.warning(
            "Captcha Solution was Incorrect or another is needed")
        self.images = []
        await self.click_humanly(self.checkbox, "")
        await self.page.wait_for_timeout(2000)
        await self.click_humanly(self.checkbox, "")
        await self.captcha_solver()

    # Main Functions
    async def check_captcha(self):
        try:
            await self.page.goto("https://democaptcha.com/demo-form-eng/hcaptcha.html")
        except:
            self.logger.error("Site didn´t load")
            return False
        # Collecting all Images requested from hCaptcha (Captcha Images)
        self.images = []

        async def image_append(route, request):
            if request.resource_type == "image" and "hcaptcha" in request.url:
                self.images.append(request.url)
            await route.continue_()
        await self.page.route("https://imgs.hcaptcha.com/*", image_append)
        # Clicking Captcha Checkbox
        try:
            self.checkbox = self.page.frame_locator(
                '[title *= "hCaptcha security challenge"]').locator('[id="checkbox"]')
            await self.checkbox.scroll_into_view_if_needed(timeout=5000)
        except Exception as e:
            self.logger.error("Captcha didn´t load")
            return False
        await self.click_humanly(self.checkbox, "")
        await self.page.wait_for_timeout(2000)
        captcha = await self.captcha_solver()

        await self.close()

    async def generate_unclaimed(self):
        # Going on Discord Register Site
        try:
            await self.page.goto("https://discord.com/")
        except:
            self.logger.error("Site didn´t load")
            await self.close()
            return False
        # Setting Up TokenLog
        await self.log_token()
        self.token = None
        # Click Open InBrowser Button
        await self.click_humanly("", '[class *= "gtm-click-class-open-button"]')
        # Typing Username
        await self.type_humanly('[class *= "username"]', self.faker.username)
        # Clicking Tos and Submit Button
        try:
            await self.click_humanly("", "[class *='termsCheckbox']", timeout=5000)
        except Exception as e:
            self.logger.debug("No TOS Checkbox was detected")
            pass
        await self.click_humanly("", '[class *= "gtm-click-class-register-button"]')
        # Collecting all Images requested from hCaptcha (Captcha Images)
        self.images = []

        async def image_append(route, request):
            if request.resource_type == "image" and "hcaptcha" in request.url:
                self.images.append(request.url)
            await route.continue_()
        await self.page.route("https://imgs.hcaptcha.com/*", image_append)
        # Clicking Captcha Checkbox
        try:
            self.checkbox = self.page.frame_locator(
                '[title *= "hCaptcha security challenge"]').locator('[id="checkbox"]')
            await self.checkbox.scroll_into_view_if_needed(timeout=5000)
        except:
            self.logger.error("Captcha didn´t load")
            await self.close()
            return False
        await self.click_humanly(self.checkbox, "")
        await self.page.wait_for_timeout(2000)
        captcha = await self.captcha_solver()

        while not self.token:
            await self.page.wait_for_timeout(2000)

        self.logger.info(f"Generated Token: {self.token}")
        await asyncio.sleep(2)

        is_locked = await self.is_locked()
        if is_locked:
            self.logger.error(f"Token {self.token} is locked!")
            await self.close()
            return
        else:
            self.logger.info(
                f"Token: {self.token} is unlocked! Flags: {self.flags}")

        await self.page.wait_for_timeout(3000)
        try:
            await self.type_humanly('[id="react-select-2-input"]', self.faker.birth_day)
            await self.page.keyboard.press("Enter")
            await self.type_humanly('[id="react-select-3-input"]', self.faker.birth_month)
            await self.page.keyboard.press("Enter")
            await self.type_humanly('[id="react-select-4-input"]', self.faker.birth_year)
            await self.page.keyboard.press("Enter")
            await self.page.wait_for_timeout(1000)
            await self.page.keyboard.press("Enter")
        except:
            pass

        if self.email_verification:
            self.logger.info("Claiming Account...")
            claim = await self.claim_account()
            if claim:
                self.logger.info("Verifying email...")
                email_v = await self.confirm_email()

        if self.humanize:
            await self.humanize_token()

        with open(self.output_file, 'a') as file:
            file.write(
                f"{self.token}:{self.inbox.address}:{self.faker.password}\n")

        await self.close()

    async def generate_token(self):
        # Going on Discord Register Site
        try:
            await self.page.goto("https://discord.com/register")
        except:
            self.logger.error("Site didn´t load")
            await self.close()
            return False
        # Setting Up TokenLog
        await self.log_token()
        self.token = None
        # Typing Email, Username, Password
        self.inbox = TempMail.generateInbox()
        await self.type_humanly('[name="email"]', self.inbox.address if self.email_verification else str(self.person.username+f"{random.randint(10, 99)}@gmail.com"))
        await self.type_humanly('[name="username"]', self.faker.username)
        await self.type_humanly('[name="password"]', self.faker.password)
        # Typing BirthDay, BirthMonth, BirthYear
        await self.type_humanly('[id="react-select-2-input"]', self.faker.birth_day)
        await self.page.keyboard.press("Enter")
        await self.type_humanly('[id="react-select-3-input"]', self.faker.birth_month)
        await self.page.keyboard.press("Enter")
        await self.type_humanly('[id="react-select-4-input"]', self.faker.birth_year)
        # Clicking Tos and Submit Button
        try:
            await self.click_humanly("", "[type='checkbox']")
        except Exception as e:
            self.logger.debug("No TOS Checkbox was detected")
            pass
        await self.click_humanly("", '[type="submit"]')
        # Collecting all Images requested from hCaptcha (Captcha Images)
        self.images = []

        async def image_append(route, request):
            if request.resource_type == "image" and "hcaptcha" in request.url:
                self.images.append(request.url)
            await route.continue_()
        await self.page.route("https://imgs.hcaptcha.com/*", image_append)
        # Clicking Captcha Checkbox
        try:
            self.checkbox = self.page.frame_locator(
                '[title *= "hCaptcha security challenge"]').locator('[id="checkbox"]')
            await self.checkbox.scroll_into_view_if_needed(timeout=5000)
        except:
            self.logger.error("Captcha didn´t load")
            await self.close()
            return False
        await self.click_humanly(self.checkbox, "")
        await self.page.wait_for_timeout(2000)
        captcha = await self.captcha_solver()

        while not self.token:
            await self.page.wait_for_timeout(2000)

        self.logger.info(f"Generated Token: {self.token}")
        await self.page.wait_for_timeout(2000)

        is_locked = await self.is_locked()
        if is_locked:
            self.logger.error(f"Token {self.token} is locked!")
            await self.close()
            return
        else:
            self.logger.info(
                f"Token: {self.token} is unlocked! Flags: {self.flags}")

        if self.email_verification:
            self.logger.info("Verifying email...")
            email_v = await self.confirm_email()

        if self.humanize:
            await self.humanize_token()

        with open(self.output_file, 'a') as file:
            file.write(
                f"{self.token}:{self.inbox.address}:{self.faker.password}\n")

        self.logger.info("Successfully Generated Account! Closing Browser...")

        await self.close()

    # Discord Helper Functions
    async def log_token(self):
        async def check_json(route, request):
            await route.continue_()
            try:
                response = await request.response()
                await response.finished()
                json = await response.json()
                if json.get("token"):
                    self.token = json.get("token")
            except Exception:
                pass

        await self.page.route("https://discord.com/api/**", check_json)

    async def is_locked(self):
        token_check = httpx.get('https://discord.com/api/v9/users/@me/library',
                                headers={"Authorization": self.token}).status_code == 200
        if token_check:
            r = httpx.get(
                'https://discord.com/api/v9/users/@me', headers={"Authorization": self.token})
            response = r.json()
            self.id = response.get("id")
            self.email = response.get("email")
            self.username = response.get("username")
            self.discriminator = response.get("discriminator")
            self.tag = f"{self.username}#{self.discriminator}"
            self.flags = response.get("public_flags")

        return not token_check

    async def humanize_token(self):
        self.logger.info("Humanizing Token...")
        # Initializing Discum if not already initialized
        if 'bot' not in dir(self):
            self.bot = discum.Client(
                token=self.token, log=False, user_agent=self.faker.useragent, proxy=self.proxy if self.proxy else None)
        else:
            self.bot.switchAccount(self.token)

        # Setting Random Avatar
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            pics = await self.httpx.get(
                "https://api.github.com/repos/itschasa/Discord-Scraped/git/trees/cbd70ab66ea1099d31d333ab75e3682fd2a80cff")
            random_pic = random.choice(pics.json().get("tree")).get("path")
            pic_url = f"https://raw.githubusercontent.com/itschasa/Discord-Scraped/main/avatars/{random_pic}"
            pic = await self.httpx.get(pic_url)
            tmp.write(pic.content)
            tmp.seek(0)

            self.bot.setAvatar(tmp.name)

        # Setting AboutME
        quote = await self.httpx.get("https://free-quotes-api.herokuapp.com")
        quote = quote.json().get("quote")
        self.bot.setAboutMe(quote)

        # Setting Hypesquad
        hypesquad = random.choice(
            ["bravery", "brilliance", "balance"])
        self.bot.setHypesquad(hypesquad)

        self.logger.info(f"Set Hypesquad, Bio and ProfilePic!")

    async def claim_account(self):
        self.bot = discum.Client(
            token=self.token, log=False, user_agent=self.faker.useragent, proxy=self.proxy if self.proxy else None)
        self.inbox = TempMail.generateInbox()

        self.bot._Client__user_password = self.faker.password
        response = self.bot.setEmail(self.inbox.address)
        if not response.status_code == 200:
            try:
                self.logger.error(
                    f"Couldnt set email! Response: {response.json()}")
            except:
                self.logger.error(f"Couldnt set email!")
            return False
        else:
            self.logger.info("Successfully set email! Verifying...")
            try:
                if response.json().get("token"):
                    self.token = response.json().get("token")
            except:
                pass
            return True

    async def confirm_email(self):
        self.logger.info("Confirming Email...")
        # Getting the email confirmation link from the email
        self.scrape_emails = True
        while self.scrape_emails:
            emails = TempMail.getEmails(self.inbox)
            for mail in emails:
                if "mail.discord.com" in str(mail.sender):
                    for word in mail.body.split():
                        if "https://click.discord.com" in word:
                            self.email_link = word
                            self.scrape_emails = False
                            break

        # Confirming the email by link
        await self.page.goto(self.email_link)
        # Collecting all Images requested from hCaptcha (Captcha Images)
        self.images = []

        async def image_append(route, request):
            if request.resource_type == "image" and "hcaptcha" in request.url:
                self.images.append(request.url)
            await route.continue_()
        await self.page.route("https://imgs.hcaptcha.com/*", image_append)
        # Clicking Captcha Checkbox
        try:
            self.checkbox = self.page.frame_locator(
                '[title *= "hCaptcha security challenge"]').locator('[id="checkbox"]')
            await self.checkbox.scroll_into_view_if_needed(timeout=5000)
        except:
            self.logger.info("No Email Captcha was detected!")
            return True
        await self.click_humanly(self.checkbox, "")
        await self.page.wait_for_timeout(2000)
        captcha = await self.captcha_solver()
        return True

    # Testing (Maybe used later?)
    async def login_token(self):
        # Going on Discord Register Site
        try:
            await self.page.goto("https://discord.com/register")
        except:
            self.logger.error("Site didn´t load")
            return False
        await self.page.evaluate(str('setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"' + self.token + '"`}, 2500); setTimeout(() => {location.reload();}, 2500);'))
        await self.page.wait_for_timeout(5000)
        # self.logger.info("Claiming Account...")
        # claim = await self.claim_account()
        # if not claim:
        #     return False
        # self.logger.info("Verifying email...")
        # email_v = await self.confirm_email()
        # self.logger.info(self.token)
        await self.humanize_token()
        await self.close()


async def main():
    print(""" _____     __     ______     __         ______     ______     __  __    
/\  __-.  /\ \   /\  ___\   /\ \       /\  __ \   /\  ___\   /\ \/ /    
\ \ \/\ \ \ \ \  \ \___  \  \ \ \____  \ \ \/\ \  \ \ \____  \ \  _"-.  
 \ \____-  \ \_\  \/\_____\  \ \_____\  \ \_____\  \ \_____\  \ \_\ \_\ 
  \/____/   \/_/   \/_____/   \/_____/   \/_____/   \/_____/   \/_/\/_/    | Made by Vinyzu  
                                                                           | https://github.com/Vinyzu/DiscordGenerator""")
    mode = input("[Select] - [Generation Mode]\n" + "<1> Generate Unclaimed Token\n" +
                 "<2> Generate Token\n" + "<3> Test Captcha\n" + "</> ")
    if mode not in ("1", "2", "3"):
        raise ValueError("Invalid Mode provided")
    else:
        mode = int(mode)

    if mode in (1, 2):
        email = input("[Select] - [Email Verification]\n" + "<1> Verification Enabled\n" +
                      "<2> No Verification\n" + "</> ")
        if email not in ("1", "2"):
            raise ValueError("Invalid Mode provided")
        else:
            email = True if email == "1" else False
    else:
        email = False

    if mode in (1, 2):
        humanize = input("[Select] - [Token Humanization]\n" + "<1> Humanization Enabled\n" +
                         "<2> No Humanization\n" + "</> ")
        if humanize not in ("1", "2"):
            raise ValueError("Invalid Mode provided")
        else:
            humanize = True if humanize == "1" else False
    else:
        humanize = False

    threads = input("[Input] - [Threads Amount]\n" + "</> ")
    try:
        threads = int(threads)
    except:
        raise ValueError("Invalid ThreadAmount provided")

    proxy_file = input("[Drag&Drop] - [Proxy File]\n" +
                       "<?> Or Leave empty for Proxyless Mode\n" + "</> ")
    if proxy_file:
        if not os.path.isfile(proxy_file):
            raise ValueError("Provided ProxyPath isnt a file!")
        proxies = open(proxy_file, 'r').readlines()
    else:
        proxies = None

    output_file = input("[Drag&Drop] - [Output File]\n" +
                        "<?> Or Leave empty to use output.txt\n" + "</> ")
    if output_file:
        if not os.path.isfile(output_file):
            raise ValueError("Provided OutputPath isnt a file!")
    else:
        output_file = "output.txt"

    os.system('cls' if os.name == 'nt' else 'clear')

    while True:
        threadz = []
        for _ in range(threads):
            proxy = random.choice(proxies) if proxies else None
            threadz.append(Generator().initialize(
                proxy, mode, output_file, email, humanize))

        await asyncio.gather(*threadz)
        await asyncio.sleep(2)


if __name__ == '__main__':
    asyncio.run(main())
