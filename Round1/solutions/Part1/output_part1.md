# Bosch-TheThree

> Install "wine" if you in Linux and want to execute file `.exe`

## Challenge 1:

- Run file `server.exe` and go to "http://localhost:8080/login/{password}".

- Solution:

![](https://imgtr.ee/images/2023/05/19/26iP2.png)

- Check password

![](https://imgtr.ee/images/2023/05/21/2tzKL.png)

> The flag would be `301349920110`

## Challenge 2:

- Run file `get-flag.exe` with the arguments is the name of the user

- Note that we reverse the file `get-flag.exe` and find this line

![](https://imgtr.ee/images/2023/05/21/2tEwM.png)

> The flag would be `P`

## Challenge 3:

- Run file `get-flag.exe` with the arguments is the name of the user name

- Again, reverse the file `get-flag.exe` we got this

![](https://imgtr.ee/images/2023/05/21/2tu31.png)

- Easy to buffer overflow by passing a string

```bash
    get-flag.exe iiiiiiiiiiiiia
```

- It will be return the flag `Flag is M4G1CW0RD`

![](https://imgtr.ee/images/2023/05/21/2tf0X.png)

> The flag would be `M4G1CW0RD`

![]()

## CHallenge 4:

- Run file `exploit.py`

> cat `exploit.py`

```python
record = [{
    "plaintext": "001333b95c1edb3ef145a4a9f52f7b9a",
    "ciphertext": "bb28b7e3f49355b7a236ad2745d68cb25",
    "iv" : "70359350f329603f0da99a1f9151d844"
}]

from pwn import xor
p_1 = bytes.from_hex("001333b95c1edb3ef145a4a9f52f7b9a")
c_1 = bytes.from_hex("bb28b7e3f49355b7a236ad2745d68cb25")
c_2 = bytes.from_hex("fdfa29ef6547ef37a64a1bb2c629c5cc")

p_2 = xor(xor(c_1, c_2), p_1)

print(p_2)
```

> python `exploit.py`

- The output would look like

```cmd
    b'Obdiplostemonnus'
```

> The flag would be `Obdiplostemonnus`

## Challenge 5

- SHA-1 digest of the flag is 0x074df9a7789c61abe1bfde590c743a7c29fef60d

- After reverse the given digest

![](https://imgtr.ee/images/2023/05/21/2tPq3.png)

> The flag would be `weakpassword`

## Challenge 6

- The ciphertext is `kxblqpuxkjubxocfjancnlqwxuxprnb`

- After decrypting the ciphertext, we got

![](https://imgtr.ee/images/2023/05/21/2tjcl.png)

> The flag would be `boschglobalsoftwaretechnologies`
