class User {
  final int id;
  final String email;
  final String fullName;
  final String? phone;
  final String? avatarUrl;
  final bool isAdmin;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    this.phone,
    this.avatarUrl,
    this.isAdmin = false,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      fullName: json['full_name'],
      phone: json['phone'],
      avatarUrl: json['avatar_url'],
      isAdmin: json['is_admin'] ?? false,
    );
  }
} 