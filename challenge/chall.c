

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

    /* Leak system() address so participants don't need a libc database */
    printf("Gift for you: %p\n", (void *)system);

    do {
        fgets(buf, sizeof(buf), stdin);
        printf(buf);               /* <-- format-string vulnerability */
    } while (strncmp(buf, "quit", 4) != 0);

    return 0;
}
