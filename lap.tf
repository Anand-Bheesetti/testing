


resource "aws_iam_group" "app_admins" {
  name = "app-admins"
}
resource "aws_iam_policy_attachment" "admin_policy" {
  group      = aws_iam_group.app_admins.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess" 
}


resource "aws_iam_group" "app_readonly" {
  name = "app-readonly"
}
resource "aws_iam_policy_attachment" "readonly_policy" {
  group      = aws_iam_group.app_readonly.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess" 
}


resource "aws_iam_user" "app_user" {
  name = "app-deployer"
}


resource "aws_iam_user_group_membership" "user_membership_violation" {
  user   = aws_iam_user.app_user.name
  groups = [
    aws_iam_group.app_admins.name,
    aws_iam_group.app_readonly.name 
  ]
}
