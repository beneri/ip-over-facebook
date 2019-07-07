import re
import pickle
import logging
from os.path import join
from os import makedirs
import requests
from appdirs import user_data_dir

appname = "ip-over-facebook"


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
        # Cache will store cookies, username and fb_dtsg in a file
        self.cache_file = ''

        self.s = requests.Session()
        self.cache_file_path = cache_file_path
        makedirs(user_data_dir(appname), exist_ok=True)

    @property
    def logged_in(self):
        response = self.s.post('https://www.facebook.com/settings',
                               headers=self.headers)
        return "You must log in to continue" not in response.text

    @property
    def fb_dtsg(self):
        response = self.s.get(f'https://facebook.com/{self.username}/about',
                              headers=self.headers)

        m = re.search('fb_dtsg" value="(.*?)"', response.text)

        if m:
            return m.group(1)
        else:
            return None

    @property
    def about(self) -> str:
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

    @about.setter
    def about(self, message: str):
        params = {
            'dpr': '1.5'
        }

        data = {
            'fb_dtsg': self.fb_dtsg,
            'textarea': message,
            'privacy[8787635733]': '286958161406148'  # Private
            # ('privacy[8787635733]', '300645083384735'), # Public
        }

        self.s.post('https://www.facebook.com/profile/async/edit'
                    '/infotab/save/about_me/',
                    headers=self.headers, params=params, data=data)

    @property
    def username(self):
        response = self.s.get('https://facebook.com/', headers=self.headers)
        m = re.search('_2s25 _606w" href="https://www.facebook.com/(.*?)"',
                      response.text)

        if m:
            return m.group(1)
        else:
            return None

    def save_cache_to_file(self):
        cache = {'fb_dtsg': self.fb_dtsg,
                 'username': self.username,
                 'cookies': requests.utils.dict_from_cookiejar(self.s.cookies)}
        with open(self.cache_file_path, 'wb') as f:
            pickle.dump(cache, f)

    def load_cache_from_file(self):
        with open(self.cache_file_path, 'rb') as f:
            cache = pickle.load(f)
            logging.debug(f"Got {self.fb_dtsg} {self.username}")
            self.s.cookies = requests\
                .utils.cookiejar_from_dict(cache['cookies'])
            return cache

    def login(self, username, password):
        if self.cache_file_path:
            logging.debug("Trying to load data from cache")
            cache_data = None
            try:
                cache_data = self.load_cache_from_file()
                logging.debug("Data loaded from cache")

                if not self.logged_in:
                    logging.warning("Cache invalid, "
                                    "continuing with normal log in")
                    cache_data = None
                    logging.debug("Resetting requests session")
                    self.s = requests.Session()
                else:
                    return True

            except FileNotFoundError:
                logging.warning("Cache file not found")

            if not cache_data:
                logging.warning("Could not load data from cache")

                self.s.get("https://www.facebook.com/")

                params = {
                    'login_attempt': '1',
                    'lwv': '111'
                }

                data = {
                    'email': username,
                    'pass': password
                }

                logging.debug("Sending credentials")
                response = self.s.post('https://www.facebook.com/login.php',
                                       headers=self.headers,
                                       params=params,
                                       data=data)

                # Previous version was language dependant
                if "approvals_code" in response.text:
                    logging.info("Two-factor auth required,"
                                 " using 6-digit code")
                    self.handle_two_factor_code()

                logging.debug("Fetching username")

                logging.info(f"Username: {self.username}")
                if not self.username:
                    logging.error("Error: login failed")
                    return None

                logging.debug("Try to write data to cache")
                try:
                    self.save_cache_to_file()
                    logging.debug("Data saved in cache")
                except Exception:
                    logging.warning("Could not store data in cache")
                    return True

                logging.debug("Fetching fb_dtsg")
                logging.debug(f"fb_dtsg: {self.fb_dtsg}")
                logging.info("Login done")
                return True

    def handle_two_factor_code(self):
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

    def handle_two_factor_fido(self):
        raise NotImplementedError

    def send(self, data=None):
        if data:
            logging.debug(f"Sending {len(data)} bytes")
            self.about = data
            return len(data)
        else:
            return 0

    def recv(self):
        logging.debug("Receiving data")
        return self.about
