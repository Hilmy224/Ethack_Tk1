/* flag - execute-only binary with an intentionally simple format-string bug.
 *
 * The flag is embedded as a global variable.  The binary asks for a format
 * string and uses it directly in printf(fmt, secret_flag), so %s can leak it.
 */

#include <stdio.h>
#include <stdlib.h>

static const char secret_flag[] = "CTF{easy_fstring_s_leak}";

static void setup(void) {
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

int main(void) {
    char fmt[128];

    setup();

    puts("Now where we?");


    if (!fgets(fmt, sizeof(fmt), stdin)) {
        return 1;
    }

    printf(fmt, secret_flag); 
    return 0;
}
