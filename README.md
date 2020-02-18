# Cryptography-Assignment 2

## Basic requirement of assignment
- Implement a secure socket progamming 
- A `server-socket.py` which is your file system
- A `client-socket.py `which is your front end
- Provide integrity, confidentiality and non-repudiation protection

## About The Project
Cryptography-Assignment 2 is a extension of our PSEC socket programming. The project is for students to reinforce the cryptographic concepts and information security principles covered in ACG.

### Context
- Your team has developed an automated menu system with a whole list of features.
- With overwhelming demand and limited budget, the management has decided to setup additional outlets outside SP, using public WIFI (e.g. Wireless@SG).

### Tasks to be done:
- Enhance the design
- Implement security mechanisms needed to ensure the
**confidentiality**, **integrity**, and **non-repudiation**
- Other enhancement features

## Dependencies
The following tools should be installed before starting:
- [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/)
- [Captcha](https://pypi.org/project/captcha/)
- [pycryptodomex](https://pypi.org/project/pycryptodomex/)
- [Cryptography](https://pypi.org/project/cryptography/)

## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

You should update pip to the latest version to improve the functionality or be obligatory for security purposes.
* pip
```sh
python -m pip install --upgrade pip
```

### Installation

1. Install OpenPyXL module
```sh
pip install openpyxl
```
2. Install Captcha module
```sh
pip install captcha
```
3. Install PyCryptodomex
```sh
pip3 install pycryptodomex
```
4. Install Cryptography
```sh
pip3 install cryptography
```

### Usage
To start trying out the code, run the python files in this order. Run each of them in a different terminal.
```sh
# terminal 0
python3 server-socket.py
```
```sh
# terminal 1
python3 client-socket.py
```

#### Login Details
| UID | Username | Password |
| ----|:--------:|:--------:|
|  01 | root     | toor     |
|  02 | John     | John     |

## License
Currently there is no licensing to this project.

## Contributor
- [junyan-l](https://github.com/junyan-l)