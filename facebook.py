import requests
import time
import base64
import pickle
import re
import hashlib



class Facebook:

    headers = {
        'origin': 'https://www.facebook.com',
        'accept-encoding': 'gzip',
        'accept-language': 'en-US,en;q=1.0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded',
        'accept': '*/*',
        'referer': 'https://www.facebook.com/',
        'authority': 'www.facebook.com',
    }
    fb_dtsg = ''
    username = ''
    # Cache will store cookies, username and fb_dtsg in a file
    cache_file = ''
    # Must be multiple of 4 to be streamable. Other than that, the bigger the better.
    MAXSIZE = 4*259434
    # a unique string the client will search for
    initStr = "initUnique"


    def __init__(self, cf):
        self.s = requests.Session()
        self.cache_file = cf

    def saveCacheToFile(self):
        cache = {'fb_dtsg': self.fb_dtsg, 'username': self.username, 'cookies': requests.utils.dict_from_cookiejar(self.s.cookies)}
        with open(self.cache_file, 'w') as f:
            pickle.dump(cache, f)

    def loadCacheFromFile(self):
        with open(self.cache_file) as f:
            cache = pickle.load(f)
            self.fb_dtsg = cache['fb_dtsg']
            self.username = cache['username']
            print "Got ", self.fb_dtsg, self.username
            self.s.cookies = requests.utils.cookiejar_from_dict( cache['cookies']  )
            return cache

    def login(self,u,p):
        if self.cache_file:
            print "Try loading data from cache"
            cache_data = None
            try:
                cache_data = self.loadCacheFromFile()
                print "Data loaded from cache"

                if( not self.successfulLogin() ):
                    print "Cache is not valid, continuing with normal log in"
                    cache_data = None
                    print "Resetting requests session"
                    self.s = requests.Session()
                else:
                    print "Test login was sucessful"

            except:
                print "Problem reading from cache file"

            if not cache_data:
                print "Could not load data from cache"

                r = self.s.get("https://www.facebook.com/")

                params = (
                    ('login_attempt', '1'),
                    ('lwv', '111'),
                )

                data = [
                ('email', u),
                ('pass', p),
                ]

                print "Sending credentials"
                response = self.s.post('https://www.facebook.com/login.php', headers=self.headers, params=params, data=data)

                print "Fetching username"
                self.setUsername()
                print "Username ", self.username
                if not self.username:
                    print "Error: login failed"
                    return None
                print "Fetching fb_dtsg"
                self.setFbDtsg()
                print "fb_dtsg ", self.fb_dtsg
                print "Login done"

        if self.cache_file:
            print "Try writing data to cache"
            try:
                self.saveCacheToFile()
                print "Data saved in cache"
            except:
                print "Could not store data in cache"

        return True

    def successfulLogin(self):
        response = self.s.post('https://www.facebook.com/settings', headers=self.headers)
        return not ("You must log in to continue" in response.content)


    def changeAbout(self, m):

        params = (
            ('dpr', '1.5'),
        )

        data = [
        ('fb_dtsg', self.fb_dtsg),
        ('textarea', m),
        ('privacy[8787635733]', '286958161406148'),  # Private
        #('privacy[8787635733]', '300645083384735'), # Public

        ]

        response = self.s.post('https://www.facebook.com/profile/async/edit/infotab/save/about_me/', headers=self.headers, params=params, data=data)



    def getAbout(self):

        params = (
            ('section', 'bio'),
        )


        # Match for m.facebook.com since it is not rate limited.
        response = self.s.get('https://m.facebook.com/'+self.username+'/about', headers=self.headers, params=params)

        m = re.search('_5cds _2lcw _5cdt">(.*?)</div', response.content)

        if m:
            return m.group(1)
        else:
            return None

    # Sets the fb_dtsg parameter. Updates the object and returns the value
    def setFbDtsg(self):
        response = self.s.get('https://facebook.com/'+self.username+'/about', headers=self.headers)

        m = re.search('fb_dtsg" value="(.*?)"', response.content)

        if m:
            self.fb_dtsg = m.group(1)
            return m.group(1)
        else:
            return None

    # Sets the usernamer, updates the object and returns the value
    def setUsername(self):
        response = self.s.get('https://facebook.com/', headers=self.headers)

        m = re.search('_2s25 _606w" href="https://www.facebook.com/(.*?)"', response.content)

        if m:
            self.username = m.group(1)
            return m.group(1)
        else:
            return None


    def send(self, data):
        print "Acting server, trying to send " + str(len(data)) + " bytes"

        encodedData = base64.b64encode(data)

        chunks = [ encodedData[i:i+self.MAXSIZE] for i in xrange(0,len(encodedData),self.MAXSIZE) ]
        print "Splitting data into ", len(chunks), "chunks, ", self.MAXSIZE, "bytes each"


        print "Sending init"
        self.changeAbout( self.initStr + " " + str(len(chunks)) )

        while(1):
            time.sleep(0.2)
            print "Waiting for ack"
	    about = self.getAbout()
            if about == "ack":
                break

        for chunk in chunks:
            time.sleep(0.2)
            #print "Uploading ", chunk

            print "Uploading", len(chunk), "bytes"
            hash_object = hashlib.sha256(chunk)
            hex_dig = hash_object.hexdigest()
            print(hex_dig)

            self.changeAbout( chunk )
            while(1):
                time.sleep(0.2)
                print "Waiting for ack"
                about = self.getAbout()
                if about == "ack":
                    break

        print "Done, sending done"
        self.changeAbout("done")
        return len(data)

    def recv(self):
        print "Acting client, connecting to facebook"
        recvData = ""

        while(1):
            time.sleep(0.2)
            print "Waiting for init"
	    about = self.getAbout()
            if self.initStr in about:
                (aboutInit, aboutChunks) = about.split()
                print "Got int, sending ack. ", aboutChunks, " chunks in total"
                self.changeAbout( "ack" )
                break

        while(1):
            time.sleep(0.2)
            print "Waiting for data"
	    about = self.getAbout()
            if about == "done":
                print "All done"
                break
            if about and about != "ack":
                print "Got", len(about), "bytes"

                hash_object = hashlib.sha256(about)
                hex_dig = hash_object.hexdigest()
                print(hex_dig)

                recvData += base64.b64decode(about)
                #f.write( base64.b64decode(about) )
                #f.flush()
                self.changeAbout( "ack" )

        return recvData




