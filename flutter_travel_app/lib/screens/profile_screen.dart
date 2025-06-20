import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';

class ProfileScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final authData = Provider.of<AuthProvider>(context);
    final user = authData.user;
    final isAuth = authData.isAuth;

    return Scaffold(
      appBar: AppBar(
        title: Text('Профиль'),
        backgroundColor: Theme.of(context).primaryColor,
      ),
      body: isAuth && user != null
          ? SingleChildScrollView(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundColor: Theme.of(context).primaryColor,
                    backgroundImage: user.avatarUrl != null
                        ? NetworkImage(user.avatarUrl!)
                        : null,
                    child: user.avatarUrl == null
                        ? Text(
                            user.fullName.substring(0, 1).toUpperCase(),
                            style: TextStyle(
                              fontSize: 40,
                              color: Colors.white,
                            ),
                          )
                        : null,
                  ),
                  SizedBox(height: 16),
                  Text(
                    user.fullName,
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    user.email,
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey,
                    ),
                  ),
                  if (user.phone != null) ...[
                    SizedBox(height: 8),
                    Text(
                      user.phone!,
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.grey,
                      ),
                    ),
                  ],
                  SizedBox(height: 32),
                  _buildProfileMenuItem(
                    context,
                    'Мои бронирования',
                    Icons.list_alt,
                    () {
                      // Navigate to bookings
                    },
                  ),
                  _buildProfileMenuItem(
                    context,
                    'Избранное',
                    Icons.favorite,
                    () {
                      // Navigate to favorites
                    },
                  ),
                  _buildProfileMenuItem(
                    context,
                    'Мои отзывы',
                    Icons.star,
                    () {
                      // Navigate to reviews
                    },
                  ),
                  _buildProfileMenuItem(
                    context,
                    'Настройки',
                    Icons.settings,
                    () {
                      // Navigate to settings
                    },
                  ),
                  SizedBox(height: 32),
                  ElevatedButton(
                    onPressed: () {
                      authData.logout();
                    },
                    style: ElevatedButton.styleFrom(
                      primary: Colors.red,
                      minimumSize: Size(double.infinity, 50),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: Text(
                      'Выйти',
                      style: TextStyle(fontSize: 16),
                    ),
                  ),
                ],
              ),
            )
          : _buildLoginScreen(context),
    );
  }

  Widget _buildProfileMenuItem(
    BuildContext context,
    String title,
    IconData icon,
    VoidCallback onTap,
  ) {
    return Card(
      margin: EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        leading: Icon(
          icon,
          color: Theme.of(context).primaryColor,
        ),
        title: Text(title),
        trailing: Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }

  Widget _buildLoginScreen(BuildContext context) {
    final _emailController = TextEditingController();
    final _passwordController = TextEditingController();
    final authData = Provider.of<AuthProvider>(context);
    final isLoading = authData.isLoading;
    final error = authData.error;

    return Padding(
      padding: EdgeInsets.all(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Text(
            'Вход в личный кабинет',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 32),
          TextField(
            controller: _emailController,
            decoration: InputDecoration(
              labelText: 'Email',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              prefixIcon: Icon(Icons.email),
            ),
            keyboardType: TextInputType.emailAddress,
          ),
          SizedBox(height: 16),
          TextField(
            controller: _passwordController,
            decoration: InputDecoration(
              labelText: 'Пароль',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              prefixIcon: Icon(Icons.lock),
            ),
            obscureText: true,
          ),
          if (error != null) ...[
            SizedBox(height: 16),
            Text(
              error,
              style: TextStyle(
                color: Colors.red,
              ),
            ),
          ],
          SizedBox(height: 24),
          isLoading
              ? CircularProgressIndicator()
              : ElevatedButton(
                  onPressed: () {
                    authData.login(
                      _emailController.text,
                      _passwordController.text,
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    primary: Theme.of(context).primaryColor,
                    minimumSize: Size(double.infinity, 50),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    'Войти',
                    style: TextStyle(fontSize: 16),
                  ),
                ),
          SizedBox(height: 16),
          TextButton(
            onPressed: () {
              // Navigate to registration
            },
            child: Text('Зарегистрироваться'),
          ),
        ],
      ),
    );
  }
} 