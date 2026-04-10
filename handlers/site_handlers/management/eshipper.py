from core.driver.locator import Locator, ElementTypes
from core.log import getLogger

from os import getenv

logger = getLogger(__name__)

paths = {
    "go_login_page_btn": Locator(ElementTypes.id, "login"),
    "username_input": Locator(ElementTypes.id, "username"),
    "password_input": Locator(ElementTypes.id, "password"),
    "login_button": Locator(ElementTypes.css, '[aria-label="Login Button"]'),
    "usernameText": Locator(ElementTypes.css, ".userNameText"),
    "options_button": Locator(ElementTypes.css, ".dot-menu"),
    "options_menu_buttons": Locator(ElementTypes.css, ".men-item-btn"),
    "export_options_container": Locator(ElementTypes.css, ".file-cards"),
    "export_options": Locator(ElementTypes.tag, "li"),
    "export_button": Locator(ElementTypes.css, '[aria-label="Export Track Button"]'),
}


def login(sesh):
    sesh.nav.get("https://www.eshipper.com/")

    sesh.click.by_locator(paths["go_login_page_btn"])

    sesh.tabControl.focusNewestTab()

    sesh.input.by_locator(paths["username_input"], getenv("ESHIPPER_USER"))
    sesh.input.by_locator(paths["password_input"], getenv("ESHIPPER_PW"))

    sesh.click.by_locator(paths["login_button"])

    sesh.wait.element_located(paths["usernameText"])


def scrape(sesh):
    login(sesh)

    sesh.nav.get("https://ww2.eshipper.com/customer/tracking")

    sesh.click.by_locator(paths["options_button"])

    # can't find export button explicitly (consistently), so just going with second options menu item (1 - print, 2 - export)
    menu_btns = sesh.find.all(paths["options_menu_buttons"])
    _, export_btn = menu_btns

    sesh.click.element(export_btn)

    # can't find the csv option explicitly (consistently), so just going with first link (1 - csv, 2 - xl)
    export_options_container = sesh.find.element(paths["export_options_container"])
    export_options = sesh.find.all_in_parent(
        export_options_container, paths["export_options"]
    )

    export_as_csv, _ = export_options
    sesh.click.element(export_as_csv)

    sesh.click.by_locator(paths["export_button"])
