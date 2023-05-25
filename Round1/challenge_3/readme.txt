// This challenge can be solved by exploiting buffer overflow
// This flag has a score of 5.
// Beginning by running get-flag.exe. The source code of get-flag.exe is given below.

#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    int magic_word = 0xdeadbeef;
    char name[10] = {0};

    if (argc != 2)
    {
        printf("Expect one input argument.\r\n");
        return 1;
    }

   (void)memcpy(name, argv[1], 0x10);

    printf("Hello %s\r\n", name);
    if (magic_word == 0x69696969)
    {
        printf("Flag is %s", FLAG);
    }

    return 0;
}
