/* CTF Challenge: easy-fmt-got
 *
 * Vulnerability : Format-string bug in a printf(buf) loop
 * Binary flags  : Partial RELRO (GOT writable), No PIE, No stack canary
 *
 * Exploitation path:
 * 1. Leak libc address via format string (puts@GOT)
 * 2. Calculate system() and /bin/sh address from libc base
 * 3. Overwrite printf@GOT -> system
 * 4. Send "/bin/sh" to trigger system("/bin/sh")
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

int goldenfreddy = 67;

int main(void) {
    char buf[64];
    setup();

    puts("Can you get a shell?");
    puts("Solve my challenge");

    do {
        fgets(buf, sizeof(buf), stdin);
        printf(buf);               /* <-- format-string vulnerability */
    } while (strncmp(buf, "quit", 4) != 0);

    return 0;
}