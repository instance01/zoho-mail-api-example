This shows how to use OAuth with Zoho to send an E-Mail from a custom domain.
It uses Flask for catching the OAuth tokens (redirect url) and to show how to send an E-Mail from a server using a custom domain.
It also includes a thread that periodically updates the access token using the refresh token, since it becomes invalid after one hour.

## How to set up

1. Setup in the Zoho API Console as redirect uri: http://127.0.0.1:5000/callback/
2. Copy the client id and secret into `send_mail.py` at the top.
3. Configure which email to send to etc. at the top of `send_mail.py`.

Be very careful with the API domain - currently I use .eu everywhere. If you need to use .com, change both API urls!

## How to use

Click the URL printed on console.
This only has to be done once when setting up the server.
Afterwards you can go to the sendmail endpoint (127.0.0.1:5000/sendmail/) to automatically send an E-Mail using your custom domain.
