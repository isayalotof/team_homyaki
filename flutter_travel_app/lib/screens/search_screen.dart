import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/tours_provider.dart';

class SearchScreen extends StatefulWidget {
  @override
  _SearchScreenState createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _formKey = GlobalKey<FormState>();
  
  String _selectedCountry = '';
  DateTime? _startDate;
  int _duration = 7;
  String _tourType = '';
  double _priceMax = 100000;
  int _hotelStars = 3;
  String _mealType = 'BB';
  int _adults = 2;
  int _children = 0;
  
  final List<String> _countries = [
    'Россия',
    'Абхазия',
    'Армения',
    'Беларусь',
    'Грузия',
    'Казахстан',
  ];
  
  final List<String> _tourTypes = [
    'Пляжный отдых',
    'Экскурсионный',
    'Горнолыжный',
    'Оздоровительный',
    'Круиз',
  ];
  
  final List<String> _mealTypes = [
    'BB', // Завтраки
    'HB', // Полупансион
    'FB', // Полный пансион
    'AI', // Всё включено
    'UAI', // Ультра всё включено
  ];

  void _submitForm() {
    if (!_formKey.currentState!.validate()) {
      return;
    }
    
    final wizardData = {
      'destinations': [
        {
          'id': 1,
          'name': _selectedCountry,
          'type': 'country',
        }
      ],
      'dates': {
        'start': _startDate != null ? _startDate!.toIso8601String().split('T')[0] : null,
        'end': _startDate != null 
            ? DateTime(_startDate!.year, _startDate!.month, _startDate!.day + _duration).toIso8601String().split('T')[0] 
            : null,
      },
      'tourists': {
        'adults': _adults,
        'children': _children,
      },
      'preferences': {
        'tour_type': _tourType,
        'price_max': _priceMax,
      },
      'accommodation': {
        'hotel_stars': _hotelStars,
        'meal_type': _mealType,
      },
    };
    
    Provider.of<ToursProvider>(context, listen: false)
        .searchToursByWizard(wizardData)
        .then((_) {
      Navigator.of(context).pushReplacementNamed('/tours');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Конструктор туров'),
        backgroundColor: Theme.of(context).primaryColor,
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildSectionTitle('Куда хотите поехать?'),
              _buildCountryDropdown(),
              SizedBox(height: 24),
              
              _buildSectionTitle('Когда планируете путешествие?'),
              _buildDateSelector(),
              SizedBox(height: 16),
              _buildDurationSlider(),
              SizedBox(height: 24),
              
              _buildSectionTitle('Тип отдыха'),
              _buildTourTypeSelector(),
              SizedBox(height: 24),
              
              _buildSectionTitle('Бюджет'),
              _buildPriceSlider(),
              SizedBox(height: 24),
              
              _buildSectionTitle('Размещение'),
              _buildStarsSelector(),
              SizedBox(height: 16),
              _buildMealTypeSelector(),
              SizedBox(height: 24),
              
              _buildSectionTitle('Туристы'),
              _buildTouristsCounter(),
              SizedBox(height: 32),
              
              _buildSubmitButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildCountryDropdown() {
    return DropdownButtonFormField<String>(
      decoration: InputDecoration(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        hintText: 'Выберите страну',
      ),
      value: _selectedCountry.isEmpty ? null : _selectedCountry,
      items: _countries.map((country) {
        return DropdownMenuItem(
          value: country,
          child: Text(country),
        );
      }).toList(),
      onChanged: (value) {
        setState(() {
          _selectedCountry = value!;
        });
      },
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Пожалуйста, выберите страну';
        }
        return null;
      },
    );
  }

  Widget _buildDateSelector() {
    return InkWell(
      onTap: () async {
        final pickedDate = await showDatePicker(
          context: context,
          initialDate: _startDate ?? DateTime.now().add(Duration(days: 7)),
          firstDate: DateTime.now(),
          lastDate: DateTime.now().add(Duration(days: 365)),
        );
        
        if (pickedDate != null) {
          setState(() {
            _startDate = pickedDate;
          });
        }
      },
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Icon(Icons.calendar_today),
            SizedBox(width: 16),
            Text(
              _startDate == null
                  ? 'Выберите дату начала'
                  : '${_startDate!.day}.${_startDate!.month}.${_startDate!.year}',
              style: TextStyle(fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDurationSlider() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Продолжительность: $_duration дней'),
        Slider(
          value: _duration.toDouble(),
          min: 1,
          max: 30,
          divisions: 29,
          label: '$_duration дней',
          onChanged: (value) {
            setState(() {
              _duration = value.round();
            });
          },
        ),
      ],
    );
  }

  Widget _buildTourTypeSelector() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: _tourTypes.map((type) {
        return ChoiceChip(
          label: Text(type),
          selected: _tourType == type,
          onSelected: (selected) {
            setState(() {
              _tourType = selected ? type : '';
            });
          },
        );
      }).toList(),
    );
  }

  Widget _buildPriceSlider() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Максимальная цена: ${_priceMax.round()} ₽'),
        Slider(
          value: _priceMax,
          min: 10000,
          max: 500000,
          divisions: 49,
          label: '${_priceMax.round()} ₽',
          onChanged: (value) {
            setState(() {
              _priceMax = value;
            });
          },
        ),
      ],
    );
  }

  Widget _buildStarsSelector() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(5, (index) {
        return IconButton(
          icon: Icon(
            Icons.star,
            color: _hotelStars > index ? Colors.amber : Colors.grey,
          ),
          onPressed: () {
            setState(() {
              _hotelStars = index + 1;
            });
          },
        );
      }),
    );
  }

  Widget _buildMealTypeSelector() {
    return DropdownButtonFormField<String>(
      decoration: InputDecoration(
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        hintText: 'Тип питания',
      ),
      value: _mealType,
      items: _mealTypes.map((type) {
        String label;
        switch (type) {
          case 'BB':
            label = 'BB - Завтраки';
            break;
          case 'HB':
            label = 'HB - Полупансион';
            break;
          case 'FB':
            label = 'FB - Полный пансион';
            break;
          case 'AI':
            label = 'AI - Всё включено';
            break;
          case 'UAI':
            label = 'UAI - Ультра всё включено';
            break;
          default:
            label = type;
        }
        
        return DropdownMenuItem(
          value: type,
          child: Text(label),
        );
      }).toList(),
      onChanged: (value) {
        setState(() {
          _mealType = value!;
        });
      },
    );
  }

  Widget _buildTouristsCounter() {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Взрослые'),
            Row(
              children: [
                IconButton(
                  icon: Icon(Icons.remove),
                  onPressed: _adults > 1
                      ? () {
                          setState(() {
                            _adults--;
                          });
                        }
                      : null,
                ),
                Text('$_adults'),
                IconButton(
                  icon: Icon(Icons.add),
                  onPressed: () {
                    setState(() {
                      _adults++;
                    });
                  },
                ),
              ],
            ),
          ],
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Дети'),
            Row(
              children: [
                IconButton(
                  icon: Icon(Icons.remove),
                  onPressed: _children > 0
                      ? () {
                          setState(() {
                            _children--;
                          });
                        }
                      : null,
                ),
                Text('$_children'),
                IconButton(
                  icon: Icon(Icons.add),
                  onPressed: () {
                    setState(() {
                      _children++;
                    });
                  },
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSubmitButton() {
    final toursData = Provider.of<ToursProvider>(context);
    final isLoading = toursData.isLoading;
    
    return Container(
      width: double.infinity,
      height: 50,
      child: isLoading
          ? Center(child: CircularProgressIndicator())
          : ElevatedButton(
              onPressed: _submitForm,
              style: ElevatedButton.styleFrom(
                primary: Theme.of(context).primaryColor,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: Text(
                'Найти туры',
                style: TextStyle(fontSize: 18),
              ),
            ),
    );
  }
} 