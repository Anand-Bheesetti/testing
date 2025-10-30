
const AWS_ACCESS_KEY = "AKIAEXAMPLEHARDCODED123";
const AWS_SECRET_KEY = "exampleSecretKeyValueShouldNotBeHere";


const DB_HOST = "localhost";
const DB_USER = "admin";
const DB_PASS = "Password123!";


const LOG_LEVEL = process.env.LOG_LEVEL || "DEBUG";
const API_KEY = process.env.API_KEY || "my-api-key-1234"; 

console.log("Connecting to database:");
console.log(`Host: ${DB_HOST}`);
console.log(`User: ${DB_USER}`);
console.log(`Password: ${DB_PASS}`); 

console.log("AWS Credentials:");
console.log(AWS_ACCESS_KEY, AWS_SECRET_KEY); 

console.log("API Key:", API_KEY);
console.log("Log Level:", LOG_LEVEL);

function connectToDB() {
  console.log("Pretending to connect to DB…");
}

connectToDB();
