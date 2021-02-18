from proxy_checker import ProxyChecker
import random
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
# you may get different number of proxy when  you run this at


class Proxies:
    def __init__(self):
        self.req_proxy = RequestProxy()
        self.proxies = self.req_proxy.get_proxy_list()  # this will create proxy list
        self.total = len(self.proxies)
        self.getExtraProxies()
        pass

    def getExtraProxies(self):
        addrs = []
        with open("proxy_list.csv", 'r') as f:
            lines = f.readlines()
        for line in lines:
            items = line.split()
            if len(items) < 2:
                continue
            if len(items[0].split('.')) == 4:
                addrs.append(items[0]+":"+items[1])
        self.addrs = addrs

    def getProxy(self):
        # if(self.pointer+1 > self.total):
        #     self.renewProxies()
        #     self.pointer = 0
        rand_n = random.randint(0, self.total-1)
        prox = self.proxies[rand_n]
        if self.isValid(prox) == False:
            rand_n = random.randint(0, len(self.addrs)-1)
            return self.addrs[rand_n]
        # while self.isValid(prox) == False:
        #     rand_n = random.randint(0, self.total-1)
        #     prox = self.proxies[rand_n]
        #     print(prox.get_address())
        #     pass
        # self.pointer += 1

        return prox

    def isValid(self, prox):
        checker = ProxyChecker()
        return checker.check_proxy(prox.get_address())

    def getAddresses(self):
        addrs = [x.get_address() for x in self.proxies]
        return addrs


g_prox = Proxies()
