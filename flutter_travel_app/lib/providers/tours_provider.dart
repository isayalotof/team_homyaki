import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/tour.dart';

class ToursProvider with ChangeNotifier {
  List<Tour> _tours = [];
  List<Tour> _promotedTours = [];
  bool _isLoading = false;
  String? _error;

  List<Tour> get tours => [..._tours];
  List<Tour> get promotedTours => [..._promotedTours];
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchTours({
    String? search,
    double? minPrice,
    double? maxPrice,
    int? promotion,
    String? sortBy,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final queryParams = <String, String>{};
      
      if (search != null && search.isNotEmpty) {
        queryParams['search'] = search;
      }
      if (minPrice != null) {
        queryParams['min_price'] = minPrice.toString();
      }
      if (maxPrice != null) {
        queryParams['max_price'] = maxPrice.toString();
      }
      if (promotion != null) {
        queryParams['promotion'] = promotion.toString();
      }
      if (sortBy != null) {
        queryParams['sort_by'] = sortBy;
      }

      final uri = Uri.http('localhost:8000', '/api/v1/tours', queryParams);
      
      final response = await http.get(uri);
      
      if (response.statusCode != 200) {
        throw Exception('Ошибка при загрузке туров');
      }
      
      final responseData = json.decode(response.body);
      final List<Tour> loadedTours = [];
      
      for (var tourData in responseData['items']) {
        loadedTours.add(Tour.fromJson(tourData));
      }
      
      _tours = loadedTours;
      _isLoading = false;
      notifyListeners();
    } catch (error) {
      _error = error.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchPromotedTours() async {
    _isLoading = true;
    notifyListeners();

    try {
      final uri = Uri.http('localhost:8000', '/api/v1/tours', {'promotion': '1'});
      
      final response = await http.get(uri);
      
      if (response.statusCode != 200) {
        throw Exception('Ошибка при загрузке акционных туров');
      }
      
      final responseData = json.decode(response.body);
      final List<Tour> loadedTours = [];
      
      for (var tourData in responseData['items']) {
        loadedTours.add(Tour.fromJson(tourData));
      }
      
      _promotedTours = loadedTours;
      _isLoading = false;
      notifyListeners();
    } catch (error) {
      _error = error.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> searchToursByWizard(Map<String, dynamic> wizardData) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/v1/search/wizard'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(wizardData),
      );
      
      if (response.statusCode != 200) {
        throw Exception('Ошибка при поиске туров');
      }
      
      final responseData = json.decode(response.body);
      final List<Tour> loadedTours = [];
      
      for (var tourData in responseData['tours']) {
        loadedTours.add(Tour.fromJson(tourData));
      }
      
      _tours = loadedTours;
      _isLoading = false;
      notifyListeners();
    } catch (error) {
      _error = error.toString();
      _isLoading = false;
      notifyListeners();
    }
  }

  Tour findById(int id) {
    return _tours.firstWhere((tour) => tour.id == id);
  }
} 