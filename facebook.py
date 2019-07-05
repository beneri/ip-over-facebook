#!/usr/bin/env python3

import requests
import time
import base64
import pickle
import re
import hashlib
import logging


class Facebook:
    headers = {
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
    fb_dtsg = ''
    username = ''
    # Cache will store cookies, username and fb_dtsg in a file
    cache_file = ''
    # Must be multiple of 4 to be streamable.
    # Other than that, the bigger the better.
    MAXSIZE = 4*259434
    # a unique string the client will search for
    initStr = "initUnique"

    def __init__(self, cf):
        self.s = requests.Session()
        self.cache_file = cf

    def saveCacheToFile(self):
        cache = {'fb_dtsg': self.fb_dtsg,
                 'username': self.username,
                 'cookies': requests.utils.dict_from_cookiejar(self.s.cookies)}
        with open(self.cache_file, 'w') as f:
            pickle.dump(cache, f)

    def loadCacheFromFile(self):
        with open(self.cache_file) as f:
            cache = pickle.load(f)
            self.fb_dtsg = cache['fb_dtsg']
            self.username = cache['username']
            logging.debug(f"Got {self.fb_dtsg} {self.username}")
            self.s.cookies = requests\
                .utils.cookiejar_from_dict(cache['cookies'])
            return cache

    def login(self, u, p):
        if self.cache_file:
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

            except Exception:
                logging.error("Problem reading from cache file")

            if not cache_data:
                logging.warning("Could not load data from cache")

                r = self.s.get("https://www.facebook.com/")

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

                if "Two-Factor Authentication Required" in response.text:
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

        if self.cache_file:
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

    def changeAbout(self, m):
        params = {
            'dpr': '1.5'
        }

        data = {
            'fb_dtsg': self.fb_dtsg,
            'textarea': m,
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

        encodedData = base64.b64encode(data)

        chunks = [encodedData[i:i+self.MAXSIZE]
                  for i in range(len(encodedData), self.MAXSIZE)]
        logging.debug(f"Splitting data into {len(chunks)} chunks,"
                      f"{self.MAXSIZE} bytes")

        logging.debug("Sending init")
        self.changeAbout(f"{self.initStr} {len(chunks)}")

        while(1):
            time.sleep(0.2)
            logging.debug("Waiting for ack")
            about = self.getAbout()
            if about == "ack":
                break

        for chunk in chunks:
            time.sleep(0.2)

            logging.debug(f"Uploading {len(chunk)} bytes")
            hash_object = hashlib.sha256(chunk)
            hex_dig = hash_object.hexdigest()
            logging.debug(hex_dig)

            self.changeAbout(chunk)
            while(1):
                time.sleep(0.2)
                logging.debug("Waiting for ack")
                about = self.getAbout()
                if about == "ack":
                    break

        logging.info("Done, sending done")
        self.changeAbout("done")
        return len(data)

    def recv(self):
        logging.debug("Acting as a client, connecting to facebook")
        recvData = ""

        while(1):
            time.sleep(0.2)
            logging.debug("Waiting for init")
            about = self.getAbout()
            if self.initStr in about:
                (aboutInit, aboutChunks) = about.split()
                logging.debug("Got int, sending ack. {aboutChunks} chunks"
                              "in total")
                logging.debug(f"Got int, sending ack. {aboutChunks}"
                              "chunks in total")
                self.changeAbout("ack")
                break

        while(1):
            time.sleep(0.2)
            logging.debug("Waiting for data")
            about = self.getAbout()
            if about == "done":
                logging.debug("All done")
                break
            if about and about != "ack":
                logging.debug("Got {len(about)} bytes")

                hash_object = hashlib.sha256(about)
                hex_dig = hash_object.hexdigest()
                print(hex_dig)

                recvData += base64.b64decode(about)
                # f.write( base64.b64decode(about) )
                # f.flush()
                self.changeAbout("ack")

        return recvData
