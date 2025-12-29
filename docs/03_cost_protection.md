# Cost Protection

This service makes API calls to LLMs. Each API call costs money. This document outlines strategies to prevent accidental, unneccessary spend.

## API Delay

The system ensures there is a minimum of MINIMAL_API_CALL_DELAY seconds ( defined in envs ) between each API call. This ensures that should there be some sort of broken logic, which leads to API calls being called repeatedly, then it is easier to catch while debugging and at the very least it takes a while to build up large costs.

## No auto refill of credits

In Claude, there is currently not configured any auto refill of credits. So should there be a big bug, which spends all the credits then there is an upper limit to the cost.

## Max api calls

For each maze there is a maximum amount of API calls, as defined by MAX_API_CALLS set in environment variables. If it is exceeded, the solver will throw an exception and stop.

## Test protections

Running tests should not make unmocked calls to the LLM. There are 2 levels of protection against this. First the system always overrides the keys at start of pytest, to ensure that if the key is attempted used it will be used with an invalid value. Secondly, the API function to call calude is auto mocked. Should any test needs to mock it with a particular result, then it can remock the test to return another result.