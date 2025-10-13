#pragma once

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

#define MAXDATASIZE 1000

std::pair<int, std::string> read_Website(char * url, std::string match, const char* siteID, std::string logLocation);

void *get_in_addr(struct sockaddr *sa);

