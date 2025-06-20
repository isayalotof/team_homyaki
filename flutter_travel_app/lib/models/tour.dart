class Tour {
  final int id;
  final String name;
  final String description;
  final double price;
  final String imageUrl;
  final String country;
  final String city;
  final DateTime startDate;
  final DateTime endDate;
  final int duration;
  final int hotelStars;
  final String mealType;
  final bool isPromoted;

  Tour({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.imageUrl,
    required this.country,
    required this.city,
    required this.startDate,
    required this.endDate,
    required this.duration,
    required this.hotelStars,
    required this.mealType,
    this.isPromoted = false,
  });

  factory Tour.fromJson(Map<String, dynamic> json) {
    return Tour(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      price: json['price'].toDouble(),
      imageUrl: json['image_url'] ?? 'assets/images/placeholder.jpg',
      country: json['country'],
      city: json['city'],
      startDate: DateTime.parse(json['start_date']),
      endDate: DateTime.parse(json['end_date']),
      duration: json['duration'],
      hotelStars: json['hotel_stars'] ?? 3,
      mealType: json['meal_type'] ?? 'BB',
      isPromoted: json['is_promoted'] ?? false,
    );
  }
} 