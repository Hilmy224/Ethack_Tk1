#include <stdio.h>
#include <string.h>

#define MAX_SPECS    3
#define FLAG_ARG_POS 5

static const char secret_flag[] = "AmmongUs{ILoveHiyuki}";

static int count_specifiers(const char *s) {
    int n = 0;
    for (; *s != '\0'; ++s) {
        if (*s == '%') {
            if (*(s + 1) == '%') { ++s; continue; }
            ++n;
        }
    }
    return n;
}

int main(void) {
    char fmt[32];

    setvbuf(stdout, NULL, _IONBF, 0);
    puts("Now where we?");

    fgets(fmt, sizeof fmt, stdin);
    fmt[strcspn(fmt, "\n")] = '\0';

    if (count_specifiers(fmt) > MAX_SPECS) {
        puts("No.");
        return 1;
    }

    /* Four dummy args push the flag to position FLAG_ARG_POS (5) */
    printf(fmt, "Not here I wonder where?",0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0, secret_flag);
    putchar('\n');

    return 0;
}