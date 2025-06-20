import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'screens/tours_screen.dart';
import 'screens/search_screen.dart';
import 'screens/promotions_screen.dart';
import 'screens/profile_screen.dart';
import 'providers/auth_provider.dart';
import 'providers/tours_provider.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ToursProvider()),
      ],
      child: MaterialApp(
        title: 'Путешествуй по России',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          primaryColor: Color(0xFF2C3E50),
          colorScheme: ColorScheme.light(
            primary: Color(0xFF2C3E50),
            secondary: Color(0xFF3498DB),
          ),
          fontFamily: 'Roboto',
          textTheme: TextTheme(
            displayLarge: TextStyle(fontSize: 24.0, fontWeight: FontWeight.bold),
            displayMedium: TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
            bodyLarge: TextStyle(fontSize: 16.0),
            bodyMedium: TextStyle(fontSize: 14.0),
          ),
        ),
        home: MainScreen(),
        routes: {
          '/tours': (context) => ToursScreen(),
          '/search': (context) => SearchScreen(),
          '/promotions': (context) => PromotionsScreen(),
          '/profile': (context) => ProfileScreen(),
        },
      ),
    );
  }
}

class MainScreen extends StatefulWidget {
  @override
  _MainScreenState createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;
  
  final List<Widget> _screens = [
    HomeScreen(),
    ToursScreen(),
    SearchScreen(),
    PromotionsScreen(),
    ProfileScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Путешествуй по России'),
        backgroundColor: Theme.of(context).primaryColor,
      ),
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Главная',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.explore),
            label: 'Туры',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.search),
            label: 'Поиск',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.local_offer),
            label: 'Акции',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Профиль',
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Theme.of(context).colorScheme.secondary,
        unselectedItemColor: Colors.grey,
        onTap: _onItemTapped,
        type: BottomNavigationBarType.fixed,
      ),
    );
  }
} 