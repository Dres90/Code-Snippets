from time import sleep

class AmazonChecker():

    def __init__(self, driver):
        self.driver = driver

    def login(self):
        self.driver.get('https://www.amazon.fr')
        sleep(50)

    def checkAndBuy(self, link):
        self.driver.get(link)
        sleep(1)   
        try:
            cookiesButton = self.driver.find_elements_by_xpath('//*[@id="sp-cc-accept"]')
            if len(cookiesButton) > 0:
                cookiesButton[0].click()
                sleep(2)
            buyNow = self.driver.find_element_by_xpath('//*[@id="add-to-cart-button"]')
            buyNow.click()
            sleep(2)
            return True
        except Exception as e:
            print(e)
            return False