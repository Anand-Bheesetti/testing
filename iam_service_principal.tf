
resource "aws_iam_role" "lambda_exec_role" {
  name = "my-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_dynamo_policy_violation" {
  name = "lambda-dynamo-policy-violation"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect   = "Allow",
      Action   = "dynamodb:GetItem",
      
      Resource = "arn:aws:dynamodb:us-east-1:123456789012:table/*" 
    }]
  })
}
