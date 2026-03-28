/* flag – SUID helper that prints the flag.
 *
 * This binary is compiled and installed with the SUID bit set so that it
 * runs as root regardless of who invokes it.  The flag file (/flag.txt) is
 * owned by root and mode 0400, so regular users cannot read it directly –
 * they must exploit the main challenge binary to obtain a shell and then
 * execute this program.
 */

#include <stdio.h>
#include <stdlib.h>

int main(void) {
    puts("Now where were we?");

    FILE *f = fopen("/flag.txt", "r");
    if (!f) {
        perror("fopen /flag.txt");
        return 1;
    }

    char buf[256];
    while (fgets(buf, sizeof(buf), f)) {
        fputs(buf, stdout);
    }

    fclose(f);
    return 0;
}
