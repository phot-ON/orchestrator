import os

class constants():
    def __init__(self):
        self.stateLength = 12

        #self.BASE_URL_SAT = "https://st.tail3e2bc4.ts.net"
        #self.BASE_URL_GAR = "https://pc.tail3e2bc4.ts.net"
        #self.BASE_URL_MY = "https://db.tail3e2bc4.ts.net"

        self.BASE_URL_SAT = os.environ["DB_SERVER"]
        self.BASE_URL_GAR = os.environ["AUTH_SERVER"]
        self.BASE_URL_MY = os.environ["REDIRECT_SERVER"]