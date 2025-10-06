#include <cstring>
#include <iostream>
#include <netinet/in.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>
#include <errno.h>
#include <string>
#include <cstdint>
#include <string.h>
#include <netdb.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <regex>

#define PORT "80"
#define MAXDATASIZE 1000

std::string create_Out_Socket(char * address, char * directory);

int read_Website(char * url, std::string match);

void *get_in_addr(struct sockaddr *sa);

std::string create_Out_Socket(char * address);

