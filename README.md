# Shipment Tracker


Shipment Tracker is a Selenium-based automation tool for automating email update registration for various Canadian delivery services

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

## Table of Contents
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [Features](#features)
- [Screenshot](#screenshot)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Contact](#contact)

## Purpose
This is an internal tool built for Infonec, although it will work for anyone following a similar workflow. 

**Time and Energy Saver** - 
This application can save employees multiple (3-4) hours per week of the mundane, soul sucking work of registering emails (sometimes doing hundreds of these a day).

**Happier Customers** -
On top of saving time clicking through each website to register emails, it heavily **reduces the amount of errors** (e.g. missed packages) which has a time-saving ripple effect, as a reduction in errors here leads to a reduction in time spent by Customer Service soothing customer's worries, and therefore reduces the number of dissatisfied customers.


## Prerequisites
- **Operating System:** Windows / Linux / Mac
- **Required Browser:** Chrome (Beta versions supported)

## Features
- **Internal Tracking**: 
    - Remembers packages that failed to track and will retry them (can be turned off) 
    - Ignores packages it previously successfully tracked
- **Fine-tuned Controls:** modify the process as you see fit
	- Choose exactly which services to run
	- Choose how many days backwards it searches
	- Custom Chrome version
	- Custom Chrome location
	- Delay between actions (for slower internet connections)
- Supported package management services: **Freightcom**, **eShipper**, **EMS**
- Supported delivery services: **Federal Express**, **Purolator**, **Canada Post**, **UPS**, **Canpar**

## Screenshot

![screenshot](https://i.imgur.com/qOrs9UP.png)

## Installation
1. Go to releases page
2. Downloaded latest executable
3. Move executable into its own folder
4. Run the application

## Usage
> [!IMPORTANT]
> You must have an account for the package management services listed above. The whole purpose of this application is to automate email registration on these services.
1. Enter login details into *folder_the_app_is_in/data/keys.env* (see [Keys Configuration](#keys-file))
2. Select the sources (package mangement services) you would like it to automate tracking for.
3. Select the carriers (delivery services) that you would like.
4. Select settings (see [Configuration](#configuration))
5. Press Run!

## Configuration

### In-Application Settings

| Setting                          | Purpose / Usage                                                                                                                                                         |
|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Ignore already tracked shipments | Searches through local memory of packages that are already being tracked and skips the ones that are.                                                                   |
| Re-use data from previous run    | Re-uses the scraped data from package management services from the previous time the application was ran. Useful for scraping once and automating carriers individually |
| Day Difference                   | How many days backwards should the application look when scraping for packages to track                                                                                 |
| Wait time                        | How long (in seconds) should the application wait inbetween actions by default? Some actions are locked to specific times. Useful for varying internet connections.     |
| Custom Chrome location           | Allows you to set a custom location for the Chrome used by Selenium. Useful if you have multiple installations of chrome.                                               |
| Custom Chrome version            | Allows you to set a custom version. Useful for systems running older versions of Chrome                                                                                 |

### Keys File

> [!IMPORTANT]
> - If a setting is ticked on the application, **all associated keys must be present in the env file**
> - This goes into the file *keys.env* @ *folder_the_app_is_in/data/keys.env*

> [!NOTE]
> Env files follow the format: **KEY="VALUE"**

#### Package Management Websites

| Service    | Key                                |
|------------|------------------------------------|
| Eshipper   | ESHIPPER_USER <br> ESHIPPER_PW     |
| Freightcom | FREIGHTCOM_USER <br> FREIGHTCOM_PW |
| EMS        | EMS_USER <br> EMS_PW               |

#### Delivery Websites

| Service         | Key                                      |
|-----------------|------------------------------------------|
| Canada Post     | CANADAPOST_EMAIL1 <br> CANADAPOST_EMAIL2 |
| UPS             | UPS_EMAIL1 <br> UPS_EMAIL2               |
| Purolator       | PUROLATOR_NAME <br> PUROLATOR_EMAIL      |
| Federal Express | FEDEX_EMAIL                              |
| Canpar          | CANPAR_EMAIL1 <br> CANPAR_EMAIL2         |

#### Example
```
ESHIPPER_USER="eshipper1"
ESHIPPER_PW="eshipperpassword123"
FREIGHTCOM_USER="fcUsername"
FREIGHTCOM_PW="fcPasswordXD"
FEDEX_EMAIL="hi@fakemail.com"
CANPAR_EMAIL1="hi@fakemail.com"
CANPAR_EMAIL2="hi_there@fakemail.com"
```

## Contact
I am open to new experiences / opportunities. Please feel free to reach out.

** Anson Mau ** // anson.mau@proton.me // [LinkedIn](https://www.linkedin.com/in/ansonmau/) // [GitHub](https://github.com/ansonmau)
