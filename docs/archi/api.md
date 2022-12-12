# API Gateway Architecture

This schema refers to the [API Gateway module](../modules/api.md).

Important consideration:

- add_endpoint can be called multiple time duplicating corresponding resources.
- In practice, a lot of those 'resources' are just made to link function, methods and the api.
- Each endpoint generate:
    - One LambdaFunction
    - One associated role
    - One methode
    - One log group

![Screenshot](../img/API.jpg)
