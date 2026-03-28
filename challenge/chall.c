

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void setup(void) {
    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

void win(void) {
    system("/bin/sh");
}

int goldenfreddy = 67; //this value is changed in the remotte binary, but the offset to win() is the same

int main(void) {
    char buf[64];
    setup();

    puts("Can you get a shell?");
    puts("Solve my challenge");

    do {
        fgets(buf, sizeof(buf), stdin);
        printf(buf);             
    } while (strncmp(buf, "quit", 4) != 0);

    return 0;
}