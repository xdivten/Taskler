curl -i -v 'http://localhost:8080/csrf/' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Origin: http://localhost:3000' \
  -H 'Pragma: no-cache' \
  -H 'Referer: http://localhost:3000/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"'

'''
Set-Cookie:  csrftoken=1di3r9j0JIQZiy4LD6gA15RH3RDhSr8t; expires=Thu, 11 Dec 2025 17:19:41 GMT; Max-Age=31449600; Path=/; SameSite=Lax
{"X-CSRFToken":"Y7oyjBfKjsRbNu7Tsyy5JNaiJmRFDr9XPawrAAoAS0x0VS1uVuEvAIRPC3kMlI7g"}
'''

curl -i 'http://localhost:8080/_allauth/browser/v1/auth/signup' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Type: application/json' \
  -H 'Origin: http://localhost:3000' \
  -H 'Pragma: no-cache' \
  -H 'Referer: http://localhost:3000/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-site' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'X-CSRFToken: 1di3r9j0JIQZiy4LD6gA15RH3RDhSr8t' \
  -b "csrftoken=1di3r9j0JIQZiy4LD6gA15RH3RDhSr8t" \
  --data-raw '{"email":"test@gmail.com","password":"123123"}'
