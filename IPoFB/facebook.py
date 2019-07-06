#!/usr/bin/env python3.7
import requests
import time
import base64
import pickle
import re
import logging
from enum import IntEnum
from math import ceil
from os.path import join
from os import makedirs
from appdirs import user_data_dir

appname = "ip-over-facebook"


class StatusCodes(IntEnum):
    ACK = 0,
    DATA = 1,
    INIT = 2,
    DONE = 3


# Thanks SO
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def to_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_status_code(data) -> StatusCodes:
    if data:
        return StatusCodes(data.split()[0])


def wait_for_status(status: StatusCodes,
                    update_function,
                    callback_function=lambda x: True,
                    update_interval=0.2,
                    timeout=5):
    """
    Doesn't return until the update_function return the specified status.
    Before returning it calls the callback_function
    """
    start_time = time.time()
    current_time = start_time

    while current_time - start_time < timeout:
        logging.debug(f"Waiting for {status}")
        func_status = update_function()
        if func_status == status:
            return True

        time.sleep(update_interval)
        current_time = time.time()

    raise TimeoutError(f"{status} waiting timed out")


class Facebook:
    def __init__(self,
                 cache_file_path=f'{join(user_data_dir(appname), "cache")}'):
        self.headers = {
            'origin': 'https://www.facebook.com',
            'accept-encoding': 'gzip',
            'accept-language': 'en-US,en;q=1.0',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'referer': 'https://www.facebook.com/',
            'authority': 'www.facebook.com',
        }
        self.fb_dtsg = ''
        self.username = ''
        # Cache will store cookies, username and fb_dtsg in a file
        self.cache_file = ''
        # Must be multiple of 4 to be streamable.
        # Other than that, the bigger the better.
        self.MAXSIZE = 4*259434

        self.s = requests.Session()
        self.cache_file_path = cache_file_path
        makedirs(user_data_dir(appname), exist_ok=True)

    def saveCacheToFile(self):
        cache = {'fb_dtsg': self.fb_dtsg,
                 'username': self.username,
                 'cookies': requests.utils.dict_from_cookiejar(self.s.cookies)}
        with open(self.cache_file_path, 'wb') as f:
            pickle.dump(cache, f)

    def loadCacheFromFile(self):
        with open(self.cache_file_path, 'rb') as f:
            cache = pickle.load(f)
            self.fb_dtsg = cache['fb_dtsg']
            self.username = cache['username']
            logging.debug(f"Got {self.fb_dtsg} {self.username}")
            self.s.cookies = requests\
                .utils.cookiejar_from_dict(cache['cookies'])
            return cache

    def login(self, u, p):
        if self.cache_file_path:
            logging.debug("Trying to load data from cache")
            cache_data = None
            try:
                cache_data = self.loadCacheFromFile()
                logging.debug("Data loaded from cache")

                if not self.successfulLogin():
                    logging.warning("Cache invalid, "
                                    "continuing with normal log in")
                    cache_data = None
                    logging.debug("Resetting requests session")
                    self.s = requests.Session()
                else:
                    logging.debug("Test login was sucessful")
                    return True

            except FileNotFoundError:
                logging.warning("Problem reading from cache file")

            if not cache_data:
                logging.warning("Could not load data from cache")

                self.s.get("https://www.facebook.com/")

                params = {
                    'login_attempt': '1',
                    'lwv': '111'
                }

                data = {
                    'email': u,
                    'pass': p
                }

                logging.info("Sending credentials")
                response = self.s.post('https://www.facebook.com/login.php',
                                       headers=self.headers,
                                       params=params,
                                       data=data)

                # Previous versione was language dependant
                if "approvals_code" in response.text:
                    logging.info("Two-factor auth required,"
                                 " using 6-digit code")
                    self.handleTwoFactorCode()

                logging.debug("Fetching username")
                self.setUsername()

                logging.info(f"Username: {self.username}")
                if not self.username:
                    logging.error("Error: login failed")
                    return None

                logging.debug("Fetching fb_dtsg")
                self.setFbDtsg()
                logging.debug(f"fb_dtsg: {self.fb_dtsg}")
                logging.info("Login done")
                return True

        if self.cache_file_path:
            logging.debug("Try to write data to cache")
            try:
                self.saveCacheToFile()
                logging.debug("Data saved in cache")
            except Exception:
                logging.warning("Could not store data in cache")
                return True

    def successfulLogin(self):
        response = self.s.post('https://www.facebook.com/settings',
                               headers=self.headers)
        return not ("You must log in to continue" in response.text)

    def handleTwoFactorCode(self):
        # STEP 0: Force 6-digit code authentication
        params = {
            'next': '',
            'no_fido': 'true'
        }

        response = self.s.get('https://www.facebook.com/checkpoint/',
                              headers=self.headers, params=params)
        m = re.search('input.*?name="fb_dtsg".*?value="(.*?)"',
                      response.text)
        tmp_fb_dtsg = m.group(1)
        m = re.search('input.*?name="nh".*?value="(.*?)"',
                      response.text)
        tmp_nh = m.group(1)

        code = input("Enter two-factor code: ")

        # STEP 1: Send two factor code
        params = {
            'next': ''
        }

        data = {
            'fb_dtsg': tmp_fb_dtsg,
            'nh': tmp_nh,
            'approvals_code': code,
            'submit[Continue]': 'Continue'
        }

        logging.info("(1/5) Sending two factor code")
        response = self.s.post('https://www.facebook.com/checkpoint/',
                               headers=self.headers, params=params, data=data)

        # STEP 2: Save this as trusted a browser
        logging.info("(2/5) Saving browser")

        m = re.search('input.*?name="fb_dtsg".*?value="(.*?)"',
                      response.text)

        data = {
            'fb_dtsg': tmp_fb_dtsg,
            'nh': tmp_nh,
            'name_action_selected': 'save_device',
            'submit[Continue]': 'Continue'
        }

        response = self.s.post('https://www.facebook.com/checkpoint/',
                               headers=self.headers,
                               params=params, data=data)

        # STEP 3: Unlock temporary lock
        logging.info("(3/5) Unlock temporary lock")
        data = {
            'fb_dtsg': tmp_fb_dtsg,
            'nh': tmp_nh,
            'submit[Continue]': 'Continue'
        }

        response = self.s.post('https://www.facebook.com/checkpoint/',
                               headers=self.headers, params=params, data=data)

        # STEP 4: Login near ... "This was me"
        logging.info("(4/5) Strange login, yes this was me")
        data = {
            'fb_dtsg': tmp_fb_dtsg,
            'nh': tmp_nh,
            'submit[This was me]': 'This was me'
        }

        response = self.s.post('https://www.facebook.com/checkpoint/',
                               headers=self.headers, params=params, data=data)

        # STEP 5: Save browser again
        logging.info("(5/5) Saving browser, again")
        data = {
            'fb_dtsg': tmp_fb_dtsg,
            'nh': tmp_nh,
            'name_action_selected': 'save_device',
            'submit[Continue]': 'Continue'
        }

        response = self.s.post('https://www.facebook.com/checkpoint/',
                               headers=self.headers, params=params, data=data)

    def handleTwoFactorFido(self):
        raise NotImplementedError

    def changeAbout(self, message):
        params = {
            'dpr': '1.5'
        }

        data = {
            'fb_dtsg': self.fb_dtsg,
            'textarea': message,
            'privacy[8787635733]': '286958161406148'  # Private
            # ('privacy[8787635733]', '300645083384735'), # Public
        }

        response = self.s.post('https://www.facebook.com/profile/async/edit'
                               '/infotab/save/about_me/',
                               headers=self.headers, params=params, data=data)

    def getAbout(self):
        params = {
            'section': 'bio'
        }

        # Match for m.facebook.com since it is not rate limited.
        response = self.s.get(f'https://m.facebook.com/{self.username}/about',
                              headers=self.headers, params=params)

        m = re.search('_5cds _2lcw _5cdt">(.*?)</div', response.text)

        if m:
            return m.group(1)
        else:
            return None

    # Sets the fb_dtsg parameter. Updates the object and returns the value
    def setFbDtsg(self):
        response = self.s.get(f'https://facebook.com/{self.username}/about',
                              headers=self.headers)

        m = re.search('fb_dtsg" value="(.*?)"', response.text)

        if m:
            self.fb_dtsg = m.group(1)
            return m.group(1)
        else:
            return None

    # Sets the usernamer, updates the object and returns the value
    def setUsername(self):
        response = self.s.get('https://facebook.com/', headers=self.headers)

        m = re.search('_2s25 _606w" href="https://www.facebook.com/(.*?)"',
                      response.text)

        if m:
            self.username = m.group(1)
            return m.group(1)
        else:
            return None

    def send(self, data):
        logging.debug(f"Acting as a server, trying to send {len(data)} bytes")

        about = self.getAbout()

        # If is not null the channel is occupied
        if not about:
            encoded_data = base64.b64encode(data)

            number_of_chunks = ceil(len(encoded_data)/self.MAXSIZE)
            logging.debug("Splitting data into "
                          f"{number_of_chunks} chunks of max "
                          f"{self.MAXSIZE} bytes")
            # We need UTF-8 strings because otherwise facebook will garble the
            # data
            chunks = to_chunks(encoded_data.decode('UTF-8'), self.MAXSIZE)

            # Send INIT
            logging.debug(f"Sending init {StatusCodes.INIT} "
                          f"{number_of_chunks}")
            # If less than 2 digits facebook won't accept it
            self.changeAbout(f"{StatusCodes.INIT.value:02} {number_of_chunks}")
            wait_for_status(StatusCodes.ACK,
                            lambda: get_status_code(self.getAbout()))
            for chunk in chunks:
                logging.debug(f"Uploading {len(chunk)} bytes")

                self.changeAbout(f"{StatusCodes.DATA:02} {chunk}")
                wait_for_status(StatusCodes.ACK,
                                lambda: get_status_code(self.getAbout()))

            logging.info("Sending done")
            self.changeAbout(f"{StatusCodes.DONE.value:02}")
            return len(data)

    def recv(self):
        logging.debug("Acting as a client, connecting to facebook")
        recv_data = []
        number_of_chunks = 0

        logging.debug("Waiting for init")
        # 10 tries
        for _ in range(10):
            time.sleep(0.2)

            # status_code number_of_chunks
            about = self.getAbout()
            if about:
                message = about.split()
                status_code = int(message[0])

                # It means that the data connection has not been
                # initialized yet
                if number_of_chunks == 0:
                    # we initialize the number of chunks
                    if status_code == StatusCodes.INIT.value:
                        logging.debug("Receive initialized:"
                                      f" {message[1]} chunks in total")
                        self.changeAbout(f"{StatusCodes.ACK.value:02}")
                        number_of_chunks = int(message[1])
                    # the data transfer is done
                    elif status_code == StatusCodes.DONE.value:
                        logging.debug("Done downloading data")
                        # Cleanup
                        self.changeAbout("")
                        return b"".join(recv_data)
                # Something went wrong
                elif number_of_chunks < 0:
                    raise Exception("Chunks synchronization error")
                # we're transferring data
                elif number_of_chunks > 0:
                    # if we have more than 1 element in message something went
                    # wrong
                    if status_code == StatusCodes.DATA.value:
                        data = message[1].encode("UTF-8")
                        logging.debug(f"Downloading {len(data)} bytes")
                        recv_data.append(base64.b64decode(data))

                        self.changeAbout(f"{StatusCodes.ACK.value:02}")
                        number_of_chunks -= 1
