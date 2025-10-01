
resource "aws_iam_role_policy" "s3_admin_policy_violation" {
  name = "s3-admin-access-violation"
  role = "arn:aws:iam::123456789012:role/MyApplicationRole" // Dummy role ARN for context

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "s3:*",
        Resource = "*"
      }
    ]
  })
}
