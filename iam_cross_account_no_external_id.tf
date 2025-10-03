
resource "aws_iam_role" "cross_account_role_violation" {
  name = "vendor-access-role-violation"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          
          AWS = "arn:aws:iam::987654321098:root" 
        },
        Action = "sts:AssumeRole"
       
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "s3_access_attachment" {
  role       = aws_iam_role.cross_account_role_violation.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}
