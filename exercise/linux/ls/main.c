#include <stdio.h>
#include <stdlib.h>
#include <popt.h>

struct opt_ {
    int long_listing = 0;
    int help = 0;
}opt;


struct poptOption opt_table[] = {
{ "list", 'l', POPT_ARG_NONE, &(opt.long_listing), 0, "long listing format", NULL },
{ "help", '\0', POPT_ARG_NONE, &(opt.help), 0, "show this message", NULL },
{ "NULL", '\0', POPT_ARG_NONE, NULL, 0, NULL, NULL }
};

int main(int argc, char * argv[])
{
    int rc;
    poptContext opt_ctx;
    opt_ctx = poptGetContext("ls", argc, argv,
                                     opt_table, 0);
    if ((rc = poptGetNextOpt(opt_ctx)) < -1) {
        fprintf(stderr, "%s: %s\n",
                poptBadOption(opt_ctx))
    }
    printf("Hello World!\n");
    return 0;
}

