#include <stdio.h>
#include <string.h>

typedef int (*cmd_handler_t)(const char* args);

static int cmd_ping(const char* args) { return 0; }
static int cmd_status(const char* args) { return 0; }
static int cmd_quit(const char* args) { return 1; }

struct command_entry {
    const char* name;
    cmd_handler_t handler;
};

/* Command Dispatch Table */
static const struct command_entry dispatch_table[] = {
    {"PING", cmd_ping},
    {"STATUS", cmd_status},
    {"QUIT", cmd_quit},
    {NULL, NULL}
};
