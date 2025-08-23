from core.driver import WebDriverSession, ELEMENT_TYPES
from os import getenv
from core.log import getLogger

logger = getLogger()

paths = {
        "get_email_notif": (ELEMENT_TYPES['css'], '.trackEmail'),
        "buttons": (ELEMENT_TYPES['css'], '.button'),
        "email_input": (ELEMENT_TYPES['id'], 'emailAddressInput'),
        "add_email_btn": (ELEMENT_TYPES['css'], '.add'),
        "submit_btn": (ELEMENT_TYPES['id'], 'submitButton'),
        "dialog": (ELEMENT_TYPES['tag'], 'track-email-dialog'),
        "dialog_1_3": (ELEMENT_TYPES['id'], 'track-emails-dialog'),
        "dialog_2": (ELEMENT_TYPES['id'], 'add-emails-dialog'),
}

def executeScript(sesh: WebDriverSession, tracking_nums):
        for carrier, tNum in tracking_nums:
                link = "https://www.canadapost-postescanada.ca/track-reperage/en#/search?searchFor={}".format(tNum)
                sesh.get(link)

                sesh.click.path(paths['get_email_notif'])
                
                waitDialogLoad(sesh)

                dialog_txt = getDialogText(sesh)
                if "You can add or remove email addresses" in dialog_txt:
                        passDialog1(sesh)
                
                waitDialogLoad(sesh)

                email_inputs = sesh.find.all(paths['email_input'])
                if len(email_inputs) == 1:
                        sesh.click.path(paths['add_email_btn'])

                email_inputs = sesh.find.all(paths['email_input'])
                assert len(email_inputs) > 2
                sesh.input.element(email_inputs[0], getenv('CANADAPOST_EMAIL1'))
                sesh.input.element(email_inputs[1], getenv('CANADAPOST_EMAIL2'))

                sesh.click.path(paths['submit_btn'])

                waitDialogLoad(sesh)

                logger.info('completed sign up for order {}'.format(tNum))


def getDialogText(sesh: WebDriverSession):
        txt = ''
        while not txt:
                txt = sesh.read.text(paths['dialog'])

        return txt

def waitDialogLoad(sesh: WebDriverSession):
        txt = getDialogText(sesh)
        while "Get email notifications" not in txt:
                txt = getDialogText(sesh)
        return 

def passDialog1(sesh: WebDriverSession):
        waitDialogLoad(sesh)
        btns = sesh.filter.byText(sesh.find.all(paths['buttons']), 'Add')

        assert len(btns) == 1
        sesh.click.element(btns[0])

def emailInputCountCheck(sesh: WebDriverSession):
        input_elmnts = sesh.find.all(paths['email_input'])
        return len(input_elmnts) > 2