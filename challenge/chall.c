/* CTF Challenge: fmt-got
 *
 * Vulnerability : Format-string bug in a printf(buf) loop
 * Binary flags  : Partial RELRO (GOT writable), No PIE, No stack canary
 *
 * The binary leaks the runtime address of system() on startup so that
 * participants do not need a separate libc leak.  The format-string loop
 * then lets them overwrite the printf GOT entry with system(), after which
 * sending "/bin/sh" calls system("/bin/sh") and spawns a shell.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void setup(void) {
    setvbuf(stdin,  NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

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
