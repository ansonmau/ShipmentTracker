from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

logger = getLogger()

paths = {
        "get_email_notif": (ELEMENT_TYPES['css'], '.trackEmail'),
        "buttons": (ELEMENT_TYPES['css'], '.button'),
        "email_input": (ELEMENT_TYPES['id'], 'emailAddressInput'),
        "submit_btn": (ELEMENT_TYPES['id'], 'submitButton'),
        "dialog": (ELEMENT_TYPES['tag'], 'track-email-dialog'),
        "dialog_1_3": (ELEMENT_TYPES['id'], 'track-emails-dialog'),
        "dialog_2": (ELEMENT_TYPES['id'], 'add-emails-dialog'),
}

def executeScript(sesh: WebDriverSession, tracking_nums):
        for carrier, tNum in tracking_nums:
                link = "https://www.canadapost-postescanada.ca/track-reperage/en#/search?searchFor={}".format(tNum)
                sesh.get(link)

                sesh.click(paths['get_email_notif'])
                
                waitForDialog(sesh)
                dialog_txt = getDialogText(sesh)
                
                if "You can add or remove email addresses" in dialog_txt:
                        passDialog1(sesh)
                

                waitForDialog(sesh)
                sesh.inputText(paths['email_input'], getenv("CANADAPOST_EMAIL1"))
                sesh.click(paths['submit_btn'])

                waitForDialog(sesh)
                logger.info('completed sign up for order {}'.format(tNum))
                input()


def getDialogText(sesh: WebDriverSession):
        txt = ''
        while not txt:
                txt = sesh.getText(paths['dialog'])

        return txt

def waitForDialog(sesh: WebDriverSession):
        txt = getDialogText(sesh)
        while "Get email notifications" not in txt:
                txt = getDialogText(sesh)
        return 

def passDialog1(sesh: WebDriverSession):
        waitForDialog(sesh)
        btns = sesh.filterElementsByText(sesh.findAll(paths['buttons']), 'Add')

        assert len(btns) == 1
        sesh.element_click(btns[0])