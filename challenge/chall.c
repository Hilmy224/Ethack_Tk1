/* CTF Challenge: easy-fmt-got
 *
 * Vulnerability : Format-string bug in a printf(buf) loop
 * Binary flags  : Partial RELRO (GOT writable), No PIE, No stack canary
 *
 * Easier path:
 * 1. Overwrite printf@GOT with win() (fixed address because no PIE).
 * 2. Send any line to trigger the hijacked call.
 * 3. win() executes /bin/sh.
 */

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

int main(void) {
    char buf[64];

    setup();

    puts("=== easy-fmt-got ===");
    printf("hint: win() is at %p\n", (void *)win);
    puts("Overwrite printf@GOT -> win, then send anything.");

    do {
        fgets(buf, sizeof(buf), stdin);
        printf(buf);               /* <-- format-string vulnerability */
    } while (strncmp(buf, "quit", 4) != 0);

    return 0;
}
