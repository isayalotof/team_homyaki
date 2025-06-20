import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';

class AuthProvider with ChangeNotifier {
  User? _user;
  String? _token;
  bool _isLoading = false;
  String? _error;

  bool get isAuth => _token != null;
  bool get isLoading => _isLoading;
  User? get user => _user;
  String? get error => _error;

  Future<bool> tryAutoLogin() async {
    final prefs = await SharedPreferences.getInstance();
    if (!prefs.containsKey('userData')) {
      return false;
    }
    
    final userData = json.decode(prefs.getString('userData')!);
    final expiryDate = DateTime.parse(userData['expiryDate']);
    
    if (expiryDate.isBefore(DateTime.now())) {
      return false;
    }
    
    _token = userData['token'];
    _user = User(
      id: userData['id'],
      email: userData['email'],
      fullName: userData['fullName'],
      phone: userData['phone'],
      avatarUrl: userData['avatarUrl'],
      isAdmin: userData['isAdmin'],
    );
    
    notifyListeners();
    return true;
  }

  Future<void> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/v1/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );
      
      final responseData = json.decode(response.body);
      
      if (response.statusCode != 200) {
        throw Exception(responseData['detail'] ?? 'Ошибка при входе в систему');
      }
      
      _token = responseData['access_token'];
      _user = User.fromJson(responseData['user']);
      
      final prefs = await SharedPreferences.getInstance();
      final userData = json.encode({
        'token': _token,
        'id': _user!.id,
        'email': _user!.email,
        'fullName': _user!.fullName,
        'phone': _user!.phone,
        'avatarUrl': _user!.avatarUrl,
        'isAdmin': _user!.isAdmin,
        'expiryDate': DateTime.now().add(Duration(days: 7)).toIso8601String(),
      });
      
      prefs.setString('userData', userData);
      
      _isLoading = false;
      notifyListeners();
    } catch (error) {
      _error = error.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> register(String email, String password, String fullName) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/v1/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
          'full_name': fullName,
        }),
      );
      
      final responseData = json.decode(response.body);
      
      if (response.statusCode != 201) {
        throw Exception(responseData['detail'] ?? 'Ошибка при регистрации');
      }
      
      _isLoading = false;
      notifyListeners();
    } catch (error) {
      _error = error.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _token = null;
    _user = null;
    
    final prefs = await SharedPreferences.getInstance();
    prefs.remove('userData');
    
    notifyListeners();
  }
} 