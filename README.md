# URL Shortener
Study repository to implement an URL shortener with infrastructure.

# Functional Requirements
## Core Requirements
> URL Shortening: Users should be able to input a long URL and receive a unique, shortened alias. The shortened URL should use a compact format with English letters and digits to save space and ensure uniqueness.
> URL Redirection: When users access a shortened URL, the service should redirect them seamlessly to the original URL with minimal delay.
> Link Analytics: The system should be able to track the number of times each shortened URL is accessed to provide insights into link usage.

## Out of Scope
> Authentication and Authorization for users (e.g., who can create URLs or access certain analytics).
> Expiration or deletion of URLs by users.
> Advanced analytics beyond click counts (e.g., geographic tracking or device types).

## Scale Requirements
> 100M Daily Active Users
> Read:write ratio = 100: 1
> Data retention for 5 years
> Assuming 1 million write requests per day
> Assuming each entry is about 500 bytes

## Non-Functional Requirements
> High Availability: The service should ensure that all URLs are accessible 24/7, with minimal downtime, so users can reliably reach their destinations.
> Low Latency: URL redirections should occur almost instantly, ideally in under a few milliseconds, to provide a seamless experience for users.
> High Durability: Shortened URLs should be stored reliably so they persist over time, even across server failures, ensuring long-term accessibility.
> Security: The service must prevent malicious links from being created and protect user data, implementing safeguards against spam, abuse, and unauthorized access to sensitive information.

# API Endpoints
### POST /api/urls/shorten
Shorten a given long URL and return the shortened URL.

Request Body:
{
  "longUrl": "http://example.com"
}

Response Body:
{
  "shortUrl": "http://urlshort.ly/abcd"
}

### GET /api/urls/{shortUrl}
Redirect to the original long URL using the shortened URL.

Response Body:
{
  "longUrl": "http://example.com"
}



TODOS:
* Make docker work
* Implement aws
* Test terraform
* Implement authentication
* Load tests