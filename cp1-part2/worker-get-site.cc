#include <ctime>
#include <iomanip>

#include <curl/curl.h>

#include "worker-get-site.h"
#include "SocketHelper.h"
#include "worker.h"

using namespace std;
// Create a function to run a GET command on a URL input, port 80?
#define PORT "80"
#define MAXDATASIZE 1000
//#define URL "ns-mn1.cse.nd.edu"
//#define PATH "/cse30264/ads/file1.html"

static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    size_t totalSize = size * nmemb;
    std::string* buffer = static_cast<std::string*>(userp);
    buffer->append(static_cast<char*>(contents), totalSize);
    return totalSize;
}

/**
 * When a CHECK request is received from a client, process the request
 *
 * @param[in] url     URL to check for the received regex pattern
 * @param[in] pattern Regex pattern to scan site contents for
 * @param[in] siteID  Site ID used for logging purposes
 *
 * @return 0 for pattern found in site contents, 1 for pattern not found, and 2 for request error
 */
std::pair<int, std::string> read_Website(char * url, std::string match, const char* siteID, std::string logLocation) {
    char* domain = new char[BUFSIZ];
    char* path = new char[BUFSIZ];

    sscanf(url, "http://%[^/]/%[^\n]", domain, path);
    const char* cMatch = match.c_str();

    CURL *curl;
    CURLcode res;

    string readBuff;

    std::time_t rawtime;
    std::time(&rawtime);
    std::tm* timeinfo = std::localtime(&rawtime);

    std::ostringstream oss;
    oss << std::put_time(timeinfo, "%Y-%m-%d-%H-%M-%S");
    std::string formatted_time = oss.str();

    curl = curl_easy_init();
    if(curl)
    {
      long my_scope_id;
      curl_easy_setopt(curl, CURLOPT_URL, url);
      curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
      curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuff);

      /* Perform the request, res gets the return code */
      res = curl_easy_perform(curl);
      /* Check for errors */
      if(res != CURLE_OK)
      {
        fprintf(stderr, "curl_easy_perform() failed: %s\n",
                curl_easy_strerror(res));
        return std::make_pair(2, formatted_time);
      }

      /* always cleanup */
      curl_easy_cleanup(curl);
    }

    int pid = fork();
    int status;
    if (pid == 0) {
        std::vector<const char*> args;
        args.push_back("python3");
        args.push_back("findMatches.py");
        args.push_back(readBuff.c_str());
        args.push_back(cMatch);
        args.push_back(logLocation.c_str());
        args.push_back(siteID);
        args.push_back(formatted_time.c_str());
        args.push_back(nullptr);

        execvp(args[0], const_cast<char* const*>(args.data()));
    } else if (pid < 0) {
        fprintf(stderr, "ERROR: Fork failed");
        return std::make_pair(2, formatted_time);
    } else {
        waitpid(pid, &status, 0);
    }

    if (WIFEXITED(status))
    {
      return std::make_pair(int(WEXITSTATUS(status)), formatted_time);
    }
    else
    {
      return std::make_pair(2, formatted_time);
    }
}