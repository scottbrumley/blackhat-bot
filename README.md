Credentials File (private/creds.sh):
Create a File in a private sub directory called creds.sh
```#!/usr/bin/env bash
   
   BOT_TOKEN="YOUR BOT KEY HERE"
   APP_TOKEN="YOUR APP KEY HERE"
   DEMISTO_URL="YOUR XSOAR API URL HERE"
   DEMISTO_API_KEY="YOUR XSOAR API KEY HERE"
   
   TEST_BOT_TOKEN="YOUR BOT KEY HERE"
   TEST_APP_TOKEN="YOUR APP KEY HERE"
   TEST_DEMISTO_URL="YOUR XSOAR API URL HERE"
   TEST_DEMISTO_API_KEY="YOUR XSOAR API KEY HERE"
   
   
   export TEST_BOT_TOKEN
   export TEST_APP_TOKEN
   export TEST_DEMISTO_URL
   export TEST_DEMISTO_API_KEY
   
   
   export BOT_TOKEN
   export APP_TOKEN
   export DEMISTO_URL
   export DEMISTO_API_KEY
```