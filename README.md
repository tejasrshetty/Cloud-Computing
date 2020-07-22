The architecture consists of AWS services like Lambda API Gateway, Lex, Dynamo DB, Elastic Search, SNS and S3.

The flow of execution is as follows:

The user enters his perferences on the website hosted on a static S3 bucket (They include restaurant type, location, cuisine, time etc).
The request is then sent over API Gateway to a Lambda function which acts as the code hook for the Lex bot that handles all the above conversation ( ie taking in user's preferences).

Once all values are received, a second lambda function is triggered which checks for matches in the database. Elastic Search is used to store the cuisine and Restaurant ID. 
The restaurants whose cuisines match are then fetched from dynamo db along with other filters like type, location, time etc.)

The restaurants which match the criteria are sent to the end user via a message on his/her mobile phone via SNS.
