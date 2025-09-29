#include "server-get-site.h"
#include "SocketHelper.h"
#include "server.h"

using namespace std;
// Create a function to run a GET command on a URL input, port 80?
#define PORT "80"
#define MAXDATASIZE 1000
//#define URL "ns-mn1.cse.nd.edu"
//#define PATH "/cse30264/ads/file1.html"

/**
 * When a CHECK request is received from a client, process the request
 *
 * @param[in] url     URL to check for the received regex pattern
 * @param[in] pattern Regex pattern to scan site contents for
 * @param[in] siteID  Site ID used for logging purposes
 *
 * @return 0 for pattern not found, 1 for pattern found in site contents
 */
int read_Website(char * url, string match, const char* siteID) {
    char* domain = new char[BUFSIZ];
    char* path = new char[BUFSIZ];

    sscanf(url, "http://%[^/]/%[^\n]", domain, path);
    string output = create_Out_Socket(domain, path);
    const char* cOutput = output.c_str();
    const char* cMatch = match.c_str();
    int pid = fork();
    int status;
    if (pid == 0) {
        std::vector<const char*> args;
        args.push_back("python3");
        args.push_back("findMatches.py");
        args.push_back(cOutput);
        args.push_back(cMatch);
        args.push_back(siteID);
        args.push_back(nullptr);

        execvp(args[0], const_cast<char* const*>(args.data()));
    } else if (pid < 0) {
        fprintf(stderr, "ERROR: Fork failed");
        return -1;
    } else {
        waitpid(pid, &status, 0);
    }

    return status;
}

void *get_in_addr(struct sockaddr *sa)
{
    if (sa->sa_family == AF_INET) {
        return &(((struct sockaddr_in*)sa)->sin_addr);
    }

    return &(((struct sockaddr_in6*)sa)->sin6_addr);
}

string create_Out_Socket(char * address, char * directory) {
    int numbytes;
    char buf[MAXDATASIZE];
    struct addrinfo hints, *servinfo, *p;
    int rv, sockfd;
    char s[INET6_ADDRSTRLEN];

    const char * hostname = address;
    const char * port = PORT;
    const char * path = directory;

    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if ((rv = getaddrinfo(hostname, port, &hints, &servinfo)) != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return "1";
    }

    // loop through all the results and connect to the first we can
    for(p = servinfo; p != NULL; p = p->ai_next) {
        if ((sockfd = socket(p->ai_family, p->ai_socktype,
                p->ai_protocol)) == -1) {
            perror("client: socket");
            continue;
        }

        inet_ntop(p->ai_family,
            get_in_addr((struct sockaddr *)p->ai_addr),
            s, sizeof s);
        printf("client: attempting connection to %s\n", s);

        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == -1) {
            perror("client: connect");
            close(sockfd);
            continue;
        }

        break;
    }

    if (p == NULL) {
        fprintf(stderr, "client: failed to connect\n");
        return "2";
    }

    inet_ntop(p->ai_family,
            get_in_addr((struct sockaddr *)p->ai_addr),
            s, sizeof s);
    printf("client: connected to %s\n", s);

    freeaddrinfo(servinfo); // all done with this structure

    // Build HTTP request
    char request[512];
    snprintf(request, sizeof(request),
             "GET %s HTTP/1.1\r\n"
             "Host: %s\r\n"
             "Connection: close\r\n\r\n",
             path, hostname);

    send(sockfd, request, sizeof(request), 0);

    if ((numbytes = recv(sockfd, buf, MAXDATASIZE-1, 0)) == -1) {
        perror("recv");
        exit(1);
    }

    buf[numbytes] = '\0';

    printf("client: received '%s'\n",buf);

    close(sockfd);

    return buf;

}

// int test_main(int argc, char * argv[]) {
// 	string buffer;
//     char * ad_string = new char[BUFSIZ];
//     char* url = new char[BUFSIZ];
//     char* path = new char[BUFSIZ];

//     sscanf(argv[1], "http://%[^/]/%[^\n]", url, path);
//     ad_string = argv[2];
// 	return read_Website(url, ad_string, path);

// }
